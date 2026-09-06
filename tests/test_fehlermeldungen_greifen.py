"""P3.3: Fehlerbehandlung, die nicht nur so aussieht (2026-09-05).

Drei Stellen, an denen der Code Fehlerbehandlung *hatte* und sie nicht *tat*:

1. **`langgraph_workflow`** trug ein ``try: pass`` mit einem ``except``, das nie
   feuern konnte. Die gemeinte freundliche Meldung bei fehlendem ``langgraph``
   blieb aus; stattdessen kam zwanzig Zeilen später ein roher ``ImportError``
   aus ``_build_parallel_stategraph``, wo der echte Import steht.
2. **`create_graph.py`** verschluckte mit ``except Exception: pass`` auch den
   Graph-Build-Fehler, den es zwei Zeilen darüber absichtlich re-raist — und
   schrieb danach ein ``graph.json`` samt ``Wrote …``. Ein Erfolg, der keiner
   war, und eine Datei, die eine Topologie behauptet, die so nicht baut.
3. **Die CLI.** Seit P0.3 weist ein Lauf mit kaputter Config sauber ab — im
   Dashboard als roter Kasten mit allen Befunden, auf der CLI als roher
   Python-Traceback: zwanzig Zeilen Stack, in denen die Meldung unterging, und
   kein sprechender Exit-Code. **Die Prüfung war richtig, ihre Darstellung
   nicht.**

Der dritte Fall ist der teuerste, weil er den häufigsten Weg betrifft, und er
kam erst aus der P0.1-Gegenprobe dazu.
"""

from __future__ import annotations

import ast
import builtins
import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.run_simulation import EXIT_KONFIGURATION
from src.validation import BEFUND_KOPF

REPO = Path(__file__).resolve().parent.parent


# --- Blick in den Syntaxbaum, nicht in den Text -----------------------------
#
# **Warum das hier steht und nicht `in quelle` genügt:** Der erste Anlauf dieser
# Datei prüfte mit Zeichenkettensuche — `"except Exception" not in huelle`,
# `rumpf.index("from langgraph")`. Drei von drei Zusagen schlugen an, und zwar an
# den **eigenen Erklärungen**: Die Kommentare und Docstrings beschreiben den
# alten Zustand und zitieren dabei `try: pass`, `except Exception` und
# `get_llm()`. Ein Wächter, den eine Erklärung über ihn selbst umlenken kann, ist
# keiner — dieselbe Lehre wie bei den AST-Wächtern in `tests/test_web_theme.py`
# und `tests/test_cost_pressure_source.py`.


def _funktion(pfad: Path, name: str) -> ast.FunctionDef:
    baum = ast.parse(pfad.read_text(encoding="utf-8"))
    for knoten in ast.walk(baum):
        if isinstance(knoten, ast.FunctionDef) and knoten.name == name:
            return knoten
    raise AssertionError(f"{pfad.name} hat keine Funktion '{name}'")


def _name(ausdruck: ast.expr | None) -> str:
    """Der Name eines gefangenen Typs, auch bei `except (A, B)` oder `x.Y`."""

    if ausdruck is None:
        return "BaseException"  # nacktes `except:`
    if isinstance(ausdruck, ast.Name):
        return ausdruck.id
    if isinstance(ausdruck, ast.Attribute):
        return ausdruck.attr
    return ast.dump(ausdruck)


def _gefangene_typen(pfad: Path, funktion: str) -> set[str]:
    namen: set[str] = set()
    for knoten in ast.walk(_funktion(pfad, funktion)):
        if isinstance(knoten, ast.ExceptHandler):
            ziel = knoten.type
            if isinstance(ziel, ast.Tuple):
                namen.update(_name(e) for e in ziel.elts)
            else:
                namen.add(_name(ziel))
    return namen


def _erster_try(pfad: Path, funktion: str) -> ast.Try:
    for knoten in ast.walk(_funktion(pfad, funktion)):
        if isinstance(knoten, ast.Try):
            return knoten
    raise AssertionError(f"'{funktion}' in {pfad.name} hat keinen `try`-Block")


def _cli(*argumente: str) -> subprocess.CompletedProcess[str]:
    """Die CLI als eigener Prozess — nur so ist der Exit-Code echt.

    `main()` im selben Prozess aufzurufen prüfte den Rückgabewert; hier wird
    geprüft, was ein Aufrufer wirklich bekommt: Exit-Code und `stderr`.
    """

    return subprocess.run(
        [sys.executable, "-m", "src.run_simulation", *argumente],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=REPO,
        timeout=300,
    )


