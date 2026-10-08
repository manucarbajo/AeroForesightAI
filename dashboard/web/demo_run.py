"""Ein Beispieldatensatz für den Fall, dass noch nichts gerechnet wurde.

**Warum das heikel ist.** Invariante 1 sagt: Ein Lauf ohne echte Zahlen darf nie
wie ein vollwertiger aussehen. P0.1 und P0.6 haben genau dafür die Kette aus
`degraded`, `compute_mode` und Warnbanner gebaut. Ein Leitstand, der zur
Auflockerung erfundene Kennzahlen anzeigt, würde das in einem Zug wieder
einreißen.

**Wie es trotzdem geht.** Der Datensatz hier greift nur, wenn `list_runs()`
**leer** ist — es gibt dann keinen echten Lauf, mit dem man ihn verwechseln
könnte. Er trägt eine eigene Signalfarbe (`--demo`), ein Abzeichen in der
Kopfzeile, ein Banner über dem Viewport, und `status.derive` hält den Zustand
`demo` sichtbar, solange er sichtbar ist. Er wird **nie** nach `outputs/`
geschrieben und taucht **nie** in der Run-Liste auf; sobald ein echter Lauf
existiert, ist er weg.

Die Formen sind dieselben, die die echten Lader liefern
(`load_tick_mechanics`, `load_price_series`, `load_event_log`) — jede Ansicht
kennt damit genau eine Form, statt einen Sonderweg für den Demo-Fall.
`tests/test_web_demo.py` vergleicht die Schlüssel gegen ein echtes Artefakt.
"""

from __future__ import annotations

import math
from functools import lru_cache
from typing import Any

from dashboard.web import formate

#: Fester Startwert. Der Demo-Datensatz soll bei jedem Aufruf identisch sein —
#: ein Screenshot von gestern und die Seite von heute zeigen dasselbe.
SEED = 20260828

RUN_ID = "demo"
TICKS = 40
POPULATION = 1000

#: Steht als Kennzeichen in jedem Datensatz, den dieses Modul erzeugt. Wer
#: Demo-Daten weiterreicht, kann sie damit an jeder Stelle erkennen.
MARKER = "is_demo"

LABEL = "Beispieldatensatz (nicht gerechnet)"


def _rng():
    import numpy as np

    return np.random.default_rng(SEED)


def _factor_state(factor: int, tick: int) -> str:
    """Der Zustand eines Faktors im gegebenen Tick.

    Bewusst als Treppenfunktion mit wenigen Wechseln: Ein Deskriptor, der im
    Modell alle drei Ticks kippt, sähe nach Rauschen aus statt nach einer
    Strukturwende.
    """

    kipppunkte = {1: 26, 2: 14, 3: 31, 4: 19, 5: 34, 6: 22, 7: 0}
    grenze = kipppunkte.get(factor, 0)
    return f"F{factor}.2" if grenze and tick >= grenze else f"F{factor}.1"


def factor_states(tick: int) -> dict[str, str]:
    """Die sieben Faktorzustände eines Ticks."""

    return {f"F{index}": _factor_state(index, tick) for index in range(1, 8)}


@lru_cache(maxsize=1)
def tick_mechanics() -> list[dict[str, Any]]:
    """Die Tick-Tabelle — dieselben Schlüssel wie `tick_mechanics.json`."""

    rng = _rng()
    rows: list[dict[str, Any]] = []
    preis = 128.0
    bevoelkerung = POPULATION
    vorherige_rate: float | None = None

    for tick in range(1, TICKS + 1):
        # Eine Abgabe, die in zwei Stufen steigt — der übliche politische
        # Verlauf der ausgelieferten Szenarien, nicht frei erfunden.
        abgabe = 50.0 if tick < 14 else (120.0 if tick < 28 else 200.0)
        kostendruck = 96.0 + abgabe * 0.32 + 6.0 * math.sin(tick / 5.0)
        einkommen = 1.0 + 0.004 * tick

        nachfrage = 1.55 - 0.010 * tick + 0.05 * math.sin(tick / 3.0)
        rate = max(0.18, min(0.82, nachfrage * 0.46 - (preis - 128.0) / 900.0))
        rate = round(float(rate + rng.normal(0.0, 0.006)), 3)

        neuer_preis = kostendruck * 1.22 + (rate - 0.42) * 42.0
        neuer_preis = round(float(neuer_preis), 2)

        zuwachs = int(rng.integers(-4, 9)) if tick > 1 else 0
        neue_bevoelkerung = bevoelkerung + zuwachs

        rows.append(
            {
                "tick": tick,
                "pipeline_order": [
                    "apply_factor_rules",
                    "agent_round (provider/regulator)",
                    "population_booking (uses prior tick market price as reference)",
                    "consumer_narrative",
                    "market_feedback (sets final ticket price)",
                ],
                "scheduled_shocks": (
                    [
                        {
                            "property_id": "carbon_tax_level",
                            "effect_type": "set",
                            "value": abgabe,
                            "unit": "eur_per_tonne",
                        }
                    ]
                    if tick in {1, 14, 28}
                    else []
                ),
                "booking_reference_price_eur": round(preis, 2),
                "market_price_after_feedback_eur": neuer_preis,
                "market_price_delta_eur": round(neuer_preis - preis, 2),
                "booking_rate": rate,
                "prior_booking_rate": vorherige_rate,
                "booking_rate_delta": (
                    None if vorherige_rate is None else round(rate - vorherige_rate, 3)
                ),
                "population": neue_bevoelkerung,
                "population_delta": None if tick == 1 else zuwachs,
                "booked": int(round(rate * neue_bevoelkerung)),
                "carbon_tax_level": abgabe,
                "income_index": round(einkommen, 3),
                "cost_pressure_eur": round(kostendruck, 2),
                "demand_level": round(nachfrage, 3),
                "interpretation": [],
                MARKER: True,
            }
        )
        preis, bevoelkerung, vorherige_rate = neuer_preis, neue_bevoelkerung, rate

    return rows


