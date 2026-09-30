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
Elektroflotte») erkennt es nicht.

**Und es liefert seit P8-V3 das Faktenblatt** (`faktenblatt`, `faktenblatt_saetze`):
die Richtung jeder Kerngröße und jeder Faktorwechsel als Satz, gerechnet mit
derselben Schwelle, gegen die `pruefe` hält. Abschlusstext und Abfrage bekommen es
vor den Rohdaten — das Modell formuliert, statt zu deuten. Was dort nicht steht,
soll der Text nicht behaupten; erkennen kann das Modul eine solche Behauptung
weiterhin nicht.

**Es ist ein Messwerkzeug, keine Sperre.** Der Prüfsatz (`pruefsatz_sprachmodell`)
zählt damit, wie oft das Sprachmodell der Rechnung widerspricht; ob und wie ein
Befund dem Leser gezeigt wird, entscheidet P8-V3. **Fehlalarme sind teurer als
übersehene Fälle** (dieselbe Abwägung wie beim State Explorer): Eine
Richtungsaussage zählt nur, wenn ihr Satzteil genau **eine** bekannte Größe nennt
und genau **eine** Richtung — sonst lässt sich die Aussage keiner Größe zuordnen,
und sie wird übergangen statt geraten.
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
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
    "SAF-Quote": (
        ("saf_mandate_share",),
        r"\bsaf[\s\-‑]*(?:quote|anteil|mandat|beimisch)\w*|beimischquote\w*",
    ),
}

#: Was das Faktenblatt je Feld nennt: Name und Einheit (P8-V3). Die Reihenfolge ist
#: die der Wirkungskette — erst was die Welt vorgibt, dann was im Markt entsteht.
#: Ein Anteil hat die Einheit «%» und wird mal hundert geschrieben.
FAKTEN: dict[str, tuple[str, str]] = {
    "carbon_tax_level": ("CO₂-Abgabe", "€"),
    "saf_mandate_share": ("SAF-Quote", "%"),
    "cost_pressure_eur": ("Kostendruck", "€"),
    "market_price_after_feedback_eur": ("Ticketpreis", "€"),
    "booking_rate": ("Buchungsrate", "%"),
    "demand_level": ("Nachfrageniveau", ""),
}