class TestEineKaputteConfigIstEineListeKeinTraceback:
    """**Die Zusage von P3.3 im Wortlaut:** dieselbe lesbare Liste wie im Dashboard."""

    def test_ein_negativer_seed_wird_eine_lesbare_liste(self):
        ergebnis = _cli("--mock-llm", "--rounds", "1", "--quiet", "--seed", "-1")

        assert ergebnis.returncode == EXIT_KONFIGURATION, ergebnis.stderr
        assert "Traceback" not in ergebnis.stderr, (
            "Der Traceback ist zurück — die Meldung geht darin unter:\n" + ergebnis.stderr
        )
        assert BEFUND_KOPF in ergebnis.stderr, (
            "Die Kopfzeile fehlt oder lautet anders: " + ergebnis.stderr
        )
        assert "seed" in ergebnis.stderr
        assert ergebnis.stderr.strip().splitlines()[1].lstrip().startswith("- "), (
            "Die Befunde stehen nicht als Liste da:\n" + ergebnis.stderr
        )

    def test_eine_kaputte_llm_einstellung_ebenso(self):
        """Der zweite Weg in dieselbe Ausnahme — die CLI-Prüfung vor dem Client."""

        ergebnis = _cli("--rounds", "1", "--quiet", "--temperature", "99")

        assert ergebnis.returncode == EXIT_KONFIGURATION, ergebnis.stderr
        assert "Traceback" not in ergebnis.stderr
        assert "temperature" in ergebnis.stderr

    def test_der_exit_code_unterscheidet_eingabe_von_absturz(self):
        """**Nicht 1.** Ein Skript soll «deine Eingabe ist falsch» erkennen können,
        ohne die Meldung zu lesen."""

        assert EXIT_KONFIGURATION == 2
        assert _cli("--mock-llm", "--rounds", "1", "--quiet", "--seed", "-1").returncode == 2

    def test_ein_gesunder_lauf_bleibt_bei_null(self):
        """Die Hülle um `main()` darf den Erfolgsfall nicht anfassen."""

        ergebnis = _cli("--mock-llm", "--rounds", "1", "--quiet")

        assert ergebnis.returncode == 0, ergebnis.stderr

    def test_ein_programmfehler_schlaegt_weiterhin_durch(self):
        """**Kein `except Exception` an dieser Stelle.**

        Gefangen werden die *erwarteten* Fehlschläge — eine Konfiguration, die
        keinen Lauf zulässt, und ein fremder Zwischenstand. Ein `KeyError` aus
        der Engine ist keine Nachricht an den Nutzer, sondern ein Befund für die
        Entwicklung; dort ist der Stack die nützlichere Ausgabe. Eine Hülle, die
        alles fängt, wäre genau das Muster, das dieses Paket abräumt.

        **Geprüft wird der Syntaxbaum, nicht der Text.** Der erste Anlauf suchte
        `"except Exception"` als Zeichenkette und schlug an — am eigenen
        Docstring, der die Wendung zitiert. Ein Wächter, den eine Erklärung über
        ihn selbst umlenken kann, ist keiner.
        """

        import src.run_simulation as cli

        gefangen = _gefangene_typen(Path(cli.__file__), "main")

        assert "Exception" not in gefangen and "BaseException" not in gefangen, (
            f"Die Hülle um `main()` fängt {sorted(gefangen)} — damit verschwindet "
            "auch ein Programmfehler hinter einer freundlichen Meldung."
        )
        assert "ValidationError" in gefangen
        assert "CheckpointVersionError" in gefangen


