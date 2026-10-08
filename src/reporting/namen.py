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
#: Die langen Namen in `configs/factors.json` («Mobilitätsbedürfnis / Nachfrage»)
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


#: Die Merkmale einer simulierten Person — für Regeln, die die Bevölkerung
#: verschieben (`shift_rules`). Dieselben Wörter wie in Legende und Hover der
#: Animation.
MERKMAL_NAMEN: dict[str, str] = {
    "price_sensitivity": "Preisempfindlichkeit",
    "environmental_awareness": "Umweltbewusstsein",
    "income_factor": "Einkommensfaktor",
    "substitution_readiness": "Bahnbereitschaft",
    "wtp_eur": "Zahlungsbereitschaft",
    "saturation_level": "Sättigung",
    "age": "Alter",
}


def groesse_name(property_id: str) -> str:
    """Der Name einer Systemgröße für einen Satz — ohne die Einheit in Klammern.

    `PROPERTY_LABELS` ist für Achsen gebaut («CO₂-Steuer (€/t)»); in einem Satz
    steht die Einheit hinter der Zahl. Eine unbekannte Größe behält ihre Kennung.
    """

    name = PROPERTY_LABELS.get(property_id, property_id)
    for zusatz in (" / Tick",):
        name = name.removesuffix(zusatz)
    if name.endswith(")") and " (" in name:
        name = name[: name.rindex(" (")]
    return name


def einheit_kurz(einheit: str) -> str:
    """Die kurze Einheit hinter einer Zahl — leer, wo sie nichts sagt (Index, Anteil)."""

    kurz = EINHEITEN.get(einheit, ("", ""))[0]
    return "" if kurz in ("Index", "0–1", "Anteil je Tick") else kurz


def zahl(wert: float, stellen: int | None = None) -> str:
    """Eine Zahl mit Dezimalkomma; ohne `stellen` so knapp wie möglich (`:g`)."""

    text = f"{wert:g}" if stellen is None else f"{wert:.{stellen}f}"
    return text.replace(".", ",")


def prozent(anteil: float, stellen: int = 1) -> str:
    """Ein Anteil als Prozent: `prozent(0.479)` → `"47,9 %"`."""

    return f"{zahl(anteil * 100, stellen)} %"


def prozentpunkte(delta: float) -> str:
    """Eine Veränderung eines Anteils: `prozentpunkte(-0.114)` → `"−11,4 Prozentpunkte"`."""

    text = zahl(abs(delta) * 100, 1)
    return f"{'+' if delta >= 0 else '−'}{text} Prozentpunkte"
