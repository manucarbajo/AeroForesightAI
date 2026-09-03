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

    **Und die Liste schrumpft auch nicht heimlich** — genau das ist am
    2026-09-03 passiert: P2.11 hat den dritten Deselect entfernt, und dieser
    Wächter hat es gemeldet, bevor jemand die Liste vergessen konnte. Zwei sind
    übrig, beide Ollama-Hänger, beide fallen mit P4.2.
    """

    workflow = WORKFLOW.read_text(encoding="utf-8")
    deselected = set(re.findall(r"--deselect (\S+)", workflow))

    erwartet = {
        "tests/test_scenario_sweeps.py::test_run_single_sweep_short",
        "tests/test_scenario_sweeps.py::test_sweep_base_price_override_raises_ticket_price",
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


def test_documented_module_paths_exist():
    """Kein Doku-Kapitel darf auf ein Modul zeigen, das es nicht gibt.

    Gefunden bei der Gegenprobe zu P0.4–P0.6 (2026-08-27): fünf tote Pfade,
    zwei davon in **offenen** Findings — `market_rules.py` war umbenannt,
    `src/event_deltas.py`, `src/scenario_consistency.py` und
    `src/population_sampler.py` lagen längst in ihren Paketen. Ein Pfad, den es
    nicht gibt, ist die einfachste Form von "die Doku behauptet, was der Code
    nicht tut" — und die einzige, die sich mechanisch ausschließen lässt.

    Geprüft wird jeder Pfad in Backticks, der auf `.py` endet — ohne Ausnahmen.
    Ein früherer Modulname gehört in den Fließtext ("hieß bis P0.4
    market_rules.py"), nicht in eine Pfadangabe. Eine Ausnahmeliste wäre wieder
    die Sorte Aufzählung, die dem Code davonläuft.
    """

    repo = Path(__file__).resolve().parents[1]
    docs = list((repo / "docs").rglob("*.md")) + [repo / "CLAUDE.md", repo / "README.md"]

    stale: list[str] = []
    for doc in docs:
        for number, line in enumerate(doc.read_text(encoding="utf-8").splitlines(), start=1):
            for match in re.findall(r"`(src/[A-Za-z0-9_/]+\.py)`", line):
                if not (repo / match).exists():
                    stale.append(f"{doc.relative_to(repo)}:{number}: {match}")

    assert not stale, "Doku zeigt auf Module, die es nicht gibt:\n  " + "\n  ".join(stale)


def test_internal_doc_anchors_point_somewhere():
    """Ein Verweis auf eine Überschrift, die es nicht mehr gibt, führt ins Leere.

    Gefunden bei der zweiten Gegenprobe (2026-08-27): Zwei Links im Projektplan
    zeigten auf `#p05--…` und `#p06--…`, aber die Überschriften hatten
    inzwischen ein "✅ erledigt 2026-08-27" bekommen — und damit einen anderen
    Anker. Dieselbe Sorte stiller Doku-Drift wie die toten Modulpfade darüber,
    nur eine Ebene höher: Der Text stimmt, das Ziel ist weg.

    **Dateiübergreifende Anker werden seit dem 2026-08-31 mitgeprüft**, und die
    frühere Begründung dafür, es zu lassen, war falsch: «Links auf andere
    Dokumente hängen an deren Überschriften und gehören dorthin» — sie hängen
    dort, aber *niemand* sah nach. Beim Durchgang durch Phase 2 fanden sich
    **19 tote** solche Verweise (14 verschiedene), fast alle entstanden dadurch,
    dass eine Paketüberschrift eine Statusmarke bekam und der Anker damit ein
    anderer wurde.
    """

    def slug(heading: str) -> str:
        heading = re.sub(r"[^\w\s-]", "", heading.strip().lower(), flags=re.UNICODE)
        return heading.strip().replace(" ", "-")

    docs = list((ROOT / "docs").rglob("*.md")) + [ROOT / "CLAUDE.md", ROOT / "README.md"]

    ueberschriften = {
        doc.resolve(): {
            slug(m) for m in re.findall(r"^#{1,6}\s+(.*)$", doc.read_text("utf-8"), re.M)
        }
        for doc in docs
    }

    tot: list[str] = []
    for doc in docs:
        text = doc.read_text(encoding="utf-8")

        # In derselben Datei.
        for anker in sorted(set(re.findall(r"\]\(#([^)]+)\)", text))):
            if anker not in ueberschriften[doc.resolve()]:
                tot.append(f"{doc.relative_to(ROOT)}: #{anker}")

        # In einer anderen — der blinde Fleck bis 2026-08-31.
        for ziel, anker in sorted(set(re.findall(r"\]\(([^)#]+\.md)#([^)]+)\)", text))):
            pfad = (doc.parent / ziel).resolve()
            if pfad not in ueberschriften:
                tot.append(f"{doc.relative_to(ROOT)}: {ziel} gibt es nicht")
            elif anker not in ueberschriften[pfad]:
                tot.append(f"{doc.relative_to(ROOT)}: {ziel}#{anker}")

    assert not tot, "Verweise auf Überschriften, die es nicht gibt:\n  " + "\n  ".join(tot)
