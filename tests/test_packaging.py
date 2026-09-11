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

import importlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import textwrap
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"
REQUIREMENTS = ROOT / "requirements.txt"
WORKFLOW = ROOT / ".github" / "workflows" / "tests.yml"
DOCKERFILE = ROOT / "Dockerfile"
COMPOSE = ROOT / "docker-compose.yml"


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
    """Die Ausnahmeliste in der CI ist **leer**, und sie bleibt es.

    Jeder Eintrag wäre ein bekannter Fehlschlag aus `CLAUDE.md`. Kommt einer
    dazu, ohne dass er dort steht, verschwindet ein echter Fehler unbemerkt.

    **Die Liste schrumpft auch nicht heimlich** — genau das ist am 2026-09-03
    passiert: P2.11 hat den dritten Deselect entfernt, und dieser Wächter hat es
    gemeldet, bevor jemand die Liste vergessen konnte.

    **Seit P4.2 (2026-09-08) ist sie leer.** Die beiden letzten waren die
    Sweep-Tests, und sie sind nicht weggeskippt worden, sondern haben aufgehört,
    ein Sprachmodell anzufassen: `run_single_sweep(..., llm_narrative=False)`.
    Ein leerer Erwartungswert ist hier kein zahnloser Wächter, sondern die
    schärfste Fassung — jeder neue Deselect wird gemeldet.
    """

    workflow = WORKFLOW.read_text(encoding="utf-8")
    deselected = set(re.findall(r"--deselect (\S+)", workflow))

    erwartet: set[str] = set()

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


# --- Installation (P4.6) ----------------------------------------------------


def _installiert() -> bool:
    from importlib.metadata import PackageNotFoundError, distribution

    try:
        distribution("aeroforesight")
    except PackageNotFoundError:
        return False
    return True


def _namen_aus_src() -> list[str]:
    """Jeder Name, den `src/` als Modul oder Paket trägt — aus dem Verzeichnis gelesen.

    **Nur, was Python überhaupt importieren könnte:** ein gültiger Bezeichner.
    Die erste Fassung nahm jeden Verzeichnisnamen und stolperte über ein
    `aeroforesight.egg-info` aus einer früheren Installation — `find_spec` sucht
    dafür das Elternpaket `aeroforesight` und bricht ab, statt «nicht da» zu sagen.
    """

    namen = []
    for pfad in sorted((ROOT / "src").iterdir()):
        if pfad.name.startswith(("_", ".")):
            continue
        if pfad.is_dir() and pfad.name.isidentifier():
            namen.append(pfad.name)
        elif pfad.suffix == ".py" and pfad.stem.isidentifier():
            namen.append(pfad.stem)
    return namen


def _in_fremdem_verzeichnis(tmp_path: Path, code: str) -> subprocess.CompletedProcess:
    """Python in *tmp_path* starten — ohne das Repo im Suchpfad.

    `-c` legt nur das Arbeitsverzeichnis in den Suchpfad, und `PYTHONPATH` wird
    entfernt. Was dort importierbar ist, kommt also aus der Installation und
    nirgends sonst her.
    """

    umgebung = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    umgebung["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, "-c", textwrap.dedent(code)],
        cwd=tmp_path,
        env=umgebung,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
    )


