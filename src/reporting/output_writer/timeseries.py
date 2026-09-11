"""CSV timeseries writers: population, factors, properties, price, rounds, age groups."""

import json
from pathlib import Path
from typing import List

from src.models.event_models import PriceHistoryEntry
from src.models.population_models import Individual
from src.models.property_models import BookingModelConfig
from src.population.population_sampler import erschwinglichkeitsgrenze
from src.reporting.output_writer.paths import ensure_output_dir, resolve_output_path


def _write_csv(target_path: Path, rows: list[dict]) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    columns = list(rows[0].keys())
    lines = [",".join(columns)]
    for row in rows:
        lines.append(",".join(str(row.get(column, "")) for column in columns))
    with open(target_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


def save_population_timeseries(
    population_stats: list[dict],
    filename: str = "timeseries/population.csv",
    *,
    run_dir: Path | None = None,
) -> str | None:
    """Save per-tick segment booking rates derived from population_stats."""

    if not population_stats:
        return None

    rows: list[dict] = []
    for tick_stats in population_stats:
        tick = tick_stats.get("round_number")
        for segment_id, segment in tick_stats.get("segments", {}).items():
            rows.append(
                {
                    "tick": tick,
                    "segment_id": segment_id,
                    "total_individuals": segment.get("total_individuals", 0),
                    "booked_individuals": segment.get("booked_individuals", 0),
                    "booking_rate": segment.get("booking_rate", 0.0),
                    "avg_income_factor": segment.get("avg_income_factor", 1.0),
                }
            )

    if not rows:
        return None

    if run_dir is not None:
        target_path = run_dir / filename
    else:
        target_path = Path(resolve_output_path(filename, run_dir=run_dir))

    _write_csv(target_path, rows)
    return str(target_path)


def save_population_individuals(
    individuals: list,
    filename: str = "population.csv",
    *,
    run_dir: Path | None = None,
) -> str | None:
    """Save final persistent individuals (age, labels, WTP, booking)."""

    if not individuals:
        return None

    rows: list[dict] = []
    for person in individuals:
        data = person.model_dump() if hasattr(person, "model_dump") else person
        row = {
            "id": data.get("id"),
            "age": data.get("age"),
            "wtp_eur": data.get("wtp_eur"),
            "environmental_awareness": data.get("environmental_awareness"),
            "substitution_readiness": data.get("substitution_readiness"),
            "price_sensitivity": data.get("price_sensitivity"),
            "income_factor": data.get("income_factor", 1.0),
            "saturation_level": data.get("saturation_level", 0.0),
            "booked": data.get("booked"),
            "last_booked_tick": data.get("last_booked_tick"),
        }
        for label_id, active in (data.get("labels") or {}).items():
            row[label_id] = active
        rows.append(row)

    if run_dir is not None:
        target_path = run_dir / filename
    else:
        target_path = Path(resolve_output_path(filename, run_dir=run_dir))

    _write_csv(target_path, rows)
    return str(target_path)


def append_individuals_history(
    tick: int,
    individuals: list,
    filename: str = "individuals_history.csv",
    *,
    koeffizienten: BookingModelConfig,
    run_dir: Path | None = None,
) -> str | None:
    """Append individual states for a single tick to the history CSV.

    **`erschwinglichkeitsgrenze_eur` seit P5.2 (2026-09-11):** der höchste
    Ticketpreis, den die Person überhaupt bezahlen kann — aus derselben Funktion,
    mit der `booking_probability` rechnet. Die Dash-App zeigt ihn im «Surplus
    Pulse»; eine zweite Formel dort war der Fehler der abgelösten Streamlit-Ansicht.
    *koeffizienten* ist deshalb Pflicht und hat keine Vorgabe.
    """
    if not individuals:
        return None

    rows: list[dict] = []
    for person in individuals:
        data = person.model_dump() if hasattr(person, "model_dump") else person
        row = {
            "tick": tick,
            "id": data.get("id"),
            "age": data.get("age"),
            "wtp_eur": data.get("wtp_eur"),
            "environmental_awareness": data.get("environmental_awareness"),
            "substitution_readiness": data.get("substitution_readiness"),
            "price_sensitivity": data.get("price_sensitivity"),
            "income_factor": data.get("income_factor", 1.0),
            "erschwinglichkeitsgrenze_eur": round(
                erschwinglichkeitsgrenze(
                    person if isinstance(person, Individual) else Individual.model_validate(data),
                    koeffizienten=koeffizienten,
                ),
                2,
            ),
            "saturation_level": data.get("saturation_level", 0.0),
            "booked": data.get("booked"),
            "last_booked_tick": data.get("last_booked_tick"),
        }
        for label_id, active in (data.get("labels") or {}).items():
            row[label_id] = active
        rows.append(row)

    if run_dir is not None:
        target_path = run_dir / filename
    else:
        target_path = Path(resolve_output_path(filename, run_dir=run_dir))

    target_path.parent.mkdir(parents=True, exist_ok=True)
    columns = list(rows[0].keys())

    file_exists = target_path.is_file()
    lines = []
    if not file_exists:
        lines.append(",".join(columns))

    for row in rows:
        lines.append(",".join(str(row.get(column, "")) for column in columns))

    with open(target_path, "a", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")

    return str(target_path)


def save_factors_timeseries(
    rows: list[dict],
    filename: str = "timeseries/factors.csv",
    *,
    output_subdir: str | Path | None = None,
    run_dir: Path | None = None,
) -> str | None:
    """Save per-tick factor descriptor states as CSV (M5)."""

    if not rows:
        return None

    ensure_output_dir()
    if run_dir is not None:
        target_path = run_dir / filename
    else:
        target_path = Path(resolve_output_path(filename, output_subdir, run_dir=run_dir))

    _write_csv(target_path, rows)
    return str(target_path)


def save_properties_timeseries(
    rows: list[dict],
    filename: str = "timeseries/properties.csv",
    *,
    output_subdir: str | Path | None = None,
    run_dir: Path | None = None,
) -> str | None:
    """Save per-tick system property values as CSV."""

    if not rows:
        return None

    ensure_output_dir()
    if run_dir is not None:
        target_path = run_dir / filename
    else:
        target_path = Path(resolve_output_path(filename, output_subdir, run_dir=run_dir))

    _write_csv(target_path, rows)
    return str(target_path)


def save_price_history(
    price_entries: List[PriceHistoryEntry],
    filename: str = "price_history.json",
    *,
    output_subdir: str | Path | None = None,
    run_dir: Path | None = None,
) -> str:
    """
    Speichert die Preis-Historie als JSON.
        price_entries: Liste von PriceHistoryEntry-Objekten
        Default Name der Ausgabedatei: price_history.json

    Returns:
        Pfad zur gespeicherten Datei
    """
    ensure_output_dir()
    filepath = resolve_output_path(filename, output_subdir, run_dir=run_dir)
    price_data = [entry.model_dump() for entry in price_entries]
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(price_data, f, indent=2, ensure_ascii=False)
    return filepath


def save_round_history(
    round_results: List,
    filename: str = "round_history.json",
    *,
    output_subdir: str | Path | None = None,
    run_dir: Path | None = None,
) -> str:
    """
    Speichert die Rundenhistorie als JSON.
        round_results: Liste von RoundResult-Objekten
        Default Name der Ausgabedatei: round_history.json
    """
    ensure_output_dir()
    filepath = resolve_output_path(filename, output_subdir, run_dir=run_dir)

    round_data = [round_result.model_dump() for round_result in round_results]

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(round_data, f, indent=2, ensure_ascii=False)

    return filepath


def save_segment_analysis(
    round_results: List,
    filename: str = "segment_analysis.json",
    *,
    output_subdir: str | Path | None = None,
    run_dir: Path | None = None,
) -> str:
    """
    Speichert die segmentspezifischen Analysen aller Agenten als JSON.
        round_results: Liste von RoundResult-Objekten
        Default Name der Ausgabedatei: segment_analysis.json
    """
    ensure_output_dir()
    filepath = resolve_output_path(filename, output_subdir, run_dir=run_dir)

    rounds: dict = {}
    for round_result in round_results:
        round_number = round_result.round_number
        if round_number not in rounds:
            rounds[round_number] = {"tick": round_number, "agents": {}}
        for response in round_result.agent_responses:
            rounds[round_number]["agents"][response.agent_id] = {
                "reasoning": response.reasoning,
                "actions": response.actions,
                "segment_analysis": response.segment_analysis,
            }

    segment_data = list(rounds.values())

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(segment_data, f, indent=2, ensure_ascii=False)

    return filepath


def save_age_property_csv(
    population_stats: list[dict],
    filename: str = "timeseries/age_property.csv",
    *,
    run_dir: Path | None = None,
) -> str | None:
    """Save per-tick age group stats."""

    if not population_stats:
        return None

    rows: list[dict] = []
    for tick_stats in population_stats:
        tick = tick_stats.get("round_number")
        for age_group, group_stats in tick_stats.get("age_groups", {}).items():
            rows.append(
                {
                    "tick": tick,
                    "age_group": age_group,
                    "total_individuals": group_stats.get("total_individuals", 0),
                    "booked_individuals": group_stats.get("booked_individuals", 0),
                    "booking_rate": group_stats.get("booking_rate", 0.0),
                    "avg_wtp": group_stats.get("avg_wtp", 0.0),
                    "avg_income_factor": group_stats.get("avg_income_factor", 1.0),
                    "avg_awareness": group_stats.get("avg_awareness", 0.0),
                }
            )

    if not rows:
        return None

    if run_dir is not None:
        target_path = run_dir / filename
    else:
        target_path = Path(resolve_output_path(filename, run_dir=run_dir))

    _write_csv(target_path, rows)
    return str(target_path)