@lru_cache(maxsize=1)
def price_series() -> list[dict[str, Any]]:
    """Der Preisverlauf — dieselben Schlüssel wie `price_history.json`."""

    return [
        {
            "round_number": row["tick"],
            "agent_id": "market",
            "price": row["market_price_after_feedback_eur"],
            "demand_level": row["demand_level"],
            "booking_rate": row["booking_rate"],
            # `load_factor` steht in echten Laeufen bislang auf 0.0 — der
            # Beispieldatensatz erfindet dafuer keinen Wert.
            "load_factor": 0.0,
            MARKER: True,
        }
        for row in tick_mechanics()
    ]


@lru_cache(maxsize=1)
def event_log() -> list[dict[str, Any]]:
    """Ereignisse — dieselben Schlüssel wie `event_log.json`."""

    ereignisse: list[dict[str, Any]] = []
    for row in tick_mechanics():
        tick = row["tick"]
        ereignisse.append(
            {
                "id": f"demo-market-{tick}",
                "round_number": tick,
                "source_agent": "market",
                "event_type": "market_event",
                "description": (
                    f"Markt: Ticketpreis {formate.euro(row['market_price_after_feedback_eur'])}, "
                    f"Kostendruck {formate.euro(row['cost_pressure_eur'])}, "
                    f"Buchungsrate {formate.prozent(row['booking_rate'])}"
                ),
                "affected_factors": [],
                "timestamp": "",
                MARKER: True,
            }
        )
        if row["scheduled_shocks"]:
            ereignisse.append(
                {
                    "id": f"demo-regulator-{tick}",
                    "round_number": tick,
                    "source_agent": "regulator",
                    "event_type": "policy_event",
                    "description": (f"CO₂-Abgabe auf {row['carbon_tax_level']:.0f} €/t gesetzt."),
                    "affected_factors": ["F2"],
                    "timestamp": "",
                    MARKER: True,
                }
            )
    return ereignisse


@lru_cache(maxsize=1)
def population_frame():
    """Die Individuen je Tick — dieselben Spalten wie `individuals_history.csv`.

    Erzeugt in einem Zug statt je Tick, damit die Ziehung reproduzierbar bleibt:
    ein zweiter Aufruf mit anderer Reihenfolge lieferte sonst andere Zahlen.
    """

    import numpy as np
    import pandas as pd

    rng = np.random.default_rng(SEED + 1)
    anzahl = 240  # weniger als ein echter Lauf: die Szene soll lesbar bleiben

    alter = rng.integers(18, 78, size=anzahl)
    business = rng.random(size=anzahl) < 0.28
    grund_wtp = rng.normal(150.0, 42.0, size=anzahl) + business * 70.0
    bewusstsein = np.clip(rng.beta(2.2, 2.6, size=anzahl), 0.0, 1.0)
    preissensitiv = np.clip(rng.beta(2.5, 2.0, size=anzahl), 0.0, 1.0)
    substitution = np.clip(rng.beta(2.0, 3.0, size=anzahl), 0.0, 1.0)

    zeilen = []
    for row in tick_mechanics():
        tick = row["tick"]
        preis = row["market_price_after_feedback_eur"]
        # Zahlungsbereitschaft wandert leicht mit dem Einkommensindex.
        wtp = grund_wtp * row["income_index"]
        gebucht = wtp > preis * (0.75 + 0.45 * preissensitiv)
        zeilen.append(
            pd.DataFrame(
                {
                    "id": [f"demo-{i:04d}" for i in range(anzahl)],
                    "tick": tick,
                    "age": alter,
                    "wtp_eur": np.round(wtp, 2),
                    "environmental_awareness": np.round(bewusstsein, 3),
                    "price_sensitivity": np.round(preissensitiv, 3),
                    "substitution_readiness": np.round(substitution, 3),
                    "booked": gebucht,
                    "business": business,
                }
            )
        )
    return pd.concat(zeilen, ignore_index=True)


def metadata() -> dict[str, Any]:
    """Was der Kopf eines Laufs sagen würde — hier mit ehrlichem Inhalt."""

    return {
        "run_id": RUN_ID,
        "timestamp": "—",
        "ticks_completed": TICKS,
        "ticks_max": TICKS,
        "total_events": len(event_log()),
        "model": "keins",
        "market_enabled": True,
        "degraded": False,
        "llm_incident_count": 0,
        MARKER: True,
    }


def notice() -> str:
    """Der Satz, der über dem Viewport steht, solange Demo-Daten gezeigt werden."""

    return (
        "**Dies sind keine Simulationsergebnisse.** Unter `outputs/` liegt noch kein "
        "gerechneter Lauf, deshalb zeigt der Leitstand einen Beispieldatensatz — damit "
        "die Ansicht nicht leer bleibt. Sobald Sie links einen Lauf starten, ist er weg. "
        "Nichts davon wird gespeichert."
    )