class TestDieInstallationLiefertDasPaketSrc:
    """**P4.6: `pip install -e .` macht `src` importierbar — und nur `src`.**

    Bis zum 2026-09-11 nannte `pyproject.toml` keine Pakete. setuptools hielt das
    Verzeichnis `src` für das übliche src-Layout und legte es **selbst** in den
    Suchpfad. Gemessen aus `/tmp`: `import src` scheiterte, **16** Namen wie
    `models`, `llm` und `agents` lösten als lose Top-Level-Module nach `src/`
    auf, und aus dem Repo importiert gab es **zwei** verschiedene
    `SimulationState`-Klassen, je nach Importweg.

    Mit `[tool.setuptools.packages.find]` installiert setuptools einen Finder,
    der genau `src` abbildet. Nachgemessen: `import src` gelingt, kein Name aus
    `src/` löst mehr auf, und `dashboard`, `tests`, `scripts` und
    `langgraph_studio` sind dadurch nicht ungewollt sichtbar geworden.

    **Die Messung ist dieselbe wie beim Befund**, nur in einem Test: vorher lieferte
    sie 16 Namen, nachher keinen. Die CI installiert das Projekt dafür seit P4.6
    selbst — vorher tat sie es gar nicht, und dieser Wächter hätte dort nichts
    gemessen.
    """

    def test_das_projekt_ist_installiert(self):
        assert _installiert(), (
            "Die Distribution `aeroforesight` ist nicht installiert — dann misst diese "
            'Klasse nichts. Im venv: `pip install -e ".[dev]"`.'
        )

    def test_import_src_gelingt_aus_einem_fremden_verzeichnis(self, tmp_path):
        ergebnis = _in_fremdem_verzeichnis(
            tmp_path,
            """
            import src
            print(src.__file__)
            """,
        )

        assert ergebnis.returncode == 0, ergebnis.stderr
        assert Path(ergebnis.stdout.strip()).resolve().parent == (ROOT / "src").resolve()

    def test_kein_name_aus_src_loest_als_top_level_modul_nach_src_auf(self, tmp_path):
        """Gemeldet wird nur, was **in `src/` hineinzeigt** — ein fremdes Paket
        gleichen Namens wäre ein anderer Fall und kein Befund dieser Klasse."""

        namen = _namen_aus_src()
        assert len(namen) > 5, f"Verdächtig wenige Namen in src/: {namen}"

        ergebnis = _in_fremdem_verzeichnis(
            tmp_path,
            f"""
            import importlib.util
            from pathlib import Path

            src = Path({str((ROOT / "src").resolve())!r})
            treffer = []
            for name in {namen!r}:
                spec = importlib.util.find_spec(name)
                if spec is None:
                    continue
                orte = [spec.origin] if spec.origin else list(spec.submodule_search_locations or [])
                if any(o and Path(o).resolve().is_relative_to(src) for o in orte):
                    treffer.append(name)
            print(",".join(treffer))
            """,
        )

        assert ergebnis.returncode == 0, ergebnis.stderr
        aufloesend = [n for n in ergebnis.stdout.strip().split(",") if n]
        assert not aufloesend, (
            f"Diese Namen aus src/ lösen als Top-Level-Module nach src/ auf: {aufloesend}. "
            "Dann gibt es zwei Wege zu demselben Modul — und zwei Klassen gleichen Namens."
        )


# --- Typprüfer (P4.4) -------------------------------------------------------