#: Wörter für eine Richtung, **mit Wortgrenze**: Ohne sie las der erste Prüfsatz
#: «abzunehmen» als «zunehmen», also als Anstieg. «gleich» steht zuerst, weil
#: «nicht gestiegen» sonst an «gestiegen» hinge.
RICHTUNGEN: dict[str, str] = {
    "gleich": r"\bkeine\s+(?:nennenswerte\s+)?veränderung|\bunverändert|\bbleib\w*\s+(?:etwa\s+|annähernd\s+|nahezu\s+)?(?:stabil|gleich|konstant)|\bstagnier\w*|\bnicht\s+(?:gestiegen|gesunken|verändert)",
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


def _schreiben(wert: float, einheit: str) -> str:
    if einheit == "%":
        text = f"{wert * 100:.1f} %"
    elif einheit:
        text = f"{wert:.2f} {einheit}"
    else:
        text = f"{wert:.2f}"
    return text.replace(".", ",")


@dataclass(frozen=True)
class Fakt:
    """Der Verlauf einer Größe über einen Lauf — gerechnet, nicht gedeutet (P8-V3)."""

    groesse: str
    einheit: str
    anfang: float
    ende: float
    tiefst: float
    hoechst: float
    richtung: str  # "steigt" | "sinkt" | "gleich"
    erster_tick: int
    letzter_tick: int

    @property
    def satz(self) -> str:
        von = _schreiben(self.anfang, self.einheit)
        bis = _schreiben(self.ende, self.einheit)
        ticks = f"Tick {self.erster_tick} bis {self.letzter_tick}"
        if self.tiefst == self.hoechst:
            return f"{self.groesse} bleibt unverändert bei {von} ({ticks})."
        spanne = (
            f"tiefster Wert {_schreiben(self.tiefst, self.einheit)}, "
            f"höchster {_schreiben(self.hoechst, self.einheit)}"
        )
        if self.richtung == "gleich":
            return (
                f"{self.groesse} bleibt etwa gleich: {von} am Anfang, {bis} am Ende "
                f"({ticks}; {spanne})."
            )
        return f"{self.groesse} {self.richtung} von {von} auf {bis} ({ticks}; {spanne})."


def faktenblatt(ticks: list[dict[str, Any]]) -> list[Fakt]:
    """Je Größe aus `FAKTEN` ihr Verlauf — dieselbe Richtung, gegen die `pruefe` hält.

    **Eine Quelle für Text und Prüfung.** Das Sprachmodell bekommt diese Sätze,
    statt die Richtung aus Zahlenreihen selbst zu deuten; die Prüfung misst
    gegen dieselbe Rechnung (`_richtung`, `SCHWELLE`). Eine Größe ohne zwei
    Werte fehlt — über sie sagt das Blatt nichts, also darf es der Text auch nicht.
    """

    fakten: list[Fakt] = []
    for feld, (groesse, einheit) in FAKTEN.items():
        paare = [
            (int(t["tick"]), float(t[feld]))
            for t in ticks
            if isinstance(t.get(feld), (int, float)) and t.get("tick") is not None
        ]
        richtung = _richtung(ticks, feld)
        if len(paare) < 2 or richtung is None:
            continue
        werte = [wert for _, wert in paare]
        fakten.append(
            Fakt(
                groesse=groesse,
                einheit=einheit,
                anfang=werte[0],
                ende=werte[-1],
                tiefst=min(werte),
                hoechst=max(werte),
                richtung=richtung,
                erster_tick=paare[0][0],
                letzter_tick=paare[-1][0],
            )
        )
    return fakten


def faktorwechsel(zeilen: list[dict[str, Any]], namen: dict[str, str] | None = None) -> list[str]:
    """Je Faktor ein Satz: wo er anfängt, wo er endet, wie oft er wechselt.

    ``zeilen`` sind die Zeilen von ``timeseries/factors.csv`` (``tick``, ``F1`` …),
    ``namen`` bildet Faktor- und Zustandskennungen auf ihre Bezeichnung ab.
    """

    namen = namen or {}
    if len(zeilen) < 1:
        return []
    faktoren = sorted(k for k in zeilen[0] if k != "tick")

    def benannt(kennung: str) -> str:
        bezeichnung = namen.get(kennung)
        return f"{kennung} «{bezeichnung}»" if bezeichnung else kennung

    saetze: list[str] = []
    for faktor in faktoren:
        zustaende = [str(z.get(faktor)) for z in zeilen if z.get(faktor)]
        if not zustaende:
            continue
        wechsel = sum(a != b for a, b in zip(zustaende, zustaende[1:]))
        kopf = f"{faktor} ({namen[faktor]})" if faktor in namen else faktor
        if wechsel == 0:
            saetze.append(f"{kopf} bleibt den ganzen Lauf bei {benannt(zustaende[0])}.")
        elif zustaende[0] == zustaende[-1]:
            saetze.append(
                f"{kopf} beginnt und endet bei {benannt(zustaende[0])}, "
                f"wechselt dazwischen {wechsel}-mal."
            )
        else:
            saetze.append(
                f"{kopf} wechselt von {benannt(zustaende[0])} zu {benannt(zustaende[-1])} "
                f"({wechsel}-mal im Lauf)."
            )
    return saetze


def laufzeilen(run_dir: Path) -> list[dict[str, Any]]:
    """Die Ticks eines Laufs mit allen Größen, die das Faktenblatt kennt.

    ``tick_mechanics.json`` trägt Preis, Buchungsrate und CO₂-Abgabe, die SAF-Quote
    aber nicht — sie steht als Systemgröße in ``timeseries/properties.csv`` und
    wird je Tick dazugenommen, wo sie im Tick noch fehlt.
    """

    pfad = run_dir / "tick_mechanics.json"
    daten = json.loads(pfad.read_text(encoding="utf-8")) if pfad.is_file() else {}
    ticks = [dict(t) for t in (daten.get("ticks") or []) if isinstance(t, dict)]

    eigenschaften = run_dir / "timeseries" / "properties.csv"
    if eigenschaften.is_file():
        with eigenschaften.open(encoding="utf-8", newline="") as datei:
            je_tick: dict[int, dict[str, str]] = {}
            for zeile in csv.DictReader(datei):
                try:
                    je_tick[int(zeile["tick"])] = zeile
                except (KeyError, ValueError):
                    continue
        for tick in ticks:
            zeile = je_tick.get(int(tick.get("tick", -1)), {})
            for feld in FAKTEN:
                if feld not in tick and zeile.get(feld) not in (None, ""):
                    try:
                        tick[feld] = float(zeile[feld])
                    except ValueError:
                        pass
    return ticks


def faktenblatt_saetze(
    run_dir: Path, faktoren: list[dict[str, Any]], namen: dict[str, str] | None = None
) -> list[str]:
    """Das Faktenblatt eines Laufs als Sätze: erst die Kerngrößen, dann die Faktoren.

    Abschlusstext und Abfrage bekommen es **vor** den Rohdaten (P8-V3): Das
    Sprachmodell formuliert die Richtung, statt sie aus Zahlenreihen zu deuten.
    """

    return [fakt.satz for fakt in faktenblatt(laufzeilen(run_dir))] + faktorwechsel(faktoren, namen)


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
