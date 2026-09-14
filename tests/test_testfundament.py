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

import ast
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


def ohne_test(verzeichnis: Path, muster: list[str]) -> list[str]:
    """Jede eingesammelte Datei, in der pytest **keinen einzigen Test** findet.

    Gesucht wird über den Syntaxbaum: eine Funktion `test…` oder eine Klasse
    `Test…` auf Modulebene. Ein Name allein genügt nicht — gezählt wird, was
    pytest wirklich ausführt.
    """

    befunde = []
    for pfad in sorted(verzeichnis.rglob("*.py")):
        if "__pycache__" in pfad.parts or not any(fnmatch.fnmatch(pfad.name, m) for m in muster):
            continue
        baum = ast.parse(pfad.read_text(encoding="utf-8"))
        hat_test = any(
            (isinstance(k, (ast.FunctionDef, ast.AsyncFunctionDef)) and k.name.startswith("test"))
            or (isinstance(k, ast.ClassDef) and k.name.startswith("Test"))
            for k in baum.body
        )
        if not hat_test:
            befunde.append(str(pfad.relative_to(verzeichnis)))
    return befunde


class TestJedeTestdateiEnthaeltEinenTest:
    """**Ein Dateiname ist kein Test.** Die Zusage darüber hat nur den Namen geprüft.

    Der Anlass war `test_output_writer.py`, seit dem ersten Commit
    (2026-08-18): 30 Anweisungen auf Modulebene, keine Funktion, keine
    Zusicherung. Es lief bei jedem Einsammeln — also *vor* jeder Fixture —,
    schrieb dabei nach `outputs/` und meldete einen Fehler mit
    `print("[ERROR] …")`, den niemand las. Die Regel darüber war erfüllt, weil
    die Datei `test_…` hieß.
    """

    def test_jede_eingesammelte_datei_enthaelt_einen_test(self):
        befunde = ohne_test(TESTS, _einsammelmuster())

        assert not befunde, (
            "Diese Dateien sammelt pytest ein, finden aber keinen Test darin:\n  "
            + "\n  ".join(befunde)
            + "\n\nCode auf Modulebene läuft beim Einsammeln, vor jeder Fixture, "
            "und kann nicht scheitern — er kann nur etwas ausgeben."
        )

    def test_der_waechter_saehe_eine_solche_datei(self, tmp_path):
        (tmp_path / "test_echt.py").write_text("def test_x():\n    assert True\n", encoding="utf-8")
        (tmp_path / "test_klasse.py").write_text("class TestX:\n    pass\n", encoding="utf-8")
        (tmp_path / "test_skript.py").write_text("print('laeuft')\n", encoding="utf-8")
        (tmp_path / "test_nur_helfer.py").write_text("def hilf():\n    pass\n", encoding="utf-8")

        befunde = ohne_test(tmp_path, ["test_*.py"])

        assert befunde == ["test_nur_helfer.py", "test_skript.py"]


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
    Aus `/tmp` gestartet laufen die Tests grün, und die CI installierte das
    Projekt bis P4.6 gar nicht (`pip install -r requirements.txt`).

    **`pip install -e .` trug dazu bis P4.6 nichts bei — und das war die erste,
    falsche Begründung dieses Wächters.** Die Editable-Installation legte `src/`
    *selbst* in den Suchpfad, nicht sein Elternverzeichnis; `import src`
    scheiterte damit außerhalb von pytest und außerhalb des
    Repo-Wurzelverzeichnisses. Seit P4.6 installiert sie das Paket `src` richtig.
    **Dieser Wächter hängt trotzdem nicht an der Installation** — getragen wird
    der Import in den Tests von pytest, und das gilt auch ohne installiertes
    Projekt.

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


