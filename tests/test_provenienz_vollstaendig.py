"""Kein Startpfad lässt ein Herkunftsfeld weg — es fiele still auf `False`.

**Gefunden am 2026-08-30 beim Nachmessen eines Dashboard-Laufs.** Er trug
`compute_mode: "llm"`, `mock_llm: false` und `degraded: false` — während gar kein
Sprachmodell erreichbar war und die Agentenbeiträge im Protokoll wörtlich
`"why": "mock"` sagten. Der Mock hatte gerechnet, und das Artefakt behauptete
einen vollwertigen Lauf.

Die Ursache war eine Auslassung, kein Fehler: `launch_from_draft` baut für
`save_run_metadata` ein `SimpleNamespace` und führte darin `deterministic_only`,
aber **nicht** `mock_llm`. Auf der anderen Seite steht
`bool(getattr(args, "mock_llm", False))` — ein fehlendes Feld ist von einem
abgeschalteten nicht zu unterscheiden. Damit war **jeder** Dashboard-Lauf
«Ohne Sprachmodell» als LLM-Lauf protokolliert.

Das trifft die zweite Hälfte von Invariante 1: *Ein Lauf ohne Sprachmodell darf
nicht wie ein vollwertiger aussehen.* Und es ist derselbe Mechanismus, gegen den
P0.7 und P1.9-W5.1 angetreten sind — ein Default, der eine Auslassung in eine
Aussage verwandelt.

**Dieser Test prüft keine Liste, sondern die Kopplung.** Er liest aus
`metadata.py` und `provenance.py` heraus, welche `args`-Felder die Herkunft
bestimmen, und hält jeden Startpfad dagegen. Ein neues Herkunftsfeld ist damit
sofort abgedeckt, auch wenn niemand diese Datei anfasst.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
METADATA = REPO_ROOT / "src" / "reporting" / "output_writer" / "metadata.py"
PROVENANCE = REPO_ROOT / "src" / "reporting" / "output_writer" / "provenance.py"

#: Felder, die `args` **nicht** tragen muss, weil sie nachweislich anderswoher
#: kommen. Jede Ausnahme mit Grund — eine wachsende Liste hier wäre der Anfang
#: derselben Umgehung, die dieser Test verhindern soll.
AUSNAHMEN = {
    # Der Seed kommt aus dem Zustand: Dort steht der tatsächlich benutzte,
    # während `args.seed` bei einem Multi-Run nur der Ausgangswert der Folge ist.
    "seed",
    # Beide sind rein beschreibend und dürfen fehlen — dann steht in der
    # Oberfläche der Vorgabename bzw. nichts.
    "simulation_name",
    "simulation_description",
}


def _herkunftsfelder() -> set[str]:
    """Welche `args`-Felder die Herkunft eines Laufs bestimmen.

    Gelesen statt aufgezählt: Jeder `getattr(args, "x", …)` in den beiden
    Modulen, die `run_metadata.json` füllen.
    """

    gefunden: set[str] = set()
    for pfad in (METADATA, PROVENANCE):
        baum = ast.parse(pfad.read_text(encoding="utf-8"))
        for knoten in ast.walk(baum):
            if not isinstance(knoten, ast.Call):
                continue
            if not (isinstance(knoten.func, ast.Name) and knoten.func.id == "getattr"):
                continue
            if len(knoten.args) < 2:
                continue
            ziel, name = knoten.args[0], knoten.args[1]
            if not (isinstance(ziel, ast.Name) and ziel.id == "args"):
                continue
            if isinstance(name, ast.Constant) and isinstance(name.value, str):
                gefunden.add(name.value)
    return gefunden - AUSNAHMEN


def _felder_des_namespace(quelle: str, anker: str) -> set[str]:
    """Die Schlüsselwörter eines `SimpleNamespace(...)`-Aufrufs im Quelltext."""

    baum = ast.parse(quelle)
    treffer: set[str] = set()
    for knoten in ast.walk(baum):
        if not isinstance(knoten, ast.Call):
            continue
        func = knoten.func
        name = getattr(func, "id", None) or getattr(func, "attr", None)
        if name != "SimpleNamespace":
            continue
        felder = {kw.arg for kw in knoten.keywords if kw.arg}
        if anker in felder:
            treffer |= felder
    return treffer


def test_die_herkunftsfelder_werden_gelesen_nicht_geraten():
    """Der Detektor selbst — sonst prüfte der Test unten gegen eine leere Menge."""

    felder = _herkunftsfelder()

    assert "mock_llm" in felder, (
        "Der Durchlauf findet `mock_llm` nicht mehr in den Herkunftsmodulen. "
        "Entweder ist es weg, oder es wird jetzt anders gelesen als über "
        "`getattr(args, …)` — dann greift dieser Test ins Leere."
    )
    assert len(felder) >= 3, f"Verdächtig wenige Herkunftsfelder gefunden: {felder}"


def test_der_dashboard_startpfad_traegt_alle_herkunftsfelder():
    """`launch_from_draft` baut zwei Namespaces — Einzellauf und Wiederholungen."""

    from dashboard import run_launcher

    quelle = inspect.getsource(run_launcher)
    noetig = _herkunftsfelder()

    fehlend = {}
    for anker in ("run_id",):
        felder = _felder_des_namespace(quelle, anker)
        assert felder, "Kein `SimpleNamespace` mit `run_id` gefunden"
        luecke = sorted(noetig - felder)
        if luecke:
            fehlend[anker] = luecke

    assert not fehlend, (
        f"Der Dashboard-Startpfad lässt Herkunftsfelder weg: {fehlend}.\n"
        "`save_run_metadata` fällt bei einem fehlenden Feld auf einen Default "
        "zurück — eine Auslassung wird damit zu einer Aussage. Genau so wurde "
        "jeder Mock-Lauf als vollwertiger LLM-Lauf protokolliert."
    )


def test_der_waechter_wuerde_eine_auslassung_bemerken():
    """Ein Namespace ohne `mock_llm` muss auffallen."""

    quelle = "from types import SimpleNamespace\nx = SimpleNamespace(run_id='r', model='m')\n"
    felder = _felder_des_namespace(quelle, "run_id")

    assert felder == {"run_id", "model"}
    assert "mock_llm" not in felder, "Die Auslassung bliebe unbemerkt"


def test_ein_mock_lauf_heisst_im_artefakt_auch_so(tmp_path):
    """Die Wirkung, nicht nur die Form: `compute_mode` sagt `mock_llm`."""

    from types import SimpleNamespace

    from dashboard.config_catalog import default_config_draft, prepare_simulation_state
    from src.reporting.output_writer.metadata import save_run_metadata

    state = prepare_simulation_state(default_config_draft())
    args = SimpleNamespace(
        model="llama3.2",
        base_url="http://localhost:11434",
        temperature=0.7,
        max_tokens=2048,
        no_market=False,
        deterministic_only=False,
        mock_llm=True,
    )

    import json

    daten = json.loads(Path(save_run_metadata(state, args, run_dir=tmp_path)).read_text("utf-8"))

    assert daten["mock_llm"] is True
    assert daten["compute_mode"] == "mock_llm", (
        f"Ein Mock-Lauf trägt `compute_mode: {daten['compute_mode']}` — "
        "dann sieht er im Dashboard aus wie ein vollwertiger."
    )
