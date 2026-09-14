"""Beschriftungen und Erklärungen aller Parameter.

Jeder Eintrag trägt zwei Texte. `short` steht unter dem Eingabefeld und ist
bewusst eine Zeile — im Editor soll man arbeiten, nicht lesen. `detail` steht
auf der Seite «Dokumentation» und erklärt die Wirkung im Zusammenhang.

Die Wirkungsbeschreibungen sind aus `src/market/simulation_functions.py`,
`src/market/market_feedback.py` und `src/population/population_sampler.py`
abgeleitet. Ändert sich dort die Mechanik, gehört der Text hier nachgezogen.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Param:
    label: str
    short: str
    detail: str = ""
    unit: str = ""
    technical: str = ""

    def full_label(self) -> str:
        return f"{self.label} ({self.unit})" if self.unit else self.label


@dataclass(frozen=True)
class Group:
    """Ein Themenblock der Dokumentationsseite."""

    title: str
    intro: str
    paths: list[str] = field(default_factory=list)


PARAMS: dict[str, Param] = {
    # --- Lauf ------------------------------------------------------------
    "scenario_mode": Param(
        label="Womit starten?",
        short="Standard, ein fertiges Szenario oder Ihre eigenen Einstellungen.",
        detail="«Standard» rechnet mit den hinterlegten Werten des Modells. «Szenario-Preset» lädt "
        "eine vorbereitete Annahmenwelt, die Sie danach anpassen können. «Eigene Parameter» "
        "geht von dem aus, was in den übrigen Tabs eingestellt ist.",
    ),
    "sweep_id": Param(
        label="Szenario-Preset",
        short="Ein fertiges Bündel von Annahmen als Ausgangspunkt.",
        detail="Ein Preset legt Faktorlage, Politik und Kosten in einem Zug fest. Über "
        "«Werte übernehmen» wandern sie in den Entwurf und lassen sich einzeln verändern.",
    ),
    "rounds": Param(
        label="Länge des Laufs",
        short="Ein Tick ist ein Monat Modellzeit, ohne Kalenderdatum.",
        unit="Ticks",
        detail="Ein Tick ist ein Monat Modellzeit: 40 Ticks sind gut drei Jahre, 120 sind "
        "zehn. Ein Datum trägt er trotzdem nicht — das Modell rechnet in Monaten, legt sie "
        "aber auf keinen Kalender. Mehr Ticks heißt mehr Gelegenheiten für Anpassung und "
        "Rückkopplung zwischen Preis und Nachfrage.",
    ),
    "run_count": Param(
        label="Wiederholungen",
        short="Zeigt, wie stabil ein Ergebnis ist.",
        detail="Derselbe Aufbau wird mehrfach gerechnet, der Zufallsstartwert zählt dabei "
        "hoch. Weichen die Läufe stark voneinander ab, trägt die Aussage nicht.",
    ),
    "run_all_sweeps": Param(
        label="Alle Szenarien vergleichen",
        short="Rechnet jedes Preset einmal durch.",
        detail="Läuft ohne Agenten-Dialog und damit deutlich schneller. Die Ergebnisse stehen "
        "danach unter «Ergebnisse», eines je Szenario.",
    ),
    "simulation_name": Param(
        label="Name des Laufs",
        short="Erscheint in der Lauf-Auswahl und im Bericht.",
        detail="Ohne Namen steht dort die Kennung des Laufs. Bei mehreren Läufen ist die Liste dann "
        "kaum noch zu lesen.",
    ),
    "simulation_description": Param(
        label="Fragestellung",
        short="Wozu dieser Lauf gerechnet wird.",
        detail="Landet im Bericht und hilft später, einen Lauf wiederzuerkennen.",
    ),
    # --- Rahmenbedingungen -----------------------------------------------
    "base_price": Param(
        label="Startpreis eines Tickets",
        short="Preis im ersten Tick.",
        unit="€",
        technical="price_model.base_price",
        detail="Setzt den Maßstab für den gesamten Preisverlauf, bevor Kosten und "
        "Marktreaktion darauf wirken.",
    ),
    "apply_custom_overrides": Param(
        label="Eigene Werte anwenden",
        short="Aus: Der Lauf nutzt nur die hinterlegten Werte des Modells.",
        detail="Ist der Schalter aus, bleiben alle Anpassungen an Faktoren und Systemgrößen "
        "wirkungslos. Das ist die häufigste Ursache dafür, dass eine Änderung im Ergebnis "
        "nicht auftaucht.",
    ),
    "preisstrategie": Param(
        label="Preisstrategie",
        short="Wie der Anbieter in diesem Szenario preist.",
        detail="«auslastung» senkt den Preis, bis die Plätze gefüllt sind; «marge» hält den "
        "Aufschlag und lässt die Auslastung schwanken. Ohne eigene Wahl gilt die Strategie "
        "des Szenarios.",
    ),
    # --- Preisbildung ----------------------------------------------------
    "market_feedback_edit.enabled": Param(
        label="Airline passt den Preis an",
        short="Aus: Der Preis folgt allein den Kosten.",
        technical="market_feedback.enabled",
        detail="Eingeschaltet steuert die Airline den Preis aktiv über die beobachtete "
        "Auslastung — das übliche Yield Management. Ausgeschaltet bleibt nur die "
        "Kostenseite übrig, was die Nachfrageseite isoliert sichtbar macht.",
    ),
    "market_feedback_edit.target_booking_rate": Param(
        label="Ziel-Auslastung",
        short="Darüber steigt der Preis, darunter fällt er.",
        unit="0–1",
        technical="market_feedback.target_booking_rate",
        detail="Die Auslastung, auf die die Airline hinsteuert. Ein niedrigerer Zielwert "
        "führt tendenziell zu höheren Preisen, weil die Airline schon bei schwächerer "
        "Auslastung anzieht. Dieser Wert ist der Steuerungspunkt des gesamten Preismodells.",
    ),
    "market_feedback_edit.marginal_cost_fraction": Param(
        label="Preisuntergrenze",
        short="Darunter wird kein Ticket verkauft.",
        unit="Anteil der Kosten",
        technical="market_feedback.marginal_cost_fraction",
        detail="Welcher Teil der Stückkosten als echte Grenzkosten gilt. Ein höherer Wert "
        "heißt, dass die Airline einen Preiskampf weniger weit mitgehen kann.",
    ),
    "market_feedback_edit.markup_adjustment_per_tick": Param(
        label="Reaktionsstärke",
        short="Höher heißt nervösere Preisbewegungen.",
        unit="je Tick",
        technical="market_feedback.markup_adjustment_per_tick",
        detail="Wie kräftig die Airline nachsteuert, wenn die Auslastung vom Ziel abweicht.",
    ),
    "market_feedback_edit.damping": Param(
        label="Dämpfung",
        short="Niedriger heißt ruhigere Preise.",
        technical="market_feedback.damping",
        detail="Bremst die Reaktion zusätzlich ab. Bei hohen Werten folgt die Airline jeder "
        "Schwankung der Nachfrage.",
    ),
    "market_feedback_edit.max_price_change_fraction": Param(
        label="Preisdeckel",
        short="So weit darf sich der Preis je Tick bewegen.",
        unit="0–1",
        technical="market_feedback.max_price_change_fraction",
        detail="Harte Obergrenze nach oben wie nach unten. Verhindert Sprünge, die kein "
        "realer Anbieter durchsetzen könnte.",
    ),
    "market_feedback_edit.booking_weight": Param(
        label="Kopplung an die Buchungen",
        short="0 folgt dem Trend, 1 den tatsächlichen Buchungen.",
        unit="0–1",
        technical="market_feedback.booking_weight",
        detail="Woran sich die Nachfrage des nächsten Ticks orientiert. Höhere Werte machen "
        "das Modell reaktiver, aber auch schwankungsanfälliger.",
    ),
    # --- Sättigung -------------------------------------------------------
    "saturation_edit.booking_increase": Param(
        label="Sättigung nach einer Buchung",
        short="1 heißt: vorerst kein weiterer Flug.",
        unit="0–1",
        technical="saturation.booking_increase",
        detail="Wie stark eine gebuchte Reise den Wunsch nach der nächsten dämpft. Bei 0 "
        "ändert eine Buchung nichts.",
    ),
    "saturation_edit.utility_penalty_factor": Param(
        label="Wirkung der Sättigung",
        short="Höher heißt: Gesättigte buchen deutlich seltener.",
        technical="saturation.utility_penalty_factor",
        detail="Wie stark sich aufgebaute Sättigung in der Kaufentscheidung niederschlägt, "
        "auch wenn der Preis stimmt.",
    ),
    # --- Segmente --------------------------------------------------------
    "segment.prevalence": Param(
        label="Anteil an der Bevölkerung",
        short="Wie viele Personen zu diesem Segment gehören.",
        unit="0–1",
        detail="Die Anteile sind unabhängig voneinander — eine Person kann mehreren "
        "Segmenten angehören, sofern sie nicht in derselben exklusiven Gruppe liegen.",
    ),
    "segment.saturation_decay": Param(
        label="Erholung je Tick",
        short="0 kommt nie zurück, 1 schon im nächsten Tick.",
        unit="0–1",
        detail="Wie schnell die Sättigung dieses Segments wieder abgebaut wird.",
    ),
    "segment.wtp_multiplier": Param(
        label="Zahlungsbereitschaft",
        short="1.3 heißt: zahlt 30 % mehr als der Durchschnitt.",
        technical="modifiers.wtp_multiplier",
        detail="Faktor auf die Zahlungsbereitschaft dieses Segments.",
    ),
    "segment.base_income_delta": Param(
        label="Einkommen",
        short="Zuschlag auf das Basiseinkommen.",
        technical="modifiers.base_income_delta",
        detail="Höheres Einkommen macht ein Segment unempfindlicher gegenüber dem Preis.",
    ),
    "segment.price_sensitivity_delta": Param(
        label="Preisempfindlichkeit",
        short="Höher heißt: storniert eher, wenn es teurer wird.",
        technical="modifiers.price_sensitivity_delta",
        detail="Zuschlag auf die Preisempfindlichkeit dieses Segments.",
    ),
    "segment.substitution_readiness_multiplier": Param(
        label="Wechsel zur Bahn",
        short="Über 1 heißt: weicht schneller aus als der Durchschnitt.",
        technical="modifiers.substitution_readiness_multiplier",
        detail="Faktor darauf, wie leicht dieses Segment die Reise auf die Schiene verlegt.",
    ),
    "distribution.kind": Param(
        label="Verteilungstyp",
        short="Wie die Eigenschaft über die Bevölkerung streut.",
        detail="«normal» für symmetrische Streuung um einen Mittelwert, «beta» für Anteile "
        "zwischen zwei Grenzen, «lognormal» für rechtsschiefe Größen wie Einkommen.",
    ),
    # --- Technik ---------------------------------------------------------
    "mock_llm": Param(
        label="Rechenmodus «Ohne Sprachmodell»",
        short="Zahlen bleiben gleich, Agenten-Texte sind Platzhalter.",
        detail="Für schnelle Läufe ohne laufendes Ollama. Die Kennzahlen kommen ohnehin aus "
        "dem Rechenmodell und ändern sich dadurch nicht. Im Editor steht dieser Modus "
        "zusammen mit den beiden anderen als eine Auswahl unter «Rechenmodus».",
    ),
    "deterministic_only": Param(
        label="Rechenmodus «Nur Zahlen»",
        short="Kein Agenten-Dialog, kürzeste Laufzeit.",
        detail="Überspringt die Sprachmodell-Agenten vollständig. Es entstehen keine "
        "Ereignisse aus dem Zusammenspiel der Akteure, und der Tab «Bericht» bleibt dünn.",
    ),
    "model": Param(
        label="Ollama-Modell",
        short="Das lokal laufende Modell für die Narrative.",
    ),
    "base_url": Param(
        label="Ollama-Adresse",
        short="Läuft Ollama lokal, bleibt der Standard richtig.",
    ),
    "temperature": Param(
        label="Kreativität der Agenten",
        short="Betrifft nur Texte, nie Zahlen.",
        detail="Höhere Werte liefern überraschendere Formulierungen, niedrigere sind "
        "nüchterner und besser reproduzierbar.",
    ),
    "max_tokens": Param(
        label="Antwortlänge",
        short="Zu knapp schneidet Narrative ab.",
    ),
    "checkpoint_interval": Param(
        label="Zwischenstand sichern",
        short="Nötig zum Fortsetzen und für die Abfrage einzelner Ticks.",
        unit="Ticks",
        detail="0 schaltet die Zwischenstände ab. Ohne sie lässt sich ein Lauf später weder "
        "fortsetzen noch im Tab «Abfrage» auf einzelne Ticks hin befragen.",
    ),
    "resume_from": Param(
        label="Lauf fortsetzen",
        short="Kennung eines früheren Laufs, sonst leer lassen.",
    ),
    "use_seed": Param(
        label="Eigenen Zufallsstartwert festlegen",
        short="Nur nötig, wenn Sie einen anderen als den Standardwert wollen.",
        detail="Derselbe Aufbau liefert exakt dasselbe Ergebnis — auch ohne diese "
        "Angabe, dann mit dem Standardwert. Einen eigenen Startwert brauchen Sie, "
        "wenn Sie denselben Aufbau mehrfach mit unterschiedlicher Ziehung sehen "
        "wollen. Welcher Wert tatsächlich gerechnet wurde, steht nach dem Lauf "
        "im Bereich «Ergebnisse», Reiter «Übersicht».",
    ),
    "seed": Param(
        label="Startwert",
        short="Gleicher Wert, gleiches Ergebnis.",
    ),
    "generate_figures": Param(
        label="Auswertungsgrafiken erzeugen",
        short="Sechs Diagramme als PNG für Berichte.",
        detail="Zu finden im Bereich «Ergebnisse», Reiter «Diagramme», Abschnitt «PNG-Export».",
    ),
    "no_market": Param(
        label="Marktmodell abschalten",
        short="Preis bleibt fest, nur die Nachfrage wird simuliert.",
    ),
    "redebedarf": Param(
        label="Redebedarf-Modus",
        short="Agenten melden sich nur bei wesentlichen Änderungen.",
        detail="Führt zu kürzeren, dichteren Protokollen als der Dialog in jedem Tick.",
    ),
    "no_protocol": Param(
        label="Kein Protokoll",
        short="Spart Zeit, kostet die Nachvollziehbarkeit.",
    ),
    "no_scenarios": Param(
        label="Keine Szenarien erzeugen",
        short="Der Tab «Szenario» bleibt danach leer.",
        detail="Überspringt die Szenario-Auswertung am Ende, obwohl sie normalerweise die "
        "Hauptansicht nach einem Lauf ist.",
    ),
    # --- Systemgrößen ----------------------------------------------------
    "property.baseline": Param(
        label="Startwert",
        short="Gilt, solange keine Regel etwas anderes vorgibt.",
    ),
    "property.rules": Param(
        label="Zeitlicher Verlauf",
        short="«set» springt auf den Wert, «ramp» fährt ihn hoch.",
        detail="Regeln verändern eine Größe im Lauf, etwa für eine schrittweise steigende "
        "CO₂-Abgabe.",
    ),
    "property.is_active": Param(
        label="In diesem Lauf aktiv",
        short="Aus: Die Größe wird nicht angewendet.",
    ),
}


#: Gliederung der Dokumentationsseite. Reihenfolge ist Lesereihenfolge.
GROUPS: list[Group] = [
    Group(
        "Lauf",
        "Was gerechnet wird und in welchem Umfang.",
        [
            "scenario_mode",
            "sweep_id",
            "rounds",
            "run_count",
            "run_all_sweeps",
            "simulation_name",
            "simulation_description",
        ],
    ),
    Group(
        "Rahmenbedingungen",
        "Die exogenen Größen: Startpreis und die Frage, ob eigene Werte überhaupt greifen.",
        [
            "base_price",
            "apply_custom_overrides",
            "preisstrategie",
            "property.baseline",
            "property.rules",
            "property.is_active",
        ],
    ),
    Group(
        "Preisbildung",
        "Der Regelkreis zwischen Auslastung und Ticketpreis. Die Airline beobachtet die "
        "Buchungsrate und steuert dagegen; diese sechs Werte bestimmen, wie entschlossen "
        "sie das tut und wo ihre Grenzen liegen.",
        [
            "market_feedback_edit.enabled",
            "market_feedback_edit.target_booking_rate",
            "market_feedback_edit.marginal_cost_fraction",
            "market_feedback_edit.markup_adjustment_per_tick",
            "market_feedback_edit.damping",
            "market_feedback_edit.max_price_change_fraction",
            "market_feedback_edit.booking_weight",
        ],
    ),
    Group(
        "Sättigung",
        "Wer gerade geflogen ist, bucht so schnell nicht wieder. Ohne diesen Effekt würde "
        "die Nachfrage allein am Preis hängen.",
        [
            "saturation_edit.booking_increase",
            "saturation_edit.utility_penalty_factor",
            "segment.saturation_decay",
        ],
    ),
    Group(
        "Bevölkerung",
        "Die Nachfrageseite besteht aus Segmenten mit eigenem Verhalten. Anteil und "
        "Modifikatoren bestimmen, wie stark ein Segment das Gesamtergebnis prägt.",
        [
            "segment.prevalence",
            "segment.wtp_multiplier",
            "segment.base_income_delta",
            "segment.price_sensitivity_delta",
            "segment.substitution_readiness_multiplier",
            "distribution.kind",
        ],
    ),
    Group(
        "Technik",
        "Sprachmodell, Reproduzierbarkeit und Ausgaben. Nichts davon verändert die "
        "berechneten Zahlen, mit einer Ausnahme: dem Zufallsstartwert.",
        [
            "mock_llm",
            "deterministic_only",
            "model",
            "base_url",
            "temperature",
            "max_tokens",
            "use_seed",
            "seed",
            "checkpoint_interval",
            "resume_from",
            "generate_figures",
            "no_market",
            "redebedarf",
            "no_protocol",
            "no_scenarios",
        ],
    ),
]


def get(path: str) -> Param | None:
    return PARAMS.get(path)
