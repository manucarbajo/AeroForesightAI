"""Was ein Text über einen Lauf behauptet, gegen die Zahlen dieses Laufs gehalten (P8-V1).

Die Zahlenprüfung aus P2.5 (`state_explorer.pruefe_gegen_kontext`) fragt, ob eine
Zahl der Antwort in den Laufdaten vorkommt. **Was sie nicht sieht, hat der
Szenario-Vergleich vom 2026-09-29 gezeigt:** Texte ohne falsche Zahl, aber mit
falscher Aussage — «Die Preise für Treibhausgasemissionen steigen kontinuierlich
an» unter einem Rahmen, dessen CO₂-Abgabe über 120 Ticks bei 50 € steht; «keine
Veränderung im Ticketpreis», wo er von rund 140 auf über 400 € steigt; ein
erfundenes Datum («2023-01-01») in Daten, die keines tragen (Invariante 5); und
Texte der Agenten auf Englisch unter einer deutschen Oberfläche.

Dieses Modul misst genau diese drei Dinge — **Sprache, Datumsangaben und
Richtungsaussagen** — und nichts darüber hinaus. Eine frei erfundene Sache («eine
Elektroflotte») erkennt es nicht; dafür braucht es ein Faktenblatt, gegen das man
halten kann (P8-V3).

**Es ist ein Messwerkzeug, keine Sperre.** Der Prüfsatz (`pruefsatz_sprachmodell`)
zählt damit, wie oft das Sprachmodell der Rechnung widerspricht; ob und wie ein
Befund dem Leser gezeigt wird, entscheidet P8-V3. **Fehlalarme sind teurer als
übersehene Fälle** (dieselbe Abwägung wie beim State Explorer): Eine
Richtungsaussage zählt nur, wenn ihr Satzteil genau **eine** bekannte Größe nennt
und genau **eine** Richtung — sonst lässt sich die Aussage keiner Größe zuordnen,
und sie wird übergangen statt geraten.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

#: Ab welcher relativen Änderung vom ersten zum letzten Tick eine Größe «steigt»
#: oder «sinkt». Darunter gilt sie als gleich geblieben. Gesetzt, nicht geschätzt:
#: Fünf Prozent trennen am Szenario-Vergleich vom 2026-09-29 jede sichtbare
#: Bewegung vom Rauschen der Buchungsrate zwischen zwei Monaten.
SCHWELLE = 0.05

#: Die Größen, über die ein Text Richtungsaussagen macht, je mit den Feldern in
#: `tick_mechanics.json` und den Wörtern, an denen sie im Text erkannt wird.
#: **Die CO₂-Abgabe steht vor dem Ticketpreis**, weil «Preise für
#: Treibhausgasemissionen» sonst als Ticketpreis gelesen würde; ein Satzteil, der
#: die CO₂-Abgabe nennt, zählt deshalb nie zugleich als Ticketpreis.
#:
#: **Eine Größe kann mehrere Felder haben, und dann gilt jedes als Lesart.**
#: «Nachfrage» kann die Buchungsrate meinen oder das Nachfrageniveau; ein Befund
#: entsteht nur, wenn die Aussage **keiner** Lesart entspricht. Beim ersten
#: Prüfsatz am 2026-09-29 stand «Nachfrage» allein für die Buchungsrate — zu
#: streng für eine Messung, die Fehlalarme vermeiden soll.
GROESSEN: dict[str, tuple[tuple[str, ...], str]] = {
    "CO₂-Abgabe": (
        ("carbon_tax_level",),
        r"co(?:2|₂)[\s\-‑]*(?:preis|abgabe|steuer|kosten)\w*|treibhausgas\w*|emissions?(?:preis|kosten|handel)\w*|kohlendioxid\w*",
    ),
    "Ticketpreis": (
        ("market_price_after_feedback_eur",),
        r"(?:ticket|flug)(?:preis|kosten)\w*|\bpreis(?:e|en|es)?\b|\bpreisniveau\w*",
    ),
    "Buchungsrate": (("booking_rate",), r"buchung\w*|passagierzahl\w*|fluggäste\w*"),
    "Nachfrage": (("booking_rate", "demand_level"), r"nachfrage\w*"),
    "Kostendruck": (("cost_pressure_eur",), r"kostendruck\w*|betriebskosten\w*"),
}

#: Wörter für eine Richtung, **mit Wortgrenze**: Ohne sie las der erste Prüfsatz
#: «abzunehmen» als «zunehmen», also als Anstieg. «gleich» steht zuerst, weil
#: «nicht gestiegen» sonst an «gestiegen» hinge.
RICHTUNGEN: dict[str, str] = {
    "gleich": r"\bkeine\s+(?:nennenswerte\s+)?veränderung|\bunverändert|\bbleib\w*\s+(?:stabil|gleich|konstant)|\bstagnier\w*|\bnicht\s+(?:gestiegen|gesunken|verändert)",
    "steigt": r"\bsteig\w*|\bstieg\w*|\bgestiegen|\bwächst|\bwuchs|\bgewachsen|\bzunehm\w*|\bzuzunehm\w*|\bzugenommen|\bnimmt\s+zu|\bnahm\s+zu|\berhöh\w*|\banstieg\w*|\bhöher",
    "sinkt": r"\bsink\w*|\bsank\w*|\bgesunken|\bfällt|\bfiel\w*|\bgefallen|\babnehm\w*|\babzunehm\w*|\babgenommen|\bnimmt\s+ab|\bnahm\s+ab|\brückgang\w*|\brückläufig\w*|\bbrach\w*\s+ein|\beingebrochen|\beinbruch\w*|\bniedriger",
}

#: Ein Satz mit diesen Wörtern behauptet nichts über den Lauf, sondern erwägt
#: («Wenn die Buchungsrate-Steigerung positiv ist …») oder fragt. Der erste
#: Prüfsatz fand in einer Antwort eine erklärte Formel statt einer Antwort und
#: zählte jede Zeile als Widerspruch.
BEDINGUNG = re.compile(r"\b(?:wenn|falls|sofern|ob|angenommen)\b|=|\?")

#: Ein Kalenderdatum. Die Daten eines Laufs tragen keines (Invariante 5), also ist
#: jedes Datum in einem Text über den Lauf erfunden.
DATUM = re.compile(r"\b(?:19|20)\d{2}-\d{2}-\d{2}\b|\b\d{1,2}\.\s?\d{1,2}\.\s?(?:19|20)\d{2}\b")

#: Häufige Funktionswörter je Sprache. Gezählt wird, welche Sprache überwiegt —
#: robuster als jedes Einzelwort, und ohne eine Abhängigkeit für Spracherkennung.
_ENGLISCH = {
    "the",
    "and",
    "of",
    "to",
    "in",
    "for",
    "with",
    "on",
    "is",
    "are",
    "as",
    "by",
    "their",
    "this",
    "that",
}
_DEUTSCH = {
    "der",
    "die",
    "das",
    "und",
    "ist",
    "mit",
    "für",
    "von",
    "den",
    "im",
    "sich",
    "nicht",
    "eine",
    "auf",
    "des",
}


@dataclass(frozen=True)
class Befund:
    """Eine Stelle, an der ein Text der Rechnung oder den Regeln widerspricht."""

    art: str  # "englisch" | "datum" | "richtung"
    stelle: str  # der Satzteil, um den es geht
    erklaerung: str


def ist_englisch(text: str) -> bool:
    """Überwiegen englische Funktionswörter? Mindestens drei, damit ein Fachbegriff nicht zählt."""

    woerter = re.findall(r"[a-zäöüß]+", text.lower())
    en = sum(w in _ENGLISCH for w in woerter)
    de = sum(w in _DEUTSCH for w in woerter)
    return en >= 3 and en > de


def _richtung(ticks: list[dict[str, Any]], feld: str) -> str | None:
    werte = [float(t[feld]) for t in ticks if isinstance(t.get(feld), (int, float))]
    if len(werte) < 2:
        return None
    anfang, ende = werte[0], werte[-1]
    bezug = abs(anfang) if anfang else 1.0
    aenderung = (ende - anfang) / bezug
    return "steigt" if aenderung > SCHWELLE else "sinkt" if aenderung < -SCHWELLE else "gleich"


def verlaeufe(ticks: list[dict[str, Any]]) -> dict[str, frozenset[str]]:
    """Die Richtungen jeder Größe über den Lauf — eine je Lesart (Feld).

    Gemessen vom ersten zum letzten Tick, an dem ein Feld einen Wert hat. Eine
    Größe ohne Werte fehlt im Ergebnis — über sie lässt sich nichts prüfen.
    """

    ergebnis: dict[str, frozenset[str]] = {}
    for name, (felder, _) in GROESSEN.items():
        richtungen = {r for feld in felder if (r := _richtung(ticks, feld)) is not None}
        if richtungen:
            ergebnis[name] = frozenset(richtungen)
    return ergebnis


def _satzteile(text: str) -> list[str]:
    saetze = re.split(r"(?<=[.!?;:])\s+|\n+", text)
    teile: list[str] = []
    for satz in saetze:
        if BEDINGUNG.search(satz.lower()):
            continue
        teile.extend(
            t.strip()
            for t in re.split(r",|\bwährend\b|\bwohingegen\b|\bsowie\b|\bund\b", satz)
            if t.strip()
        )
    return teile


def _groessen_in(teil: str) -> list[str]:
    klein = teil.lower()
    gefunden: list[str] = []
    for name, (_, muster) in GROESSEN.items():
        if re.search(muster, klein):
            gefunden.append(name)
            if name == "CO₂-Abgabe":
                # «Preise für Treibhausgase» ist keine Aussage über den Ticketpreis.
                klein = re.sub(muster, " ", klein)
                klein = re.sub(r"\bpreis(?:e|en|es)?\b", " ", klein)
    return gefunden


def _richtungen_in(teil: str) -> list[str]:
    klein = teil.lower()
    gefunden: list[str] = []
    for richtung, muster in RICHTUNGEN.items():
        if re.search(muster, klein):
            gefunden.append(richtung)
            klein = re.sub(muster, " ", klein)
    return gefunden


def pruefe(text: str, ticks: list[dict[str, Any]]) -> list[Befund]:
    """Alle Befunde eines Texts über einen Lauf mit diesen Ticks."""

    befunde: list[Befund] = []
    if ist_englisch(text):
        befunde.append(Befund("englisch", text[:80], "Der Text ist überwiegend englisch."))
    for treffer in DATUM.finditer(text):
        befunde.append(
            Befund(
                "datum", treffer.group(0), "Die Daten eines Laufs tragen kein Datum (Invariante 5)."
            )
        )

    tatsaechlich = verlaeufe(ticks)
    for teil in _satzteile(text):
        groessen = _groessen_in(teil)
        richtungen = _richtungen_in(teil)
        if len(groessen) != 1 or len(richtungen) != 1:
            continue
        groesse, behauptet = groessen[0], richtungen[0]
        gerechnet = tatsaechlich.get(groesse)
        if gerechnet is not None and behauptet not in gerechnet:
            befunde.append(
                Befund(
                    "richtung",
                    teil,
                    f"{groesse}: im Text «{behauptet}», gerechnet «{' oder '.join(sorted(gerechnet))}».",
                )
            )
    return befunde
