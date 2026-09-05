"""P3.6: Das Dashboard hängt an einer Schnittstelle, nicht an Innenleben (2026-09-05).

`dashboard/run_launcher.py` importierte drei **unterstrichs-präfixierte** Namen
aus `src/run_simulation.py`: `_build_run_args`, `_save_run_outputs`,
`_write_multi_run_summary`. Ein Unterstrich sagt «privat, kann sich jederzeit
ändern» — ein Refactor der internen Helfer hätte den Launcher **stumm** gebrochen,
und niemand hätte es vor dem nächsten Dashboard-Lauf gemerkt.

**Vorgezogen am 2026-08-28** aus dem Wizard-Audit, mit einer Begründung, die über
den Refactor hinausging: Ohne eine Schnittstelle, die sagt, *was ein Startpfad
entgegennimmt*, ließ sich W1.1 nicht mechanisch halten. Diese Hälfte ist mit
`scenario_sweeps.FESTLEGUNGEN`/`UNBEACHTET` erledigt (Invariante 7); hier geht es
um die andere: die Namen.

**Warum ein Wächter und nicht nur ein Rename:** Der Import ist einmal
hineingewandert, weil es billiger war als eine Schnittstelle. Das nächste Mal
wäre es wieder billiger.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

#: Die Bäume, die aus `src/` importieren dürfen — und dabei nur Öffentliches.
#: `legacy_streamlit` ist draußen: abgelöste Oberfläche, P5.2 entfernt sie.
AUFRUFER = ("dashboard",)


def _importierte_namen(pfad: Path) -> list[tuple[int, str, str]]:
    """Jeder aus `src.*` importierte Name — auch aus Importen *innerhalb* einer Funktion.

    Genau dort saß der Befund: Der Import stand in `_run_body`, mitten im
    Ablauf, nicht im Kopf der Datei. Ein Blick auf die Importzeilen oben hätte
    ihn nie gefunden.
    """

    baum = ast.parse(pfad.read_text(encoding="utf-8"))
    gefunden: list[tuple[int, str, str]] = []
    for knoten in ast.walk(baum):
        if isinstance(knoten, ast.ImportFrom) and (knoten.module or "").startswith("src"):
            for alias in knoten.names:
                gefunden.append((knoten.lineno, knoten.module or "", alias.name))
    return gefunden


class TestKeinDashboardModulGreiftInsInnenleben:
    """**Die Zusage von P3.6 im Wortlaut.**"""

    def test_kein_unterstrich_name_aus_src(self):
        befunde: list[str] = []
        for baum in AUFRUFER:
            for pfad in sorted((ROOT / baum).rglob("*.py")):
                if "legacy_streamlit" in pfad.relative_to(ROOT).parts:
                    continue
                for zeile, modul, name in _importierte_namen(pfad):
                    if name.startswith("_"):
                        befunde.append(f"{pfad.relative_to(ROOT)}:{zeile} — {modul}.{name}")

        assert not befunde, (
            "Diese Stellen importieren Innenleben aus `src/`:\n  "
            + "\n  ".join(befunde)
            + "\n\nEin Unterstrich sagt «kann sich jederzeit ändern». Wer den Namen "
            "braucht, hebt ihn in die öffentliche Schnittstelle des Moduls — nicht "
            "den Import."
        )

    def test_der_waechter_findet_auch_einen_import_im_funktionsrumpf(self, tmp_path):
        """Der Befund saß nicht im Dateikopf, sondern in `_run_body`.

        Ein Wächter, der nur die obersten Importzeilen liest, hätte ihn nie
        gesehen — deshalb läuft er über den ganzen Syntaxbaum.
        """

        modul = tmp_path / "versteckt.py"
        modul.write_text(
            "def f():\n    from src.run_simulation import _geheim\n    return _geheim\n",
            encoding="utf-8",
        )

        assert [name for _, _, name in _importierte_namen(modul)] == ["_geheim"]

    def test_die_drei_namen_gibt_es_oeffentlich(self):
        """Umbenannt, nicht entfernt — der Launcher braucht sie weiterhin."""

        import src.run_simulation as cli

        for name in ("build_run_args", "save_run_outputs", "write_multi_run_summary"):
            assert hasattr(cli, name), f"`{name}` fehlt"
            assert name in cli.__all__, f"`{name}` steht nicht in `__all__`"

    def test_die_alten_namen_sind_weg(self):
        """Beide Namen nebeneinander stehen zu lassen wäre die schlechteste Variante:
        Der Launcher hinge weiter am alten, und niemand merkte es."""

        import src.run_simulation as cli

        for name in ("_build_run_args", "_save_run_outputs", "_write_multi_run_summary"):
            assert not hasattr(cli, name), f"`{name}` gibt es noch"

    def test_der_launcher_benutzt_die_oeffentlichen(self):
        """Nicht «es gibt sie», sondern «er nimmt sie»."""

        pfad = ROOT / "dashboard" / "run_launcher.py"
        namen = {
            name for _, modul, name in _importierte_namen(pfad) if modul == "src.run_simulation"
        }

        assert namen == {"build_run_args", "save_run_outputs", "write_multi_run_summary"}, namen

    @pytest.mark.parametrize(
        "name", ["main", "build_run_args", "save_run_outputs", "write_multi_run_summary"]
    )
    def test_was_in_all_steht_gibt_es_auch(self, name):
        """Ein `__all__`, das auf einen entfernten Namen zeigt, ist eine Zusage ins Leere."""

        import src.run_simulation as cli

        assert hasattr(cli, name)
