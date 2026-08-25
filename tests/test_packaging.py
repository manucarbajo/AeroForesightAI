"""Die Abhängigkeitslisten dürfen nicht auseinanderlaufen.

Das Projekt führt sie doppelt: `pyproject.toml` ist die Wahrheit,
`requirements.txt` existiert, weil CI und Dockerfile sie lesen. Genau diese
Doppelung hat schon einmal zugeschlagen — `dash` und `pandas` standen nur in
der einen Datei, wodurch der CI-Lauf beim Import scheiterte, während lokal
alles lief.

Diese Prüfung ist der Ersatz für die Aufmerksamkeit, die man dabei nicht
haben kann.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"
REQUIREMENTS = ROOT / "requirements.txt"
WORKFLOW = ROOT / ".github" / "workflows" / "tests.yml"


def _pyproject() -> dict:
    return tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))


def _requirements() -> list[str]:
    lines = REQUIREMENTS.read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]


def _name(spec: str) -> str:
    """`langgraph-cli[inmem]>=0.2` → `langgraph-cli`."""

    return re.split(r"[\[<>=!~;]", spec, maxsplit=1)[0].strip().lower()


def test_both_lists_name_the_same_packages():
    declared = {_name(item) for item in _pyproject()["project"]["dependencies"]}
    pinned = {_name(item) for item in _requirements()}

    assert declared == pinned, (
        f"nur in pyproject.toml: {sorted(declared - pinned)}; "
        f"nur in requirements.txt: {sorted(pinned - declared)}"
    )


def test_both_lists_use_the_same_versions():
    declared = {_name(item): item for item in _pyproject()["project"]["dependencies"]}
    pinned = {_name(item): item for item in _requirements()}

    abweichend = {
        name: (declared[name], pinned[name])
        for name in declared.keys() & pinned.keys()
        if declared[name] != pinned[name]
    }

    assert not abweichend, f"unterschiedliche Angaben: {abweichend}"


def test_development_tools_stay_out_of_the_runtime_list():
    """pytest, ruff und black gehören zu `dev`, nicht in requirements.txt."""

    pinned = {_name(item) for item in _requirements()}

    assert not ({"pytest", "ruff", "black"} & pinned)


@pytest.mark.parametrize("package", ["dash", "pandas", "plotly"])
def test_the_dashboard_can_actually_be_installed_from_the_lists(package):
    """Was die Oberfläche importiert, muss in beiden Listen stehen."""

    declared = {_name(item) for item in _pyproject()["project"]["dependencies"]}
    pinned = {_name(item) for item in _requirements()}

    assert package in declared
    assert package in pinned


# --- CI --------------------------------------------------------------------


def test_ci_skips_exactly_the_documented_failures():
    """Die Ausnahmeliste in der CI darf nicht heimlich wachsen.

    Jeder Eintrag ist ein bekannter Fehlschlag aus `CLAUDE.md`. Kommt einer
    dazu, ohne dass er dort steht, verschwindet ein echter Fehler unbemerkt.
    """

    workflow = WORKFLOW.read_text(encoding="utf-8")
    deselected = set(re.findall(r"--deselect (\S+)", workflow))

    erwartet = {
        "tests/test_scenario_sweeps.py::test_run_single_sweep_short",
        "tests/test_scenario_sweeps.py::test_sweep_base_price_override_raises_ticket_price",
        "tests/test_market_feedback.py::TestM413ConfigurablePrice::"
        "test_market_rules_resolve_marginal_cost_fraction",
    }

    assert deselected == erwartet, (
        f"zusätzlich übersprungen: {sorted(deselected - erwartet)}; "
        f"nicht mehr übersprungen: {sorted(erwartet - deselected)}"
    )


def test_the_deselected_tests_exist():
    """Ein Deselect auf einen Test, den es nicht mehr gibt, schützt nichts."""

    workflow = WORKFLOW.read_text(encoding="utf-8")
    for eintrag in re.findall(r"--deselect (\S+)", workflow):
        datei = eintrag.split("::")[0]
        assert (ROOT / datei).is_file(), f"{datei} gibt es nicht mehr"
