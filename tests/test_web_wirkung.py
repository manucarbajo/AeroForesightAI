"""Welches Feld auf welchem Startpfad wirklich ankommt (P1.9-W0.2).

Der Assistent stellt acht Schritte und rund hundertzwanzig Felder zur
Verfügung. Was davon die Simulation überhaupt erreicht, stand nirgends — und
das Audit vom 2026-08-28 hat gezeigt, warum das teuer ist: Auf dem Sweep-Pfad
erreicht **genau ein** Feld den Lauf (`rounds`), während der Preflight
weiterhin Rechenmodus, Seed, Ziel-Auslastung und Systemgrößen anzeigt, als
wären sie wirksam. Ein Nutzer beantwortet Schritt 3 und bekommt einen anderen
Rechenmodus als gewählt, ohne Hinweis.

**«Wirksam» heißt hier: es ändert, was bei der Simulation ankommt.** Nicht «es
wird irgendwo gelesen» — gelesen wird auch, was danach verworfen wird. Gemessen
wird deshalb der Unterschied: Derselbe Startpfad einmal mit dem
Auslieferungsentwurf und einmal mit genau einem geänderten Feld. Bleibt dabei
alles gleich, was die Simulation zu sehen bekommt, hat das Feld auf diesem Pfad
keine Wirkung. Das ist eine Definition ohne Annahmen über den Code — sie gilt
auch dann noch, wenn jemand den Weg dahin umbaut.

**Was die Simulation zu sehen bekommt**, ist an drei Nahtstellen greifbar:

* der `SimulationState`, den der Runner bekommt (40 KB JSON, über zwei Aufrufe
  hinweg bitgleich — deshalb taugt er direkt als Abdruck, ohne dass jemand eine
  Auswahl treffen und dabei ein Feld übersehen könnte),
* die `RunnerOptions`, mit denen der Runner gebaut wird,
* das Sprachmodell samt seiner Konfiguration.

Auf dem Sweep-Pfad gibt es keine davon: Dort wird `run_all_sweeps(...)` gerufen,
und dessen Argumente sind alles, was ankommt.

**Die Simulation selbst läuft nicht.** Sie wird an genau diesen Nahtstellen
angehalten und aufgezeichnet. Ein echter Lauf je Feld und Pfad wären über
siebzig Läufe für eine Frage, die vor dem ersten Tick entschieden ist.

**`ERWARTET` ist der heutige Stand, nicht der gewünschte.** Die Tabelle
dokumentiert, was ist — damit eine Änderung daran auffällt, in beide
Richtungen: Ein Feld, das seine Wirkung verliert, wird rot; ein Feld, das neue
Wirkung bekommt (etwa durch W1.1), wird ebenfalls rot und verlangt, dass die
Tabelle mitgezogen wird. Wer W1.1 umsetzt, ändert hier Zeilen — das ist der
Zweck.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from pathlib import Path

import pytest

from dashboard import run_launcher
from dashboard.config_catalog import ConfigDraft, default_config_draft
from src.orchestration.scenario_sweeps import vorgegebene_felder

# --- Die drei Startpfade ---------------------------------------------------

EINZELLAUF = "Einzellauf"
WIEDERHOLUNGEN = "Wiederholungen"
SWEEP = "Szenario-Vergleich"

PFADE = [EINZELLAUF, WIEDERHOLUNGEN, SWEEP]


def _entwurf(pfad: str) -> ConfigDraft:
    """Der Auslieferungsentwurf, auf den gewählten Startpfad gestellt.

    **Mit gesetztem Startwert**, und das ist kein Detail: Im Auslieferungszustand
    ist `seed` `None` und `use_seed` aus. Legt man dann nur den Schalter um,
    stirbt `draft_to_launch_config` mit `TypeError: int() argument must be ...
    not 'NoneType'` — kein Prüfbefund, ein Absturz.

    Erreichbar ist das heute nicht, und zwar aus dem denkbar schlechtesten
    Grund: Befund A7 schreibt beim Anzeigen von Schritt 3 stillschweigend
    `seed = 42` in den Entwurf, bevor jemand den Schalter finden kann. **W5.1
    räumt genau das weg und macht diesen Absturz damit erreichbar** — wer es
    umsetzt, fasst dieselbe Zeile mit an. Notiert in `audit_findings.md`.
    """

    draft = default_config_draft()
    draft.seed = 42
    draft.use_seed = True
    if pfad == WIEDERHOLUNGEN:
        draft.run_count = 3
    elif pfad == SWEEP:
        draft.run_all_sweeps = True
    return draft


# --- Die Felder und je ein anderer Wert ------------------------------------

#: Je Feld ein Wert, der sich vom Auslieferungszustand unterscheidet. Die Werte
#: sind bewusst unauffällig gültig: Es geht um Wirkung, nicht um Validierung —
#: ein Wert, den die Prüfung ablehnt, würde nur zeigen, dass die Prüfung greift.
ANDERER_WERT: dict[str, object] = {
    "rounds": 37,
    "use_seed": False,
    "seed": 4711,
    "simulation_name": "Wirkungsprobe",
    "simulation_description": "Ein anderer Beschreibungstext.",
    "apply_custom_overrides": False,
    "mock_llm": False,
    "deterministic_only": True,
    "model": "wirkungsprobe-modell",
    "base_url": "http://wirkungsprobe.invalid:1",
    "temperature": 0.13,
    "max_tokens": 1234,
    "no_market": True,
    "redebedarf": True,
    "checkpoint_interval": 7,
    "no_protocol": True,
    "no_scenarios": True,
    "generate_figures": False,
    "base_price": 123.0,
}

#: Felder, die den Startpfad **auswählen**, statt ihn zu parametrisieren. Sie
#: gehören nicht in die Messung: Sie zu ändern heißt, einen anderen Pfad zu
#: messen, nicht denselben Pfad anders.
PFADWAHL = {"run_all_sweeps", "run_count", "resume_from", "scenario_mode", "sweep_id"}

#: Felder, die **nach** dem Lauf wirken und deshalb an dieser Nahtstelle
#: zurecht nichts bewegen. Sie schalten Ausgaben, nicht die Rechnung: Protokoll,
#: Szenariotexte, Bilder entstehen alle aus dem fertigen Zustand. «Unwirksam»
#: heißt hier also nicht «kaputt» — es heißt «wirkt später».
NACH_DEM_LAUF = {"no_protocol", "no_scenarios", "generate_figures"}

#: Felder, die nur zählen, wenn wirklich ein Sprachmodell gebaut wird. Im
#: Auslieferungszustand ist `mock_llm` an, und dann liefert `_build_llm()` ein
#: `MockLLM` ohne Konfiguration — Modellname, Adresse, Temperatur und
#: Token-Grenze sind dort folgenlos. Das ist richtig so und trotzdem einen
#: eigenen Namen wert: `TestDasSprachmodellHaengtAmRechenmodus` zeigt, dass die
#: vier greifen, sobald der Rechenmodus sie braucht.
NUR_MIT_SPRACHMODELL = {"model", "base_url", "temperature", "max_tokens"}

#: Felder, deren Wirkung sich nicht durch einen einzelnen Skalar prüfen lässt
#: (verschachtelte Strukturen) oder die eine andere Datei verlangen. Sie sind
#: hier ausgenommen und **benannt**, damit die Lücke sichtbar bleibt statt
#: unsichtbar zu sein.
NICHT_GEMESSEN = {
    "property_edits": "verschachtelt; wirkt über `apply_custom_overrides` mit",
    "population_edits": "verschachtelt; wirkt über `apply_custom_overrides` mit",
    "saturation_edit": "verschachtelt; wirkt über `apply_custom_overrides` mit",
    "market_feedback_edit": "verschachtelt; wirkt über `apply_custom_overrides` mit",
    "simulation_config_file": "verlangt eine zweite Konfigurationsdatei im Repo",
    "properties_file": "verlangt eine zweite Konfigurationsdatei im Repo",
    "agents_file": "verlangt eine zweite Konfigurationsdatei im Repo",
    "factors_file": "verlangt eine zweite Konfigurationsdatei im Repo",
    "cib_file": "verlangt eine zweite Konfigurationsdatei im Repo",
    "sweep_batch_deterministic": "heute an keiner Stelle des Launchers gelesen",
}


def _messbare_felder() -> list[str]:
    return sorted(ANDERER_WERT)


# --- Der Stand, den dieser Test festhält -----------------------------------

#: Was auf welchem Pfad ankommt — gemessen am 2026-08-28.
#:
#: Der Sweep-Pfad ist der Grund für dieses Paket: `run_single_sweep` baut seinen
#: Runner selbst und schreibt `deterministic_only`, `seed` und
#: `checkpoint_interval` fest. Vom Entwurf bleibt `rounds` — und selbst das
#: nicht als Wunsch, sondern als `ticks_override`, das die `max_ticks` jedes
#: Presets überschreibt (W1.2).
#:
#: **Drei Überraschungen stecken in dieser Tabelle**, alle von der Messung
#: gefunden und nicht vorher vermutet:
#:
#: 1. **`base_price` steht nirgends.** Nicht weil es später wirkt, sondern weil
#:    es verlorengeht: `RunLaunchConfig` hat kein solches Feld, und
#:    `launch_from_draft` schickt den Entwurf durch genau diese Rundreise
#:    (`draft_to_launch_config` → `launch_config_to_draft`). `build_custom_sweep_from_draft`
#:    wertet `base_price` korrekt aus — es kommt dort nur nie an. «Startpreis
#:    selbst festlegen» im Assistenten ist über das Dashboard **wirkungslos**;
#:    über die CLI nicht. Eigener Befund, in `audit_findings.md` notiert.
#: 2. **`apply_custom_overrides` bewegt nichts**, solange niemand etwas geändert
#:    hat: Der Entwurf führt die Datei-Defaults mit, und ein Custom-Sweep daraus
#:    ergibt denselben Zustand wie gar keiner. Der Schalter wirkt erst zusammen
#:    mit einer Abweichung — deshalb steht er hier nicht, ohne dass etwas kaputt
#:    wäre.
#: 3. **Die vier Sprachmodell-Felder bewegen nichts**, solange `mock_llm` an ist
#:    — siehe `NUR_MIT_SPRACHMODELL`.
ERWARTET: dict[str, set[str]] = {
    EINZELLAUF: {
        "base_price",
        "rounds",
        "use_seed",
        "seed",
        "simulation_name",
        "simulation_description",
        "mock_llm",
        "deterministic_only",
        "no_market",
        "redebedarf",
        "checkpoint_interval",
    },
    WIEDERHOLUNGEN: {
        "base_price",
        "rounds",
        "use_seed",
        "seed",
        "simulation_name",
        "simulation_description",
        "mock_llm",
        "deterministic_only",
        "no_market",
        "redebedarf",
        "checkpoint_interval",
    },
    #: **Leer, und das ist das Ergebnis von W1.1 und W1.2.** Ein
    #: Szenario-Vergleich nimmt vom Entwurf nichts entgegen: Er rechnet alle
    #: hinterlegten Szenarien unter gleichen Bedingungen und in ihrer jeweils
    #: eigenen Länge. Bis W1.2 stand hier `rounds` — nicht als Wunsch, sondern
    #: als `ticks_override`, das die `max_ticks` jedes Presets überschrieb.
    #:
    #: Damit klärt sich auch, was der Assistent für diesen Weg fragen muss:
    #: nichts. Alles, was er sonst fragt, steht im Vertrag des Sweeps und wird
    #: dort als vorgegeben ausgewiesen (W1.3).
    SWEEP: set(),
}


# --- Die Nahtstelle --------------------------------------------------------


@dataclass
class Abdruck:
    """Alles, was von einem Entwurf bei der Simulation ankommt."""

    zustand: str | None = None
    optionen: str | None = None
    llm: str | None = None
    sweep: str | None = None

    def __str__(self) -> str:
        return f"{self.zustand}|{self.optionen}|{self.llm}|{self.sweep}"


def _llm_abdruck(llm) -> str:
    config = getattr(llm, "config", None)
    if config is None:
        return type(llm).__name__
    teile = [
        f"{name}={getattr(config, name, None)!r}"
        for name in ("base_url", "model", "temperature", "max_tokens")
    ]
    return f"{type(llm).__name__}({', '.join(teile)})"


@pytest.fixture
def abdruck_von(monkeypatch, tmp_path):
    """Gibt eine Funktion zurück: Entwurf und Pfad rein, Abdruck raus.

    Angehalten wird an drei Stellen — Runner, Sweep-Batch und alles, was
    danach auf die Platte schreibt. Was hier nicht abgefangen ist, schreibt in
    `tmp_path` und nicht in `runs/`.
    """

    import src.orchestration.scenario_sweeps as sweeps
    import src.run_simulation as run_simulation

    aufzeichnung = Abdruck()

    class _Runner:
        def __init__(self, llm=None, options=None):
            aufzeichnung.optionen = repr(dataclasses.asdict(options)) if options else None
            aufzeichnung.llm = _llm_abdruck(llm)

        def run(self, state, **kwargs):
            # `seed` steht als Argument neben dem Zustand und gehoert deshalb
            # mit in den Abdruck -- sonst saehe ein Seed, den nur der Runner
            # bekommt, wie «nicht angekommen» aus.
            aufzeichnung.zustand = f"seed={kwargs.get('seed')!r} " + (
                state.model_dump_json() if state is not None else "kein Zustand"
            )
            return state

        def run_multi(self, runs, base_state=None, **kwargs):
            aufzeichnung.zustand = f"runs={runs} " + base_state.model_dump_json()
            return type("Ergebnis", (), {"runs": []})()

    def _kein_sweep(**kwargs):
        aufzeichnung.sweep = repr(sorted(kwargs.items()))
        return None

    monkeypatch.setattr(run_launcher, "SimulationRunner", _Runner)
    monkeypatch.setattr(sweeps, "run_all_sweeps", _kein_sweep)
    monkeypatch.setattr(sweeps, "SWEEP_OUTPUT_DIR", tmp_path / "sweeps")
    monkeypatch.setattr(run_launcher, "resolve_run_output_dir", lambda run_id: tmp_path / run_id)
    monkeypatch.setattr(run_launcher, "generate_figures_for_run", lambda *_a, **_k: None)
    monkeypatch.setattr(run_simulation, "_save_run_outputs", lambda *_a, **_k: {})
    monkeypatch.setattr(run_simulation, "_build_run_args", lambda *_a, **_k: None)
    monkeypatch.setattr(run_simulation, "_write_multi_run_summary", lambda **_k: None)

    def nehmen(draft: ConfigDraft) -> Abdruck:
        aufzeichnung.zustand = aufzeichnung.optionen = None
        aufzeichnung.llm = aufzeichnung.sweep = None
        run_launcher.launch_from_draft(draft, repo_root=Path("."))
        return Abdruck(
            aufzeichnung.zustand,
            aufzeichnung.optionen,
            aufzeichnung.llm,
            aufzeichnung.sweep,
        )

    return nehmen


def _wirksame_felder(abdruck_von, pfad: str) -> set[str]:
    """Welche Felder den Abdruck dieses Pfads verändern."""

    grund = str(abdruck_von(_entwurf(pfad)))
    wirksam = set()
    for feld in _messbare_felder():
        draft = _entwurf(pfad)
        setattr(draft, feld, ANDERER_WERT[feld])
        if str(abdruck_von(draft)) != grund:
            wirksam.add(feld)
    return wirksam


# --- Die Prüfungen ---------------------------------------------------------


class TestKeinFeldWirdStillVerworfen:
    """Was der Assistent erfragt, kommt an — oder es steht hier, dass es das nicht tut."""

    @pytest.mark.parametrize("pfad", PFADE)
    def test_the_path_uses_exactly_the_documented_fields(self, abdruck_von, pfad):
        gemessen = _wirksame_felder(abdruck_von, pfad)
        erwartet = ERWARTET[pfad]

        neu_wirksam = sorted(gemessen - erwartet)
        verloren = sorted(erwartet - gemessen)

        assert not verloren, (
            f"«{pfad}» verwirft jetzt Felder, die es bisher benutzt hat: {verloren}.\n"
            "Ein Feld, das seine Wirkung verliert, ist eine stille Verhaltensänderung — "
            "der Assistent fragt es weiterhin ab."
        )
        assert not neu_wirksam, (
            f"«{pfad}» benutzt jetzt zusätzlich: {neu_wirksam}.\n"
            "Das ist vermutlich der Fortschritt aus W1.1 — dann gehört die Zeile in "
            "`ERWARTET` mitgezogen und der Preflight (W1.3) nachgeführt."
        )

    def test_the_sweep_takes_nothing_from_the_draft(self, abdruck_von):
        """Nach W1.1 und W1.2: Der Vergleich ist vollständig von den Presets bestimmt.

        Dieser Test hat einen Vorgänger, der das Gegenteil festhielt — «der
        Sweep-Pfad benutzt genau ein Feld» — und der mit W1.2 gefallen ist. Er
        stand für den offenen Befund; dieser hier steht für seine Behebung.

        Die Aussage ist stärker, als sie aussieht: Sie sagt, dass der Assistent
        für einen Szenario-Vergleich **gar nichts** erfragen muss. Alles, was er
        sonst fragt, gilt dort nicht — und steht als solches im Vertrag.
        """

        gemessen = _wirksame_felder(abdruck_von, SWEEP)

        assert gemessen == set(), (
            f"Der Szenario-Vergleich nimmt jetzt {sorted(gemessen)} vom Entwurf "
            "entgegen. Wenn das gewollt ist: `ERWARTET[SWEEP]` mitziehen, den "
            "Eintrag aus `FESTLEGUNGEN`/`UNBEACHTET` entfernen und den Preflight "
            "nachführen — sonst zeigt die Oberfläche eine wirksame Einstellung "
            "als vorgegeben an."
        )

    def test_the_dashboard_does_not_shorten_the_presets(self, abdruck_von):
        """W1.2 — jedes Szenario läuft so lang, wie es angelegt ist.

        Bis hierher schickte das Dashboard `ticks_override=int(config.rounds)`
        mit, und `rounds` hat immer einen Wert. Vier der acht ausgelieferten
        Presets sind auf 50 Ticks angelegt und liefen damit auf 40 — **drei von
        ihnen verlieren dabei ihren End-State-Meilenstein**, also genau die
        Aussage, für die das Szenario gebaut wurde.

        Geprüft wird das Argument und nicht der Lauf: `ticks_override` ist die
        einzige Stelle, an der diese Verkürzung entstehen kann.
        """

        abdruck = abdruck_von(_entwurf(SWEEP))

        assert abdruck.sweep is not None, "Der Sweep-Pfad wurde gar nicht betreten"
        assert "'ticks_override', None" in abdruck.sweep, (
            f"Das Dashboard übersteuert wieder die Länge der Presets: {abdruck.sweep}\n"
            "Ein Vergleich rechnet jedes Szenario in seiner eigenen Länge. Die CLI "
            "behält `--ticks` — sie hat mit dem Default `None` das Signal, das dem "
            "Entwurf fehlt."
        )

    def test_the_cli_keeps_its_override(self):
        """Und die CLI behält, was das Dashboard aufgibt.

        `--ticks 10000` ist der Benchmark-Weg aus dem Modul-Docstring. Er darf
        nicht mit abgeräumt werden: Dort **sagt** jemand ausdrücklich, dass er
        eine andere Länge will — der Default steht auf `None`.
        """

        quelle = Path("src/orchestration/scenario_sweeps.py").read_text(encoding="utf-8")

        assert "ticks_override=args.ticks" in quelle, (
            "Die CLI reicht ihre `--ticks` nicht mehr durch — dann gibt es keinen "
            "Weg mehr, einen Sweep bewusst auf eine andere Länge zu rechnen."
        )
        assert "effective_ticks = ticks_override or sweep.max_ticks" in quelle, (
            "`run_single_sweep` fällt nicht mehr auf `sweep.max_ticks` zurück — "
            "dann trägt W1.2 nicht mehr."
        )

    def test_the_compute_mode_does_not_survive_the_sweep(self, abdruck_von):
        """Namentlich das, was Schritt 3 des Assistenten verspricht.

        Der allgemeine Test oben würde diesen Fall mitnehmen, aber nur als
        Element einer Menge. Er hat einen eigenen Namen verdient: Er ist der
        Grund, aus dem der Preflight heute die Unwahrheit sagt.
        """

        grund = str(abdruck_von(_entwurf(SWEEP)))
        for feld in ("mock_llm", "deterministic_only", "model", "use_seed", "seed"):
            draft = _entwurf(SWEEP)
            setattr(draft, feld, ANDERER_WERT[feld])
            assert str(abdruck_von(draft)) == grund, (
                f"`{feld}` wirkt jetzt auf dem Sweep-Pfad — schön, aber der Preflight "
                "und `ERWARTET` müssen es mit erfahren (W1.1, W1.3)."
            )


class TestWasDerVergleichVerwirftStehtInSeinemVertrag:
    """Der Kern von W1.1: Verwerfen ist erlaubt, **stillschweigend** verwerfen nicht.

    Der Szenario-Vergleich rechnet alle Szenarien unter gleichen Bedingungen —
    sonst wären sie nicht vergleichbar. Diese Festlegung bleibt. Falsch daran
    war ihr Schweigen: Der Assistent fragte, der Preflight zeigte an, der Lauf
    verwarf.

    Diese beiden Prüfungen schließen den Kreis in beide Richtungen. Zusammen
    machen sie ein stilles Verwerfen unmöglich: Wer künftig ein Feld auf dem
    Sweep-Pfad fallen lässt, muss es in den Vertrag schreiben — und wer eines in
    den Vertrag schreibt, das gar nicht verworfen wird, wird ebenfalls rot.
    """

    def test_everything_the_contract_claims_is_really_fixed(self, abdruck_von):
        """Kein Eintrag im Vertrag, der in Wahrheit doch durchkommt."""

        grund = str(abdruck_von(_entwurf(SWEEP)))
        falsch_behauptet = []
        for feld in sorted(vorgegebene_felder()):
            if feld not in ANDERER_WERT:
                continue
            draft = _entwurf(SWEEP)
            setattr(draft, feld, ANDERER_WERT[feld])
            if str(abdruck_von(draft)) != grund:
                falsch_behauptet.append(feld)

        assert not falsch_behauptet, (
            f"Der Vertrag nennt {falsch_behauptet} als vorgegeben, aber sie wirken. "
            "Ein Vertrag, der zu viel behauptet, ist so schlecht wie einer, der "
            "schweigt — die Oberfläche würde eine wirksame Einstellung als "
            "wirkungslos ausgeben."
        )

    def test_nothing_is_discarded_without_being_declared(self, abdruck_von):
        """Und umgekehrt: kein verworfenes Feld ohne Eintrag.

        Das ist die Prüfung, die W0.2 in eine Zusage verwandelt. Sie kennt vier
        erlaubte Gründe, warum ein Feld auf dem Sweep-Pfad nichts bewegt — und
        jeder davon ist irgendwo aufgeschrieben. Ein fünfter, unaufgeschriebener
        Grund lässt sie fehlschlagen.
        """

        wirksam = _wirksame_felder(abdruck_von, SWEEP)
        verworfen = set(_messbare_felder()) - wirksam

        erlaubt = (
            set(vorgegebene_felder())  # steht im Vertrag
            | NACH_DEM_LAUF  # wirkt später, nicht hier
            | NUR_MIT_SPRACHMODELL  # braucht ein echtes Modell
        )

        stillschweigend = sorted(verworfen - erlaubt)
        assert not stillschweigend, (
            f"Der Szenario-Vergleich verwirft {stillschweigend}, ohne dass es "
            "irgendwo steht.\n"
            "Entweder in `scenario_sweeps.FESTLEGUNGEN` bzw. `UNBEACHTET` "
            "aufnehmen — dann sagt der Assistent es dem Nutzer (W1.3) — oder "
            "dafür sorgen, dass das Feld ankommt."
        )

    def test_the_contract_carries_the_behaviour_it_describes(self):
        """Der Vertrag ist die Quelle, nicht die Beschreibung daneben.

        Stünden die drei Werte weiterhin als Literal in `run_single_sweep` und
        die Tabelle nur daneben, liefen beide auseinander — dreimal in diesem
        Projekt schon geschehen. Deshalb wird hier geprüft, dass der Lauf die
        Werte aus dem Vertrag **liest**: Ändert man den Vertrag, ändert sich der
        Lauf mit.
        """

        quelle = Path("src/orchestration/scenario_sweeps.py").read_text(encoding="utf-8")
        bau = quelle[quelle.index("runner = SimulationRunner(") :][:600]

        assert "festgelegt[" in bau, (
            "`run_single_sweep` baut seinen Runner nicht mehr aus `FESTLEGUNGEN`. "
            "Damit ist der Vertrag zur Beschreibung geworden, und die nächste "
            "Änderung läuft ihm davon."
        )
        for feld in ("deterministic_only", "checkpoint_interval", "seed"):
            assert (
                f'festgelegt["{feld}"]' in bau
            ), f"`{feld}` steht wieder als Literal im Runner-Bau statt im Vertrag."


class TestDasSprachmodellHaengtAmRechenmodus:
    """Modellname, Adresse, Temperatur und Token-Grenze wirken — unter einer Bedingung."""

    def test_they_do_nothing_while_the_mock_is_on(self, abdruck_von):
        grund = str(abdruck_von(_entwurf(EINZELLAUF)))
        for feld in sorted(NUR_MIT_SPRACHMODELL):
            draft = _entwurf(EINZELLAUF)
            setattr(draft, feld, ANDERER_WERT[feld])
            assert str(abdruck_von(draft)) == grund, (
                f"`{feld}` wirkt jetzt auch ohne Sprachmodell. Das wäre eine Änderung an "
                "`_build_llm` — `NUR_MIT_SPRACHMODELL` und `ERWARTET` mitziehen."
            )

    def test_they_all_arrive_once_a_model_is_actually_built(self, abdruck_von):
        """Und dann auch **alle vier** — sonst fragt der Assistent ins Leere.

        Der Gegenbeweis zum Test darüber: «Bewegt nichts» darf nicht heißen
        «kommt nie an». Fiele eines der vier hier durch, wäre es derselbe
        Befund wie bei `base_price` — ein Feld, das der Assistent erfragt und
        der Launcher unterwegs verliert.
        """

        basis = _entwurf(EINZELLAUF)
        basis.mock_llm = False
        grund = str(abdruck_von(basis))

        verloren = []
        for feld in sorted(NUR_MIT_SPRACHMODELL):
            draft = _entwurf(EINZELLAUF)
            draft.mock_llm = False
            setattr(draft, feld, ANDERER_WERT[feld])
            if str(abdruck_von(draft)) == grund:
                verloren.append(feld)

        assert not verloren, (
            f"Mit echtem Sprachmodell kommen diese Felder trotzdem nicht an: {verloren}. "
            "Der Assistent fragt sie ab, der Launcher verliert sie unterwegs."
        )


#: Felder, die die Rundreise durch `RunLaunchConfig` **nicht** überleben müssen —
#: mit Grund, denn ohne Grund ist es ein Befund.
DARF_DIE_RUNDREISE_VERLIEREN = {
    "sweep_batch_deterministic": (
        "Toter Schalter: Der Launcher liest ihn an keiner Stelle. Entfernen gehört "
        "zu P5.1 (toter Code) und nicht hierher — bis dahin ist er benannt statt "
        "unsichtbar."
    ),
}


class TestDieRundreiseVerliertNichts:
    """W1.5 — und die Fehlerklasse dahinter, nicht nur ihr erster Fall.

    `launch_from_draft` schickt jeden Entwurf durch `RunLaunchConfig` und
    wieder zurück. Fehlt dort ein Feld, fällt es lautlos heraus — kein
    Fehler, keine Meldung, nur eine Einstellung, die nicht wirkt. Genau so
    ist der Startpreis verschwunden.

    Ein Test nur für `base_price` hätte den nächsten Fall dieser Art nicht
    gefangen. Dieser hier geht über **alle** Felder des Entwurfs.
    """

    def test_no_field_falls_out_on_the_way(self):
        alle = {f.name for f in dataclasses.fields(ConfigDraft)}
        proben = {feld: wert for feld, wert in ANDERER_WERT.items()}
        proben.update(
            {
                "scenario_mode": "custom",
                "sweep_id": "irgendein_szenario",
                "resume_from": "run_20200101",
                "run_all_sweeps": True,
                "run_count": 3,
                "sweep_batch_deterministic": False,
                "simulation_config_file": "andere_simulation.json",
                "properties_file": "andere_properties.json",
                "agents_file": "andere_agents.json",
                "factors_file": "andere_factors.json",
                "cib_file": "andere_cib.json",
            }
        )

        ungeprueft = sorted(alle - set(proben) - set(NICHT_GEMESSEN))
        assert not ungeprueft, (
            f"Diese Felder durchlaufen die Rundreise ungeprüft: {ungeprueft}. "
            "Eine Probe in `proben` eintragen — sonst ist der nächste stille "
            "Verlust wieder nur Zufallsfund."
        )

        verloren = []
        for feld, wert in sorted(proben.items()):
            draft = default_config_draft()
            draft.seed = 42
            draft.use_seed = True
            setattr(draft, feld, wert)
            zurueck = run_launcher.launch_config_to_draft(
                run_launcher.draft_to_launch_config(draft)
            )
            if getattr(zurueck, feld) != wert:
                verloren.append(f"  {feld}: {wert!r} → {getattr(zurueck, feld)!r}")

        unerklaert = [
            zeile
            for zeile in verloren
            if zeile.strip().split(":")[0] not in DARF_DIE_RUNDREISE_VERLIEREN
        ]
        assert not unerklaert, (
            "Diese Felder überleben die Rundreise durch `RunLaunchConfig` nicht:\n"
            + "\n".join(unerklaert)
            + "\n\nEntweder das Feld dort ergänzen und in **beiden** Richtungen "
            "verdrahten, oder es mit Grund in `DARF_DIE_RUNDREISE_VERLIEREN` "
            "eintragen. Lautlos verlieren ist keine Option — genau so ist der "
            "Startpreis verschwunden."
        )

    def test_the_known_exception_is_still_the_only_one(self):
        """Die Ausnahmeliste darf nicht heimlich wachsen.

        Ein Eintrag darin ist eine Schuld, kein Freibrief. Fiele sie leer aus,
        wäre auch das ein Befund — dann ist der tote Schalter weg und die Liste
        gehört mit ihm gelöscht.
        """

        assert set(DARF_DIE_RUNDREISE_VERLIEREN) == {"sweep_batch_deterministic"}, (
            "Die Liste der geduldeten Verluste hat sich geändert. Jeder Eintrag "
            "gehört begründet — und wieder heraus, sobald er behoben ist."
        )


class TestDerStartpreisKommtAn:
    """W1.5 — der Befund, den erst die Wirkungsmessung ans Licht gebracht hat.

    `build_custom_sweep_from_draft` wertete `base_price` immer schon korrekt
    aus. Es kam dort nur nie an: `launch_from_draft` schickt den Entwurf durch
    `RunLaunchConfig`, und diese Datenklasse hatte kein solches Feld. Der Wert
    fiel auf der Rundreise heraus, lautlos. «Startpreis selbst festlegen» war
    über das Dashboard wirkungslos — über die CLI wirkte derselbe Schalter.

    Zwei Zeilen, weil zwei Dinge stimmen müssen: der Mechanismus (das Feld
    übersteht die Rundreise) und die Wirkung (der Lauf rechnet damit). Wer nur
    das erste repariert, hat die halbe Strecke.
    """

    def test_it_survives_the_round_trip(self):
        draft = default_config_draft()
        draft.base_price = 123.0

        zurueck = run_launcher.launch_config_to_draft(run_launcher.draft_to_launch_config(draft))

        assert zurueck.base_price == 123.0, (
            "`base_price` fällt wieder aus `RunLaunchConfig` heraus — der Befund "
            "aus W1.5 ist zurück."
        )

    def test_and_therefore_reaches_the_run(self, abdruck_von):
        grund = str(abdruck_von(_entwurf(EINZELLAUF)))
        draft = _entwurf(EINZELLAUF)
        draft.base_price = ANDERER_WERT["base_price"]

        assert str(abdruck_von(draft)) != grund, (
            "Der Startpreis übersteht zwar die Rundreise, ändert am Lauf aber "
            "nichts — dann ist er weiter unten verlorengegangen."
        )


class TestEinSchalterOhneWertIstEinBefund:
    """W1.6 — der Absturz, den W0.2 nebenbei gefunden hat.

    `draft_to_launch_config` rechnet `int(draft.seed)`, sobald `use_seed` an
    ist. Bei `seed = None` ist das ein `TypeError` und kein Prüfbefund: Der
    Nutzer sieht einen Stacktrace statt eines Satzes am Feld.

    **Erreichbar war das bisher nicht, und zwar aus dem schlechtesten denkbaren
    Grund:** Der Render-Rückfall aus Befund A7 schreibt beim Anzeigen von
    Schritt 3 stillschweigend eine 42 in den Entwurf, bevor jemand den Schalter
    findet. Ein Fehler, der von einem zweiten Fehler zugedeckt wird — und W5.1
    nimmt die Decke weg.
    """

    def test_it_is_reported_at_the_field(self):
        from dashboard.config_catalog import validate_draft
        from src.validation import field_of

        draft = default_config_draft()
        draft.use_seed = True
        draft.seed = None

        befunde = validate_draft(draft)

        assert befunde, "Ein eingeschalteter Zufallsstartwert ohne Wert muss auffallen"
        assert "seed" in [field_of(b) for b in befunde], (
            "Der Befund hängt an keinem Feld — dann steht er nur im Preflight "
            "und nicht dort, wo man ihn beheben kann."
        )

    def test_the_crash_it_prevents_is_real(self):
        """Ohne die Prüfung stünde hier ein Stacktrace — nachgestellt.

        Ein Test, der nur zeigt, dass eine Meldung erscheint, belegt nicht,
        dass sie nötig war. Diese Zeile belegt es: Sie umgeht die Prüfung und
        ruft die Stelle direkt.
        """

        draft = default_config_draft()
        draft.use_seed = True
        draft.seed = None

        with pytest.raises(TypeError):
            run_launcher.draft_to_launch_config(draft)

    def test_switching_it_off_is_fine(self):
        """Und der Normalfall bleibt normal: kein Schalter, kein Befund."""

        from dashboard.config_catalog import validate_draft

        draft = default_config_draft()
        assert draft.use_seed is False and draft.seed is None
        assert validate_draft(draft) == []


class TestDerPreflightBeschreibtDenWirklichenLauf:
    """W1.3 — die Oberfläche zeigt nichts Wirkungsloses als wirksam.

    Der gemessene Ausgangspunkt war ein Satz mit drei falschen Aussagen: «alle 8
    hinterlegten Szenarien über 40 Ticks, ausgehend von der Standard-Ausgangslage
    aus `configs/`, ohne Sprachmodell; die Zahlen stimmen, die Agenten-Texte sind
    Platzhalter.» Die Ausgangslage ist je Szenario eine andere, Agenten-Texte
    gibt es überhaupt keine, und für den Abschlusstext wird Ollama sehr wohl
    gerufen.

    Geprüft wird der Satz, nicht sein Wortlaut: Ein Test, der auf Formulierungen
    besteht, macht jede Textpflege rot. Geprüft wird, dass **keine wirkungslose
    Zahl** darin steht und **die wirksame Bedingung** genannt ist.
    """

    def _satz(self, vergleich: bool) -> str:
        from dashboard.web.config_editor.start_flow import summary_sentence
        from dashboard.web.state import draft_to_dict

        draft = draft_to_dict(_entwurf(SWEEP if vergleich else EINZELLAUF))
        draft["rounds"] = 37
        return summary_sentence(draft)

    def test_it_does_not_quote_a_length_the_comparison_ignores(self):
        satz = self._satz(vergleich=True)

        assert "37" not in satz, (
            f"Der Preflight nennt beim Vergleich eine Länge aus dem Entwurf: {satz}\n"
            "Seit W1.2 läuft jedes Szenario in seiner eigenen."
        )

    def test_it_says_that_ollama_is_reached_anyway(self):
        """Die Aussage, die der Vertrag nicht abdeckt und die niemand erwartet."""

        satz = self._satz(vergleich=True)

        assert "Sprachmodell" in satz, (
            f"Der Preflight verschweigt, dass der Abschlusstext das Sprachmodell "
            f"braucht: {satz}"
        )

    def test_a_single_run_still_gets_its_own_sentence(self):
        """Und der Einzellauf verliert nichts — dort gelten die Werte ja."""

        satz = self._satz(vergleich=False)

        assert "37" in satz, "Beim Einzellauf gehört die eingestellte Länge in den Satz"

    def test_the_tiles_of_a_comparison_do_not_come_from_the_draft(self):
        """Sechs Kacheln aus dem Entwurf waren beim Vergleich sechs Behauptungen.

        Ziel-Auslastung, Segmente und aktive Systemgrößen stammen alle aus dem
        Entwurf; beim Vergleich bringt jedes Szenario seine eigenen mit. Sie
        anzuzeigen hieße, Zahlen zu nennen, mit denen nicht gerechnet wird.
        """

        from dashboard.web.config_editor.start_flow import _tiles
        from dashboard.web.state import draft_to_dict

        draft = draft_to_dict(_entwurf(SWEEP))
        text = str(_tiles(draft))

        for verraeter in ("Ziel-Auslastung", "Segmente", "Aktive Systemgrößen"):
            assert verraeter not in text, (
                f"Die Kachel «{verraeter}» steht beim Vergleich noch da, obwohl "
                "ihr Wert aus dem Entwurf kommt und dort nicht gilt."
            )

    def test_every_fixed_field_is_explained_from_the_contract(self):
        """Die Begründungen kommen aus dem Vertrag, nicht aus der Oberfläche.

        Stünden sie in `start_flow.py`, gäbe es zwei Quellen für dieselbe
        Aussage — und die Oberfläche behauptete irgendwann etwas, das der Lauf
        nicht mehr tut. Genau die Drift, gegen die W1.1 angetreten ist.
        """

        from dashboard.web.config_editor.start_flow import vorgaben_hinweis
        from dashboard.web.state import draft_to_dict

        hinweis = str(vorgaben_hinweis(draft_to_dict(_entwurf(SWEEP))))

        for feld in ("rounds", "apply_custom_overrides", "deterministic_only"):
            grund = vorgegebene_felder()[feld].grund
            assert grund[:40] in hinweis, (
                f"Die Begründung zu `{feld}` steht nicht im Hinweis — entweder "
                "fehlt sie, oder die Oberfläche formuliert eine eigene."
            )

    def test_a_single_run_gets_no_such_note(self):
        """Beim Einzellauf gilt alles, also gibt es nichts zu erklären."""

        from dashboard.web.config_editor.start_flow import vorgaben_hinweis
        from dashboard.web.state import draft_to_dict

        assert vorgaben_hinweis(draft_to_dict(_entwurf(EINZELLAUF))) is None


class TestDieMessungIstVollstaendig:
    """Ein Wächter, der Felder übersieht, ist schlechter als keiner."""

    def test_every_draft_field_is_measured_or_named(self):
        """Jedes Feld des Entwurfs wird gemessen, wählt den Pfad, oder steht als Lücke.

        Ohne diese Prüfung wüchse `ConfigDraft`, und der Wirkungstest bliebe
        grün, weil er das neue Feld schlicht nicht kennt — genau die Blindheit,
        die das Audit an den Abnahmekriterien gefunden hat.
        """

        alle = {f.name for f in dataclasses.fields(ConfigDraft)}
        abgedeckt = set(ANDERER_WERT) | PFADWAHL | set(NICHT_GEMESSEN)

        vergessen = sorted(alle - abgedeckt)
        assert not vergessen, (
            f"Neue Felder in `ConfigDraft`, die niemand auf Wirkung prüft: {vergessen}.\n"
            "Entweder einen anderen Wert in `ANDERER_WERT` eintragen, oder in "
            "`NICHT_GEMESSEN` mit Grund benennen. Stillschweigen ist keine Option."
        )

        verschwunden = sorted(abgedeckt - alle)
        assert not verschwunden, (
            f"Diese Felder gibt es in `ConfigDraft` nicht mehr: {verschwunden}.\n"
            "Der Test prüft damit ins Leere."
        )

    def test_the_probe_actually_moves_the_fingerprint(self, abdruck_von):
        """Die Messung selbst kann still blind werden — hier wird sie geprüft.

        Nähme der Abdruck den Zustand nicht wirklich auf (weil jemand die
        Nahtstelle verschiebt und `zustand` immer `None` bleibt), wäre jedes
        Feld «unwirksam», und der Sweep-Test oben bliebe trotzdem grün. Also:
        Ein Feld, von dem sicher ist, dass es wirkt, muss den Abdruck bewegen.
        """

        grund = abdruck_von(_entwurf(EINZELLAUF))
        assert grund.zustand, "Der Abdruck nimmt den Zustand gar nicht auf"
        assert grund.optionen, "Der Abdruck nimmt die RunnerOptions gar nicht auf"

        draft = _entwurf(EINZELLAUF)
        draft.rounds = ANDERER_WERT["rounds"]
        assert str(abdruck_von(draft)) != str(
            grund
        ), "Selbst die Lauflänge bewegt den Abdruck nicht — die Messung misst nichts."
