"""P2.13 — die höchstpriorisierte Regel entscheidet einen Faktor, und zwar dauerhaft.

**Der Befund, der dieses Paket ausgelöst hat** (gemessen am 2026-09-07): F6
wechselte in **jedem einzelnen Tick** den Zustand, von Tick 16 bis zum Ende des
Laufs — über 120 Ticks 105 Wechsel im Takt F6.1 → F6.2 → F6.1. Der
gesellschaftliche Wertewandel kippte monatlich.

**Die Ursache war eine fehlende Zeile in `apply_factor_rules`.** Die Schleife
markierte einen Faktor nur dann als entschieden, wenn eine Regel seinen Zustand
*änderte*. Traf die höchstpriorisierte Regel schon zu — ihr Ziel war bereits
gesetzt —, fiel der Faktor an die nächste Regel, auch an eine, die das Gegenteil
verlangt:

* `f6_flight_shaming_high_tax`: `carbon_tax_level` über 80 → **F6.2**, Priorität 10
* `f6_tech_breakthrough_acceptance`: F3 ist F3.2 → **F6.1**, Priorität 3

Ab Tick 16 treffen **beide dauerhaft** zu. Die Priorität hätte das entscheiden
sollen; sie tat es nicht, weil die höhere Regel nach ihrem eigenen Erfolg aus dem
Weg ging.

**Was daran teuer war, ist nicht das Flattern, sondern der Endzustand:** Er hing
an der **Parität** der Tickzahl. Ein Lauf über 40 Ticks endete mit F6.1, einer
über 41 mit F6.2 — bei sonst identischer Konfiguration. Und genau diesen
Endzustand lesen das Szenario-Narrativ und die CIB-Bewertung.

**Warum die Suite es nicht gesehen hat:** Sie hat es nie gemessen. Nach dem Fix
liefen alle 1669 Zusagen unverändert grün — kein einziger Test hielt das
Verhalten fest, in keiner Richtung. `test_faktoren_abgeleitet.py` prüft, dass
Faktoren ihre Startlage vergessen (ein Tick genügt dafür), und niemand hat
darüber hinaus geschaut.

**Diese Datei hält deshalb eine Zusage und keinen Ist-Stand** — anders als
`test_faktoren_abgeleitet.py` oder `test_nachfragetreiber.py`. Ein rotes
Ergebnis heißt hier: Ein Faktor kippt wieder im Takt, und der Endzustand eines
Laufs hängt an seiner Länge.
"""

from __future__ import annotations

import pytest

from src.config_loader import build_initial_state
from src.llm.studio_helpers import MockLLM
from src.market.factor_dynamics import apply_factor_rules
from src.orchestration.simulation_runner import RunnerOptions, SimulationRunner

#: So lang wie ein Standardlauf. Die echten Übergänge liegen bei Tick 15 bis 17;
#: was danach kommt, ist der Bereich, in dem das Flattern lief.
TICKS = 40


def _verlauf() -> list[dict[str, str]]:
    """Ein deterministischer Lauf, und die Faktorlage **je Tick**.

    Der Zustand führt sie selbst mit (`factor_timeseries`) — dieselbe Quelle,
    aus der `timeseries/factors.csv` geschrieben wird. Der Wächter misst damit
    das, was auch im Artefakt landet, und nicht eine Nachbildung daneben.
    """

    zustand = build_initial_state()
    zustand.clock.max_ticks = TICKS
    runner = SimulationRunner(
        llm=MockLLM(),
        options=RunnerOptions(
            enable_market=True,
            enable_cib=True,
            verbose_ticks=False,
            checkpoint_interval=10_000,
        ),
    )
    ergebnis = runner.run(zustand)
    ende = getattr(ergebnis, "state", ergebnis)
    return list(ende.factor_timeseries)


