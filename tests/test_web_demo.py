"""Der Beispieldatensatz des Leitstands (P1.5).

Er ist die heikelste Zutat dieses Pakets. Invariante 1 sagt: Ein Lauf ohne echte
Zahlen darf nie wie ein vollwertiger aussehen — P0.1 und P0.6 haben dafür die
ganze Kette aus `degraded`, `compute_mode` und Warnbanner gebaut. Ein Leitstand
mit erfundenen Kennzahlen risse das in einem Zug wieder ein.

Vier Zusagen halten ihn im Zaum, und alle vier stehen hier:

1. Er greift **nur**, wenn es keinen echten Lauf gibt.
2. Er ist als Demo **markiert** — im Datensatz, in der Zustandsanzeige und im
   Banner über dem Viewport.
3. Er trägt **dieselben Schlüssel** wie ein echtes Artefakt. Nicht aus
   Ordnungsliebe: Sonst bräuchte jede Ansicht einen zweiten Weg, und der zweite
   Weg ist der, den niemand pflegt.
4. Er **schreibt nichts** — weder nach `outputs/` noch in die Run-Liste.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from dashboard.web import demo_run, run_data, status
from dashboard.web.app import scene_block
from dashboard.web.views import telemetry

REPO_ROOT = Path(__file__).resolve().parents[1]


def _text(component) -> str:
    return str(component)


def _ein_echtes_artefakt(name: str):
    """Ein beliebiges echtes Artefakt dieses Namens aus `outputs/`.

    Der Vergleich läuft gegen die Wirklichkeit, nicht gegen eine im Test
    gepflegte Schlüsselliste — sonst prüfte er nur, ob zwei Kopien derselben
    Annahme übereinstimmen.
    """

    for path in sorted((REPO_ROOT / "outputs").rglob(name)):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        rows = payload.get("ticks") if isinstance(payload, dict) else payload
        if isinstance(rows, list) and rows:
            return rows
    return None


# --- 1. Er greift nur im Leerfall ------------------------------------------


class TestErGreiftNurOhneEchtenLauf:
    def test_no_selection_means_demo(self):
        assert run_data.load(None).is_demo

    def test_a_selection_pointing_nowhere_falls_back_to_demo(self, tmp_path):
        """Ein gelöschtes Run-Verzeichnis ist kein Grund für eine leere Seite."""

        verschwunden = {"run_id": "weg", "run_dir": str(tmp_path / "gibt-es-nicht")}

        assert run_data.load(verschwunden).is_demo

    def test_the_population_cache_notices_a_rewritten_file(self, tmp_path):
        """Ein neu gerechneter Lauf gleichen Namens darf nicht alte Punkte zeigen.

        Die History wird gecacht, weil die Szene bei jedem Schritt der
        Zeitleiste neu entsteht. Der Schlüssel trägt Größe und Änderungszeit
        mit — sonst bliebe der erste gelesene Stand für immer stehen.
        """

        run_dir = tmp_path / "run_echt"
        run_dir.mkdir()
        (run_dir / "run_metadata.json").write_text("{}", encoding="utf-8")
        kopf = (
            "id,tick,age,wtp_eur,environmental_awareness,price_sensitivity,"
            "substitution_readiness,booked,business\n"
        )
        erste = "a,1,30,100,0.5,0.5,0.5,True,False\n"
        zweite = "b,1,40,120,0.6,0.4,0.3,False,True\n"

        history = run_dir / "individuals_history.csv"
        history.write_text(kopf + erste, encoding="utf-8")
        daten = run_data.load({"run_id": "run_echt", "run_dir": str(run_dir)})

        assert len(run_data.population(daten)) == 1

        history.write_text(kopf + erste + zweite, encoding="utf-8")

        assert len(run_data.population(daten)) == 2, "der Cache hat die Änderung verschluckt"

    def test_a_real_run_wins(self, tmp_path):
        run_dir = tmp_path / "run_echt"
        run_dir.mkdir()
        (run_dir / "run_metadata.json").write_text(
            json.dumps({"run_id": "run_echt", "ticks_completed": 3}), encoding="utf-8"
        )
        (run_dir / "tick_mechanics.json").write_text(
            json.dumps({"ticks": [{"tick": 1, "booking_rate": 0.5}]}), encoding="utf-8"
        )

        geladen = run_data.load({"run_id": "run_echt", "run_dir": str(run_dir)})

        assert not geladen.is_demo
        assert geladen.max_tick == 1


# --- 2. Er ist überall als Demo erkennbar -----------------------------------


class TestErIstUeberallMarkiert:
    def test_every_row_carries_the_marker(self):
        for row in demo_run.tick_mechanics():
            assert row[demo_run.MARKER] is True
        for row in demo_run.price_series():
            assert row[demo_run.MARKER] is True
        for row in demo_run.event_log():
            assert row[demo_run.MARKER] is True

    def test_the_status_says_demo(self):
        zustand = status.derive(running=False, demo=True, degraded=False)

        assert zustand.tone == status.DEMO
        assert zustand.is_demo
        assert "keine Simulationsergebnisse" not in zustand.label  # das Label bleibt kurz
        assert "Beispieldatensatz" in zustand.detail

    def test_a_running_simulation_outranks_the_demo_state(self):
        """Was sich von selbst ändert, schlägt alles andere."""

        assert status.derive(running=True, demo=True, degraded=True).tone == status.RUNNING

    def test_the_viewport_carries_the_notice_above_the_scene(self):
        gerendert = _text(scene_block(run_data.demo(), 1))

        assert "keine Simulationsergebnisse" in gerendert
        assert "af-alert--demo" in gerendert

    def test_a_real_run_gets_no_notice(self, tmp_path):
        run_dir = tmp_path / "run_echt"
        run_dir.mkdir()
        (run_dir / "run_metadata.json").write_text("{}", encoding="utf-8")
        daten = run_data.load({"run_id": "run_echt", "run_dir": str(run_dir)})

        assert "af-alert--demo" not in _text(scene_block(daten, 1))


# --- 3. Dieselbe Form wie ein echtes Artefakt -------------------------------


class TestDieselbeFormWieEinEchterLauf:
    """Eine Ansicht darf keinen zweiten Weg für den Demo-Fall brauchen."""

    def test_tick_rows_carry_every_key_a_real_run_has(self):
        echt = _ein_echtes_artefakt("tick_mechanics.json")
        if echt is None:
            pytest.skip("Kein echtes `tick_mechanics.json` unter `outputs/`.")

        fehlend = set(echt[0]) - set(demo_run.tick_mechanics()[0])

        assert not fehlend, f"Im Demo-Datensatz fehlen: {sorted(fehlend)}"

    def test_price_rows_carry_every_key_a_real_run_has(self):
        echt = _ein_echtes_artefakt("price_history.json")
        if echt is None:
            pytest.skip("Kein echtes `price_history.json` unter `outputs/`.")

        fehlend = set(echt[0]) - set(demo_run.price_series()[0])

        assert not fehlend, f"Im Demo-Datensatz fehlen: {sorted(fehlend)}"

    def test_event_rows_carry_every_key_a_real_run_has(self):
        echt = _ein_echtes_artefakt("event_log.json")
        if echt is None:
            pytest.skip("Kein echtes `event_log.json` unter `outputs/`.")

        fehlend = set(echt[0]) - set(demo_run.event_log()[0])

        assert not fehlend, f"Im Demo-Datensatz fehlen: {sorted(fehlend)}"

    def test_the_population_frame_has_the_columns_the_scene_reads(self):
        frame = run_data.population(run_data.demo())

        assert {"tick", "wtp_eur", "environmental_awareness", "booked"} <= set(frame.columns)

    def test_every_tick_has_seven_factor_states(self):
        for tick in (1, 20, demo_run.TICKS):
            zustaende = run_data.demo().factors_at(tick)
            assert set(zustaende) == {f"F{i}" for i in range(1, 8)}

    def test_the_telemetry_renders_from_it(self):
        gerendert = _text(telemetry.render(run_data.demo(), 12))

        assert "Buchungsrate" in gerendert
        assert "Ticketpreis" in gerendert


# --- 4. Er ist reproduzierbar und schreibt nichts ---------------------------


class TestErIstReproduzierbarUndFolgenlos:
    def test_two_calls_give_the_same_numbers(self):
        """Ein Screenshot von gestern und die Seite von heute zeigen dasselbe."""

        demo_run.tick_mechanics.cache_clear()
        erste = [row["booking_rate"] for row in demo_run.tick_mechanics()]
        demo_run.tick_mechanics.cache_clear()
        zweite = [row["booking_rate"] for row in demo_run.tick_mechanics()]

        assert erste == zweite

    def test_it_never_appears_in_the_run_list(self):
        from dashboard.run_browser import list_runs

        assert demo_run.RUN_ID not in {run.run_id for run in list_runs()}

    def test_it_writes_no_file(self, tmp_path, monkeypatch):
        """Kontrolle am Verhalten, nicht am Code: nach dem Aufbau ist nichts da."""

        monkeypatch.chdir(tmp_path)
        demo_run.tick_mechanics.cache_clear()
        demo_run.population_frame.cache_clear()
        run_data.demo()
        run_data.population(run_data.demo())

        assert list(tmp_path.iterdir()) == []

    def test_its_metadata_does_not_claim_a_model(self):
        """«Modell llama3.2» neben erfundenen Zahlen wäre die schlimmste Zeile."""

        assert demo_run.metadata()["model"] == "keins"
        assert demo_run.metadata()[demo_run.MARKER] is True
