"""Haken sitzen richtig, und Werte bleiben in ihrer Box (P1.7).

Zwei Befunde am Bild, beide von Manu gemeldet:

1. **Werte traten aus ihrer Kachel.** `ui.metric_tile` ist für kurze Zahlen
   gebaut — 2xl, fett, Ziffern gleicher Breite. «Standard-Ausgangslage» und
   «Ohne Sprachmodell» sind aber Text und sprengten in einer dreispaltigen Reihe
   ihre Karte.
2. **Der Haken saß oben in der Karte.** Gemessen: Die Karte «Achterbahn der
   Extreme» war 137 px hoch, der Haken saß bei 12 % ihrer Höhe. Auf einer
   Fläche, die man als Ganzes auswählt, gehört er in die Mitte.

Dazu die Falle, die beim Beheben auffiel: Bis Dash 3 mussten Anordnung und
Ausrichtung als `labelStyle` inline gesetzt werden, weil `dcc.Checklist` selbst
inline schrieb. **Dash 4 tut das nicht mehr** — die Dicts wirkten nicht, und
eine Änderung daran blieb folgenlos. Sie sind entfernt; dieser Wächter hält
fest, dass sie nicht zurückkommen.

Pixel kann er nicht messen — dafür bräuchte er einen Browser. Er prüft die
Größen, aus denen die Pixel entstehen: welche Regel im Stylesheet steht, und
dass keine Komponente ihre Ausrichtung wieder an Dash übergibt.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from dashboard.web import components as ui

CSS = Path(__file__).resolve().parents[1] / "dashboard" / "web" / "assets" / "dashboard.css"
KOMPONENTEN = Path(__file__).resolve().parents[1] / "dashboard" / "web" / "components.py"


def _regel(selektor: str) -> str:
    """Der Regelrumpf eines Selektors — leer, wenn es ihn nicht gibt."""

    treffer = re.search(re.escape(selektor) + r"\s*\{([^}]*)\}", CSS.read_text(encoding="utf-8"))
    return treffer.group(1) if treffer else ""


class TestDerHakenSitztRichtig:
    """Karte mittig, Liste an der ersten Textzeile — beides absichtlich."""

    def test_a_card_centres_its_mark(self):
        assert "align-items: center" in _regel(".af-radio--cards label")

    def test_a_list_aligns_its_mark_with_the_first_line(self):
        """In einer Liste entsteht so eine gerade Spalte von Haken."""

        rumpf = _regel(".af-check label,\n.af-radio label")
        assert "align-items: flex-start" in rumpf

    def test_the_card_drops_the_line_offset(self):
        """Der Versatz, der den Haken in einer Liste auf die Grundlinie zieht,
        ließe ihn auf einer Karte drei Pixel unter der Mitte hängen."""

        assert "margin-top: 0" in _regel('.af-radio--cards input[type="radio"]')


class TestKeineAusrichtungGehtMehrAnDash:
    """Die Falle: `labelStyle` wirkt seit Dash 4 nicht mehr.

    Wer die Ausrichtung dort wieder hinschriebe, änderte nichts — und würde
    lange suchen. Genau das ist beim Zentrieren des Hakens passiert.
    """

    @pytest.mark.parametrize("name", ["labelStyle", "inputStyle"])
    def test_no_component_hands_its_layout_to_dash(self, name):
        quelle = KOMPONENTEN.read_text(encoding="utf-8")

        assert f"{name}=" not in quelle, (
            f"`{name}` ist seit Dash 4 wirkungslos — das Label trägt keinen "
            "Inline-Stil mehr. Die Ausrichtung gehört nach `dashboard.css`."
        )

    def test_the_old_style_dicts_are_gone(self):
        quelle = KOMPONENTEN.read_text(encoding="utf-8")

        for name in ("CHECK_LABEL_STYLE", "SWITCH_LABEL_STYLE", "CARD_LABEL_STYLE"):
            assert name not in quelle.split('"""')[0] + quelle, (
                f"`{name}` ist wieder da. Es wirkt nicht — siehe Kommentar in " "`components.py`."
            )


class TestKeinWertTrittAusSeinerKachel:
    def test_a_prose_value_gets_the_smaller_setting(self):
        """Der Zahlensatz ist für «Standard-Ausgangslage» zu groß."""

        zahl = str(ui.metric_tile("Länge", "40 Ticks"))
        text = str(ui.metric_tile("Szenario", "Standard-Ausgangslage", prose=True))

        assert "text-2xl" in zahl
        assert "text-2xl" not in text

    def test_every_tile_value_can_be_capped(self):
        """`af-tile__value` trägt den Umbruch — ohne die Klasse greift er nicht."""

        assert "af-tile__value" in str(ui.metric_tile("Szenario", "x", prose=True))
        assert "af-tile__value" in str(ui.metric_tile("Länge", 40))

    def test_the_cap_breaks_inside_a_long_word(self):
        """`anywhere`, nicht `break-word`.

        Letzteres bricht ein Wort erst, wenn es allein in einer Zeile immer noch
        nicht passt — in einer schmalen Spalte steht «Standard-Ausgangslage»
        dann trotzdem heraus.
        """

        assert "overflow-wrap: anywhere" in _regel(".af-tile__value")

    def test_grid_children_may_shrink_below_their_content(self):
        """Ohne `min-width: 0` schiebt ein langes Wort die ganze Spalte auf."""

        assert "min-width: 0" in _regel(".af-grid > *")

    def test_the_grid_helper_carries_the_class(self):
        assert "af-grid" in str(ui.grid(ui.metric_tile("a", 1)))
