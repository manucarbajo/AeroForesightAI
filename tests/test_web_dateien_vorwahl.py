"""«Dateien» öffnet mit dem Abschlusstext, nicht mit einem Zwischenstand.

Befund 16 der Abnahme vom 2026-09-30: Gewählt war die erste Datei der Liste,
alphabetisch ein Checkpoint aus `checkpoints/`.
"""

from __future__ import annotations

from dashboard.web.views import files


def _lauf(tmp_path, *namen):
    for name in namen:
        pfad = tmp_path / name
        pfad.parent.mkdir(parents=True, exist_ok=True)
        pfad.write_text("{}", encoding="utf-8")
    return tmp_path


def _gewaehlt(run_dir) -> str:
    return files.vorwahl(files._options(run_dir))


def test_der_abschlusstext_ist_vorgewaehlt(tmp_path):
    lauf = _lauf(
        tmp_path, "checkpoints/checkpoint_tick_1.json", "run_metadata.json", "run_scenario.md"
    )

    assert _gewaehlt(lauf) == "run_scenario.md"
    assert 'value="run_scenario.md"' in str(files.render(lauf, "x")).replace("'", '"')


def test_ohne_abschlusstext_die_angaben_zum_lauf(tmp_path):
    lauf = _lauf(tmp_path, "checkpoints/checkpoint_tick_1.json", "run_metadata.json")

    assert _gewaehlt(lauf) == "run_metadata.json"


def test_ein_zwischenstand_nur_wenn_es_nichts_anderes_gibt(tmp_path):
    assert _gewaehlt(_lauf(tmp_path, "checkpoints/a.json", "event_log.json")) == "event_log.json"
    assert _gewaehlt(_lauf(tmp_path / "b", "checkpoints/a.json")) == "checkpoints/a.json"