def _flattern(verlauf: list[dict[str, str]]) -> list[str]:
    """Jede Stelle, an der ein Faktor mit Periode 1 hin und her kippt.

    **Gesucht ist `A → B → A` in drei aufeinanderfolgenden Ticks.** Das ist die
    präzise Form des Befunds und nicht bloß «hat sich oft geändert»: Ein Faktor
    *darf* zurückwechseln, wenn die Welt es hergibt — ein Rahmenszenario nimmt
    die CO₂-Abgabe durchaus wieder zurück, und dann ist der Rückweg richtig.
    Was keine exogene Größe hergibt, ist ein Wechsel **im Tick-Takt**.
    """

    if len(verlauf) < 3:
        return []
    faktoren = [k for k in verlauf[0] if k != "tick"]
    befunde = []
    for fid in faktoren:
        for i in range(len(verlauf) - 2):
            a, b, c = (verlauf[i + n].get(fid) for n in range(3))
            if a != b and a == c:
                befunde.append(
                    f"{fid}: Tick {verlauf[i]['tick']}–{verlauf[i + 2]['tick']} " f"{a} → {b} → {c}"
                )
                break  # Eine Stelle je Faktor genügt als Nachweis
    return befunde


@pytest.fixture(scope="module")
def verlauf() -> list[dict[str, str]]:
    return _verlauf()


class TestKeinFaktorKipptImTakt:
    """**Die tragende Zusage dieser Datei.**"""

    def test_der_verlauf_deckt_den_ganzen_lauf(self, verlauf):
        """Sonst misst die Zusage unten einen Ausschnitt und ist trotzdem grün."""

        assert len(verlauf) == TICKS, (
            f"{len(verlauf)} Einträge für {TICKS} Ticks — der Verlauf ist "
            "unvollständig, und dann sagt die Zusage darunter nichts."
        )

    def test_kein_faktor_wechselt_hin_und_zurueck(self, verlauf):
        befunde = _flattern(verlauf)

        assert not befunde, (
            "Diese Faktoren kippen im Tick-Takt — der Endzustand eines Laufs "
            "hängt damit an seiner Länge:\n  " + "\n  ".join(befunde)
        )

    def test_die_uebergaenge_liegen_am_anfang_und_hoeren_auf(self, verlauf):
        """Die Gegenprobe: Der Wächter darf nicht durch **Stillstand** grün sein.

        Ein Lauf, in dem sich nie etwas bewegt, hat auch kein Flattern — und
        wäre ein anderer Befund. Gemessen liegen die echten Übergänge bei Tick
        15 bis 17 (CO₂-Abgabe springt auf 120, SAF-Mandat auf 5 %); danach
        kommt nichts mehr.
        """

        wechsel = [
            (int(verlauf[i + 1]["tick"]), fid)
            for i in range(len(verlauf) - 1)
            for fid in verlauf[0]
            if fid != "tick" and verlauf[i][fid] != verlauf[i + 1][fid]
        ]

        assert wechsel, "Kein einziger Faktorwechsel — dann prüft der Wächter nichts."
        assert len(wechsel) <= 10, (
            f"{len(wechsel)} Wechsel über {TICKS} Ticks. Vor P2.13 waren es 111 über "
            "120 Ticks, davon 105 allein F6."
        )


