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


def eingriffe_in_sys_path(quelltext: str) -> list[int]:
    """Jede Zeile, in der `sys.path` **dauerhaft** verändert wird — über den Syntaxbaum.

    **Eine Textsuche wäre hier falsch**, und das ist gemessen: Beim Anlegen
    dieses Wächters standen drei der sieben Treffer für `sys.path` in `tests/`
    in Docstrings und Kommentaren — einer davon in dieser Datei.

    **`monkeypatch.syspath_prepend` zählt nicht**: pytest nimmt es nach dem Test
    zurück. Gemeldet wird, was den Prozess für alle folgenden Tests verändert.
    """

    import ast

    def ist_sys_path(knoten: ast.AST) -> bool:
        return (
            isinstance(knoten, ast.Attribute)
            and knoten.attr == "path"
            and isinstance(knoten.value, ast.Name)
            and knoten.value.id == "sys"
        )

    veraendernd = {"append", "insert", "extend", "remove", "pop", "clear"}
    zeilen: list[int] = []
    for knoten in ast.walk(ast.parse(quelltext)):
        if isinstance(knoten, ast.Call) and isinstance(knoten.func, ast.Attribute):
            if ist_sys_path(knoten.func.value) and knoten.func.attr in veraendernd:
                zeilen.append(knoten.lineno)
        elif isinstance(knoten, (ast.Assign, ast.AugAssign)):
            ziele = knoten.targets if isinstance(knoten, ast.Assign) else [knoten.target]
            for ziel in ziele:
                if ist_sys_path(ziel) or (
                    isinstance(ziel, ast.Subscript) and ist_sys_path(ziel.value)
                ):
                    zeilen.append(knoten.lineno)
    return sorted(zeilen)


class TestKeinTestVerbiegtDenSuchpfad:
    """**Kein Test verbiegt den Suchpfad — `src` macht pytest selbst importierbar.**

    `tests/` ist ein Paket (`tests/__init__.py`), und im Standard-Importmodus
    `prepend` legt pytest das erste Verzeichnis darüber ohne `__init__.py` vor
    den Suchpfad: das Wurzelverzeichnis des Repos. **Gemessen am 2026-09-11:**
    Aus `/tmp` gestartet laufen die Tests grün, und die CI installiert das
    Projekt gar nicht (`pip install -r requirements.txt`).

    **`pip install -e .` trägt dazu nichts bei — und das war die erste, falsche
    Begründung dieses Wächters.** Die Editable-Installation legt `src/` *selbst*
    in den Suchpfad, nicht sein Elternverzeichnis; `import src` scheitert damit
    außerhalb von pytest und außerhalb des Repo-Wurzelverzeichnisses. Wer eine
    Testdatei direkt als Skript startet, bekommt deshalb seit dem Wegfall der
    Eingriffe einen `ModuleNotFoundError` — der Weg ist `pytest <datei>`.

    **Die drei Eingriffe bis zum 2026-09-11 waren funktional wirkungslos**, weil
    pytest den Pfad ohnehin anlegt — und genau deshalb irreführend: Sie
    behaupteten eine Abhängigkeit, die es nicht gab, und verdeckten, woher `src`
    wirklich kommt. Der Befund nannte drei Stellen mit `append`; es waren zwei
    `append` und ein `insert` in `test_scenario_sweeps.py`, der in keiner Liste
    stand.
    """

    def test_kein_dauerhafter_eingriff_in_sys_path(self):
        befunde = [
            f"{pfad.relative_to(ROOT)}:{zeile}"
            for pfad in sorted(TESTS.rglob("*.py"))
            if "__pycache__" not in pfad.parts
            for zeile in eingriffe_in_sys_path(pfad.read_text(encoding="utf-8"))
        ]

        assert not befunde, (
            "Diese Stellen verändern sys.path für den ganzen Testprozess:\n  "
            + "\n  ".join(befunde)
            + "\n\nFür die Tests macht pytest `src` selbst importierbar (tests/ ist "
            "ein Paket, Importmodus prepend). Wer für einen einzelnen Test einen Pfad "
            "braucht, nimmt `monkeypatch.syspath_prepend` — das nimmt pytest danach "
            "zurück."
        )

    def test_der_waechter_sieht_jede_form_und_keine_prosa(self):
        """Ohne diese Zusage wäre grün nur die Abwesenheit einer Messung.

        Die ersten drei Zeilen des Beispiels **erwähnen** `sys.path` nur — die
        Falle, in die eine Textsuche liefe. Die vier danach verändern ihn.
        """

        quelltext = '''"""Ein Docstring, der sys.path.append(...) nur erwähnt."""
import sys
# sys.path.insert(0, "nur ein Kommentar")
sys.path.append("a")
sys.path.insert(0, "b")
sys.path += ["c"]
sys.path[:0] = ["d"]
'''

        assert eingriffe_in_sys_path(quelltext) == [4, 5, 6, 7]