def handgemachte_umbiegungen(quelltext: str) -> list[str]:
    """Jede Stelle, an der ein Test ein Attribut eines **importierten** Namens von Hand setzt.

    Gemeint ist das Muster `alt = modul.X` · `modul.X = neu` · … · `modul.X = alt`,
    und `setattr(modul, "X", neu)` als zweite Schreibweise derselben Sache. Ein
    **lokales** Objekt (`draft.feld = …`, `setattr(draft, …)`) ist kein Fund: Es
    entsteht im Test und verschwindet mit ihm. `monkeypatch.setattr` ist ein
    Methodenaufruf und damit ebenfalls keiner.
    """

    import ast

    baum = ast.parse(quelltext)
    importiert: set[str] = set()
    for knoten in ast.walk(baum):
        if isinstance(knoten, ast.Import):
            importiert.update((a.asname or a.name).split(".")[0] for a in knoten.names)
        elif isinstance(knoten, ast.ImportFrom):
            importiert.update(a.asname or a.name for a in knoten.names)

    def ist_importiert(ausdruck: ast.expr) -> bool:
        return isinstance(ausdruck, ast.Name) and ausdruck.id in importiert

    funde: list[tuple[int, str]] = []
    for knoten in ast.walk(baum):
        if isinstance(knoten, (ast.Assign, ast.AugAssign)):
            ziele = knoten.targets if isinstance(knoten, ast.Assign) else [knoten.target]
            for ziel in ziele:
                if isinstance(ziel, ast.Attribute) and ist_importiert(ziel.value):
                    funde.append((knoten.lineno, ast.unparse(ziel)))
        elif (
            isinstance(knoten, ast.Call)
            and isinstance(knoten.func, ast.Name)
            and knoten.func.id in {"setattr", "delattr"}
            and knoten.args
            and ist_importiert(knoten.args[0])
        ):
            funde.append((knoten.lineno, f"{knoten.func.id}({ast.unparse(knoten.args[0])}, …)"))
    return [f"{zeile}: {was}" for zeile, was in sorted(funde)]


class TestKeinTestBiegtEinModulVonHandUm:
    """**Wer für einen Test ein Modul umbiegt, nimmt `monkeypatch`.**

    Bis zum 2026-09-11 gab es fünf handgemachte Stellen in vier Dateien. **Drei
    stellten im `finally` zurück** und waren korrekt. **Zwei nicht** — beide in
    `test_dashboard_service.py`, und beide lagen im selben Muster: Ein Attribut
    (`CONFIGS_DIR`, `SWEEPS_DIR`) wurde auf ein `mkdtemp`-Verzeichnis gesetzt und
    **am Ende des `try`-Blocks** zurückgestellt, dessen `finally` das Verzeichnis
    löschte. Scheiterte eine Zusicherung dazwischen, zeigte das Attribut für
    **jeden folgenden Test der Sitzung** auf ein gelöschtes Verzeichnis — ein
    Fehlschlag, der seine Ursache weit weg von sich meldet.

    Gefunden wurden sie nicht über eine Liste, sondern beim Lesen der
    `mkdtemp`-Blöcke für P4.1 — und dann über **dieses** Merkmal gesucht: Eine
    Stelle war gesehen, fünf gab es.
    """

    def test_keine_handgemachte_umbiegung(self):
        befunde = [
            f"{pfad.relative_to(ROOT)}:{fund}"
            for pfad in sorted(TESTS.rglob("*.py"))
            if "__pycache__" not in pfad.parts
            for fund in handgemachte_umbiegungen(pfad.read_text(encoding="utf-8"))
        ]

        assert not befunde, (
            "Diese Stellen setzen ein Attribut eines importierten Namens von Hand:\n  "
            + "\n  ".join(befunde)
            + '\n\n`monkeypatch.setattr(modul, "NAME", wert)` stellt nach dem Test '
            "zurück — auch dann, wenn eine Zusicherung dazwischen scheitert."
        )

    def test_der_waechter_sieht_beide_schreibweisen_und_keine_lokalen_objekte(self):
        """Ohne diese Zusage wäre grün nur die Abwesenheit einer Messung."""

        quelltext = """import dashboard.config_catalog as catalog
from pathlib import Path


def test_x(monkeypatch, tmp_path):
    alt = catalog.CONFIGS_DIR
    catalog.CONFIGS_DIR = tmp_path
    setattr(catalog, "SWEEPS_DIR", tmp_path)
    monkeypatch.setattr(catalog, "CONFIGS_DIR", tmp_path)
    draft = object()
    draft.feld = 1
    setattr(draft, "feld", 2)
    Path.home = None
"""

        assert [fund.split(": ", 1)[0] for fund in handgemachte_umbiegungen(quelltext)] == [
            "7",
            "8",
            "13",
        ]


