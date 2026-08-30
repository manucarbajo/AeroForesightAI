from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

import pytest

from src.reporting.figure_generator import (
    RunSeries,
    extract_series_from_run_dir,
    generate_all_figures,
    generate_run_figures,
    plot_factor_states,
    plot_price_vs_booking,
    plot_scenario_comparison,
)


def _write_sample_run(
    run_dir: Path, *, booking_start: float = 0.5, price_start: float = 120.0
) -> None:
    """Ein Lauf auf der Platte.

    *booking_start* und *price_start* gibt es, damit ein zweiter Aufruf **andere**
    Bilder erzeugt — ohne das schreiben die deterministischen Plots sich selbst
    mit identischem Inhalt, und ein Teilstand bliebe unsichtbar.
    """

    run_dir.mkdir(parents=True, exist_ok=True)
    ticks = [
        {
            "tick": i,
            "booking_rate": booking_start + i * 0.01,
            "market_price_after_feedback_eur": price_start + i,
            "carbon_tax_level": 50.0 if i < 15 else 120.0,
            "income_index": 1.0,
        }
        for i in range(1, 21)
    ]
    (run_dir / "tick_mechanics.json").write_text(json.dumps({"ticks": ticks}), encoding="utf-8")
    (run_dir / "run_metadata.json").write_text(
        json.dumps({"simulation_name": "Test Run"}), encoding="utf-8"
    )
    (run_dir / "timeseries").mkdir(exist_ok=True)
    with (run_dir / "timeseries" / "factors.csv").open("w", encoding="utf-8") as handle:
        handle.write("tick,F1,F2\n")
        for i in range(1, 21):
            handle.write(f"{i},F1.1,F2.1\n")
    with (run_dir / "timeseries" / "age_property.csv").open("w", encoding="utf-8") as handle:
        handle.write("tick,age_group,booking_rate\n")
        for i in range(1, 6):
            handle.write(f"{i},18-25,0.45\n")
            handle.write(f"{i},51-65,0.55\n")


class TestFigureGenerator:
    def test_extract_series_from_run_dir(self):
        tmpdir = Path(tempfile.mkdtemp(prefix="fig_run_"))
        try:
            run_dir = tmpdir / "run_test"
            _write_sample_run(run_dir)
            series = extract_series_from_run_dir(run_dir)
            assert len(series.ticks) == 20
            assert series.booking_rate[0] == 0.51
            assert series.carbon_tax[14] == 120.0
        finally:
            shutil.rmtree(tmpdir)

    def test_plot_functions_write_png(self):
        tmpdir = Path(tempfile.mkdtemp(prefix="fig_plot_"))
        try:
            series_a = RunSeries(
                label="A",
                ticks=[1, 2, 3],
                booking_rate=[0.5, 0.52, 0.54],
                ticket_price=[100.0, 101.0, 102.0],
            )
            series_b = RunSeries(
                label="B",
                ticks=[1, 2, 3],
                booking_rate=[0.6, 0.58, 0.56],
                ticket_price=[110.0, 109.0, 108.0],
            )
            out = Path(tmpdir)
            p1 = plot_scenario_comparison([series_a, series_b], out / "cmp.png", metric="booking")
            p2 = plot_price_vs_booking(series_a, out / "pvb.png")
            p3 = plot_factor_states(
                RunSeries(label="X", factor_ticks=[1, 2], factor_values={"F1": [1.1, 1.2]}),
                out / "fac.png",
            )
            assert p1.is_file() and p1.stat().st_size > 0
            assert p2.is_file() and p2.stat().st_size > 0
            assert p3.is_file() and p3.stat().st_size > 0
        finally:
            shutil.rmtree(tmpdir)

    def test_generate_run_figures_writes_manifest(self):
        tmpdir = Path(tempfile.mkdtemp(prefix="fig_run_gen_"))
        try:
            run_dir = Path(tmpdir) / "run_test"
            _write_sample_run(run_dir)
            result = generate_run_figures(run_dir)
            assert len(result.figure_paths) == 6
            assert (run_dir / "figures" / "manifest.json").is_file()
            assert (run_dir / "figures" / "price_vs_booking.png").is_file()
        finally:
            shutil.rmtree(tmpdir)

    def test_generate_all_figures_skip_sweeps(self):
        tmpdir = Path(tempfile.mkdtemp(prefix="fig_all_"))
        try:
            run_dir = Path(tmpdir) / "run_ref"
            fig_dir = Path(tmpdir) / "figures"
            _write_sample_run(run_dir)
            result = generate_all_figures(
                output_dir=fig_dir,
                reference_run_dir=run_dir,
                run_sweeps=False,
            )
            assert len(result.figure_paths) >= 5
            assert (fig_dir / "price_vs_booking.png").is_file()
            assert (fig_dir.parent / "scenario_runs.md").is_file()
        finally:
            shutil.rmtree(tmpdir)