def erbende_testcases(quelltext: str) -> list[str]:
    """Jede Klasse, die von einem `TestCase` aus `unittest` erbt — über den Syntaxbaum.

    **Gesucht wird das Erben, nicht der Import.** `from unittest.mock import patch`
    ist ein gewöhnliches Werkzeug und darf nicht anschlagen; `mock.Mock` als
    Basisklasse ebenso wenig. Gemeldet wird eine Basis, die ein `…TestCase` aus
    dem Modul `unittest` ist — gleich, unter welchem Namen es importiert wurde.
    """

    import ast

    baum = ast.parse(quelltext)
    modul_aliase: set[str] = set()
    klassen_aliase: set[str] = set()
    for knoten in ast.walk(baum):
        if isinstance(knoten, ast.Import):
            for alias in knoten.names:
                if alias.name == "unittest":
                    modul_aliase.add(alias.asname or alias.name)
        elif isinstance(knoten, ast.ImportFrom) and knoten.module == "unittest":
            for alias in knoten.names:
                if alias.name.endswith("TestCase"):
                    klassen_aliase.add(alias.asname or alias.name)

    def ist_testcase(basis: ast.expr) -> bool:
        if isinstance(basis, ast.Attribute) and isinstance(basis.value, ast.Name):
            return basis.value.id in modul_aliase and basis.attr.endswith("TestCase")
        return isinstance(basis, ast.Name) and basis.id in klassen_aliase

    return [
        f"{knoten.lineno}: {knoten.name}"
        for knoten in ast.walk(baum)
        if isinstance(knoten, ast.ClassDef) and any(ist_testcase(b) for b in knoten.bases)
    ]


class TestEinTestIstEineFunktionOderEineKlasseOhneUnittest:
    """**Die Suite spricht einen Stil: pytest.**

    Bis zum 2026-09-11 erbten drei Dateien von `unittest.TestCase` —
    `test_agent_node.py`, `test_save_final_narrative.py` und
    `test_simulation_runner_e2e.py` —, ohne technischen Grund. Das war nicht nur
    uneinheitlich: Einer `TestCase`-Methode reicht pytest **keine Fixtures**
    herein. Wer dort `tmp_path` oder `monkeypatch` brauchte, griff zu
    `tempfile` und Handarbeit — genau die Muster, gegen die P4.1 antritt.

    **Umgestellt mit einer Prüfung, nicht per Augenmaß:** Vor und nach jeder
    Datei wurden die Menge der Testnamen, die Zahl der Zusicherungen und die
    Multimenge **aller** String-Konstanten verglichen. Einziger Unterschied
    war `'__main__'` aus der entfernten `unittest.main()`-Zeile; jede
    JSON-Antwort der Mocks und jede Prompt-Erwartung ist byte-gleich
    geblieben. Zeilen im Inneren mehrzeiliger Strings wurden dafür bewusst
    nicht umgerückt — sonst hätte sich der Wortlaut der Mock-Antworten
    geändert.
    """

    def test_keine_klasse_erbt_von_unittest_testcase(self):
        befunde = [
            f"{pfad.relative_to(ROOT)}:{fund}"
            for pfad in sorted(TESTS.rglob("*.py"))
            if "__pycache__" not in pfad.parts
            for fund in erbende_testcases(pfad.read_text(encoding="utf-8"))
        ]

        assert not befunde, (
            "Diese Klassen erben von unittest.TestCase:\n  "
            + "\n  ".join(befunde)
            + "\n\nIn einer TestCase-Methode gibt es keine pytest-Fixtures. Ein Test "
            "ist eine Funktion `def test_…()` oder eine Klasse `class Test…:` ohne "
            "Basisklasse; Zusicherungen sind `assert`."
        )

    def test_der_waechter_sieht_jede_form_und_nicht_mock(self):
        """Ohne diese Zusage wäre grün nur die Abwesenheit einer Messung."""

        quelltext = """import unittest
import unittest as ut
from unittest import TestCase
from unittest import IsolatedAsyncioTestCase as Asynchron
from unittest import mock
from unittest.mock import patch


class A(unittest.TestCase):
    pass


class B(ut.TestCase):
    pass


class C(TestCase):
    pass


class D(Asynchron):
    pass


class E(mock.Mock):
    pass


class TestF:
    pass
"""

        assert [fund.split(": ")[1] for fund in erbende_testcases(quelltext)] == [
            "A",
            "B",
            "C",
            "D",
        ]
