"""Der Reiter «Bericht» klappt jeden Tick zu (P7.6, Befund 16 der Abnahme vom 2026-09-30).

Der Bericht des Pitch-Falls war als ein Markdown-Block 63 Bildschirme lang.
Gegliedert wird beim Anzeigen — die Datei bleibt, wie sie ist, und ein Bericht
von vor dem 2026-10-01 («## Tick-Übersicht») wird genauso gegliedert.
"""

from __future__ import annotations

from dash import html

from dashboard.web.views import narrative

BERICHT = """# Simulationsbericht: Probe

## Überblick
- **Gerechnete Ticks:** 2 von 2

## Geplante Änderungen der Systemgrößen
Vorgegeben vom Szenario, in diesem Lauf:
- **Tick 1:** CO₂-Steuer springt auf 50 €/t

## {kopf}

### Tick 1

**37,0 %** gebucht (370 von 1000) · Preis 139,55 → 140,05 € (+0,50 €) · Vorgaben: Bevölkerung 1000 Personen

#### Wer bucht

- **Familien:** 26 von 84 gebucht (31,0 %)

### Tick 2

**30,0 %** gebucht (300 von 1000), −7,0 Prozentpunkte · Preis 140,05 → 139,00 € (−1,05 €)

**Faktorwechsel:** Gesellschaft F6.1 → F6.2

## Faktorlage am Ende
- **Gesellschaft:** F6.2 – Starkes Klimabewusstsein
"""


def _details(knoten) -> list:
    if isinstance(knoten, html.Details):
        return [knoten]
    kinder = getattr(knoten, "children", None)
    if isinstance(kinder, (list, tuple)):
        return [d for k in kinder for d in _details(k)]
    return _details(kinder) if kinder is not None and not isinstance(kinder, str) else []


def test_jeder_tick_ist_ein_zugeklappter_abschnitt(tmp_path):
    (tmp_path / "final_narrative.md").write_text(
        BERICHT.format(kopf="Tick für Tick"), encoding="utf-8"
    )

    gerendert = narrative.render(tmp_path, "probe")
    klappen = _details(gerendert)

    assert len(klappen) == 3, "Vorgaben des Szenarios und zwei Ticks"
    assert not any(k.open for k in klappen)
    assert "Vorgaben des Szenarios" in str(klappen[0])
    text = str(gerendert)
    assert "Tick 1 · 37,0 % gebucht (370 von 1000) · Preis 139,55 → 140,05 € (+0,50 €)" in text
    assert "Faktorlage am Ende" in text


def test_ein_faktorwechsel_ist_markiert():
    gliederung = narrative.gliedern(BERICHT.format(kopf="Tick für Tick"))

    assert [t.faktorwechsel for t in gliederung.ticks] == [False, True]


def test_ein_alter_bericht_wird_genauso_gegliedert():
    gliederung = narrative.gliedern(BERICHT.format(kopf="Tick-Übersicht"))

    assert [t.titel for t in gliederung.ticks] == ["Tick 1", "Tick 2"]
    assert gliederung.schluss.startswith("## Faktorlage am Ende")


def test_ohne_tickabschnitt_bleibt_er_ein_block(tmp_path):
    (tmp_path / "final_narrative.md").write_text("# Kurz\n\nNur Text.\n", encoding="utf-8")

    assert _details(narrative.render(tmp_path, "probe")) == []


def test_die_vorgaben_stehen_nicht_im_offenen_kopf():
    gliederung = narrative.gliedern(BERICHT.format(kopf="Tick für Tick"))

    assert "CO₂-Steuer springt" not in gliederung.kopf
    assert "CO₂-Steuer springt" in gliederung.vorgaben
    assert "## Überblick" in gliederung.kopf
