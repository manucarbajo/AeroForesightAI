"""P3.11: Die Lauf-Argumente sind ein Vertrag, kein Namensraum (2026-09-05).

`save_run_outputs`, `build_run_args` und `save_run_metadata` bekamen bis dahin
ein `argparse.Namespace` bzw. `types.SimpleNamespace` und lasen daraus mit
``getattr(args, "feld", False)``. Kein Modell sagte, was ein Startpfad liefern
muss; `dashboard/run_launcher.py` baute den Namensraum an **zwei** Stellen von
Hand mit je fünfzehn Feldern.

**Der Schaden ist zweimal eingetreten, beide Male am Rechenmodus** — also an der
Angabe, wie ein Lauf gerechnet wurde:

* ``mock_llm`` fehlte, und jeder Dashboard-Lauf «Ohne Sprachmodell» wurde als
  vollwertiger LLM-Lauf protokolliert (zweite Gegenprobe zu P0.6).
* ``llm_narrative`` wurde von `build_run_args` **gar nicht mitkopiert**; aus
  ``deterministic_with_llm_narrative`` wurde beim Durchreichen
  ``deterministic_only``.

Der zweite Fall ist erst bei der Umsetzung von P3.11 aufgefallen — er war
latent, weil heute kein Pfad diese Kombination durch `build_run_args` schickt.
**Latent heißt nicht harmlos:** Er wäre bei der nächsten Änderung aufgewacht,
und ein Lauf hätte im eigenen Artefakt etwas Falsches über sich behauptet.
"""

from __future__ import annotations

import ast
from pathlib import Path
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from src.models.run_models import RunArgs, run_args_from
from src.reporting.output_writer.provenance import compute_mode

ROOT = Path(__file__).resolve().parent.parent

#: Die Module, die aus den Lauf-Argumenten ein Artefakt schreiben.
SCHREIBER = (
    Path("src") / "reporting" / "output_writer" / "metadata.py",
    Path("src") / "reporting" / "output_writer" / "provenance.py",
    Path("src") / "run_simulation.py",
)


def _vollstaendig(**overrides) -> RunArgs:
    basis = dict(
        model="llama3.2",
        base_url="http://127.0.0.1:11434",
        temperature=0.7,
        max_tokens=2048,
        mock_llm=False,
        deterministic_only=False,
        llm_narrative=False,
    )
    basis.update(overrides)
    return RunArgs(**basis)


class TestEinFehlendesFeldFaelltAuf:
    """Die tragende Zusage: eine Auslassung ist keine Aussage mehr."""

    @pytest.mark.parametrize("feld", ["mock_llm", "deterministic_only", "llm_narrative"])
    def test_ein_feld_des_rechenmodus_ist_pflicht(self, feld):
        """**Die Trennlinie des Modells.** Ein falscher Wert *hier* lässt den Lauf
        im eigenen Artefakt etwas Falsches über sich behaupten."""

        felder = {
            k: v for k, v in _vollstaendig().model_dump().items() if k != feld and v is not None
        }
        with pytest.raises(ValidationError, match=feld):
            RunArgs(**felder)

    def test_die_meldung_nennt_das_feld(self):
        with pytest.raises(ValidationError) as fehler:
            RunArgs(model="m", base_url="u", temperature=0.1, max_tokens=1)

        text = str(fehler.value)
        for feld in ("mock_llm", "deterministic_only", "llm_narrative"):
            assert feld in text, f"{feld} wird nicht genannt"

    def test_ein_tippfehler_im_feldnamen_faellt_auf(self):
        """`extra="forbid"`: Der Namensraum nahm alles entgegen, was man
        hineinschrieb — `deterministic_ony=True` hätte niemand bemerkt."""

        with pytest.raises(ValidationError, match="deterministic_ony"):
            _vollstaendig(deterministic_ony=True)

    def test_was_ein_lauf_nebenbei_tut_darf_fehlen(self):
        """Die Gegenrichtung. Wer alles zur Pflicht macht, erzeugt fünfzehn
        Felder, die jeder Aufrufer stumpf ausschreibt, und gewinnt nichts."""

        args = _vollstaendig()

        assert args.no_protocol is False
        assert args.no_scenarios is False
        assert args.run_index == 1
        assert args.seed is None


