"""Kein Konsument verwechselt Erzähltes mit Gerechnetem (P1.3).

Bis zum 2026-08-30 lagen beide Sammlungen im selben untypisierten Dict
(`cib_matrix.metadata`), unter Namen, die sich um ein Wort unterschieden:
`scenario_candidates` für die gerechneten Kandidaten, `scenarios` für das
LLM-Narrativ. Und das Narrativ trug Zahlen — seine `key_relationships` nannten
Einflusswerte zwischen Deskriptoren, geklemmt, aber **erfunden**. Sie hießen
`influence`, genau wie `CIBCell.influence`, und lagen im selben Artefakt.

**Diese Datei misst die Zusage, statt sie zu zählen.** Sie erzeugt ein echtes
Narrativ über einen Mock-Aufruf, geht das geschriebene Ergebnis durch und
verlangt für **jeden** Zahlenwert darin, dass sein Feldname die Herkunft trägt.
Eine handgepflegte Liste erwischter Felder fände nur die Fälle, die es schon
gab.
"""

from __future__ import annotations

import json

import pytest

from src.cib.scenario_agent_node import ScenarioAgentNode, render_scenarios_markdown
from src.models.scenario_models import ERZAEHLT, GERECHNET, ErzaehlteSzenarien

#: Feldnamen, unter denen eine Zahl stehen darf, ohne dass sie behauptet ist:
#: Ordnungszahlen und Ähnliches, die keine Wirkung ausdrücken.
HARMLOS = {"id", "rank", "index"}


class _Antwort:
    """Ein Sprachmodell, das genau das liefert, was der Prompt verlangt."""

    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def call(self, prompt: str) -> str:  # noqa: ARG002 - der Prompt ist hier egal
        return json.dumps(self._payload, ensure_ascii=False)


def _narrativ_mit_zahlen() -> dict:
    return {
        "scenarios": [
            {
                "id": "S1",
                "title": "Regulierung greift durch",
                "narrative": "Die Abgabe wirkt, die Nachfrage weicht auf die Schiene aus.",
                "selected_descriptors": ["F2.2", "F5.2"],
                "key_relationships": [
                    {"source": "F2.2", "target": "F5.2", "influence": 3, "why": "Kostendruck"},
                    {"source": "F5.2", "target": "F1.1", "influence": -2, "why": "Verlagerung"},
                ],
                "implications": ["Kurzstrecke verliert zuerst"],
            }
        ]
    }


class TestDieGrenzeStehtImSchema:
    """Zwei Strukturen, nicht zwei Schlüssel."""

    def test_the_two_collections_are_not_one_word_apart(self):
        """`scenarios` und `scenario_candidates` waren genau das."""

        from src.reporting.output_writer.provenance import RUN_PRODUCED_MATRIX_METADATA

        szenario_schluessel = sorted(
            k for k in RUN_PRODUCED_MATRIX_METADATA if "szenarien" in k or "scenario" in k
        )

        assert szenario_schluessel == ["erzaehlte_szenarien", "gerechnete_szenarien"], (
            "Die Szenario-Schlüssel im Lauf-Zustand sind nicht die erwarteten: "
            f"{szenario_schluessel}"
        )
        a, b = szenario_schluessel
        assert a not in b and b not in a, "Ein Schlüssel steckt im anderen"

    def test_every_collection_carries_its_own_provenance(self):
        """Auch wer nur das JSON sieht, kann die Herkunft beantworten."""

        from src.models.scenario_models import GerechneteSzenarien

        assert ErzaehlteSzenarien().model_dump()["herkunft"] == ERZAEHLT
        assert GerechneteSzenarien().model_dump()["herkunft"] == GERECHNET
        assert ERZAEHLT != GERECHNET


