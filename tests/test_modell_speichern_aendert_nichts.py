"""Speichern ohne Änderung lässt `properties.json` Zeichen für Zeichen, wie sie ist.

**Befund 14 der Abnahme vom 2026-09-30:** «Speichern ohne Änderung entfernt den
Zeilenumbruch am Ende von `properties.json`». Jeder Schreiber in
`config_catalog` rief `json.dump` ohne abschließenden Zeilenumbruch; danach
zeigte `git diff` eine geänderte Datei, ohne dass sich ein Wert geändert hatte.

Verglichen wird ohne Rücksicht auf Zeilenenden: Unter Windows schreibt Python im
Textmodus `\\r\\n`, und Git gleicht das beim Einchecken an.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from dashboard import config_catalog as cc

QUELLE = Path(__file__).resolve().parents[1] / "configs" / "properties.json"


@pytest.fixture
def kopie(tmp_path, monkeypatch) -> Path:
    shutil.copy(QUELLE, tmp_path / "properties.json")
    monkeypatch.setattr(cc, "CONFIGS_DIR", tmp_path)
    return tmp_path / "properties.json"


def _inhalt(pfad: Path) -> str:
    return pfad.read_bytes().decode("utf-8").replace("\r\n", "\n")


@pytest.mark.parametrize(
    "speichern",
    [
        lambda: cc.save_market_feedback_to_file(cc.extract_market_feedback_from_file()),
        lambda: cc.save_saturation_to_file(cc.extract_saturation_from_file()),
    ],
    ids=["preisbildung", "saettigung"],
)
def test_speichern_ohne_aenderung_aendert_nichts(kopie, speichern):
    vorher = _inhalt(kopie)

    speichern()

    assert _inhalt(kopie).endswith("}\n"), "Der Zeilenumbruch am Ende fehlt"
    assert _inhalt(kopie) == vorher
