"""Alles, was das Sprachmodell schreibt, ist deutsch verlangt — an jedem Aufruf (P8-V2).

Am 2026-09-29 waren 15 von 17 Texten der Agenten englisch; die Anweisung fehlte
bei den Agenten und der Szenario-Node, und Abschlusstext und Abfrage verlangten
Deutsch je auf eigene Weise. Seither steht sie an einer Stelle
(`src/llm/sprache.py`), und jeder Aufrufer hängt sie über `auf_deutsch` an.

**Der Wächter sucht statt aufzuzählen:** Er findet jeden Aufruf ``.call(`` in
``src/`` im Syntaxbaum und verlangt, dass sein Prompt durch `auf_deutsch` geht.
Wer morgen einen fünften Aufrufer baut, bekommt Bescheid, ohne dass ihn jemand
einträgt. **Ob das Modell der Anweisung folgt**, misst der Prüfsatz
(`python -m src.reporting.pruefsatz_sprachmodell`, Spalte «englisch») — das kann
kein Test ohne Sprachmodell.
"""

from __future__ import annotations

import ast
from pathlib import Path

from src.agents.agent_node import AgentNode
from src.config_loader import build_initial_state
from src.llm import AUSGABESPRACHE, auf_deutsch

SRC = Path(__file__).resolve().parents[1] / "src"

#: Aufrufe ``.call(``, die kein Prompt an ein Sprachmodell sind oder ihn nur
#: weiterreichen — je mit Grund. Eine Ausnahme ohne Fundstelle wird gemeldet.
AUSNAHMEN = {
    (
        "llm/studio_helpers.py",
        "client",
    ): "LocalOllama reicht den fertigen Prompt seines Aufrufers an den Client weiter",
    (
        "reporting/pruefsatz_sprachmodell.py",
        "OllamaClient",
    ): "Erreichbarkeitsprobe vor dem Prüfsatz, kein Text für einen Leser",
    ("run_simulation.py", "subprocess"): "startet einen Prozess, fragt kein Modell",
}


def _empfaenger(knoten: ast.expr) -> str:
    while isinstance(knoten, (ast.Attribute, ast.Call)):
        knoten = knoten.value if isinstance(knoten, ast.Attribute) else knoten.func
    return knoten.id if isinstance(knoten, ast.Name) else type(knoten).__name__


def _aufrufe() -> list[tuple[str, str, ast.Call]]:
    gefunden = []
    for pfad in sorted(SRC.rglob("*.py")):
        baum = ast.parse(pfad.read_text(encoding="utf-8"))
        for knoten in ast.walk(baum):
            if isinstance(knoten, ast.Call) and isinstance(knoten.func, ast.Attribute):
                if knoten.func.attr == "call":
                    gefunden.append(
                        (pfad.relative_to(SRC).as_posix(), _empfaenger(knoten.func.value), knoten)
                    )
    return gefunden


def _geht_durch_auf_deutsch(knoten: ast.Call) -> bool:
    if not knoten.args:
        return False
    erstes = knoten.args[0]
    if (
        isinstance(erstes, ast.Call)
        and isinstance(erstes.func, ast.Name)
        and erstes.func.id == "auf_deutsch"
    ):
        return True
    # `self.build_prompt(...)` in der Abfrage: der Prompt entsteht dort schon mit `auf_deutsch`.
    return (
        isinstance(erstes, ast.Call)
        and isinstance(erstes.func, ast.Attribute)
        and erstes.func.attr == "build_prompt"
    )


class TestJederAufrufVerlangtDeutsch:
    def test_es_gibt_ueberhaupt_aufrufe(self):
        """Ohne diesen Test wäre der nächste für immer grün, sobald die Suche nichts findet."""

        assert len([a for a in _aufrufe() if (a[0], a[1]) not in AUSNAHMEN]) >= 4

    def test_jeder_prompt_geht_durch_auf_deutsch(self):
        ohne = [
            f"src/{datei}:{knoten.lineno} ({empfaenger}.call)"
            for datei, empfaenger, knoten in _aufrufe()
            if (datei, empfaenger) not in AUSNAHMEN and not _geht_durch_auf_deutsch(knoten)
        ]
        assert not ohne, (
            "Diese Aufrufe schicken einen Prompt ohne die Sprachanweisung an das Modell — "
            "`auf_deutsch(prompt)` aus `src.llm` davor setzen:\n  " + "\n  ".join(ohne)
        )

    def test_jede_ausnahme_hat_eine_fundstelle(self):
        vorhanden = {(datei, empfaenger) for datei, empfaenger, _ in _aufrufe()}
        verwaist = [f"{d} ({e})" for d, e in AUSNAHMEN if (d, e) not in vorhanden]
        assert not verwaist, "Ausnahmen ohne Aufruf dahinter: " + ", ".join(verwaist)

    def test_build_prompt_der_abfrage_benutzt_auf_deutsch(self):
        """Die eine Stelle, an der der Wächter einem Methodennamen vertraut, wird selbst geprüft."""

        quelle = (SRC / "reporting" / "state_explorer.py").read_text(encoding="utf-8")
        baum = ast.parse(quelle)
        methode = next(
            k for k in ast.walk(baum) if isinstance(k, ast.FunctionDef) and k.name == "build_prompt"
        )
        assert any(
            isinstance(k, ast.Call) and isinstance(k.func, ast.Name) and k.func.id == "auf_deutsch"
            for k in ast.walk(methode)
        )


class TestDieAnweisungKommtAn:
    def test_der_agent_bekommt_sie_am_ende(self):
        class Merker:
            prompt = ""

            def call(self, prompt: str) -> str:
                Merker.prompt = prompt
                return '{"reasoning": "", "actions": ["NO_OP"], "state_changes": [], "events": []}'

        state = build_initial_state()
        consumer = next(agent for agent in state.agents if agent.id == "consumer")
        AgentNode(config=consumer, llm=Merker()).invoke(state)
        assert Merker.prompt.rstrip().endswith(AUSGABESPRACHE)

    def test_vor_der_aufforderung_zu_antworten(self):
        prompt = auf_deutsch("Frage: Wie war der Preis?", schluss="\n\nANSWER:")
        assert prompt.endswith("ANSWER:")
        assert prompt.index(AUSGABESPRACHE) < prompt.index("ANSWER:")

    def test_kennungen_bleiben_ausdruecklich_unuebersetzt(self):
        """`agent_node` erkennt `NO_OP` am genauen Wort — übersetzt, bräche das Einlesen."""

        for kennung in ("NO_OP", "event_type", "F1.1"):
            assert kennung in AUSGABESPRACHE
