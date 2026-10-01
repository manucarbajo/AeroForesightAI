"""Der Demo-Schalter der Abfrage hat einen Namen (Befund N5 der Gegenprüfung).

Die Beispielantwort und das Handbuch nannten ihn «Demo ohne Ollama», das
Kästchen «Beispielantworten ohne Sprachmodell» — wer der Antwort folgte, suchte
ein Kästchen, das es nicht gibt.
"""

from __future__ import annotations

from pathlib import Path

from dashboard.web.views import explorer

HANDBUCH = Path(__file__).resolve().parents[1] / "docs" / "handbuch" / "abfrage.md"


def test_die_beispielantwort_nennt_das_kaestchen():
    antwort = explorer._MockLLM(None).call("Was geschah?")

    assert f"«{explorer.DEMO_SCHALTER}»" in antwort
    assert "Ollama" not in antwort


def test_das_handbuch_nennt_das_kaestchen():
    text = HANDBUCH.read_text(encoding="utf-8")

    assert f"«{explorer.DEMO_SCHALTER}»" in text
    assert "Demo ohne Ollama" not in text
