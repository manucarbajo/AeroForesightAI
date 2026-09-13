"""Höchstens acht kategoriale Töne je Figur, der Rest grau gruppiert (P7.1-U1.5).

**Der Befund (Q11 des UI/UX-Audits):** Der Szenario-Vergleich zeichnete zehn
Läufe in den zehn Tönen der Standardfolge, darunter vier Navy-Stufen — in einer
Legende lassen sich so viele Farben nicht zuverlässig auseinanderhalten.

**Was gilt:** Die Farbfolge hat acht Töne je Modus, ohne Grau. **Von Haiko
entschieden am 2026-09-13:** Ab der neunten Reihe ohne eigene Farbe bekommen die
ersten sieben einen Ton, der Rest teilt sich ein Grau unter **einem**
Legendeneintrag «Weitere (n)». Reihen mit eigener Farbe sind Rollen (Preis,
Buchung, Bänder) und bleiben unberührt.
"""

from __future__ import annotations

import json

import plotly.graph_objects as go
from dash import dcc

from dashboard.web import theme
from dashboard.web.views import figures


def _kurven(anzahl: int, **spur: object) -> go.Figure:
    return go.Figure(
        data=[
            go.Scatter(x=[1, 2], y=[i, i + 1], mode="lines", name=f"Lauf {i}", **spur)
            for i in range(anzahl)
        ]
    )


def _legende(fig: go.Figure) -> list[str]:
    return [spur.name for spur in fig.data if spur.showlegend is not False]


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


class TestAchtToeneUndDerRestGrau:
    def test_each_mode_has_eight_distinct_tones_without_grey(self):
        for mode in theme.MODES:
            toene = theme.COLORWAYS[mode]

            assert len(toene) == 8, f"{mode}: {len(toene)} Töne, zugesagt sind acht"
            assert len(set(toene)) == 8, f"{mode}: Töne doppelt: {toene}"
            assert (
                theme.PALETTE[mode]["neutral"] not in toene
            ), f"{mode}: Das Grau für «Weitere» steht selbst in der Farbfolge"

    def test_eight_series_keep_their_own_tone(self):
        fig = theme.style_figure(_kurven(8))

        assert _legende(fig) == [f"Lauf {i}" for i in range(8)]
        assert all(spur.line.color is None for spur in fig.data), "Acht Reihen wurden umgefärbt"

    def test_a_ninth_series_joins_the_rest(self):
        for mode in theme.MODES:
            fig = theme.style_figure(_kurven(10), mode=mode)
            grau = theme.PALETTE[mode]["neutral"]

            assert _legende(fig) == [f"Lauf {i}" for i in range(7)] + ["Weitere (3)"]
            assert [spur.line.color for spur in fig.data[:7]] == theme.COLORWAYS[mode][:7]
            rest = [spur for spur in fig.data if spur.name in {"Lauf 7", "Lauf 8", "Lauf 9"}]
            assert all(spur.line.color == grau and spur.showlegend is False for spur in rest)

    def test_applying_it_twice_changes_nothing(self):
        fig = theme.style_figure(theme.style_figure(_kurven(10)))

        assert _legende(fig).count("Weitere (3)") == 1
        assert len(fig.data) == 11

    def test_roles_with_their_own_colour_are_left_alone(self):
        fig = theme.style_figure(_kurven(10, line=dict(color="#123456")))

        assert "Weitere (3)" not in _legende(fig)
        assert all(spur.line.color == "#123456" for spur in fig.data)

    def test_the_scenario_comparison_shows_at_most_eight_entries(self, tmp_path):
        """Die Stelle, an der der Befund lag — mit zehn Läufen, wie in `outputs/sweeps/`."""

        sweeps = tmp_path / "sweeps"
        for i in range(10):
            ordner = sweeps / f"sweep_szenario_{i}"
            ordner.mkdir(parents=True)
            (ordner / "run_metadata.json").write_text(
                json.dumps({"rahmen": {"id": f"s{i}", "name": f"Szenario {i}"}}), encoding="utf-8"
            )
            ticks = [
                {"tick": t, "booking_rate": 0.4, "market_price_after_feedback_eur": 100.0}
                for t in (1, 2)
            ]
            (ordner / "tick_mechanics.json").write_text(
                json.dumps({"ticks": ticks}), encoding="utf-8"
            )

        figuren = _figuren(figures._view_szenarien(sweeps / "sweep_szenario_0"))

        assert figuren, "Der Vergleich zeichnet keine Figur — misst der Test ins Leere?"
        for figur in figuren:
            legende = _legende(figur)
            assert len(legende) <= 8, f"«{figur.layout.title.text}»: {len(legende)} Einträge"
            assert "Weitere (3)" in legende, f"«{figur.layout.title.text}»: {legende}"