class TestDieKopfzeileKommtAusEinerQuelle:
    """C2 hatte zwei Hälften, und die zweite ist die, die wiederkommt.

    Die eine war der Wortlaut: `validierungsfehler:`, klein geschrieben und ohne
    Satzform — die **erste Zeile**, die ein CLI-Nutzer liest, und das direkt
    neben einem ordentlich gebauten Satz («Der Zwischenstand passt nicht zu
    dieser Fassung:»). Die andere: Derselbe Text stand an **drei** Stellen
    wörtlich — in `validate_state`, im LLM-Zweig der CLI und als Rückfall in
    `_melde_befunde`. Drei Quellen für einen Satz, und niemand hätte gemerkt,
    wenn zwei davon auseinanderlaufen.

    Der Wortlaut ist Geschmackssache und braucht keinen Wächter. **Die eine
    Quelle braucht einen** — dieselbe Klasse wie P2.11 (zwei Quellen für
    `marginal_cost_fraction`) und wie das Lesemaß aus P3.17.
    """

    #: Wo eine wörtliche Kopfzeile stehen dürfte — nirgends außer an der
    #: Konstante selbst. `tests/` ist draußen: Ein Test darf den erwarteten Text
    #: nennen, sonst prüfte er nur, dass eine Konstante gleich sich selbst ist.
    BAEUME = ("src", "dashboard")

    def test_kein_modul_schreibt_die_kopfzeile_woertlich(self):
        from src.validation import BEFUND_KOPF

        befunde: list[str] = []
        for baum in self.BAEUME:
            for pfad in sorted((REPO / baum).rglob("*.py")):
                if "legacy" in pfad.parts:
                    continue
                quelle = pfad.read_text(encoding="utf-8-sig")
                if BEFUND_KOPF not in quelle:
                    continue
                # Die Definition selbst ist die Quelle und darf ihn tragen.
                if pfad == REPO / "src" / "validation.py":
                    continue
                for nr, zeile in enumerate(quelle.splitlines(), start=1):
                    if BEFUND_KOPF in zeile:
                        befunde.append(f"{pfad.relative_to(REPO).as_posix()}:{nr}")

        assert not befunde, (
            "Diese Stellen schreiben die Kopfzeile wörtlich statt `BEFUND_KOPF` zu "
            "benutzen:\n  " + "\n  ".join(befunde) + "\n\nVor C2 stand sie an drei "
            "Stellen; zwei Quellen für einen Satz laufen früher oder später auseinander."
        )

    def test_beide_werfenden_wege_tragen_denselben_kopf(self):
        """Gemessen, nicht gelesen: zwei Ausnahmen, dieselbe erste Zeile.

        Der eine Weg ist `validate_state` (kaputte Config), der andere die
        CLI-Prüfung der LLM-Angaben. Vor C2 hatten sie zufällig denselben
        Wortlaut, weil beide dieselbe Zeichenkette hingeschrieben hatten.
        """

        from src.validation import BEFUND_KOPF

        aus_config = _cli("--mock-llm", "--rounds", "1", "--quiet", "--seed", "-1").stderr
        aus_llm = _cli("--rounds", "1", "--quiet", "--temperature", "99").stderr

        for name, ausgabe in (("Config", aus_config), ("LLM", aus_llm)):
            erste = ausgabe.strip().splitlines()[0]
            assert erste == BEFUND_KOPF, f"{name}-Weg beginnt mit {erste!r}"

    def test_die_kopfzeile_ist_ein_satz(self):
        """Die eine Zusage zum Wortlaut, die sich prüfen lässt.

        Nicht «sie klingt gut», sondern: Sie fängt groß an und endet mit einem
        Doppelpunkt, wie die Kopfzeile des Checkpoint-Zweigs daneben. Der alte
        Text erfüllte beides nicht.
        """

        from src.validation import BEFUND_KOPF

        assert BEFUND_KOPF[0].isupper(), BEFUND_KOPF
        assert BEFUND_KOPF.endswith(":"), BEFUND_KOPF
        assert "fehler" not in BEFUND_KOPF.lower(), (
            "Die Kopfzeile nennt den Namen der Ausnahme statt zu sagen, was "
            f"passiert ist: {BEFUND_KOPF!r}"
        )


