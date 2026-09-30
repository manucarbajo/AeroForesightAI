"""Eine Antwort des Sprachmodells mit echtem Zeilenumbruch in einem Text wird gelesen (P8-V5).

**Der Befund vom 2026-09-30:** Beim ersten Vorführbestand kam der Abschlusstext
bei drei von sechs Läufen aus der Vorlage. `llama3.2` hatte geantwortet, aber
in einen langen JSON-Text einen echten Zeilenumbruch geschrieben statt `\n` —
und `json.loads` weist Steuerzeichen in Zeichenketten ab. Die Antwort unten ist
gekürzt, ihre Form wörtlich: Umbruch im Text, Komma vor der Klammer.
"""

from __future__ import annotations

from src.cib.scenario_agent_node import _extract_json_object as lies_szenarien
from src.reporting.run_scenario_generator.prompt import _extract_json_object as lies_abschlusstext

ANTWORT = (
    '{\n  "title": "Nachhaltigkeitskrise bei hohem Wachstum",\n'
    '  "run_narrative": "Die Buchungsrate sinkt. (F3.2)]\n  \n  [Der Trend setzt sich fort.",\n'
    '  "scenarios": [\n    {"candidate_id": "C1", "story": "Absatz eins.\n\nAbsatz zwei."},\n'
    '    {"candidate_id": "C2", "story": "Kurz."},\n  ],\n}'
)


def test_der_abschlusstext_liest_einen_zeilenumbruch_im_text():
    gelesen = lies_abschlusstext(ANTWORT)

    assert gelesen is not None
    assert len(gelesen["scenarios"]) == 2
    assert "\n" in gelesen["run_narrative"]


def test_die_szenario_node_liest_ihn_ebenso():
    gelesen = lies_szenarien('{"narrative": "Zeile eins\nZeile zwei", "scenarios": []}')

    assert gelesen == {"narrative": "Zeile eins\nZeile zwei", "scenarios": []}
