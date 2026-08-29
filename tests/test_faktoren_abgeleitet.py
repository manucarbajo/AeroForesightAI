"""P2.0 — wie viel von der Faktorlage der Lauf schon selbst erzeugt.

Die Entscheidung «Rahmen statt Richter» will Faktoren, die aus dem Lauf
**abgeleitet** werden, statt ihn zu bestimmen. Bevor jemand dafür etwas umbaut,
gehört gemessen, wie weit das heute schon zutrifft — als Wirkungstest, nicht als
Codelektüre. Dasselbe Verfahren wie `test_web_wirkung.py`: zwei Läufe, alles
gleich außer der Startlage (einmal alle Faktoren auf `.1`, einmal auf `.2`), und
dann nachsehen, was von der Vorgabe übrig bleibt.

**Gemessen am 2026-08-29 gegen die ausgelieferte Konfiguration** — Zahl der
Faktoren, die ihre Startlage vergessen haben, nach *n* Ticks:

    Ticks   1   2   3   4   5   6   8  10  15  20
    gleich  4   6   5   6   6   6   6   6   6   7

Drei Gruppen stecken darin, und die Aufteilung ist der eigentliche Befund:

* **F2, F3, F6, F7 — der Rahmen.** Sie vergessen ihre Startlage **im ersten
  Tick**, weil ihre Regeln an *exogenen* Systemgrößen hängen: CO₂-Abgabe
  (F2, F6), SAF-Quote (F3), Ölpreis (F7). Für diese vier ist «Rahmen statt
  Richter» **bereits gebaut** — die Außenwelt setzt sie, nicht die Eingabe.
* **F1, F5 — der Lauf.** Sie folgen Buchungsrate und Gesellschaftsfaktor und
  brauchen ein paar Ticks. Der Einbruch bei Tick 3 ist kein Messfehler: Solange
  F4 zwischen den beiden Läufen auseinanderliegt, laufen auch die Buchungsraten
  auseinander, und F1 kippt in beiden Läufen zu verschiedenen Zeitpunkten.
* **F4 — die Vorgabe.** Es hält seine Startlage über den halben Lauf. Kein
  Fehler, sondern ein **Totband**: Seine Regeln greifen unter 115 (`F4.1`) und
  über 135 (`F4.2`), ein Hysteresefenster gegen Flattern. Der `cost_pressure`
  startet bei rund 118 und wächst je Tick um etwa eins — er liegt also bis etwa
  Tick 20 dazwischen, und dort feuert keine der beiden Regeln.

**Geprüft wird unten nur die erste Gruppe.** Sie ist die stabile Aussage und der
tragende Teil: Vier von sieben Faktoren sind schon heute reine Rahmengrößen. Die
Tabelle darüber ist Beschreibung, keine Zusage — eine Sperrklinke auf «genau
sechs nach sechs Ticks» wäre über den Tick-3-Einbruch hinweg spröde und würde
bei jeder Schwellenänderung rot, ohne etwas Tragendes zu sagen.

**Was daraus folgt und hier nicht steht:** Der Schritt «Faktorlage» im
Assistenten (P1.9-W3.3) fragt sieben Auswahlen ab; vier davon sind nach einem
Tick überschrieben. Das ist ein Befund für P1.9 und P2.0-C, kein Testgegenstand —
dieser Test misst nur, was der Fall ist.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.config_loader import build_initial_state
from src.llm.studio_helpers import MockLLM
from src.orchestration.simulation_runner import RunnerOptions, SimulationRunner

REPO_ROOT = Path(__file__).resolve().parents[1]
PROPERTIES = REPO_ROOT / "configs" / "properties.json"

FACTOR_IDS = [f"F{i}" for i in range(1, 8)]

#: Die Faktoren, die an **exogenen** Systemgrößen hängen und ihre Startlage
#: schon im ersten Tick vergessen. Für sie ist die Umdrehung bereits gebaut.
RAHMENFAKTOREN = {"F2", "F3", "F6", "F7"}

#: Ein Tick genügt für die geprüfte Aussage — und hält den Test schnell.
TICKS = 1


def _lauf(startziffer: str) -> dict[str, str]:
    """Ein Mock-Lauf mit allen sieben Faktoren auf `.<startziffer>`."""

    state = build_initial_state()
    state.clock.max_ticks = TICKS
    for fid in FACTOR_IDS:
        faktor = state.environment.factors.get(fid)
        ziel = f"{fid}.{startziffer}"
        if faktor is not None and ziel in faktor.possible_states:
            faktor.current_state = ziel

    runner = SimulationRunner(
        llm=MockLLM(),
        options=RunnerOptions(
            enable_market=True,
            enable_cib=True,
            verbose_ticks=False,
            checkpoint_interval=10_000,
        ),
    )
    ergebnis = runner.run(state)
    ende = getattr(ergebnis, "state", ergebnis)
    return {fid: ende.environment.factors[fid].current_state for fid in FACTOR_IDS}


@pytest.fixture(scope="module")
def endlagen() -> tuple[dict[str, str], dict[str, str]]:
    """Zwei Läufe, gegensätzliche Startlage, sonst identisch."""

    return _lauf("1"), _lauf("2")


class TestDerRahmenSetztVierFaktorenSchonHeute:
    """Die tragende Aussage: Für F2, F3, F6, F7 ist die Vorgabe folgenlos."""

    def test_sie_vergessen_ihre_startlage_im_ersten_tick(
        self, endlagen: tuple[dict[str, str], dict[str, str]]
    ) -> None:
        aus_eins, aus_zwei = endlagen
        haengen_geblieben = {
            fid: (aus_eins[fid], aus_zwei[fid])
            for fid in sorted(RAHMENFAKTOREN)
            if aus_eins[fid] != aus_zwei[fid]
        }
        assert not haengen_geblieben, (
            "Diese Faktoren galten als Rahmengrößen — ihre Startlage sollte nach "
            f"einem Tick überschrieben sein, ist es aber nicht: {haengen_geblieben}. "
            "Entweder ist eine Regel weggefallen, oder ihre Schwelle liegt jetzt "
            "neben dem, was die exogene Trajektorie im ersten Tick erreicht. "
            "Beides verkleinert die Grundlage von P2.0."
        )

    def test_es_sind_genau_diese_vier(
        self, endlagen: tuple[dict[str, str], dict[str, str]]
    ) -> None:
        """Sperrklinke in beide Richtungen.

        Kommt ein fünfter dazu, ist das eine gute Nachricht — und der Anlass, die
        Menge oben und die Stufenbeschreibung von P2.0 nachzuziehen. Ein
        schweigend gewachsener Wert wäre wieder aus dem falschen Grund grün.
        """

        aus_eins, aus_zwei = endlagen
        gemessen = {fid for fid in FACTOR_IDS if aus_eins[fid] == aus_zwei[fid]}
        assert gemessen == RAHMENFAKTOREN, (
            "Die Menge der Faktoren, die nach einem Tick von ihrer Startlage "
            "unabhängig sind, hat sich verschoben.\n"
            f"  erwartet: {sorted(RAHMENFAKTOREN)}\n"
            f"  gemessen: {sorted(gemessen)}\n"
            "Das ist kein Fehler, sondern eine Nachricht: Der Docstring dieses "
            "Moduls und die Stufenbeschreibung von P2.0 im Projektplan gehören "
            "nachgezogen."
        )

    def test_jede_ihrer_regeln_haengt_an_einer_exogenen_groesse(self) -> None:
        """Der Grund, nicht nur die Wirkung — sonst wäre die Gruppe Zufall."""

        daten = json.loads(PROPERTIES.read_text(encoding="utf-8"))
        exogen = {p["id"] for p in daten["system_properties"]} - {
            "ticket_price",
            "provider_markup",
        }

        ohne_exogene_quelle: list[str] = []
        for regel in daten["factor_rules"]:
            if regel["factor_id"] not in RAHMENFAKTOREN:
                continue
            klausel = regel.get("when") or {}
            quelle = klausel.get("system_property")
            # F6 hängt zusätzlich an F3, das seinerseits exogen getrieben ist —
            # eine Kette aus Rahmengrößen bleibt eine Rahmengröße.
            if quelle in exogen or klausel.get("factor") in RAHMENFAKTOREN:
                continue
            ohne_exogene_quelle.append(f"{regel['id']} ({klausel})")

        assert not ohne_exogene_quelle, (
            "Eine Regel eines Rahmenfaktors hängt nicht mehr an einer exogenen "
            f"Größe: {ohne_exogene_quelle}. Dann ist der Faktor keine reine "
            "Rahmengröße mehr."
        )


class TestDasTotbandErklaertF4:
    """Nicht «F4 ist kaputt», sondern «cost_pressure liegt zwischen den Schwellen»."""

    def test_die_beiden_schwellen_lassen_eine_luecke(self) -> None:
        regeln = [
            r
            for r in json.loads(PROPERTIES.read_text(encoding="utf-8"))["factor_rules"]
            if r["factor_id"] == "F4"
        ]
        assert len(regeln) == 2, f"F4 hat nicht mehr genau zwei Regeln: {regeln}"

        nach_oben = next(r for r in regeln if "above" in (r.get("when") or {}))
        nach_unten = next(r for r in regeln if "below" in (r.get("when") or {}))

        untere = float(nach_unten["when"]["below"])
        obere = float(nach_oben["when"]["above"])

        assert nach_unten["when"].get("metric") == "cost_pressure"
        assert nach_oben["when"].get("metric") == "cost_pressure"
        assert untere < obere, "die Schwellen überlappen — dann gäbe es kein Totband"

        # Der gemessene cost_pressure-Bereich der ersten Ticks eines Laufs mit
        # ausgelieferter Konfiguration: rund 118 bis 122.
        assert untere <= 118.0 and 122.0 <= obere, (
            f"Das Totband ({untere} … {obere}) deckt den gemessenen "
            "cost_pressure-Bereich 118–122 der frühen Ticks nicht mehr ab. Dann "
            "leitet sich F4 früher ab als beschrieben — Docstring nachziehen."
        )