class TestDurchreichenVerliertNichts:
    """Der zweite, latente Befund — und warum er nicht harmlos war."""

    def test_llm_narrative_ueberlebt_das_bauen(self):
        """**Der Kern.** Vorher kopierte `build_run_args` das Feld nicht mit, und
        `compute_mode` sprang von `deterministic_with_llm_narrative` auf
        `deterministic_only`."""

        basis = _vollstaendig(deterministic_only=True, llm_narrative=True)

        gebaut = run_args_from(basis, run_index=2, seed=7)

        assert compute_mode(basis) == "deterministic_with_llm_narrative"
        assert compute_mode(gebaut) == compute_mode(basis)

    def test_jedes_feld_ueberlebt_das_bauen(self):
        """Nicht nur das eine: Geprüft wird die **ganze** Menge.

        Ein Test auf `llm_narrative` allein hätte den Befund von P0.6
        (`mock_llm`) nicht gefunden — und der nächste Verlust träfe ein drittes
        Feld.
        """

        basis = _vollstaendig(
            deterministic_only=True,
            llm_narrative=True,
            no_market=True,
            no_protocol=True,
            no_scenarios=True,
            no_run_scenario=True,
            redebedarf=True,
            quiet=True,
            simulation_name="Name",
            simulation_description="Beschreibung",
        )

        gebaut = run_args_from(basis, run_index=3, seed=9)

        unverandert = {
            k: v for k, v in basis.model_dump().items() if k not in ("run_index", "seed")
        }
        assert {
            k: v for k, v in gebaut.model_dump().items() if k not in ("run_index", "seed")
        } == unverandert
        assert (gebaut.run_index, gebaut.seed) == (3, 9)

    def test_ein_loser_namensraum_geht_weiterhin_hinein(self):
        """Die CLI reicht ihr `argparse.Namespace` durch — das muss es bleiben."""

        lose = SimpleNamespace(
            model="m",
            base_url="u",
            temperature=0.1,
            max_tokens=1,
            mock_llm=True,
            deterministic_only=False,
            llm_narrative=False,
        )

        assert run_args_from(lose, run_index=1, seed=None).model == "m"

    def test_was_das_modell_nicht_kennt_kommt_nicht_mit(self):
        """Ein Feld, das niemand liest, reist nicht stillschweigend mit.

        `sweep` und `run_id` standen so in den handgebauten Namensräumen —
        gesetzt, nie gelesen.
        """

        lose = SimpleNamespace(
            model="m",
            base_url="u",
            temperature=0.1,
            max_tokens=1,
            mock_llm=True,
            deterministic_only=False,
            llm_narrative=False,
            sweep="business_as_usual",
        )

        assert not hasattr(run_args_from(lose, run_index=1, seed=None), "sweep")