class TestEinFigurensatzEntstehtGanzOderGarNicht:
    """Ein abgebrochener Lauf hinterlässt keinen stillen Teilstand (P1.2).

    **Der Befund war doppelt.** `generate_run_figures` schrieb die PNGs direkt an
    ihren Platz und das Manifest danach: Brach ein Plot ab, lagen die vorher
    fertigen Bilder da — und ein **altes** Manifest aus einem früheren Lauf blieb
    daneben liegen und passte nicht mehr dazu. Die Ergebnisansicht zeigte dann
    einen Satz aus neuen und alten Bildern, ohne dass irgendwo stand, dass er
    keiner ist.

    Gemessen wird deshalb nicht «es gab einen Fehler», sondern: **Was liegt
    danach auf der Platte?**
    """

    def _abzug(self, figures_dir: Path) -> dict[str, bytes]:
        """Jede Datei mit ihrem Inhalt — ein Vergleich, der auch Teilstände sieht."""

        return {p.name: p.read_bytes() for p in sorted(figures_dir.iterdir()) if p.is_file()}

    def test_a_failing_plot_leaves_the_previous_set_untouched(self, monkeypatch):
        """**Mit geänderten Daten dazwischen, und das ist der Punkt.**

        Die erste Fassung dieses Tests rechnete zweimal dieselben Daten und war
        grün, ohne dass am Code etwas repariert war: Die Plots sind
        deterministisch, also überschrieben die ersten beiden Bilder sich selbst
        mit identischem Inhalt — ein Byte-Vergleich sah nichts. Der Teilstand
        wird erst sichtbar, wenn das Neue anders aussieht als das Alte. Genau so
        entsteht er auch in Wirklichkeit: Ein zweiter Lauf schreibt in dasselbe
        Verzeichnis.
        """

        from src.reporting.figure_generator import run_figures as modul

        tmpdir = Path(tempfile.mkdtemp(prefix="fig_atom_"))
        try:
            run_dir = tmpdir / "run_test"
            _write_sample_run(run_dir)

            generate_run_figures(run_dir)
            vorher = self._abzug(run_dir / "figures")
            assert len(vorher) >= 2, "Der erste Durchlauf hat gar nichts geschrieben"

            _write_sample_run(run_dir, booking_start=0.2, price_start=300.0)

            def _scheitert(*args, **kwargs):
                raise RuntimeError("Plot abgebrochen")

            # Der dritte von sechs: Zwei Bilder sind fertig, wenn es knallt.
            monkeypatch.setattr(modul, "plot_system_dynamics", _scheitert)

            with pytest.raises(RuntimeError):
                generate_run_figures(run_dir)

            nachher = self._abzug(run_dir / "figures")

            assert nachher == vorher, (
                "Der abgebrochene Lauf hat den vorhandenen Figurensatz verändert.\n"
                f"  vorher:  {sorted(vorher)}\n"
                f"  nachher: {sorted(nachher)}\n"
                "Ein Satz entsteht ganz oder gar nicht — sonst zeigt die "
                "Ergebnisansicht neue und alte Bilder nebeneinander."
            )
        finally:
            shutil.rmtree(tmpdir)

    def test_a_failed_run_leaves_a_visible_remnant(self, monkeypatch):
        """Was nicht fertig wurde, verschwindet nicht spurlos.

        Ein liegengebliebenes Werkstattverzeichnis ist ein **sichtbarer**
        Fehlerrest. Das ist der Unterschied zu vorher: Damals sah ein halber Satz
        aus wie ein ganzer.
        """

        from src.reporting.figure_generator import run_figures as modul

        tmpdir = Path(tempfile.mkdtemp(prefix="fig_rest_"))
        try:
            run_dir = tmpdir / "run_test"
            _write_sample_run(run_dir)

            monkeypatch.setattr(
                modul,
                "plot_system_dynamics",
                lambda *a, **k: (_ for _ in ()).throw(RuntimeError("Plot abgebrochen")),
            )
            with pytest.raises(RuntimeError):
                generate_run_figures(run_dir)

            assert (run_dir / modul.WERKSTATT).is_dir(), (
                "Kein Rest vom abgebrochenen Lauf — dann lässt sich hinterher "
                "nicht sehen, dass einer abgebrochen ist."
            )
            assert not (
                run_dir / "figures"
            ).exists(), "Es gab vorher keinen Satz — dann darf danach auch keiner dastehen."
        finally:
            shutil.rmtree(tmpdir)

    def test_a_leftover_workshop_does_not_block_the_next_run(self, monkeypatch):
        """Nach einem Abbruch muss der nächste Lauf wieder durchkommen."""

        from src.reporting.figure_generator import run_figures as modul

        tmpdir = Path(tempfile.mkdtemp(prefix="fig_wieder_"))
        try:
            run_dir = tmpdir / "run_test"
            _write_sample_run(run_dir)

            monkeypatch.setattr(
                modul,
                "plot_system_dynamics",
                lambda *a, **k: (_ for _ in ()).throw(RuntimeError("Plot abgebrochen")),
            )
            with pytest.raises(RuntimeError):
                generate_run_figures(run_dir)
            monkeypatch.undo()

            generate_run_figures(run_dir)

            manifest = json.loads((run_dir / "figures" / "manifest.json").read_text("utf-8"))
            assert manifest["figures"], "Der zweite Lauf hat kein Manifest geschrieben"
            assert not (
                run_dir / modul.WERKSTATT
            ).exists(), "Die Werkstatt bleibt nach einem geglückten Lauf stehen"
        finally:
            shutil.rmtree(tmpdir)

    def test_every_named_figure_really_exists(self):
        """Das Manifest nennt nichts, was nicht dasteht."""

        tmpdir = Path(tempfile.mkdtemp(prefix="fig_voll_"))
        try:
            run_dir = tmpdir / "run_test"
            _write_sample_run(run_dir)
            generate_run_figures(run_dir)

            figures_dir = run_dir / "figures"
            manifest = json.loads((figures_dir / "manifest.json").read_text("utf-8"))
            fehlend = [
                name for name in manifest["figures"].values() if not (figures_dir / name).is_file()
            ]

            assert not fehlend, f"Das Manifest nennt Dateien, die es nicht gibt: {fehlend}"
        finally:
            shutil.rmtree(tmpdir)
