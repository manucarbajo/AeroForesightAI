"""Klartext zu jedem Parameter — an einer Stelle, zum Lesen am Stück.

Die Oberfläche richtet sich an Anwender, nicht an Modellbauer. Deshalb gilt
für jeden Eintrag hier:

- **Beschriftung** in der Sprache der Sache (Luftverkehr, Preisbildung,
  Nachfrage), nicht in der des Codes. Aus «Logit-Penalty-Faktor» wird
  «Wirkung der Sättigung auf die Buchungsneigung».
- **Wirkung** sagt, was sich am *Ergebnis* ändert, und in welche Richtung.
  Nicht, welche Formel angefasst wird.
- **technisch** nennt den Feldnamen in `configs/*.json`. Er bleibt sichtbar,
  damit sich Oberfläche und Konfigurationsdateien zuordnen lassen — nur
  eben klein und nachrangig.

Die Wirkungsbeschreibungen sind aus `src/market/simulation_functions.py`,
`src/market/market_rules.py` und `src/population/population_sampler.py`
abgeleitet. Ändert sich dort die Mechanik, gehört der Text hier nachgezogen.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Param:
    """Ein Parameter, wie ihn ein Anwender sehen soll."""

    label: str
    effect: str
    technical: str = ""
    unit: str = ""

    def hint(self) -> str:
        """Erklärung plus Einheit und technischer Name als eine Zeile."""

        parts = [self.effect]
        if self.unit:
            parts.append(f"Einheit: {self.unit}.")
        if self.technical:
            parts.append(f"`{self.technical}`")
        return " ".join(parts)


#: Schlüssel ist der Pfad im Draft — derselbe, den das Eingabefeld trägt.
PARAMS: dict[str, Param] = {
    # --- Lauf ------------------------------------------------------------
    "scenario_mode": Param(
        label="Womit starten?",
        effect="«Standard» rechnet mit den Dateien unter `configs/`. «Szenario-Preset» "
        "lädt eine vorbereitete Annahmenwelt. «Eigene Parameter» geht von dem aus, "
        "was Sie in den folgenden Tabs einstellen.",
    ),
    "sweep_id": Param(
        label="Szenario-Preset",
        effect="Ein fertiges Bündel von Annahmen — Faktorlage, Politik, Kosten. "
        "Guter Ausgangspunkt, den Sie danach anpassen können.",
    ),
    "rounds": Param(
        label="Länge des Laufs",
        effect="Anzahl der Simulationsrunden. Ein Tick ist eine Modellrunde und steht "
        "bewusst für keinen Kalenderzeitraum — mehr Ticks heißt nicht «mehr Jahre», "
        "sondern mehr Gelegenheiten für Anpassung und Rückkopplung.",
        unit="Ticks",
    ),
    "run_count": Param(
        label="Wiederholungen",
        effect="Wie oft derselbe Aufbau unabhängig gerechnet wird; der Zufallsstartwert "
        "zählt dabei hoch. Zeigt, wie stabil ein Ergebnis ist — weichen die Läufe stark "
        "voneinander ab, trägt die Aussage nicht.",
    ),
    "run_all_sweeps": Param(
        label="Alle Szenarien nacheinander vergleichen",
        effect="Rechnet jedes hinterlegte Preset einmal durch, ohne Agenten-Dialog. "
        "Ergebnis landet unter `outputs/sweeps/`.",
    ),
    "simulation_name": Param(
        label="Name des Laufs",
        effect="Erscheint in der Run-Liste und im Bericht. Ohne Namen wird die Run-ID "
        "verwendet — bei mehreren Läufen schnell unübersichtlich.",
    ),
    "simulation_description": Param(
        label="Fragestellung",
        effect="Wozu dieser Lauf gerechnet wird. Landet im Bericht und hilft später, "
        "einen Lauf wiederzuerkennen.",
    ),
    # --- Rahmenbedingungen -----------------------------------------------
    "base_price": Param(
        label="Startpreis eines Tickets",
        effect="Preis in der ersten Runde, bevor Kosten und Marktreaktion darauf wirken. "
        "Setzt den Maßstab für den gesamten Preisverlauf.",
        unit="EUR",
        technical="price_model.base_price",
    ),
    "apply_custom_overrides": Param(
        label="Eigene Werte anwenden",
        effect="Aus: Der Lauf nutzt die Dateien unter `configs/` unverändert, alle "
        "Anpassungen in diesem Editor bleiben wirkungslos.",
    ),
    # --- Preisbildung ----------------------------------------------------
    "market_feedback_edit.enabled": Param(
        label="Airline passt den Preis an die Nachfrage an",
        effect="Aus: Der Ticketpreis folgt allein den Kosten. An: Die Airline steuert "
        "den Preis aktiv über die beobachtete Auslastung — das übliche Yield Management.",
        technical="market_feedback.enabled",
    ),
    "market_feedback_edit.target_booking_rate": Param(
        label="Ziel-Auslastung",
        effect="Die Auslastung, auf die die Airline hinsteuert. Liegt die tatsächliche "
        "Buchungsrate darüber, erhöht sie den Preis — darunter senkt sie ihn. Ein "
        "niedrigerer Zielwert führt deshalb tendenziell zu höheren Preisen: Die Airline "
        "zieht schon bei schwächerer Auslastung an.",
        unit="Anteil 0–1",
        technical="market_feedback.target_booking_rate",
    ),
    "market_feedback_edit.marginal_cost_fraction": Param(
        label="Preisuntergrenze",
        effect="Welcher Teil der Stückkosten als echte Grenzkosten gilt. Darunter wird "
        "kein Ticket verkauft, auch bei schwacher Nachfrage nicht. Höher heißt: Die "
        "Airline kann einen Preiskampf weniger weit mitgehen.",
        unit="Anteil der Kosten, 0–1",
        technical="market_feedback.marginal_cost_fraction",
    ),
    "market_feedback_edit.markup_adjustment_per_tick": Param(
        label="Reaktionsstärke je Runde",
        effect="Wie kräftig die Airline nachsteuert, wenn die Auslastung vom Ziel "
        "abweicht. Höher = schnellere, nervösere Preisbewegungen.",
        technical="market_feedback.markup_adjustment_per_tick",
    ),
    "market_feedback_edit.damping": Param(
        label="Dämpfung",
        effect="Bremst diese Reaktion zusätzlich. Niedriger = ruhigere Preisverläufe, "
        "höher = die Airline folgt jeder Schwankung.",
        technical="market_feedback.damping",
    ),
    "market_feedback_edit.max_price_change_fraction": Param(
        label="Maximale Preisänderung je Runde",
        effect="Harter Deckel: So weit darf sich der Ticketpreis in einer Runde "
        "höchstens bewegen, nach oben wie nach unten. Verhindert Preissprünge, die "
        "kein realer Anbieter durchsetzen könnte.",
        unit="Anteil 0–1",
        technical="market_feedback.max_price_change_fraction",
    ),
    "market_feedback_edit.booking_weight": Param(
        label="Kopplung an die tatsächlichen Buchungen",
        effect="Woran sich die Nachfrage der nächsten Runde orientiert. 0 = allein am "
        "Wachstumstrend, 1 = allein an den beobachteten Buchungen. Höher macht das "
        "Modell reaktiver, aber auch schwankungsanfälliger.",
        unit="Anteil 0–1",
        technical="market_feedback.booking_weight",
    ),
    # --- Sättigung -------------------------------------------------------
    "saturation_edit.booking_increase": Param(
        label="Sättigung nach einer Buchung",
        effect="Wie stark eine gebuchte Reise den Wunsch nach der nächsten dämpft. "
        "1.0 heißt: Wer einmal gebucht hat, fällt vorerst ganz als Nachfrager aus. "
        "0 heißt: Eine Buchung ändert nichts.",
        unit="Anteil 0–1",
        technical="saturation.booking_increase",
    ),
    "saturation_edit.utility_penalty_factor": Param(
        label="Wirkung der Sättigung auf die Buchungsneigung",
        effect="Wie stark sich aufgebaute Sättigung in der Kaufentscheidung "
        "niederschlägt. Höher = gesättigte Personen buchen deutlich seltener, selbst "
        "wenn der Preis stimmt.",
        technical="saturation.utility_penalty_factor",
    ),
    # --- Segmente --------------------------------------------------------
    "segment.prevalence": Param(
        label="Anteil an der Bevölkerung",
        effect="Wie viele der simulierten Personen zu diesem Segment gehören. "
        "Die Anteile sind unabhängig — eine Person kann mehreren Segmenten angehören.",
        unit="Anteil 0–1",
    ),
    "segment.saturation_decay": Param(
        label="Erholung je Runde",
        effect="Wie schnell die Sättigung wieder abgebaut wird. 0 = wer gebucht hat, "
        "kommt nie zurück. 1 = schon in der nächsten Runde wieder voll buchbereit.",
        unit="Anteil 0–1",
    ),
    "segment.wtp_multiplier": Param(
        label="Zahlungsbereitschaft",
        effect="Faktor auf die Zahlungsbereitschaft dieses Segments. 1.3 heißt: Dieses "
        "Segment zahlt 30 % mehr als der Durchschnitt.",
        technical="modifiers.wtp_multiplier",
    ),
    "segment.base_income_delta": Param(
        label="Einkommen (Zu-/Abschlag)",
        effect="Wird auf das Basiseinkommen dieses Segments aufgeschlagen. Höheres "
        "Einkommen macht unempfindlicher gegenüber dem Preis.",
        technical="modifiers.base_income_delta",
    ),
    "segment.price_sensitivity_delta": Param(
        label="Preisempfindlichkeit (Zu-/Abschlag)",
        effect="Höher = dieses Segment reagiert stärker auf Preisänderungen und "
        "storniert die Reise eher, wenn es teurer wird.",
        technical="modifiers.price_sensitivity_delta",
    ),
    "segment.substitution_readiness_multiplier": Param(
        label="Wechselbereitschaft zur Bahn",
        effect="Faktor darauf, wie leicht dieses Segment auf die Bahn ausweicht. "
        "Über 1 heißt: wechselt schneller als der Durchschnitt.",
        technical="modifiers.substitution_readiness_multiplier",
    ),
    # --- Verteilungen ----------------------------------------------------
    "distribution.kind": Param(
        label="Verteilungstyp",
        effect="Wie die Eigenschaft über die Bevölkerung streut. «normal» für "
        "symmetrische Streuung um einen Mittelwert, «beta» für Anteile zwischen zwei "
        "Grenzen, «lognormal» für rechtsschiefe Größen wie Einkommen.",
    ),
    # --- Technik ---------------------------------------------------------
    "mock_llm": Param(
        label="Ohne Ollama rechnen",
        effect="Die Kennzahlen bleiben identisch — sie kommen ohnehin aus Python. "
        "Nur die erzählenden Texte der Agenten sind dann Platzhalter. Für schnelle "
        "Läufe ohne lokales Sprachmodell.",
    ),
    "deterministic_only": Param(
        label="Ganz ohne Agenten-Dialog",
        effect="Überspringt die Sprachmodell-Agenten vollständig. Schnellster Modus; "
        "liefert die Zahlen, aber keine Ereignisse aus dem Zusammenspiel der Akteure.",
    ),
    "model": Param(
        label="Ollama-Modell",
        effect="Name des lokal laufenden Modells, das die Agenten-Narrative schreibt.",
    ),
    "base_url": Param(
        label="Ollama-Adresse",
        effect="Wo Ollama erreichbar ist. Läuft es auf demselben Rechner, bleibt der "
        "Standard richtig.",
    ),
    "temperature": Param(
        label="Kreativität der Agenten",
        effect="Höher = überraschendere Formulierungen und Ereignisse, niedriger = "
        "nüchterner und besser reproduzierbar. Betrifft ausschließlich Texte, nie Zahlen.",
    ),
    "max_tokens": Param(
        label="Maximale Antwortlänge",
        effect="Obergrenze je Agenten-Antwort. Zu knapp führt zu abgeschnittenen "
        "Narrativen, zu großzügig kostet Rechenzeit.",
    ),
    "checkpoint_interval": Param(
        label="Zwischenstand sichern",
        effect="Alle wie viel Runden ein Zwischenstand geschrieben wird. Nötig, um "
        "einen Lauf später fortzusetzen oder im Tab «Abfrage» einzelne Runden "
        "nachzuschlagen. 0 schaltet das ab.",
        unit="Ticks",
    ),
    "resume_from": Param(
        label="Lauf fortsetzen",
        effect="Run-ID oder Pfad eines früheren Laufs, an dessen Zwischenstand "
        "angeknüpft wird. Leer lassen für einen neuen Lauf.",
    ),
    "use_seed": Param(
        label="Zufallsstartwert festlegen",
        effect="An: Derselbe Aufbau liefert exakt dasselbe Ergebnis — Voraussetzung, "
        "um zwei Läufe sauber zu vergleichen.",
    ),
    "seed": Param(
        label="Startwert",
        effect="Die Zahl, aus der die Zufallsentscheidungen abgeleitet werden. "
        "Gleicher Wert, gleiches Ergebnis.",
    ),
    "generate_figures": Param(
        label="Auswertungsgrafiken erzeugen",
        effect="Legt nach dem Lauf sechs Diagramme als PNG ab — für Berichte und "
        "Präsentationen. Zu finden unter «Ergebnisse ansehen» → «Figures» → «PNG-Export».",
    ),
    "no_market": Param(
        label="Marktmodell abschalten",
        effect="Der Preis bleibt unverändert; nur die Nachfrageseite wird simuliert. "
        "Nützlich, um die Wirkung der Bevölkerung isoliert zu sehen.",
    ),
    "redebedarf": Param(
        label="Redebedarf-Modus",
        effect="Agenten melden sich nur zu Wort, wenn sich für sie etwas Wesentliches "
        "geändert hat, statt in jeder Runde. Kürzere, dichtere Protokolle.",
    ),
    "no_protocol": Param(
        label="Kein Protokoll schreiben",
        effect="Spart Zeit und Speicher, kostet aber die Nachvollziehbarkeit des "
        "Agenten-Dialogs.",
    ),
    "no_scenarios": Param(
        label="Keine Szenarien erzeugen",
        effect="Überspringt die Szenario-Auswertung am Ende. Der Tab «Szenario» bleibt "
        "dann leer — er ist normalerweise die Hauptansicht nach einem Lauf.",
    ),
    # --- Properties ------------------------------------------------------
    "property.baseline": Param(
        label="Startwert",
        effect="Gilt ab der ersten Runde, solange keine Regel etwas anderes vorgibt.",
    ),
    "property.rules": Param(
        label="Zeitlicher Verlauf",
        effect="Regeln verändern den Wert im Lauf: «set» springt ab der genannten "
        "Runde auf einen neuen Wert, «ramp» fährt ihn über mehrere Runden hoch. "
        "So bilden Sie etwa eine schrittweise steigende CO₂-Abgabe ab.",
    ),
    "property.is_active": Param(
        label="In diesem Lauf aktiv",
        effect="Aus: Die Größe wird im Lauf nicht angewendet.",
    ),
}


def get(path: str) -> Param | None:
    return PARAMS.get(path)


def label(path: str, fallback: str = "") -> str:
    param = PARAMS.get(path)
    return param.label if param else fallback


def hint(path: str, fallback: str | None = None) -> str | None:
    param = PARAMS.get(path)
    return param.hint() if param else fallback