class TestJedeSignaturSagtWasSieLiefert:
    """P3.15: Eine Annotation, die ihrem Rumpf widerspricht, hebelt Invariante 4 aus.

    **Der Befund war kein Tippfehler, sondern eine halbe Umstellung.** P3.11 hat
    `sweep_metadata_args` von einem `SimpleNamespace` auf `RunArgs` umgestellt und
    die Signatur stehen lassen: ``-> SimpleNamespace``. Damit sagte sie einem
    Leser und jedem Werkzeug, das Rückgabetypen auswertet, es käme ein formloser
    Namensraum heraus — genau die Aussage, gegen die P3.11 angetreten ist.

    **Warum `ruff` schwieg:** Die falsche Annotation hielt den Import
    ``from types import SimpleNamespace`` am Leben. Ein toter Import, der von
    einer Lüge benutzt wird, sieht wie ein lebender aus. Und das Projekt hat
    keinen Typprüfer — weder mypy noch pyright in `pyproject.toml` oder der CI —,
    also prüfte niemand die Annotation gegen das `return`.

    **Warum dieser Wächter die Erzeuger sucht statt sie aufzuzählen:** Eine Liste
    der drei heutigen Stellen fängt einen Rückfall an bekannter Stelle und
    übersieht die vierte. Gesucht wird deshalb am Syntaxbaum nach dem
    *Mechanismus* — jedes `return`, das ein `RunArgs` baut oder weitergibt —, und
    dann muss die Signatur dieser Funktion es auch sagen. Dieselbe Bauform wie
    bei Invariante 1 und beim Farbfundament.

    **Was er nicht ersetzt:** einen Typprüfer. Er deckt genau eine Familie ab,
    weil genau die einen Schaden angerichtet hat; die allgemeine Antwort steht
    als eigenes Paket in Phase 4.
    """

    #: Die Bäume, in denen ein Erzeuger stehen darf. `tests` bleibt draußen —
    #: dort baut jeder Test seine Vorlagen, und eine Annotation dort trägt keine
    #: Grenze.
    BAEUME = ("src", "dashboard")

    #: Was als «erzeugt Lauf-Argumente» gilt: der Konstruktor selbst und die
    #: eine Fabrik, die ihn füllt.
    ERZEUGER_NAMEN = {"RunArgs", "run_args_from"}

    @classmethod
    def _erzeuger(cls) -> list[tuple[Path, ast.FunctionDef]]:
        """Jede Funktion, deren `return` Lauf-Argumente liefert."""

        gefunden: list[tuple[Path, ast.FunctionDef]] = []
        for baum_name in cls.BAEUME:
            for pfad in sorted((ROOT / baum_name).rglob("*.py")):
                if "legacy" in pfad.parts:
                    continue
                baum = ast.parse(pfad.read_text(encoding="utf-8-sig"))
                for knoten in ast.walk(baum):
                    if not isinstance(knoten, ast.FunctionDef):
                        continue
                    for inner in ast.walk(knoten):
                        if not isinstance(inner, ast.Return) or inner.value is None:
                            continue
                        aufruf = inner.value
                        if not isinstance(aufruf, ast.Call):
                            continue
                        name = getattr(aufruf.func, "id", None) or getattr(
                            aufruf.func, "attr", None
                        )
                        if name in cls.ERZEUGER_NAMEN:
                            gefunden.append((pfad.relative_to(ROOT), knoten))
                            break
        return gefunden

    def test_es_gibt_ueberhaupt_erzeuger(self):
        """Ein Wächter, der nichts findet, könnte auch blind sein."""

        erzeuger = self._erzeuger()
        namen = {funktion.name for _, funktion in erzeuger}
        assert "sweep_metadata_args" in namen, (
            "Die Fundstelle des Befunds wird nicht mehr gefunden — dann prüft dieser "
            f"Wächter nichts. Gefunden: {sorted(namen)}"
        )
        assert len(erzeuger) >= 3, sorted(namen)

    def test_jeder_erzeuger_gibt_runargs_zurueck_und_sagt_es(self):
        befunde: list[str] = []
        for relativ, funktion in self._erzeuger():
            rueckgabe = funktion.returns
            gesagt = ast.unparse(rueckgabe) if rueckgabe is not None else "— keine —"
            if gesagt != "RunArgs":
                befunde.append(
                    f"{relativ.as_posix()}:{funktion.lineno} — {funktion.name}() "
                    f"liefert RunArgs, sagt aber «{gesagt}»"
                )

        assert not befunde, (
            "Diese Signaturen widersprechen ihrem Rumpf:\n  "
            + "\n  ".join(befunde)
            + "\n\nInvariante 4 hängt daran, dass die Typangabe stimmt: Wer hier "
            "etwas anderes liest als RunArgs, hält die Grenze für formlos."
        )

    def test_der_waechter_wuerde_die_luege_bemerken(self):
        """Nachgestellt wird die Form, in der der Befund wirklich stand."""

        quelle = "def f(x) -> SimpleNamespace:\n    return RunArgs(a=1)\n"
        baum = ast.parse(quelle)
        funktion = baum.body[0]
        assert isinstance(funktion, ast.FunctionDef)
        liefert_runargs = any(
            isinstance(k, ast.Return)
            and isinstance(k.value, ast.Call)
            and getattr(k.value.func, "id", None) == "RunArgs"
            for k in ast.walk(funktion)
        )
        assert liefert_runargs, "Der Wächter erkennt den Erzeuger nicht"
        assert (
            ast.unparse(funktion.returns) != "RunArgs"
        ), "Die nachgestellte Lüge sieht für den Wächter wie die Wahrheit aus"

    def test_und_die_rueckgabe_ist_zur_laufzeit_wirklich_eine(self):
        """Die Annotation zu prüfen ist Codelektüre — das hier ist die Messung.

        `sweep_metadata_args` ist der einzige Erzeuger, der sich ohne Aufbau
        rufen lässt; die anderen zwei brauchen einen Träger. Also wird er
        gerufen.
        """

        from src.orchestration.scenario_sweeps import sweep_metadata_args

        assert type(sweep_metadata_args()) is RunArgs

    def test_kein_parameter_ohne_wirkung(self):
        """`sweep_id` war unbenutzt, seit sein einziges Feld entfiel (P3.15).

        Zwei verschiedene Kennungen ergaben gemessen identische Argumente — ein
        Aufrufer übergab also eine Angabe in der Annahme, sie werde verwendet.
        Geprüft wird nicht «der Parameter ist weg», sondern die Eigenschaft, die
        ihn wertlos machte: **Der Aufruf trägt kein Argument, das nichts ändert.**

        **Bis P4.2 stand hier die Abkürzung dafür** — ``not signature().parameters``,
        also «gar kein Parameter». Das war dieselbe Zusage nur, solange es
        keinen gab, und es war die falsche Sorte Wächter: eine **Aufzählung**
        des heutigen Zustands statt der Eigenschaft dahinter. Am 2026-09-08 hat
        er deshalb einen Parameter gemeldet, der wirkt (``llm_narrative``
        entscheidet über ``compute_mode``) — die Meldung war formal richtig und
        sachlich falsch, und die eigene Fehlermeldung sagte bereits, was
        stattdessen gilt: «Wenn er wirkt, gehört ein Test daneben, der es
        zeigt.»

        **Jetzt wird gemessen.** Jeder boolesche Parameter wird umgelegt, und
        das Ergebnis muss sich ändern. Ein Parameter, für den sich keine Probe
        bilden lässt, lässt den Wächter ebenfalls rot werden — unmessbar ist
        hier kein Freibrief, sondern genau die Lage, aus der P3.15 kam.
        """

        import inspect

        from src.orchestration.scenario_sweeps import sweep_metadata_args

        signatur = inspect.signature(sweep_metadata_args)
        standard = sweep_metadata_args()
        wirkungslos: list[str] = []
        unmessbar: list[str] = []

        for name, parameter in signatur.parameters.items():
            if parameter.default is inspect.Parameter.empty or not isinstance(
                parameter.default, bool
            ):
                unmessbar.append(name)
                continue
            if sweep_metadata_args(**{name: not parameter.default}) == standard:
                wirkungslos.append(name)

        assert not unmessbar, (
            f"Für {unmessbar} lässt sich hier keine Probe bilden — der Wächter kann "
            "nicht sagen, ob der Parameter wirkt. Entweder er bekommt hier eine "
            "Probe, oder er gehört weg (P3.15)."
        )
        assert not wirkungslos, (
            f"{wirkungslos} ändert an den Lauf-Argumenten nichts. Ein Aufrufer "
            "übergibt das in der Annahme, es werde verwendet — genau der Zustand, "
            "aus dem P3.15 kam."
        )