def tempfile_importe(quelltext: str) -> list[str]:
    """Jeder Import von `tempfile` — in jeder Form und an jeder Stelle, auch im Funktionsrumpf."""

    import ast

    funde: list[tuple[int, str]] = []
    for knoten in ast.walk(ast.parse(quelltext)):
        if isinstance(knoten, ast.Import):
            funde += [
                (knoten.lineno, f"import {a.name}")
                for a in knoten.names
                if a.name.split(".")[0] == "tempfile"
            ]
        elif (
            isinstance(knoten, ast.ImportFrom) and (knoten.module or "").split(".")[0] == "tempfile"
        ):
            funde.append((knoten.lineno, f"from {knoten.module} import …"))
    return [f"{zeile}: {was}" for zeile, was in sorted(funde)]


class TestEinTestLegtKeinTempVerzeichnisVonHandAn:
    """**Ein Temp-Verzeichnis kommt aus `tmp_path`, nicht aus `tempfile`.**

    Der Befund zählte 32 `tempfile.mkdtemp` mit `try`/`finally: shutil.rmtree`.
    Beim Anfassen waren es **39 Stellen in sechs Dateien**: 36 `mkdtemp`, zwei
    `TemporaryDirectory` in `test_save_final_narrative.py` — einer Datei, die
    als `unittest.TestCase` gar kein `tmp_path` bekommen konnte — und ein
    `gettempdir`, das ein **geteiltes** Systemverzeichnis als Beleg dafür nahm,
    dass ein Lauf *nicht* existiert. `tmp_path` ist leer, per Konstruktion.

    **Gesucht wird deshalb der Import, nicht die Funktion.** Eine Liste der
    Funktionen hätte genau die Lücke, aus der dieser Wächter kommt.

    **Umgestellt per Skript mit Gegenprüfung gegen den Stand davor:** In jeder
    Datei sind Testnamen und Zusicherungen gleich geblieben; verschwunden sind
    ausschließlich die 36 `mkdtemp`-Präfixe, hinzugekommen ist nichts. Zeilen
    innerhalb mehrzeiliger Literale wurden nicht umgerückt — bestimmt über die
    Positionen im Syntaxbaum, weil Python 3.12 f-Strings anders in Tokens
    zerlegt als gewöhnliche Strings.
    """

    def test_kein_test_importiert_tempfile(self):
        befunde = [
            f"{pfad.relative_to(ROOT)}:{fund}"
            for pfad in sorted(TESTS.rglob("*.py"))
            if "__pycache__" not in pfad.parts
            for fund in tempfile_importe(pfad.read_text(encoding="utf-8"))
        ]

        assert not befunde, (
            "Diese Stellen importieren tempfile:\n  "
            + "\n  ".join(befunde)
            + "\n\nEin Temp-Verzeichnis kommt aus dem Fixture `tmp_path` — pytest legt "
            "es je Test leer an und räumt es selbst auf, auch nach einem Fehlschlag."
        )

    def test_der_waechter_sieht_jede_importform_und_keine_prosa(self):
        """Ohne diese Zusage wäre grün nur die Abwesenheit einer Messung."""

        quelltext = '''"""Ein Docstring, der import tempfile nur erwähnt."""
import tempfile
import tempfile as tf
from tempfile import mkdtemp


def test_x(tmp_path):
    from tempfile import TemporaryDirectory
'''

        assert [fund.split(": ", 1)[0] for fund in tempfile_importe(quelltext)] == [
            "2",
            "3",
            "4",
            "8",
        ]


