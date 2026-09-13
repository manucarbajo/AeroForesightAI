"""Reihennamen und Einheiten kommen aus einer Quelle (P7.1-U1.5).

**Der Befund (Q11 des UI/UX-Audits):** «Was die Politik bewirkt» benannte seine
Reihen mit Spaltennamen (`carbon_tax_level`, …), die linke Achse trug die
geratene Einheit «Betrag (EUR/t o. ä.)» für zwei verschiedene Größen, «Wer noch
fliegt» baute Segmentnamen aus der Kennung («Eco Conscious»), und der
Szenario-Vergleich benannte Läufe nach ihrem Ordner («Co2 Delayed»). Lesbare
Namen gab es für acht von sechzehn Systemgrößen, und das Diagramm benutzte sie
nicht einmal.

**Was gilt:** Namen und Einheiten stehen in `dashboard/config_catalog.py` —
`PROPERTY_LABELS`, `EINHEITEN`, `SEGMENT_NAMEN` —, und jede Größe, jede Einheit
und jedes Segment aus `configs/properties.json` hat dort einen Eintrag. **Jede
Figur der vier Aussagen** wird auf einem künstlichen Lauf gerendert: Keine Reihe
heißt wie eine Kennung, jede y-Achse, auf der eine Reihe liegt, nennt ihre
Einheit, und Szenarien heißen nach ihrem Rahmen.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import plotly.graph_objects as go
import pytest
from dash import dcc

from dashboard import config_catalog as katalog
from dashboard.web.views import figures

PROPERTIES = json.loads(
    (Path(__file__).resolve().parents[1] / "configs" / "properties.json").read_text(
        encoding="utf-8"
    )
)
SYSTEMGROESSEN = [p for p in PROPERTIES["system_properties"] if isinstance(p, dict)]
SEGMENTE = [
    p["id"]
    for p in PROPERTIES.get("individual_properties", [])
    if isinstance(p, dict) and p.get("type") == "boolean"
]

#: Eine Kennung: Kleinbuchstaben mit mindestens einem Unterstrich.
_KENNUNG = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)+$")

#: Eine Einheit im Achsentitel: etwas in Klammern.
_EINHEIT = re.compile(r"\(.+\)")


def _figuren(baum) -> list[go.Figure]:
    gefunden: list[go.Figure] = []
    stapel = [baum]
    while stapel:
        knoten = stapel.pop()
        if isinstance(knoten, (list, tuple)):
            stapel.extend(knoten)
            continue
        if isinstance(knoten, dcc.Graph) and getattr(knoten, "figure", None) is not None:
            figur = knoten.figure
            gefunden.append(figur if isinstance(figur, go.Figure) else go.Figure(figur))
        kinder = getattr(knoten, "children", None)
        if kinder is not None and not isinstance(kinder, str):
            stapel.append(kinder)
    return gefunden


def _befunde(figur: go.Figure, wo: str, kennungen: set[str]) -> list[str]:
    """Reihen, die wie eine Kennung heißen, und y-Achsen ohne Einheit."""

    befunde: list[str] = []
    titel = figur.layout.title.text or "(ohne Titel)"
    achsen: set[str] = set()
    for spur in figur.data:
        name = spur.name or ""
        if name and (_KENNUNG.match(name) or name.lower().replace(" ", "_") in kennungen):
            befunde.append(f"{wo} «{titel}»: Reihe «{name}» heißt wie eine Kennung")
        achsen.add(getattr(spur, "yaxis", None) or "y")
    for achse in sorted(achsen):
        schluessel = "yaxis" if achse == "y" else f"yaxis{achse[1:]}"
        achsentitel = figur.layout[schluessel].title.text or ""
        if not _EINHEIT.search(achsentitel):
            befunde.append(f"{wo} «{titel}»: y-Achse «{achsentitel}» nennt keine Einheit")
    return befunde


@pytest.fixture
def lauf(tmp_path):
    """Zwei Szenario-Läufe mit allem, was die vier Aussagen zeichnen."""

    sweeps = tmp_path / "sweeps"
    spalten = ["tick", *figures.POLICY_COLUMNS, *figures.COST_COLUMNS]
    for kennung, name in (
        ("business_as_usual", "Business as Usual (A1+B1)"),
        ("co2_delayed", "CO₂-Verzögerung"),
    ):
        ordner = sweeps / f"sweep_{kennung}"
        (ordner / "timeseries").mkdir(parents=True)
        (ordner / "run_metadata.json").write_text(
            json.dumps({"rahmen": {"id": kennung, "name": name, "quelle": "preset"}}),
            encoding="utf-8",
        )
        ticks = [
            {
                "tick": t,
                "booking_rate": 0.4,
                "ticket_price": 100.0 + t,
                "cost_pressure": 80.0,
                "provider_markup": 20.0,
            }
            for t in (1, 2, 3)
        ]
        (ordner / "tick_mechanics.json").write_text(json.dumps({"ticks": ticks}), encoding="utf-8")
        zeilen = [",".join(spalten)] + [
            ",".join([str(t)] + ["1"] * (len(spalten) - 1)) for t in (1, 2, 3)
        ]
        (ordner / "timeseries" / "properties.csv").write_text(
            "\n".join(zeilen) + "\n", encoding="utf-8"
        )
        population = (
            "tick,segment_id,total_individuals,booked_individuals,booking_rate,avg_income_factor\n"
        )
        population += "".join(f"{t},{s},10,4,0.4,1.0\n" for t in (1, 2) for s in SEGMENTE)
        (ordner / "timeseries" / "population.csv").write_text(population, encoding="utf-8")
        (ordner / "timeseries" / "age_property.csv").write_text(
            "tick,age_group,booking_rate\n1,18-25,0.3\n2,18-25,0.35\n", encoding="utf-8"
        )
    return sweeps / "sweep_business_as_usual"


def _kennungen() -> set[str]:
    return {p["id"] for p in SYSTEMGROESSEN} | set(SEGMENTE)


AUSSAGEN = {
    "Preis und Nachfrage": figures._view_nachfrage,
    "Was die Politik bewirkt": figures._view_politik,
    "Wer noch fliegt": figures._view_wer,
    "Die Szenarien nebeneinander": figures._view_szenarien,
}


class TestNamenUndEinheitenAusEinerQuelle:
    def test_every_system_property_has_a_name_and_a_known_unit(self):
        ohne_name = sorted(
            p["id"] for p in SYSTEMGROESSEN if p["id"] not in katalog.PROPERTY_LABELS
        )
        ohne_einheit = sorted(
            f"{p['id']} ({p.get('unit')})"
            for p in SYSTEMGROESSEN
            if p.get("unit") and p["unit"] not in katalog.EINHEITEN
        )

        assert not ohne_name, f"Systemgrößen ohne Namen in `PROPERTY_LABELS`: {ohne_name}"
        assert not ohne_einheit, f"Einheiten ohne Eintrag in `EINHEITEN`: {ohne_einheit}"

    def test_every_segment_has_a_name(self):
        ohne = sorted(s for s in SEGMENTE if s not in katalog.SEGMENT_NAMEN)

        assert SEGMENTE, "Keine Segmente in configs/properties.json gefunden"
        assert not ohne, f"Segmente ohne Namen in `SEGMENT_NAMEN`: {ohne}"

    @pytest.mark.parametrize("aussage", list(AUSSAGEN))
    def test_no_chart_names_a_series_by_its_column(self, lauf, aussage):
        figuren = _figuren(AUSSAGEN[aussage](lauf))
        befunde = [b for figur in figuren for b in _befunde(figur, aussage, _kennungen())]

        assert (
            figuren
        ), f"«{aussage}» zeichnet auf dem künstlichen Lauf keine Figur — misst der Test ins Leere?"
        assert not befunde, "\n  ".join(["Namen und Einheiten:", *befunde])

    def test_scenarios_are_named_after_their_frame(self, lauf):
        namen = {
            spur.name for figur in _figuren(figures._view_szenarien(lauf)) for spur in figur.data
        }

        assert (
            "CO₂-Verzögerung" in namen
        ), f"Der Vergleich benennt Läufe nicht nach ihrem Rahmen: {namen}"
        assert "Co2 Delayed" not in namen

    def test_the_guard_would_notice_a_relapse(self):
        falsch = go.Figure(
            data=[
                go.Scatter(x=[1], y=[1], name="carbon_tax_level"),
                go.Scatter(x=[1], y=[1], name="Eco Conscious"),
            ],
            layout=dict(title="Probe", yaxis_title="Betrag"),
        )
        richtig = go.Figure(
            data=[go.Scatter(x=[1], y=[1], name="CO₂-Steuer (EUR/t)")],
            layout=dict(title="Probe", yaxis_title="Betrag (EUR/t)"),
        )

        assert len(_befunde(falsch, "Probe", _kennungen())) == 3
        assert _befunde(richtig, "Probe", _kennungen()) == []
