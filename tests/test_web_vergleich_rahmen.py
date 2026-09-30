"""Der Szenario-Vergleich zeigt nur die heutigen Rahmenszenarien (P8-V10).

**Der Befund:** Die Ansicht «Die Szenarien nebeneinander» nahm jeden Ordner
unter `outputs/sweeps/` mit — auch Läufe unter Szenarien, die es längst nicht
mehr gibt («Short Test Sweep», «High Base Price»). Darunter stand ein Satz mit
einem Fehler: «… Szenario-Läufe unter aus einem Szenario-Vergleich».

Welche Läufe dazugehören, leitet die Ansicht so ab wie der Filter «Prüfläufe»
im Lauf-Browser: aus `rahmenszenarien`, derselben Quelle, aus der ein Vergleich
seine Rahmen nimmt.
"""

from __future__ import annotations

import json
from pathlib import Path

from dashboard.config_catalog import rahmenszenarien
from dashboard.web.views import figures


def _lauf(sweeps: Path, kennung: str, rahmen: dict | None) -> Path:
    ordner = sweeps / f"sweep_{kennung}"
    ordner.mkdir(parents=True)
    metadaten = {} if rahmen is None else {"rahmen": rahmen}
    (ordner / "run_metadata.json").write_text(json.dumps(metadaten), encoding="utf-8")
    ticks = [
        {"tick": t, "booking_rate": 0.4, "market_price_after_feedback_eur": 100.0} for t in (1, 2)
    ]
    (ordner / "tick_mechanics.json").write_text(json.dumps({"ticks": ticks}), encoding="utf-8")
    return ordner


def _bestand(tmp_path: Path) -> Path:
    """Die heutigen Rahmen, dazu ein Prüflauf und ein Lauf ohne Rahmenangabe."""

    sweeps = tmp_path / "sweeps"
    for rahmen in rahmenszenarien():
        _lauf(sweeps, rahmen.id, {"id": rahmen.id, "name": rahmen.name, "quelle": "preset"})
    _lauf(
        sweeps, "test_short", {"id": "test_short", "name": "Short Test Sweep", "quelle": "preset"}
    )
    _lauf(sweeps, "ohne_rahmen", None)
    return sweeps


def _spurnamen(gezeichnet) -> set[str]:
    namen: set[str] = set()

    def _suche(knoten) -> None:
        figur = getattr(knoten, "figure", None)
        if figur is not None:
            namen.update(spur.name for spur in figur.data)
        kinder = getattr(knoten, "children", None)
        for kind in kinder if isinstance(kinder, list) else [kinder]:
            if kind is not None and not isinstance(kind, str):
                _suche(kind)

    _suche(gezeichnet)
    return namen


class TestNurHeutigeRahmen:
    def test_ein_pruef_lauf_steht_nicht_im_vergleich(self, tmp_path):
        sweeps = _bestand(tmp_path)
        start = sweeps / f"sweep_{rahmenszenarien()[0].id}"

        geschwister = figures.sweep_geschwister(start)

        assert {p.name for p in geschwister} == {f"sweep_{r.id}" for r in rahmenszenarien()}

    def test_die_kurven_tragen_nur_rahmennamen(self, tmp_path):
        sweeps = _bestand(tmp_path)

        namen = _spurnamen(figures._view_szenarien(sweeps / f"sweep_{rahmenszenarien()[0].id}"))

        assert namen, "Der Vergleich zeichnet keine Kurve — misst der Test ins Leere?"
        assert namen == {r.name for r in rahmenszenarien()}, namen

    def test_ein_lauf_unter_eigenen_werten_zaehlt_nicht(self, tmp_path):
        """Auch mit der Kennung eines Rahmens: Wer nicht unter dem Preset stand, ist keiner."""

        sweeps = tmp_path / "sweeps"
        kennung = rahmenszenarien()[0].id
        _lauf(sweeps, kennung, {"id": kennung, "quelle": "abgeleitet"})

        assert figures.sweep_geschwister(sweeps / f"sweep_{kennung}") == []


class TestDerSatzDarunter:
    def test_er_nennt_die_ausgeblendeten(self, tmp_path):
        sweeps = _bestand(tmp_path)
        text = str(figures._view_szenarien(sweeps / f"sweep_{rahmenszenarien()[0].id}"))

        assert f"die {len(rahmenszenarien())} Rahmenszenarien" in text
        assert "2 Läufe unter Szenarien, die heute kein Rahmen sind, sind ausgeblendet" in text
        assert "unter aus" not in text

    def test_ohne_ausgeblendete_schweigt_er_davon(self):
        assert "ausgeblendet" not in figures._vergleich_satz(4, 0)
        assert "Ein Lauf unter einem Szenario" in figures._vergleich_satz(4, 1)