class TestDerFehlerwegScheitertNichtSelbst:
    """Ein Fehlerweg, der an einem Zeichen zerbricht, ist keiner.

    Gemessen: Die Windows-Konsole dieses Projekts steht auf `cp1252`, und in
    `src/` stehen 46 Zeichenketten mit Zeichen, die dieser Zeichensatz nicht
    kennt (`→`, `≥`, `₂`, `Δ`). **Heute enthält kein Validierungsbefund eines
    davon** — aber ein einziges genügte, um die Liste durch einen
    `UnicodeEncodeError` zu ersetzen: einen Traceback genau an der Stelle, an
    der P3.3 gerade einen weggeräumt hat. Der weitere Umgang mit diesen 46
    Stellen ist ein eigener Befund (P3.10).
    """

    # **Hier stand bis P3.14 ein Test, der seine eigene Zusage nie geprüft hat.**
    # Er ersetzte `builtins.print` durch eine Fassung, die cp1252-Fehler wirft,
    # ließ `sys.stderr` aber das Auffangobjekt von `capsys` — und dessen
    # `encoding` ist **utf-8**. Der Ausweichpfad kodierte also nach utf-8, wo
    # `backslashreplace` nichts zu ersetzen hat; geschrieben wurde
    # `'… cost_pressure ≥ 0,8 …'` mit echtem Zeichen. Durchgegangen ist er über
    # das zweite Glied seiner eigenen Bedingung:
    #
    #     assert "u2265" in ausgabe or "≥" in ausgabe
    #
    # Eine Attrappe, die an einer Stelle scheitert und an der anderen so tut,
    # als sei alles in Ordnung, prüft die Verbindung dazwischen nicht. Ersetzt
    # durch den Test darunter: ein echter Strom, dessen `write` wirft **und**
    # dessen `encoding` cp1252 sagt — in beiden Bauformen.

    @pytest.mark.parametrize("mit_puffer", [True, False], ids=["mit .buffer", "ohne .buffer"])
    def test_der_ausweichpfad_braucht_keinen_byte_puffer(self, monkeypatch, mit_puffer):
        """**Prüfling und Prüfer teilten dieselbe Voraussetzung** (P3.14, B2 des Audits).

        Der Test darüber schreibt in den `stderr` von `capsys` — und der *hat*
        einen `.buffer`. Der Ausweichpfad las genau dieses Attribut, und ein
        Strom ohne machte aus dem `UnicodeEncodeError` einen `AttributeError`:
        einen Traceback an der Stelle, an der P3.3 einen weggeräumt hat.

        Ein Tee, ein Wrapper einer Oberfläche oder ein Testharnisch ist genau so
        ein Strom. Beide Formen laufen hier durch dieselbe Zusage, damit der
        pufferlose Fall nicht wieder der ungeprüfte ist.
        """

        import io
        import sys

        from src.run_simulation import _melde_befunde

        class NurText(io.TextIOBase):
            """Ein Strom mit `write` und sonst nichts — kein `buffer`."""

            def __init__(self) -> None:
                self.stuecke: list[str] = []

            @property
            def encoding(self) -> str:
                return "cp1252"

            def write(self, s: str) -> int:
                s.encode("cp1252")  # wirft, wie die echte Konsole
                self.stuecke.append(s)
                return len(s)

        class MitPuffer(NurText):
            """Dieselbe Konsole, aber mit Byte-Puffer darunter — wie `capsys`."""

            def __init__(self) -> None:
                super().__init__()
                self._roh = io.BytesIO()

            @property
            def buffer(self) -> io.BytesIO:
                return self._roh

        strom = MitPuffer() if mit_puffer else NurText()
        monkeypatch.setattr(sys, "stderr", strom)

        _melde_befunde(BEFUND_KOPF, ["Bedingung: cost_pressure ≥ 0,8 (CO₂-Abgabe)"])

        ausgabe = "".join(strom.stuecke)
        assert "cost_pressure" in ausgabe, "Der Befund ist verschwunden"
        assert "u2265" in ausgabe, "Das unschreibbare Zeichen wurde nicht nachschlagbar ersetzt"
        assert "u2082" in ausgabe, "CO₂ ebenso"
        # Was die Konsole kann, bleibt stehen — `backslashreplace` ersetzt nur,
        # was sie nicht kann. Sonst wäre jede Umlautmeldung unlesbar.
        assert "0,8" in ausgabe