class TestDiePrioritaetEntscheidetAuchWennSieSchonErfuelltIst:
    """Der Mechanismus, ohne Lauf — schnell und ohne Umweg über die Config.

    Die Zusage oben misst das Ergebnis. Diese hier misst die **Ursache**, und
    zwar an einem gebauten Fall: zwei Regeln auf denselben Faktor, die höhere
    schon erfüllt, die niedrigere widersprechend. Vor P2.13 gewann die
    niedrigere.
    """

    #: Ein Tick, an dem die Bedingung der gebauten Regeln **wirklich** zutrifft.
    #: Die ausgelieferte CO₂-Abgabe steht bei Tick 1 auf 50 und springt erst bei
    #: Tick 15 auf 120. Der erste Anlauf dieser Klasse setzte Tick 1 — dort traf
    #: keine der beiden Regeln zu, und die Zusage «die niedrigere überschreibt
    #: nicht» war grün, weil überhaupt nichts geschah. Aufgefallen ist das nur,
    #: weil die Gegenprobe daneben (die *setzen* muss) fehlschlug.
    TICK_MIT_HOHER_ABGABE = 20

    def _zustand_mit_zwei_regeln(self, ziel_hoch: str, ziel_niedrig: str):
        from src.market.property_engine import resolve_system_properties
        from src.models.property_models import FactorRule

        zustand = build_initial_state()
        zustand.clock.current_tick = self.TICK_MIT_HOHER_ABGABE
        properties = zustand.properties
        # **Die Voraussetzung prüfen, nicht annehmen.**
        abgabe = resolve_system_properties(self.TICK_MIT_HOHER_ABGABE, properties)[
            "carbon_tax_level"
        ]
        assert abgabe > 80, (
            f"Bei Tick {self.TICK_MIT_HOHER_ABGABE} steht die CO₂-Abgabe auf {abgabe}; "
            "die gebauten Regeln greifen dann nicht, und beide Zusagen darunter "
            "messen nichts."
        )
        # Nur die beiden gebauten Regeln, damit nichts anderes hineinspielt.
        properties.factor_rules = [
            FactorRule.model_validate(
                {
                    "id": "hoch",
                    "factor_id": "F6",
                    "when": {"system_property": "carbon_tax_level", "above": 80},
                    "effect": {"set_state": ziel_hoch},
                    "priority": 10,
                }
            ),
            FactorRule.model_validate(
                {
                    "id": "niedrig",
                    "factor_id": "F6",
                    "when": {"system_property": "carbon_tax_level", "above": 80},
                    "effect": {"set_state": ziel_niedrig},
                    "priority": 3,
                }
            ),
        ]
        return zustand

    def test_die_niedrigere_regel_ueberschreibt_nicht(self):
        """Der Fall, aus dem der Befund kam."""

        zustand = self._zustand_mit_zwei_regeln("F6.2", "F6.1")
        zustand.environment.factors["F6"].current_state = "F6.2"

        apply_factor_rules(zustand)

        assert zustand.environment.factors["F6"].current_state == "F6.2", (
            "Die Regel mit Priorität 3 hat den Faktor überschrieben, obwohl die "
            "Regel mit Priorität 10 zutraf und ihr Ziel schon gesetzt war."
        )

    def test_und_sie_setzt_ihn_weiterhin_wenn_sie_gewinnt(self):
        """Die Gegenprobe: Der Fix darf die Regeln nicht **stillstellen**.

        Ein `updated_factors.add()` an der falschen Stelle machte aus dem
        Flattern einen eingefrorenen Faktor — auch falsch, und von der Zusage
        oben nicht zu unterscheiden.
        """

        zustand = self._zustand_mit_zwei_regeln("F6.2", "F6.1")
        zustand.environment.factors["F6"].current_state = "F6.1"

        apply_factor_rules(zustand)

        assert zustand.environment.factors["F6"].current_state == "F6.2", (
            "Die höchstpriorisierte Regel hat den Faktor nicht gesetzt — der Fix "
            "hat die Auswertung stillgestellt statt sie zu entscheiden."
        )


def test_der_waechter_wuerde_das_flattern_erkennen():
    """Ohne diese Zusage wäre grün nur die Abwesenheit einer Messung."""

    echt = [
        {"tick": 1, "F6": "F6.1"},
        {"tick": 2, "F6": "F6.2"},
        {"tick": 3, "F6": "F6.1"},
    ]
    ruhig = [
        {"tick": 1, "F6": "F6.1"},
        {"tick": 2, "F6": "F6.2"},
        {"tick": 3, "F6": "F6.2"},
    ]

    assert _flattern(echt), "Der Detektor sieht ein A → B → A nicht."
    assert not _flattern(ruhig), "Der Detektor meldet einen sauberen Übergang."
