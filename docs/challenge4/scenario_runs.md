# Szenario-Läufe und Figures (M10)

Automatisch erzeugte Visualisierungen für Strategic Foresight / Challenge 4.

## Foresight-Szenarien (deterministisch, 50 Ticks)

| Szenario | ID | Consistency |
| --- | --- | --- |
| Business as Usual (A1+B1) | `business_as_usual` | 0.573 |
| CO₂-Verzögerung | `co2_delayed` | 0.443 |
| Freiwillige Wende (A2+B2) | `freiwillige_wende` | 0.339 |
| Transformationskonflikt (B2 vs A1) | `transformation_conflict` | 0.482 |

## Referenzlauf (Referenz (Standard-Config))

- Ticks: 40
- Booking: 46.4% → 59.3%

## Figures

- **Szenario-Vergleich Booking:** `figures\scenario_comparison_booking.png`
- **Szenario-Vergleich Preis:** `figures\scenario_comparison_price.png`
- **CIB Consistency Scores:** `figures\scenario_cib_scores.png`
- **Preis vs. Booking:** `figures\price_vs_booking.png`
- **CO₂-Policy-Shock:** `figures\policy_shock_co2_booking.png`
- **Systemdynamik:** `figures\system_dynamics.png`
- **Faktor-Zustände:** `figures\factor_states.png`
- **Alterssegmente:** `figures\age_segment_booking.png`

## Erzeugung

```powershell
python -m src.figure_generator
```