class TestEinFehlenderGraphSagtWasFehlt:
    """Fall 1: Der echte Import steht jetzt im `try`."""

    def test_der_versuch_enthaelt_den_echten_import(self):
        """Ein `try: pass` kann nicht fehlschlagen — deshalb der Blick in den Syntaxbaum.

        Das Paket wirklich zu entfernen wäre der bessere Test und ist hier nicht
        machbar: `langgraph` ist Kern-Abhängigkeit, und ein `sys.modules`-Trick
        prüfte die Attrappe statt den Import.

        **Nicht als Textsuche.** Der Kommentar über dem `try` erklärt den alten
        Zustand und zitiert dabei `try: pass` — eine Suche nach diesen Zeichen
        fände die Erklärung statt des Codes.
        """

        import src.orchestration.langgraph_workflow as workflow

        versuch = _erster_try(Path(workflow.__file__), "build_playground_stategraph")

        importe = [
            knoten.module or ""
            for knoten in ast.walk(ast.Module(body=versuch.body, type_ignores=[]))
            if isinstance(knoten, ast.ImportFrom)
        ]
        assert any(modul.startswith("langgraph") for modul in importe), (
            "Im `try` steht kein `langgraph`-Import — dann kann der "
            "`except`-Zweig nie feuern, und genau das war der Befund."
        )
        assert not any(isinstance(k, ast.Pass) for k in versuch.body)
        assert [_name(h.type) for h in versuch.handlers] == ["ImportError"]

    def test_die_meldung_nennt_den_weg(self):
        import src.orchestration.langgraph_workflow as workflow

        quelle = Path(workflow.__file__).read_text(encoding="utf-8")

        assert "pip install -e" in quelle, "Eine Meldung ohne Ausweg ist eine Sackgasse"
        assert "[studio]" not in quelle, (
            "`langgraph` ist Kern-Abhängigkeit und kein Extra — ein Extra zu "
            "nennen, das es nicht gibt, schickt den Leser ins Leere."
        )

    def test_geprueft_wird_vor_dem_sprachmodell(self):
        """Ohne Graph braucht niemand ein Sprachmodell.

        Die Reihenfolge entscheidet, welche der beiden Meldungen der Nutzer
        sieht — und «kein Ollama erreichbar» wäre hier die falsche.
        """

        import src.orchestration.langgraph_workflow as workflow

        pfad = Path(workflow.__file__)
        versuch = _erster_try(pfad, "build_playground_stategraph")
        funktion = _funktion(pfad, "build_playground_stategraph")
        aufrufe = [
            knoten.lineno
            for knoten in ast.walk(funktion)
            if isinstance(knoten, ast.Call)
            and isinstance(knoten.func, ast.Name)
            and knoten.func.id == "get_llm"
        ]

        assert aufrufe, "Kein `get_llm()` gefunden — der Test prüft dann nichts"
        assert versuch.lineno < min(aufrufe), (
            "Das Sprachmodell entsteht vor der Graph-Prüfung — dann sieht der "
            "Nutzer «kein Ollama erreichbar», wo «kein langgraph» richtig wäre."
        )


class TestEinKaputterGraphBrichtSichtbarAb:
    """Fall 2: kein `graph.json` und kein `Wrote …`, wenn der Build scheitert."""

    def test_der_build_fehler_wird_nicht_verschluckt(self, monkeypatch, tmp_path):
        import langgraph_studio.create_graph as skript

        class KaputtesModul:
            graph = None

            @staticmethod
            def get_build_error():
                return RuntimeError("Knoten 'market' hat keine Kante")

        monkeypatch.setitem(sys.modules, "langgraph_studio.graph", KaputtesModul)
        monkeypatch.setattr(skript, "ROOT", tmp_path)

        with pytest.raises(RuntimeError, match="keine Kante"):
            skript.main()

        assert not (tmp_path / "graph.json").exists(), (
            "Ein kaputter Build hat trotzdem eine Datei hinterlassen — sie "
            "behauptet eine Topologie, die so nicht baut."
        )

    def test_ein_gesunder_build_schreibt_die_datei(self, monkeypatch, tmp_path):
        import langgraph_studio.create_graph as skript

        class GesundesModul:
            graph = object()

            @staticmethod
            def get_build_error():
                return None

        monkeypatch.setitem(sys.modules, "langgraph_studio.graph", GesundesModul)
        monkeypatch.setattr(skript, "ROOT", tmp_path)

        assert skript.main() == 0

        payload = json.loads((tmp_path / "graph.json").read_text(encoding="utf-8"))
        assert payload["nodes"] and payload["edges"]

    def test_ohne_das_paket_entsteht_die_datei_mit_hinweis(self, monkeypatch, tmp_path, capsys):
        """**Ein fehlendes Paket ist kein kaputter Graph**, und nur das zweite
        ist ein Befund.

        Die Topologie steht als Daten im Skript und braucht `langgraph` nicht —
        sie ist eine Beschreibung, keine Ausführung. Gesagt wird es trotzdem:
        Eine Datei, die ohne Gegenprobe entstanden ist, soll das nicht
        verschweigen.
        """

        import langgraph_studio.create_graph as skript

        echter_import = builtins.__import__

        def ohne_graph_modul(name, *args, **kwargs):
            if name == "langgraph_studio.graph":
                raise ImportError("No module named 'langgraph'")
            return echter_import(name, *args, **kwargs)

        monkeypatch.delitem(sys.modules, "langgraph_studio.graph", raising=False)
        monkeypatch.setattr(builtins, "__import__", ohne_graph_modul)
        monkeypatch.setattr(skript, "ROOT", tmp_path)

        assert skript.main() == 0

        assert (tmp_path / "graph.json").exists()
        assert "ungeprüft" in capsys.readouterr().out