def klassennamen(wurzel: Path) -> dict[str, list[str]]:
    """Jeder Klassenname unter `wurzel`, mit Datei und Zeile jeder Definition."""

    import ast

    namen: dict[str, list[str]] = {}
    for pfad in sorted(wurzel.rglob("*.py")):
        if "__pycache__" in pfad.parts:
            continue
        for knoten in ast.walk(ast.parse(pfad.read_text(encoding="utf-8"))):
            if isinstance(knoten, ast.ClassDef):
                ort = f"{pfad.relative_to(wurzel.parent)}:{knoten.lineno}"
                namen.setdefault(knoten.name, []).append(ort)
    return namen


def verschattungen(produkt: Path, tests: Path) -> list[str]:
    """Jede Klasse unter `tests`, die so heißt wie eine Klasse unter `produkt`."""

    im_produkt = klassennamen(produkt)
    return [
        f"{ort} — gleichnamig mit {', '.join(im_produkt[name])}"
        for name, orte in sorted(klassennamen(tests).items())
        if name in im_produkt
        for ort in orte
    ]


class TestKeineTestklasseVerschattetEinenProduktnamen:
    """**Ein Testdoppel trägt den Namen dessen, wofür es im Test da ist.**

    Bis zum 2026-09-11 hieß `MockLLM` in `tests/` dreimal und in `src/` einmal
    — vier verschiedene Dinge unter einem Namen. Der Produkt-Mock
    (`src.llm.studio_helpers.MockLLM`) antwortet absichtlich mit `NO_OP`; die
    drei Testdoppel antworten mit Inhalt. Wer in einer Testdatei `MockLLM`
    las, konnte nicht wissen, welches davon gemeint war. Der Befund sah
    «vierfach near-identisch» und schlug ein gemeinsames Fixture vor.

    **Umbenannt nach Zweck, nicht zusammengelegt:** `FesteAntwort`,
    `VorschlagendeAgenten`, `SprechendeAgenten`. Beim Einführen traf diese Regel
    genau `MockLLM` von 126 Klassennamen aus `src/` — und sonst nichts.

    **Nicht erfasst, und das ist gewollt:** Namen, die nur *innerhalb* von
    `tests/` mehrfach vorkommen (`_App`, `_MitschreibendeApp`, `_StummesLLM`).
    Sie sind privat und verschatten nichts aus dem Produkt.
    """

    def test_keine_testklasse_heisst_wie_eine_klasse_aus_src(self):
        assert klassennamen(
            ROOT / "src"
        ), "In src/ wurde keine einzige Klasse gefunden — dann misst dieser Wächter nichts."

        befunde = verschattungen(ROOT / "src", TESTS)

        assert not befunde, (
            "Diese Testklassen heißen wie eine Klasse aus src/:\n  "
            + "\n  ".join(befunde)
            + "\n\nEin Testdoppel trägt den Namen dessen, wofür es im Test da ist — "
            "sonst ist beim Lesen nicht zu erkennen, ob das Produkt oder ein Nachbau "
            "gemeint ist."
        )

    def test_der_waechter_sieht_eine_verschattung(self, tmp_path):
        """Ohne diese Zusage wäre grün nur die Abwesenheit einer Messung."""

        (tmp_path / "src").mkdir()
        (tmp_path / "tests").mkdir()
        (tmp_path / "src" / "a.py").write_text("class MockLLM:\n    pass\n", encoding="utf-8")
        (tmp_path / "tests" / "test_b.py").write_text(
            "class MockLLM:\n    pass\n\n\nclass FesteAntwort:\n    pass\n", encoding="utf-8"
        )

        befunde = verschattungen(tmp_path / "src", tmp_path / "tests")

        assert len(befunde) == 1, befunde
        assert "test_b.py:1 — gleichnamig mit" in befunde[0], (
            "Der Fund zeigt nicht auf die MockLLM-Klasse in Zeile 1 — FesteAntwort in "
            f"Zeile 5 darf nicht gemeldet werden: {befunde}"
        )
        assert befunde[0].endswith("a.py:1"), befunde
