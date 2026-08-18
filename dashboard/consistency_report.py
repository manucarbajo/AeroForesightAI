"""Cross-checks generated run artifacts against each other for QA/debugging."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from dashboard.run_browser import load_event_log, load_price_series, load_tick_mechanics

CheckStatus = Literal["ok", "warn", "fail"]


@dataclass(frozen=True)
class ConsistencyCheck:
    check_id: str
    title: str
    status: CheckStatus
    detail: str


def run_consistency_checks(run_dir: Path | str) -> list[ConsistencyCheck]:
    """Cross-check generated artefacts for presentation and debugging."""

    base = Path(run_dir)
    checks: list[ConsistencyCheck] = []

    required_files = [
        "run_metadata.json",
        "event_log.json",
        "price_history.json",
        "tick_mechanics.json",
        "final_narrative.md",
    ]
    missing = [name for name in required_files if not (base / name).is_file()]
    checks.append(
        ConsistencyCheck(
            check_id="required_files",
            title="Pflicht-Artefakte vorhanden",
            status="fail" if missing else "ok",
            detail=(
                "Fehlt: " + ", ".join(missing)
                if missing
                else "Alle Kern-Dateien liegen im Run-Ordner."
            ),
        )
    )

    ticks = load_tick_mechanics(base)
    prices = load_price_series(base)
    events = load_event_log(base)

    price_by_tick = {
        int(row["round_number"]): float(row["price"])
        for row in prices
        if row.get("round_number") is not None and row.get("price") is not None
    }

    price_mismatches: list[str] = []
    for row in ticks:
        tick = int(row.get("tick", -1))
        expected = row.get("market_price_after_feedback_eur")
        actual = price_by_tick.get(tick)
        if expected is None or actual is None:
            continue
        if abs(float(expected) - float(actual)) > 0.05:
            price_mismatches.append(
                f"Tick {tick}: mechanics={expected:.2f}, price_history={actual:.2f}"
            )

    checks.append(
        ConsistencyCheck(
            check_id="price_alignment",
            title="Ticketpreis: tick_mechanics ↔ price_history",
            status="fail" if price_mismatches else "ok",
            detail=(
                "; ".join(price_mismatches[:5]) if price_mismatches else "Preise stimmen überein."
            ),
        )
    )

    delta_events = [event for event in events if "[delta:" in str(event.get("description", ""))]
    checks.append(
        ConsistencyCheck(
            check_id="delta_events",
            title="Python-Delta-Events im event_log",
            status="ok" if delta_events else "warn",
            detail=(
                f"{len(delta_events)} Delta-Events gefunden (source=system/provider/market)."
                if delta_events
                else "Keine [delta:…]-Events — Run evtl. ohne Delta-Events oder ohne Markt-Feedback."
            ),
        )
    )

    booking_delta_ticks = [
        int(row["tick"]) for row in ticks if row.get("booking_rate_delta") not in (None, 0, 0.0)
    ]
    missing_booking_deltas = []
    for tick in booking_delta_ticks:
        has_delta = any(
            event.get("round_number") == tick
            and "[delta:" in str(event.get("description", ""))
            and "booking" in str(event.get("description", "")).lower()
            for event in events
        )
        if not has_delta:
            missing_booking_deltas.append(tick)

    checks.append(
        ConsistencyCheck(
            check_id="booking_delta_events",
            title="Booking-Deltas protokolliert",
            status="warn" if missing_booking_deltas else "ok",
            detail=(
                "Ticks ohne Booking-Delta-Event: " + ", ".join(map(str, missing_booking_deltas[:8]))
                if missing_booking_deltas
                else "Booking-Änderungen sind als Delta-Events sichtbar."
            ),
        )
    )

    checkpoint_dir = base / "checkpoints"
    checkpoint_files = list(checkpoint_dir.rglob("tick_*.json")) if checkpoint_dir.is_dir() else []
    checks.append(
        ConsistencyCheck(
            check_id="checkpoints",
            title="Checkpoints für State Explorer",
            status="ok" if checkpoint_files else "warn",
            detail=(
                f"{len(checkpoint_files)} Checkpoint-Dateien unter checkpoints/."
                if checkpoint_files
                else "Keine Checkpoints — Explorer nutzt nur CSV/JSON-Artefakte."
            ),
        )
    )

    return checks