class TestJedeZahlImNarrativSagtWoherSieKommt:
    """Der eigentliche Befund: Das Narrativ trägt Zahlen."""

    def _zahlen_mit_ihren_feldern(self, knoten, pfad=()):
        """Jeden Zahlenwert der Struktur mit dem Feldnamen, unter dem er steht."""

        if isinstance(knoten, dict):
            for schluessel, wert in knoten.items():
                yield from self._zahlen_mit_ihren_feldern(wert, (*pfad, str(schluessel)))
        elif isinstance(knoten, list):
            for eintrag in knoten:
                yield from self._zahlen_mit_ihren_feldern(eintrag, pfad)
        elif isinstance(knoten, bool):
            return
        elif isinstance(knoten, (int, float)):
            yield pfad, knoten

    def test_no_number_in_the_narrative_hides_its_origin(self):
        """**Gemessen an der Struktur, nicht an einer Liste bekannter Felder.**

        Jede Zahl im erzählten Teil muss unter einem Feldnamen stehen, der ihre
        Herkunft trägt — oder unter einem, der offensichtlich keine Wirkung
        ausdrückt. Ein neues Feld mit einem harmlosen Namen fällt damit auf,
        auch wenn niemand es hier einträgt.
        """

        from src.models.scenario_models import ErzaehlteBeziehung, ErzaehltesSzenario

        erzaehlt = ErzaehlteSzenarien(
            szenarien=[
                ErzaehltesSzenario(
                    id="S1",
                    title="T",
                    key_relationships=[
                        ErzaehlteBeziehung(source="F1.1", target="F2.1", behaupteter_einfluss=3)
                    ],
                )
            ]
        )

        namenlos = [
            (pfad, wert)
            for pfad, wert in self._zahlen_mit_ihren_feldern(erzaehlt.model_dump())
            if pfad[-1] not in HARMLOS and "behauptet" not in pfad[-1]
        ]

        assert not namenlos, (
            "Diese Zahlen im erzählten Teil sagen nicht, dass sie behauptet sind:\n  "
            + "\n  ".join(f"{'.'.join(p)} = {w}" for p, w in namenlos)
            + "\n\nEin Feld, das eine Wirkung ausdrückt, heißt `behaupteter_…` — "
            "sonst steht es im selben Vokabular wie `CIBCell.influence`."
        )

    def test_the_word_influence_does_not_appear_in_the_narrative(self):
        """`influence` ist der Name des **echten** Matrixwerts."""

        rohtext = json.dumps(ErzaehlteSzenarien().model_json_schema(), ensure_ascii=False)

        assert '"influence"' not in rohtext, (
            "Das Schema des Narrativs kennt ein Feld `influence` — genau den "
            "Namen, den `CIBCell` für den gerechneten Wert benutzt."
        )


class TestDerBerichtSagtEsAuchInWorten:
    """Ein Schema hilft niemandem, der das Markdown liest."""

    def test_the_report_marks_the_claimed_numbers(self, monkeypatch):
        from src.models.scenario_models import ErzaehlteBeziehung, ErzaehltesSzenario

        erzaehlt = ErzaehlteSzenarien(
            szenarien=[
                ErzaehltesSzenario(
                    id="S1",
                    title="Titel",
                    key_relationships=[
                        ErzaehlteBeziehung(
                            source="F2.2", target="F5.2", behaupteter_einfluss=3, why="Kosten"
                        )
                    ],
                )
            ]
        )

        class _Zustand:
            class config:  # noqa: N801 - Attrappe
                name = "Probe"

            cib_matrix = None

        text = render_scenarios_markdown(erzaehlt.model_dump(), _Zustand())

        assert "behauptet" in text.lower(), (
            "Der Bericht nennt die erzählten Werte nicht als behauptet:\n" + text
        )
        assert (
            "key_relationships" not in text
        ), "Der Bericht zeigt den technischen Feldnamen statt einer Aussage"


class TestDerKnotenLegtBeidesGetrenntAb:
    """Am laufenden Knoten, nicht nur am Modell."""

    def test_the_node_stores_two_distinguishable_collections(self, cib_state):
        knoten = ScenarioAgentNode(llm=_Antwort(_narrativ_mit_zahlen()))
        ergebnis = knoten.invoke(cib_state)

        metadata = ergebnis.cib_matrix.metadata
        assert "gerechnete_szenarien" in metadata
        assert "erzaehlte_szenarien" in metadata
        assert "scenarios" not in metadata, "Der alte, mehrdeutige Schlüssel ist zurück"
        assert "scenario_candidates" not in metadata

        erzaehlt = metadata["erzaehlte_szenarien"]
        beziehung = erzaehlt["szenarien"][0]["key_relationships"][0]
        assert "influence" not in beziehung
        assert beziehung["behaupteter_einfluss"] == 3