class TestKeinSchreiberRaetMehr:
    """Ein `getattr(args, …, default)` in einem Schreiber ist eine zweite Quelle."""

    def test_kein_getattr_mit_rueckfall_auf_die_lauf_argumente(self):
        befunde: list[str] = []
        for relativ in SCHREIBER:
            baum = ast.parse((ROOT / relativ).read_text(encoding="utf-8"))
            for knoten in ast.walk(baum):
                if not (isinstance(knoten, ast.Call) and isinstance(knoten.func, ast.Name)):
                    continue
                if knoten.func.id != "getattr" or len(knoten.args) < 3:
                    continue
                ziel = knoten.args[0]
                if isinstance(ziel, ast.Name) and ziel.id == "args":
                    name = knoten.args[1]
                    feld = name.value if isinstance(name, ast.Constant) else "?"
                    befunde.append(f"{relativ.as_posix()}:{knoten.lineno} — {feld}")

        assert not befunde, (
            "Diese Stellen raten wieder einen Wert der Lauf-Argumente:\n  "
            + "\n  ".join(befunde)
            + "\n\nDer Vorgabewert gehört ins Modell, damit er an *einer* Stelle "
            "steht — sonst kann jede Stelle einen anderen haben."
        )

    def test_der_waechter_wuerde_einen_rueckfall_bemerken(self):
        """Nachgestellt wird die Form, in der der Befund wirklich stand."""

        quelle = 'x = bool(getattr(args, "mock_llm", False))\n'
        baum = ast.parse(quelle)
        treffer = [
            k
            for k in ast.walk(baum)
            if isinstance(k, ast.Call)
            and isinstance(k.func, ast.Name)
            and k.func.id == "getattr"
            and len(k.args) >= 3
        ]

        assert treffer, "Der Wächter erkennt die Form nicht, in der der Befund stand"

    def test_die_startpfade_bauen_ein_typisiertes_modell(self):
        """Nicht «es gibt das Modell», sondern «sie benutzen es».

        Geprüft am Syntaxbaum, weil ein Startpfad seinen Namensraum auch wieder
        von Hand bauen könnte, ohne dass ein Test es merkt.
        """

        for relativ in (
            Path("dashboard") / "run_launcher.py",
            Path("src") / "orchestration" / "scenario_sweeps.py",
        ):
            quelle = (ROOT / relativ).read_text(encoding="utf-8")
            baum = ast.parse(quelle)
            gebaut = {
                k.func.id
                for k in ast.walk(baum)
                if isinstance(k, ast.Call) and isinstance(k.func, ast.Name)
            }

            assert "RunArgs" in gebaut, f"{relativ.as_posix()} baut keine `RunArgs`"
            assert "SimpleNamespace" not in gebaut, (
                f"{relativ.as_posix()} baut wieder einen formlosen Namensraum — "
                "dann ist ein vergessenes Feld wieder von einem abgeschalteten "
                "nicht zu unterscheiden."
            )
