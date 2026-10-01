"""Wie Größen, Einheiten, Segmente und Faktoren auf Deutsch heißen — die eine Quelle.

Bis zum 2026-10-01 standen diese Tabellen in `dashboard/config_catalog.py` und
waren damit für Diagramme, Modell-Bereich und Handbuch die eine Quelle — aber
nicht für den Rechenkern, der nicht aus dem Dashboard importieren darf. Der
Bericht eines Laufs (`final_narrative.md`) schrieb deshalb Kennungen
(«price_sensitive», «kapazitaet_index»). Hier stehen sie für beide;
`config_catalog` reicht sie unverändert weiter.
"""

from __future__ import annotations

#: **Die Namen der Systemgrößen — die eine Quelle** für Diagramme, Modell-Bereich
#: und Handbuch (P7.1-U1.5). Bis zum 2026-09-13 standen hier acht von sechzehn;
#: die übrigen erschienen als Kennung (`maintenance_cost_index`), und das
#: Diagramm «Was die Politik bewirkt» benannte **alle** seine Reihen so, weil es
#: die Liste gar nicht benutzte. `tests/test_web_diagrammnamen.py` hält jede
#: Größe aus `configs/properties.json` gegen diese Liste.
PROPERTY_LABELS: dict[str, str] = {
    "carbon_tax_level": "CO₂-Steuer (€/t)",
    "saf_mandate_share": "SAF-Mandat (0–1)",
    "demand_growth_rate": "Nachfragewachstum / Tick",
    "income_index": "Einkommensindex",
    "oil_price_index": "Ölpreis-Index",
    "fuel_price_change": "Treibstoff-Trend / Tick",
    "efuel_subsidy": "E-Fuel-Subvention",
    "bevoelkerungsentwicklung": "Bevölkerung (Personen)",
    "provider_markup": "Anbieter-Marge (€)",
    "ticket_price": "Ticketpreis (€)",
    "kapazitaet_index": "Kapazitätsindex",
    "altersmittel_jahre": "Altersmittel (Jahre)",
    "erneuerungsrate": "Erneuerungsrate / Tick",
    "maintenance_cost_index": "Wartungskostenindex",
    "staff_cost_index": "Personalkostenindex",
    "airport_fee": "Flughafengebühr (€)",
}

#: Einheiten aus `properties.json` — (kurz für Achsentitel, lang für Tabellen).
#: Bis zum 2026-09-13 lebte eine zweite, halbe Fassung im Handbuch
#: (`docs_reference.UNIT_LABELS`), und sie sprach noch von «Runde» statt Tick.
EINHEITEN: dict[str, tuple[str, str]] = {
    "eur_per_tonne": ("€/t", "€ je Tonne"),
    "fraction": ("0–1", "Anteil (0–1)"),
    "fraction_per_tick": ("Anteil je Tick", "Anteil je Tick"),
    "share_per_tick": ("Anteil je Tick", "Anteil je Tick"),
    "index": ("Index", "Index (1.0 = Basis)"),
    "eur": ("€", "Euro"),
    "EUR": ("€", "Euro"),
    "persons": ("Personen", "Personen"),
    "years": ("Jahre", "Jahre"),
    "%": ("%", "Prozent"),
}

#: Die Namen der Bevölkerungssegmente — dieselbe Quelle für die Karten im
#: Modell-Bereich und die Linien in «Wer noch fliegt». Vorher entstand der Name
#: an beiden Stellen aus der Kennung («Eco Conscious»).
SEGMENT_NAMEN: dict[str, str] = {
    "business": "Geschäftsreisende",
    "family": "Familien",
    "price_sensitive": "Preisbewusste",
    "eco_conscious": "Umweltbewusste",
    "frequent_flyer": "Vielflieger",
}


#: Die Kurznamen der sieben Faktoren — für die Faktorleiste über der Szene (P7.5-U5.3,
#: von Haiko entschieden am 2026-09-15: eine Reihe, Kurzname und Zustand als Marke).
#: Die langen Namen in `configs/factors.json` («Mobilitaetsbeduerfnis / Nachfrage»)
#: passen bei 1280 px in keinen Chip; gemessen blieben je Chip 72 px. Die Wörter sind
#: die des Domain-Glossars in CLAUDE.md.
FAKTOR_KURZNAMEN: dict[str, str] = {
    "F1": "Nachfrage",
    "F2": "Regulierung",
    "F3": "Technologie",
    "F4": "Wirtschaft",
    "F5": "Alternativen",
    "F6": "Gesellschaft",
    "F7": "Geopolitik",
}


def segment_name(segment_id: str) -> str:
    """Der Name eines Segments — für ein unbekanntes die Kennung in Lesbarform."""

    return SEGMENT_NAMEN.get(segment_id, segment_id.replace("_", " "))