@pytest.fixture
def cib_state():
    """Ein Zustand mit Matrix — sonst steigt der Knoten sofort wieder aus."""

    from src.config_loader import build_initial_state

    zustand = build_initial_state()
    if zustand.cib_matrix is None:
        pytest.skip("Kein CIB-Matrix im Ausgangszustand — dann prüft dieser Test nichts")
    return zustand


# --- Der Weg vom Node ins Artefakt (P2.0-B) --------------------------------


class TestDerSchluesselDriftetNichtWiederWeg:
    """Zweimal derselbe Fehler, eine Ebene auseinander.

    P1.3 hat die Metadaten-Schlüssel umbenannt (`scenarios` →
    `erzaehlte_szenarien`) und dabei `render_scenarios_markdown` mitgezogen —
    der Kommentar dort hält es fest. **Nicht mitgezogen wurde
    `run_simulation.py`**, das den alten Schlüssel weiterlas. Ergebnis: Jeder
    Lauf schrieb ein leeres `scenarios.json`, und niemand hat es bemerkt, weil
    niemand die Datei liest.

    Diese Tests prüfen den **Weg**, nicht die Namen: Was der Node ablegt, muss
    der Schreiber finden, und was der Schreiber übergibt, muss der Bericht
    lesen können. Ein Umbenennen, das eine der beiden Seiten vergisst, wird rot.
    """

    def test_der_schreiber_liest_den_schluessel_des_nodes(self):
        """Der Bauplan von `run_simulation`, gegen den Node gehalten."""

        import inspect

        from src import run_simulation
        from src.cib import scenario_agent_node

        quelle = inspect.getsource(run_simulation)
        block = quelle[quelle.index("scenarios_path = save_scenarios") - 2000 :]

        abgelegt = "erzaehlte_szenarien"
        assert abgelegt in inspect.getsource(
            scenario_agent_node.ScenarioAgentNode.invoke
        ), "Der Node legt das Narrativ unter einem anderen Schlüssel ab."
        assert abgelegt in block, (
            "`run_simulation` liest nicht den Schlüssel, unter dem der Node ablegt. "
            "Genau so ist das Artefakt seit P1.3 leer geblieben."
        )

    def test_das_artefakt_traegt_das_narrativ_und_nicht_nichts(self, cib_state):
        """Der Weg als Ganzes, an einem echten Mock-Narrativ gemessen."""

        state = ScenarioAgentNode(llm=_Antwort(_narrativ_mit_zahlen())).invoke(cib_state)

        nutzlast = (state.cib_matrix.metadata or {}).get("erzaehlte_szenarien") or {"szenarien": []}

        assert nutzlast.get("szenarien"), "Der Node hat kein Narrativ abgelegt"

        bericht = render_scenarios_markdown(nutzlast, state)
        assert "_Keine Szenarien generiert._" not in bericht, (
            "Der Bericht findet das Narrativ nicht — die Form der Nutzlast passt nicht "
            "zu dem, was er liest."
        )

    def test_der_bericht_sagt_woher_die_konstellationen_kommen(self, cib_state):
        bericht = render_scenarios_markdown({"szenarien": []}, cib_state)

        assert "Einflussmatrix" in bericht and "nicht aus" in bericht, (
            "Der Bericht steht in einem Lauf-Verzeichnis und sagt nicht, dass seine "
            "Konstellationen aus der Matrix stammen statt aus dem Lauf."
        )

    def test_der_nenner_ist_die_zahl_der_bewerteten(self):
        """«1 von 1 konsistent» machte aus einem Befund eine Erfolgsmeldung."""

        from pathlib import Path

        from src.cib.scenario_consistency import ScenarioDeriver
        from src.models.cib_models import CIBMatrix

        matrix = CIBMatrix.model_validate(
            json.loads(Path("configs/cib_frozen.json").read_text(encoding="utf-8"))
        )
        ergebnis = ScenarioDeriver(matrix).derive_scenarios(top_n=3, allow_inconsistent=False)

        assert ergebnis.total_evaluated == 128, (
            f"Der Nenner ist {ergebnis.total_evaluated} statt 128 — dann zählt er "
            "wieder die behaltenen statt die bewerteten Konstellationen."
        )
        assert ergebnis.consistent_count <= ergebnis.total_evaluated