class TestDerTypprueferLaeuftUeberEineListeDieWaechst:
    """**P4.4: mypy prüft die Grenzen — und der Umfang steht im Werkzeug.**

    Bis zum 2026-09-11 hatte das Projekt keinen Typprüfer. `sweep_metadata_args`
    war mit `-> SimpleNamespace` annotiert und lieferte `RunArgs` — zwölf Tage lang
    bei grünem `ruff` (P3.15). Invariante 4 hängt daran, dass eine Typangabe
    stimmt, und ohne Prüfer stimmte sie nur zufällig.

    **Nicht das ganze Repo:** Die Liste in `[tool.mypy] files` fängt bei den
    Grenzen an und wächst. Diese Klasse hält fest, dass sie das tut, was sie
    verspricht — keine tote Zeile darin (die den Umfang still verkleinerte), und
    ein Befehl in der CI, der sie ausführt.
    """

    def _konfig(self) -> dict:
        return _pyproject()["tool"]["mypy"]

    def test_die_liste_ist_nicht_leer_und_jede_zeile_gibt_es(self):
        dateien = self._konfig().get("files", [])

        assert dateien, "Die mypy-Liste ist leer — dann prüft der Typprüfer nichts."
        fehlend = [d for d in dateien if not (ROOT / d).exists()]
        assert not fehlend, (
            f"Diese Einträge der mypy-Liste gibt es nicht: {fehlend}. Eine tote Zeile "
            "verkleinert den Umfang still."
        )

    def test_die_ci_fuehrt_mypy_aus(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")

        assert re.search(r"^\s+run:\s+mypy\s*$", workflow, re.M), (
            "tests.yml führt `mypy` nicht aus — dann gilt die Liste nur lokal, und eine "
            "Annotation, die ihrem return widerspricht, bleibt in der CI grün."
        )

    def test_mypy_steht_im_extra_dev(self):
        dev = {_name(item) for item in _pyproject()["project"]["optional-dependencies"]["dev"]}

        assert (
            "mypy" in dev
        ), "mypy fehlt im Extra `dev` — `pip install -e .[dev]` brächte ihn nicht."


# --- Container --------------------------------------------------------------


def _dockerfile_zeile(anweisung: str) -> str:
    zeilen = [
        z
        for z in DOCKERFILE.read_text(encoding="utf-8").splitlines()
        if z.startswith(anweisung + " ")
    ]
    assert len(zeilen) == 1, f"Das Dockerfile hat {len(zeilen)} {anweisung}-Zeilen"
    return zeilen[0].removeprefix(anweisung + " ")


class TestDerContainerStartetDieAktiveOberflaeche:
    """**Der Container startet, was heute die Oberfläche ist — und ist von außen erreichbar.**

    Bis zum 2026-09-11 lautete der Startbefehl `python -m streamlit run
    dashboard/app.py`: eine Datei, die es seit der Dash-Migration nicht mehr gab,
    auf der abgelösten Oberfläche. Gemessen wird an der **echten CLI** der App,
    nicht am Text des Dockerfiles: Der naheliegende Fix — nur den Modulpfad
    tauschen — hätte eine App gestartet, die auf 127.0.0.1 lauscht und aus dem
    Container heraus niemand erreicht.
    """

    def test_das_modul_im_startbefehl_liegt_in_diesem_repo(self):
        befehl = json.loads(_dockerfile_zeile("CMD"))
        assert befehl[:2] == ["python", "-m"], f"Kein `python -m`-Start: {befehl}"

        spec = importlib.util.find_spec(befehl[2])
        assert spec is not None and spec.origin, f"Das Modul `{befehl[2]}` gibt es nicht."
        ort = Path(spec.origin).resolve()
        assert ort.is_relative_to(ROOT) and not ort.relative_to(ROOT).parts[0].startswith("."), (
            f"`{befehl[2]}` kommt nicht aus diesem Repo, sondern aus {ort} — "
            "der Container startete dann fremden Code statt der Oberfläche."
        )

    def test_die_app_lauscht_nach_aussen_auf_dem_freigegebenen_port(self, monkeypatch):
        befehl = json.loads(_dockerfile_zeile("CMD"))
        modul = importlib.import_module(befehl[2])
        aufrufe: list[dict] = []
        monkeypatch.setattr(modul.app, "run", lambda **kw: aufrufe.append(kw))
        monkeypatch.setattr(sys, "argv", [befehl[2], *befehl[3:]])

        modul.main()

        assert len(aufrufe) == 1, "`main()` hat die App nicht gestartet."
        assert aufrufe[0]["host"] == "0.0.0.0", (
            f"Die App lauscht auf {aufrufe[0]['host']!r} — aus dem Container heraus "
            "erreicht sie dann niemand."
        )
        assert aufrufe[0]["port"] == int(_dockerfile_zeile("EXPOSE"))

    def test_compose_gibt_denselben_port_frei(self):
        port = int(_dockerfile_zeile("EXPOSE"))

        assert f'"{port}:{port}"' in COMPOSE.read_text(
            encoding="utf-8"
        ), f"docker-compose.yml gibt Port {port} nicht frei."
