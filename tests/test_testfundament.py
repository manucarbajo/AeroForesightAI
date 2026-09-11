"""P4.1/P4.2: Was für **jede** Datei in `tests/` gilt — gesucht, nicht aufgezählt (2026-09-11).

Die beiden Pakete nannten ihre Befunde als Liste: 32 `mkdtemp` in fünf Dateien,
`MockLLM` in vier, `sys.path.append` in drei, ein Debug-Skript. Beim Anfassen
stimmte **keine** dieser Listen mehr vollständig — es waren 36 `mkdtemp`, dazu
zwei `TemporaryDirectory` und ein `gettempdir`, die niemand mitgezählt hatte,
und neben den drei `append` stand ein `insert`, den der Befund nicht nannte.

**Dieselbe Klasse wie P3.8, die Kontextparameter aus Invariante 1 und die
Farbklassen aus Regel 4:** Eine Liste fängt die Fälle, die jemand gesehen hat.
Ein Wächter, der über das **Merkmal** sucht, fängt auch den nächsten. Jede Klasse
unten hält deshalb eine Eigenschaft der ganzen Suite fest, keinen Dateinamen.
"""

from __future__ import annotations

import fnmatch
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TESTS = ROOT / "tests"

#: Die beiden Dateinamen, die pytest selbst vergibt und nicht als Test einsammelt.
#: Keine Ausnahmeliste für Einzelfälle — wer einen Helfer braucht, legt ihn als
#: Fixture in `conftest.py` ab, wo pytest ihn findet.
VON_PYTEST_VERGEBEN = {"__init__.py", "conftest.py"}


def _einsammelmuster() -> list[str]:
    """Wonach pytest Testdateien sucht — **aus der Konfiguration, nicht angenommen**.

    Ohne Eintrag gilt der pytest-Standard. Wer `python_files` in `pyproject.toml`
    setzt, verschiebt damit auch diesen Wächter, statt ihn still falsch zu machen.
    """

    konfig = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    optionen = konfig.get("tool", {}).get("pytest", {}).get("ini_options", {})
    muster = optionen.get("python_files", ["test_*.py", "*_test.py"])
    return muster.split() if isinstance(muster, str) else list(muster)


def nicht_eingesammelt(verzeichnis: Path, muster: list[str]) -> list[str]:
    """Jede `.py`-Datei unter `verzeichnis`, die pytest **nicht** als Test ausführt."""

    return sorted(
        str(pfad.relative_to(verzeichnis))
        for pfad in verzeichnis.rglob("*.py")
        if "__pycache__" not in pfad.parts
        and pfad.name not in VON_PYTEST_VERGEBEN
        and not any(fnmatch.fnmatch(pfad.name, m) for m in muster)
    )


class TestJedeDateiInTestsWirdAuchAusgefuehrt:
    """**Eine Datei in `tests/`, die pytest nicht einsammelt, täuscht Abdeckung vor.**

    Der Anlass war `debug_run_sequential.py` (gelöscht mit P4.2, 2026-09-11): ein
    Skript mit `main()`, einer zeichengleichen Kopie von Aufbau und Mock aus
    `test_simulation_runner_e2e.py` und einem Aufruf der privaten Methode
    `_build_sequential_runner`. Es lief noch — aber nie in einem Testlauf, und
    wer den Ordner überflog, zählte es mit.
    """

    def test_kein_skript_das_pytest_nicht_einsammelt(self):
        befunde = nicht_eingesammelt(TESTS, _einsammelmuster())

        assert not befunde, (
            "Diese Dateien in tests/ führt pytest nie aus:\n  "
            + "\n  ".join(befunde)
            + "\n\nEin Test gehört in eine Datei, die pytest findet; ein Helfer als "
            "Fixture in conftest.py; ein Werkzeug nach scripts/."
        )

    def test_der_waechter_saehe_ein_solches_skript(self, tmp_path):
        """Ohne diese Zusage wäre grün nur die Abwesenheit einer Messung."""

        (tmp_path / "__init__.py").write_text("", encoding="utf-8")
        (tmp_path / "conftest.py").write_text("", encoding="utf-8")
        (tmp_path / "test_echt.py").write_text("", encoding="utf-8")
        (tmp_path / "debug_lauf.py").write_text("", encoding="utf-8")

        assert nicht_eingesammelt(tmp_path, ["test_*.py", "*_test.py"]) == ["debug_lauf.py"]
