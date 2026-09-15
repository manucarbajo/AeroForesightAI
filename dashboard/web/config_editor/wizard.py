"""Einrichten als Schrittfolge — ein Schritt, eine Frage (P1.7-C).

Vorher war das Einrichten eine Bildlaufstrecke: bei 1280 px **7,3 Bildschirme**,
und die vier Editor-Reiter lagen unten hinter einer Trennlinie. Reiter unterhalb
des Falzes sind keine Gliederung — man findet sie nur, wenn man ohnehin schon
weiß, dass es sie gibt. Wer zum ersten Mal hier stand, sah eine Wand und wusste
nicht, was als Nächstes zu tun ist.

Jetzt steht **eine** Frage auf dem Schirm, links die Liste aller Schritte mit
dem Stand, unten «Zurück» und «Weiter». Der Bildschirm sagt damit von selbst,
wo man ist, was noch kommt, und was der nächste Griff ist.

**Die Zusage aus P1.1 bleibt gültig: drei Entscheidungen genügen.** Die Schritte
vier bis sieben sind ausdrücklich als *optional* gekennzeichnet, jeder ist
überspringbar, und ab Schritt drei führt ein Weg direkt zum Schluss. Eine
Schrittfolge, die acht Stationen erzwingt, wäre ein Rückschritt gegenüber dem,
was P1.1 erreicht hat.

Zwei Regeln, die hier leicht zu brechen wären:

* **Nur der sichtbare Schritt steht im DOM.** Sonst stünden Felder doppelt, und
  eine doppelte Dash-ID ist ein Laufzeitfehler im Browser.
* **Ein Schrittwechsel schreibt nichts zurück.** Er tauscht nur, was zu sehen
  ist; gespeichert wird weiterhin ausschließlich vom Feld in den Store
  (Einbahnstraße aus P1.1). Ein Schritt, der beim Verlassen Werte setzte, führte
  dieselbe Zahl an zwei Stellen — genau der Fehler, den P1.1 bei der Lauflänge
  gemacht und wieder ausgebaut hat.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from dash import ALL, Input, Output, State, ctx, dcc, html, no_update

from dashboard.config_catalog import rahmenszenarien
from dashboard.web import components as ui
from dashboard.web.config_editor import controls as c
from dashboard.web.config_editor import delta, experiment, llm_pipeline, start_flow
from dashboard.web.state import STORE_ID, initial_draft_dict

#: Welcher Schritt gerade offen ist. Als Store und nicht als Adresse, weil ein
#: halb ausgefülltes Formular kein Ort ist, den man verlinken oder mit dem
#: Zurück-Knopf des Browsers ansteuern will.
#:
#: `None` ist kein Schritt, sondern der **Einstieg** (siehe `entry`). Der Store
#: wird nicht gespeichert: Wer «Einrichten» öffnet, steht damit immer vor der
#: Frage, welche Art von Lauf es werden soll — nicht mitten in einem Formular,
#: das er vor einer Stunde halb ausgefüllt hat.
STEP_STORE = "wizard-step-store"

#: Welche Schritte tatsächlich offen waren. Eigener Store und **nicht** eine
#: Erweiterung von `STEP_STORE`: Dessen Form (`None` oder eine Zahl) wird an
#: mehreren Stellen gelesen und in drei Testdateien festgehalten; sie in ein
#: Wörterbuch zu verwandeln, hieße alle davon anzufassen, für einen Wert, der
#: unabhängig davon lebt.
#:
#: Wie `STEP_STORE` **nicht** gespeichert: Wer «Einrichten» neu öffnet, fängt am
#: Einstieg an, und dann ist noch nichts besucht.
VISITED_STORE = "wizard-visited-store"

#: Wo man hergekommen ist — der Stapel für «Zurück» (P1.9-W2.3).
#:
#: Bis hierher rechnete «Zurück» schlicht `aktuell - 1`. Für den geraden Weg
#: durch die Schritte stimmt das; für jeden anderen nicht. Wer über
#: «Szenario-Vergleich starten» auf Schritt 8 kam, landete mit einem Klick in
#: Schritt 7 «Technik» — in Feineinstellungen zum Sprachmodell, die er nie sehen
#: wollte und die auf seinem Pfad ohnehin nicht gelten. Wer über die Liste von
#: Schritt 1 auf 7 sprang, landete auf 6.
#:
#: Ein Zurück-Knopf, der irgendwo hinführt statt dorthin, wo man war, ist kein
#: Zurück-Knopf. Er braucht einen Verlauf, keine Subtraktion.
HISTORY_STORE = "wizard-history-store"

#: Der Einstieg — der Zustand vor dem ersten Schritt.
ENTRY = None

CONTENT = "wizard-content"
RAIL = "wizard-rail"
BACK = "wizard-back"
NEXT = "wizard-next"
SKIP = "wizard-skip"
#: Zweiter Auslöser für den Start — **nicht** ein zweiter Startpfad. Er hängt am
#: selben Callback wie der Knopf im Bedienfeld, mit derselben Prüfung und
#: demselben `runner.start`.
START = "wizard-start"

#: Sprungziel je Schritt der Schrittliste.
JUMP = "wizard-jump"

#: Wo die Begründung steht, wenn «Weiter» oder «Lauf starten» gesperrt ist.
#: **Ein gesperrter Knopf ohne Erklärung ist nur ärgerlich** — er sagt «nein»
#: und verschweigt, wogegen. Die Meldung steht deshalb neben dem Knopf, nicht
#: irgendwo oben auf der Seite.
GATE = "wizard-gate"

#: Was der Screenreader beim Schrittwechsel hört (P1.9-W5.3).
#:
#: **Eine eigene Region, nicht der Zähler im Inhalt.** Beim Wechsel tauscht
#: `_render` den ganzen Inhaltsbaum aus; eine Live-Region **innerhalb** eines
#: ausgetauschten Teilbaums wird nicht zuverlässig vorgelesen, weil sie im
#: Moment der Änderung selbst neu entsteht. Diese hier bleibt stehen und
#: bekommt nur neuen Text — das ist der Fall, für den `aria-live` gebaut ist.
#:
#: Gemessen hatte das Dokument **null** Live-Regionen: Schrittwechsel,
#: Statusmeldungen und Feldfehler waren für einen Screenreader stumm.
ANSAGE = "wizard-ansage"

#: Die drei Wege des Einstiegs. Jeder ist ein eigener Knopf und **bleibt im
#: DOM**, auch wenn die Schrittfolge läuft — nur ausgeblendet. Dash führt einen
#: Callback gar nicht erst aus, wenn auch nur *ein* Eingang fehlt (Regel 6 der
#: Architektur-Map); ein Weg, den es auf Schritt 3 nicht gibt, legte die ganze
#: Navigation lahm.
WAY_NEW = "wizard-way-new"
WAY_SWEEP = "wizard-way-sweep"
WAY_RESUME = "wizard-way-resume"

#: Wirte, deren **Sichtbarkeit** zwischen Einstieg und Schrittfolge umgeschaltet
#: wird. Ausblenden statt weglassen, aus demselben Grund wie oben.
ENTRY_HOST = "wizard-entry-host"
CONTENT_HOST = "wizard-content-host"
RAIL_HOST = "wizard-rail-host"
NAV_HOST = "wizard-nav-host"
HEAD_HOST = "wizard-head-host"
#: Das Raster aus Schrittliste und Inhalt. Trägt eine Kennung, weil seine
#: Spaltenaufteilung sich mit dem Schritt ändert (W5.4) — am Einstieg gibt es
#: keine Schrittliste, und dann darf ihr auch kein Platz reserviert werden.
GRID = "wizard-grid"

_VISIBLE: dict = {}
_HIDDEN = {"display": "none"}

#: Ausgang des clientseitigen Callbacks, der nach oben scrollt. Er schreibt
#: nichts — Dash verlangt aber einen Ausgang.
SCROLL_SINK = "wizard-scroll-sink"


@dataclass(frozen=True)
class Step:
    """Ein Schritt: Was gefragt wird, und ob er beantwortet werden muss."""

    key: str
    title: str
    lede: str
    body: Callable[[dict], object] | None = None
    #: `False` heißt: darf übersprungen werden, ohne dass etwas fehlt.
    required: bool = True


STEPS: list[Step] = [
    Step(
        "szenario",
        "Was soll gerechnet werden?",
        "Die Annahmenwelt, von der der Lauf ausgeht. Ein vorbereitetes Szenario ist der "
        "schnellste Einstieg — es legt Politik, Kosten und Konjunktur in einem Zug fest. "
        "Die Faktorlage entsteht daraus im Lauf.",
        lambda draft: start_flow.scenario_step(draft, number=None),
    ),
    Step(
        "umfang",
        "Wie weit reicht der Lauf?",
        "Ein Tick ist ein Monat, vierzig sind gut drei Jahre — in den Zahlen steht "
        "trotzdem kein Datum. Mehr Ticks heißt vor allem mehr Gelegenheiten für "
        "Rückkopplung zwischen Preis und Nachfrage.",
        lambda draft: start_flow.scope_step(draft, number=None),
    ),
    Step(
        "modus",
        "Womit wird gerechnet?",
        "Die Zahlen sind in allen drei Fällen dieselben — die Auswahl bestimmt nur, wie "
        "viel dazu erzählt wird.",
        lambda draft: start_flow.mode_step(draft, number=None),
    ),
    # **Der Schritt «Ausgangslage» ist mit P2.0-C entfallen.** Er fragte sieben
    # Faktorzustände ab, und gemessen war die Antwort folgenlos: Vier der sieben
    # Faktoren sind nach *einem* Tick überschrieben, weil ihre Regeln an
    # exogenen Systemgrößen hängen; in allen vier Presets, die eine Vorgabe
    # trugen, landeten alle sieben auf denselben Zuständen wie ohne sie
    # (`tests/test_faktoren_abgeleitet.py`). Ein Rahmenszenario setzt die
    # exogenen Verläufe — die Faktorlage entsteht daraus im Lauf. Sie vorher zu
    # setzen hieße, die Antwort vor die Rechnung zu stellen.
    #
    # Der Schalter «Eigene Werte anwenden» ist mit nach Schritt 1 umgezogen: Ob
    # die eigenen Werte gelten, gehört zur Wahl des Ausgangspunkts.
    # **«Rahmenbedingungen» und «Nachfrage & Preisbildung» standen hier bis
    # P1.9-W3.1.** Sie sind in den Bereich «Modell» umgezogen: zusammen 168
    # Bedienelemente und 3,0 bzw. 4,0 Bildschirme, während die drei
    # Entscheidungsschritte davor mit drei, fünf und zehn Feldern auskamen. In
    # einer Liste mit gleichem Gewicht geführt, machte das die Zählung «Schritt
    # 5 von 8» bedeutungslos — der fünfte Schritt war das Vielfache aller
    # anderen zusammen. Ein Experiment einzurichten und ein Modell zu pflegen
    # sind zwei Tätigkeiten; sie in dieselbe Schrittfolge zu legen geht nur
    # zulasten einer von beiden.
    Step(
        "ablage",
        "Lauf & Ablage",
        "Fragestellung und die Dateien, aus denen der Lauf liest.",
        experiment.layout,
        required=False,
    ),
    Step(
        "technik",
        "Technik",
        "Sprachmodell, Adresse, Zeitgrenzen.",
        llm_pipeline.layout,
        required=False,
    ),
    Step(
        "start",
        "Prüfen & Starten",
        "Der letzte Blick — und dann los.",
        None,
    ),
]

#: Ab hier ist alles Feinjustierung. Nach Schritt 3 sind die drei Entscheidungen
#: aus P1.1 getroffen, und der Weg zum Start steht offen.
LAST_REQUIRED = 2
FINAL = len(STEPS) - 1


def schritt(key: str) -> int:
    """Wo ein Schritt steht, gefunden über seinen Schlüssel statt über eine Zahl.

    Die Positionen haben sich mit W3.1, W3.3 und P2.0-C dreimal bewegt, und jedes
    Mal musste eine Hand jede Zahl nachziehen, die einen Schritt meinte. Über den
    Schlüssel bleibt eine Zuordnung richtig, wenn ein Schritt dazukommt. **Ein
    unbekannter Schlüssel scheitert laut**: Ein still gewählter Rückfall sperrte
    «Weiter» im falschen Schritt.
    """

    for index, step in enumerate(STEPS):
        if step.key == key:
            return index
    raise KeyError(f"Keinen Schritt mit dem Schlüssel {key!r}")


#: In welchem Schritt ein beanstandetes Feld eingestellt wird (P1.9-W2.2).
#:
#: `src/validation.py` hängt seine Befunde an ein Feld — sechs Felder sind es
#: heute. Damit «Weiter» sperren kann, muss die Schrittfolge wissen, **wo** ein
#: Befund hingehört.
#:
#: **Eine Tabelle, ja — aber eine bewachte.** P1.1 hat eine Zuordnung
#: «Schlüsselwort → Feld» im Dashboard ausdrücklich abgelehnt, weil sie still
#: bricht, sobald jemand einen Meldungstext umformuliert. Hier ist es kein
#: Schlüsselwort, sondern der Feldname, den die Prüfung selbst vergibt; und die
#: Zuordnung wird nicht geglaubt, sondern geprüft: `tests/test_web_wizard.py`
#: rendert jeden Schritt, liest heraus, welche Felder er wirklich zeigt, und
#: meldet jede Zeile, die nicht mehr stimmt. Wer ein Feld in einen anderen
#: Schritt verschiebt, sieht rot.
#:
#: Zur Laufzeit gerendert würde es das Problem lösen, ohne eine Tabelle zu
#: brauchen — kostete aber acht Schrittbäume je Tastendruck, darunter die beiden
#: mit zusammen 168 Bedienelementen.
FELD_SCHRITT: dict[str, int] = {
    "rounds": schritt("umfang"),
    "seed": schritt("modus"),
    "simulation_name": FINAL,
    # **Über den Schlüssel, nicht als Zahl.** Bis zum 2026-09-15 standen hier
    # Positionen, nach P2.0-C von Hand um eins nach vorn gerückt.
    # `test_web_wizard` gleicht die Tabelle gegen die wirklich gerenderten
    # Felder ab — eine von Hand gepflegte Zahl lief sonst still weg, und dann
    # sperrte «Weiter» im falschen Schritt.
    "model": schritt("technik"),
    # **Mit P3.4 dazugekommen**, und der Wächter hat es gemeldet, nicht ein
    # Blick: Seit `validate_llm_settings` auch den Endpunkt prüft, kann ein
    # Befund an `base_url` hängen — ohne diese Zeile landete er auf «Prüfen &
    # Starten», also *nicht* in dem Schritt, in dem das Feld steht.
    "base_url": schritt("technik"),
    "temperature": schritt("technik"),
    "max_tokens": schritt("technik"),
}

#: Wohin ein Befund gehört, dessen Feld die Schrittfolge nicht kennt. «Prüfen &
#: Starten» ist der ehrliche Ort: Dort steht ohnehin der vollständige Preflight,
#: und dort wird gestartet. Ein Befund ohne Feld — etwa eine unlesbare
#: Konfigurationsdatei — hat keinen anderen Platz.
SCHRITT_OHNE_FELD = FINAL


def blocker_je_schritt(errors: list) -> dict[int, list[str]]:
    """Die Befunde, nach dem Schritt sortiert, in dem man sie beheben kann."""

    from src.validation import field_of

    verteilt: dict[int, list[str]] = {}
    for eintrag in errors or []:
        schritt = FELD_SCHRITT.get(field_of(eintrag) or "", SCHRITT_OHNE_FELD)
        verteilt.setdefault(schritt, []).append(str(eintrag))
    return verteilt


def gate(draft: dict, step) -> tuple[bool, bool, object]:
    """Ob «Weiter» und «Lauf starten» offen sind — und warum nicht.

    Zwei verschiedene Tore, aus zwei verschiedenen Gründen:

    * **«Weiter»** sperrt nur, wenn der Befund **in diesem Schritt** behoben
      werden kann. Sonst stünde man auf Schritt 1 fest wegen eines Modellnamens,
      den man erst in Schritt 7 einstellt — eine Sackgasse, keine Führung.
    * **«Lauf starten»** sperrt bei **jedem** Befund. Von dort geht es nicht
      weiter, sondern los; ein Lauf mit kaputter Konfiguration scheitert
      irgendwo im ersten Tick, mit einer Meldung, die niemandem hilft.

    Bis hierher gab es kein Tor. `_navigate` prüfte nichts, «Weiter» war nie
    gesperrt, und `_start` lehnte erst nach dem Klick ab. Man konnte durch acht
    Schritte laufen und am Ende erfahren, dass Schritt 2 ungültig war.
    """

    jetzt = resolve(step)
    if is_entry(jetzt):
        return False, False, None

    verteilt = blocker_je_schritt(start_flow.errors_for(draft))
    if not verteilt:
        return False, False, None

    hier = verteilt.get(jetzt, [])
    anderswo = sorted(s for s in verteilt if s != jetzt)

    if hier:
        text = "**Hier stimmt noch etwas nicht.** " + " · ".join(f"`{e}`" for e in hier)
    else:
        wohin = ", ".join(f"Schritt {s + 1} ({STEPS[s].title})" for s in anderswo)
        text = f"**Der Lauf kann so nicht starten.** Zu beheben in: {wohin}."

    return bool(hier), True, ui.hinweis(text, "fehler")


def clamp(step) -> int:
    try:
        value = int(step)
    except (TypeError, ValueError):
        return 0
    return max(0, min(value, FINAL))


def is_entry(step) -> bool:
    """Ob der Einstieg gemeint ist statt eines Schritts.

    `clamp` bleibt davon unberührt: Es beantwortet die Frage «welcher Schritt?»
    und macht aus allem Unbrauchbaren den ersten. Der Einstieg ist aber kein
    unbrauchbarer Schritt, sondern ein eigener Ort — deshalb eine eigene Frage.
    """

    return step is None


def resolve(step) -> int | None:
    """Der Store-Wert als Ort: der Einstieg, oder ein gültiger Schritt."""

    return ENTRY if is_entry(step) else clamp(step)


# --- Der Einstieg: drei Wege -----------------------------------------------


def _hauptweg(weiter: bool) -> str:
    """Welcher der drei Wege der hervorgehobene ist (P1.9-W5.6).

    **Das hier ist ein Fachurteil, keine Messung** — und es steht so im Plan.
    Wir haben keine Nutzungsdaten; was wir haben, ist die Struktur der Wege:

    * «Neuen Lauf einrichten» ist der **Erstnutzungsfall**. Wer zum ersten Mal
      hier steht, hat nichts, was er weiterverwenden könnte.
    * «Letzte Einstellungen weiterverwenden» ist der **Wiederholfall**, und der
      ist über die Lebensdauer eines Projekts der mit Abstand häufigste: Man
      rechnet denselben Aufbau mehrfach, mit kleinen Änderungen dazwischen.
    * «Szenario-Vergleich» ist ein **Spezialfall** — mächtig, aber selten, und
      er ist nie das, womit jemand anfängt.

    Der einzige belastbare Anhaltspunkt, den die Oberfläche wirklich hat, ist
    also nicht «wie oft», sondern **«gibt es überhaupt etwas fortzusetzen»** —
    und genau danach richtet sich die Hervorhebung. Etwas anderes wäre geraten.

    **Die Reihenfolge bleibt dabei fest**, und auch das ist eine Entscheidung:
    Wer die Wege je nach Zustand umsortiert, nimmt dem wiederkehrenden Nutzer
    das Einzige, was er hier schon kann — hinsehen, wo der Weg letztes Mal lag.
    Gewicht darf sich ändern, Ort nicht.

    Ein gesperrter Weg wird nie hervorgehoben: Eine betonte Karte, die auf
    einen Klick nicht reagiert, ist schlimmer als eine unbetonte.
    """

    return WAY_RESUME if weiter else WAY_NEW


def _way(
    ident: str,
    symbol: str,
    title: str,
    text: str,
    *,
    disabled: bool = False,
    gewicht: str = "neben",
) -> html.Button:
    """Ein Weg als ganzflächige Schaltfläche.

    Karte *und* Knopf wäre ein Ziel im Ziel; hier ist die ganze Fläche das Ziel.

    *gewicht* ist `"haupt"` für **genau einen** der drei Wege — siehe
    `_hauptweg`. Drei gleich große, gleich betonte Karten stellen drei Fragen,
    wo eine zu beantworten ist.
    """

    return html.Button(
        [
            ui.icon(symbol, "af-way__icon text-2xl"),
            html.Div(
                [
                    html.Span(title, className="af-way__title"),
                    html.Span(text, className="af-way__text"),
                ],
                className="af-way__body",
            ),
            ui.icon("chevron_right", "af-way__chevron text-base"),
        ],
        id=ident,
        className=f"af-way af-way--{gewicht}",
        n_clicks=0,
        disabled=disabled,
    )


def touched(draft: dict | None) -> bool:
    """Ob am Entwurf schon etwas eingestellt wurde.

    Verglichen wird gegen den Auslieferungszustand, nicht gegen ein einzelnes
    Merkmal: Was «eigene Einstellungen» sind, entscheidet der Entwurf als
    Ganzes. Der Draft-Store hält sie über einen Neuladen hinweg
    (`storage_type="session"`) — genau das macht den dritten Weg möglich.
    """

    return bool(draft) and draft != initial_draft_dict()


def _with_sweeps(draft: dict | None, alle: bool) -> dict:
    """Den Entwurf mit genau einer geänderten Aussage zurückgeben.

    Eine flache Kopie und kein `patch`-Aufruf, damit hier sichtbar bleibt, dass
    **ein** Feld geschrieben wird und sonst nichts.
    """

    data = dict(draft or {})
    data["run_all_sweeps"] = alle
    return data


def entry(draft: dict | None = None) -> html.Div:
    """Die Frage vor der Schrittfolge: Welche Art von Lauf soll es werden?

    Bis hierher landete man unmittelbar auf Schritt 1. Damit war «alle Szenarien
    nacheinander rechnen» eine Ankreuzoption hinter der Feinabstimmung des
    zweiten Schritts — man findet sie nur, wenn man schon weiß, dass es sie
    gibt. Dasselbe galt für den häufigsten Fall überhaupt: Der Entwurf steht
    noch im Store, man will ihn nur noch einmal starten, und dafür acht Fragen
    durchzublättern ist Arbeit ohne Ertrag.

    Die drei Wege sagen jeder genau eine Sache — und **schreiben** auch nur je
    eine: «Neuen Lauf einrichten» stellt sicher, dass es ein Lauf ist,
    «Szenario-Vergleich» stellt sicher, dass es alle sind, «Weiterverwenden»
    fasst den Entwurf nicht an. Ohne das erste Schreiben bliebe ein einmal
    gewählter Vergleich beim nächsten Weg still aktiv, und man startete acht
    Läufe, wo man einen wollte.
    """

    weiter = touched(draft)
    # **Gezählt wird, was der Vergleich rechnet** (P7.2-U2.1): die Rahmen, nicht
    # der ganze Ordner. Bis zum 2026-09-11 stand hier «Alle 8 hinterlegten
    # Szenarien», während der Prüfschritt «alle 4 Rahmenszenarien» sagte.
    rahmen = len(rahmenszenarien())
    haupt = _hauptweg(weiter)

    def _gewicht(ident: str) -> str:
        return "haupt" if ident == haupt else "neben"

    return html.Div(
        [
            html.Div(
                [
                    _way(
                        WAY_NEW,
                        "tune",
                        "Neuen Lauf einrichten",
                        "Die Fragen der Reihe nach — Szenario, Länge, Rechenmodus. "
                        "Drei genügen bis zum Start, alles Weitere ist vorbelegt.",
                        gewicht=_gewicht(WAY_NEW),
                    ),
                    _way(
                        WAY_SWEEP,
                        "compare_arrows",
                        "Szenario-Vergleich starten",
                        (
                            f"Alle {rahmen} Rahmenszenarien nacheinander rechnen "
                            "und am Ende nebeneinanderlegen."
                            if rahmen
                            else "Zurzeit ist kein Rahmenszenario hinterlegt."
                        ),
                        disabled=not rahmen,
                        gewicht=_gewicht(WAY_SWEEP),
                    ),
                    _way(
                        WAY_RESUME,
                        "history",
                        "Letzte Einstellungen weiterverwenden",
                        (
                            "Direkt zu «Prüfen & Starten», mit dem, was zuletzt eingestellt war."
                            if weiter
                            else "Noch nichts eingestellt — dieser Weg öffnet sich, sobald Sie "
                            "einmal etwas geändert haben."
                        ),
                        disabled=not weiter,
                        gewicht=_gewicht(WAY_RESUME),
                    ),
                ],
                className="af-ways",
            ),
            html.P(
                "Jeder Weg führt in dieselbe Schrittfolge; Sie können jederzeit "
                "zwischen den Schritten springen.",
                className=f"{ui.CAPTION} mt-6",
            ),
        ],
        id=ENTRY_HOST + "-body",
    )


def _besucht_aus(gespeichert, current: int | None) -> set[int]:
    """Die besuchten Schritte aus dem Store — plus dem, der gerade offen ist.

    Den offenen mit aufzunehmen erspart eine Reihenfolge-Falle: Sonst müsste
    jeder Schreiber daran denken, und ein vergessener Fall hieße, dass ein
    Schritt nach dem Verlassen als übersprungen dasteht, obwohl man ihn gerade
    gesehen hat.
    """

    besucht = {int(i) for i in (gespeichert or []) if isinstance(i, (int, float))}
    if current is not None:
        besucht.add(int(current))
    return besucht


# --- Die Schrittliste ------------------------------------------------------


#: Die vier Zustände eines Schritts in der Liste: Symbol und Klartext für den
#: Tooltip. **Vier und nicht drei**, obwohl P1.9-W2.1 drei vorsah — der vierte
#: ist der, um den es dem Paket geht: *übersprungen*.
#:
#: Bis hierher gab es nur zwei Sorten, und sie hingen allein an der Position:
#: Alles vor dem offenen Schritt galt als erledigt, mit Häkchen. Gemessen nach
#: einem Klick auf «Szenario-Vergleich starten» standen so **sieben Häkchen für
#: sieben Schritte, die nie auf dem Schirm waren**.
#:
#: «Nicht besucht» allein hätte gereicht, um das abzustellen. Es beantwortet
#: aber nicht die Frage, die man an dieser Stelle wirklich hat: *Habe ich etwas
#: übergangen?* Ein Schritt, der noch kommt, und einer, an dem man
#: vorbeigesprungen ist, sehen sonst gleich aus.
_ZUSTAENDE = {
    "besucht": ("check", "besucht"),
    "current": ("radio_button_checked", "offen"),
    "uebersprungen": ("remove", "übersprungen"),
    "offen": ("radio_button_unchecked", "noch nicht geöffnet"),
}


def _zustand(index: int, current: int | None, besucht: set[int]) -> str:
    """Wie ein Schritt in der Liste dasteht.

    **Besucht heißt gesehen, nicht bearbeitet.** Eine strengere Lesart —
    «beantwortet» — ließe sich nicht messen: Jedes Feld ist vorbelegt, und wer
    einen sinnvollen Vorschlag stehen lässt, hat trotzdem entschieden. Gesehen
    zu haben ist die Aussage, die dieser Haken ehrlich tragen kann.
    """

    if index == current:
        return "current"
    if index in besucht:
        return "besucht"
    if current is not None and index < current:
        return "uebersprungen"
    return "offen"


def _rail_entry(index: int, step: Step, current: int | None, besucht: set[int]) -> html.Button:
    zustand = _zustand(index, current, besucht)
    symbol, klartext = _ZUSTAENDE[zustand]

    return html.Button(
        [
            ui.icon(symbol, "af-step__icon text-base"),
            html.Span(
                [
                    html.Span(step.title, className="af-step__title"),
                    (
                        html.Span("optional", className="af-step__tag")
                        if not step.required
                        else None
                    ),
                ],
                className="af-step__text",
            ),
        ],
        id={"type": JUMP, "index": index},
        className=f"af-step af-step--{zustand}",
        n_clicks=0,
        title=f"Schritt {index + 1} ({klartext}): {step.title}",
        **{"aria-current": "step" if zustand == "current" else None},
    )


def rail(current: int | None, besucht: set[int] | None = None) -> html.Div:
    """Alle Schritte auf einen Blick — wo man ist, was war, und was übergangen wurde.

    Auf dem Einstieg ist noch kein Schritt offen; die Liste steht dann zwar im
    DOM (ihre Sprungknöpfe sind Eingänge), aber unsichtbar — eine Schrittliste
    ohne aktuellen Schritt beantwortet keine Frage.
    """

    gesehen = besucht or set()
    uebersprungen = sum(
        1 for i in range(len(STEPS)) if _zustand(i, current, gesehen) == "uebersprungen"
    )

    return html.Div(
        [
            html.P("Ihre Schritte", className="af-step__heading"),
            html.Div(
                [_rail_entry(i, step, current, gesehen) for i, step in enumerate(STEPS)],
                className="af-steps",
            ),
            # Nur wenn es etwas zu sagen gibt. Eine Zeile, die immer dasteht und
            # meistens «0 übersprungen» meldet, liest nach dem zweiten Mal
            # niemand mehr.
            (
                html.P(
                    (
                        f"{uebersprungen} übersprungen"
                        if uebersprungen > 1
                        else "1 Schritt übersprungen"
                    ),
                    className="af-step__hinweis",
                )
                if uebersprungen
                else None
            ),
        ],
        id=RAIL,
        className="af-wizard__rail",
        style=_HIDDEN if is_entry(current) else _VISIBLE,
    )


# --- Der Schritt selbst ----------------------------------------------------


def _final_step(draft: dict) -> html.Div:
    """Der letzte Blick vor dem Start.

    Der Ausgang — starten — steht **nicht** hier, sondern in der
    Navigationsleiste (gesichert wird seit P7.4-U4.5 oben rechts):
    Dort sitzt auf jedem Schritt der nächste Griff,
    und der letzte Schritt soll keine Ausnahme sein. Technisch kommt dazu, dass
    die Leiste immer im DOM liegt; ein Knopf, den es nur auf einem Schritt gibt,
    legte jeden Callback lahm, der ihn als Eingang führt.
    """

    return html.Div(
        [
            # **Der Name des Laufs steht hier** (P1.9-W4.1), und zwar als
            # Erstes. Er lag bis dahin im optionalen Schritt «Lauf & Ablage»,
            # an dem drei von vier Wegen vorbeiführen: «Szenario-Vergleich»,
            # «Weiterverwenden» und «Direkt zum Start» landen unmittelbar hier.
            # Alle Läufe hießen deshalb «Flugverkehr Szenarioplanung MVP», und
            # die Run-Liste war nach kurzer Zeit unbrauchbar.
            #
            # Dieser Schritt ist der einzige, den **jeder** Weg passiert — der
            # Name gehört deshalb hierher und nirgendwo anders hin.
            # Knopf **neben** dem Feld, nicht darunter: Eine eigene Zeile kostete
            # 0,07 Bildschirme auf dem einen Schritt, den jeder Weg passiert.
            # **Ohne Kartenrahmen seit P7.4-U4.4**: Er kostete 48 px Polsterung um
            # ein einziges Feld.
            html.Div(
                [
                    c.text(
                        "simulation_name",
                        draft.get("simulation_name", ""),
                        label="Name dieses Laufs",
                        hint="So erscheint er später in der Auswahl der Kopfzeile.",
                        class_name="flex-1 min-w-[16rem]",
                    ),
                    html.Div(
                        ui.button(
                            "Vorschlag",
                            id=c.action_id("suggest-name"),
                            variant="secondary",
                            icon_name="auto_awesome",
                        ),
                        className="af-neben-feld",
                    ),
                ],
                className="flex items-start gap-4 flex-wrap mb-4",
            ),
            # **Was abweicht, steht im Preflight an seiner Stelle** (P7.4-U4.4): nach
            # den Werten und vor den Hinweisen, statt ganz unten.
            start_flow.preflight(
                draft,
                start_flow.errors_for(draft),
                slot="wizard",
                abweichungen=delta.layout(draft),
            ),
        ]
    )


def heading(current: int | None) -> html.Div:
    """Die Überschrift des Bereichs — **nur auf dem Einstieg** (P1.9-W3.5).

    Dort beantwortet sie eine echte Frage: Womit fange ich an? In der
    Schrittfolge tat sie das nicht mehr. Sie sagte auf **jedem** der sieben
    Schritte dasselbe («Beantworten Sie eine Frage nach der anderen. Drei
    genügen …») — eine Einführung, die man einmal liest und danach sechsmal
    überspringt, während direkt darunter «Schritt 4 von 7» und der Titel der
    Frage stehen.

    Gemessen kostete sie mit ihrem Abstand **116 px auf jedem Schritt**. Bei
    einem Rahmen von 327 px und einem sichtbaren Bereich von 744 px ist das
    keine Kleinigkeit: Es war das größte einzelne Stück des Rahmens, und der
    Rahmen kostete auf fünf von sieben Schritten mehr als der Inhalt.

    Der Titel der Frage trägt seither die `h1` (siehe `content`) — der Bereich
    verliert damit keine Überschrift, sie steht nur dort, wo sie etwas sagt.
    """

    if is_entry(current):
        return ui.page_heading(
            "Lauf einrichten",
            "Womit möchten Sie anfangen? Jeder Weg führt zum selben Ziel — nur über "
            "unterschiedlich viele Fragen.",
        )
    return html.Div()


def grid_class(current: int | None) -> str:
    """Ob das Raster eine Spalte für die Schrittliste vorhält (W5.4).

    **Am Einstieg gibt es keine Liste** — und bis W5.4 trotzdem ihre Spalte:
    gemessen `grid-template-columns: 240px 760px` bei 1040 px Zone, während die
    Liste dort `display: none` war. 240 px Leere links neben der Frage, mit der
    alles anfängt.

    Die Klasse gehört an den Callback, der den Schritt wechselt, nicht ans
    erste Zeichnen: `layout` läuft einmal: Beim ersten Anlauf blieb der Einstieg
    danach auf **jedem** Schritt gesetzt, und die Spalte war überall 1040 px
    breit. Gemessen, nicht vermutet.
    """

    return "af-wizard af-wizard--einstieg" if is_entry(resolve(current)) else "af-wizard"


def content(draft: dict, current: int) -> html.Div:
    """Der offene Schritt — und **nur** er.

    Alle anderen bleiben aus dem DOM: Ihre Felder tragen dieselben Pattern-IDs,
    und zweimal dieselbe ID ist für Dash ein Laufzeitfehler.
    """

    step = STEPS[current]
    koerper = _final_step(draft) if step.body is None else step.body(draft)

    return html.Div(
        [
            html.Div(
                [
                    html.P(
                        f"Schritt {current + 1} von {len(STEPS)}",
                        className="af-wizard__counter",
                    ),
                    # **`h1`, seit die Bereichsüberschrift in der Schrittfolge
                    # entfällt** (W3.5). Der Titel der Frage *ist* die
                    # Überschrift dieses Bildschirms — die Klasse bleibt `H2`,
                    # weil sich an der Optik nichts ändern soll. Größe und
                    # Rangordnung sind zwei verschiedene Dinge.
                    html.H1(
                        step.title,
                        className=ui.H2,
                        # Fokusziel nach einem Schrittwechsel (W5.3). Ohne
                        # `tabIndex` lässt sich eine Überschrift nicht
                        # fokussieren; `-1` heißt «per Skript, nicht per Tab»
                        # — sie soll nicht in die Tabreihenfolge geraten.
                        tabIndex=-1,
                    ),
                    # **Die Lede ist Fliesstext** (2026-09-12). Bis dahin
                    # stand sie in `ui.CAPTION`, also in der Rolle einer
                    # Bildunterschrift bei 12 px -- und war damit gemessen der
                    # schmalste Text des Bildschirms: 409 px von 760, weil
                    # 12-px-Prosa fuer 75 Zeichen nur 416 px braucht. Sie
                    # teilt jetzt die Groesse des Textes, den sie einleitet.
                    html.P(step.lede, className=f"{ui.LEDE} mt-1"),
                ],
                className="mb-6",
            ),
            html.Div(koerper, id="wizard-body"),
        ],
        id=CONTENT,
        className="af-wizard__content",
    )


def navigation(current: int | None) -> html.Div:
    """«Zurück» und «Weiter» — und der Weg am Feinschliff vorbei.

    Der Abkürzungsknopf steht ab Schritt drei: Dort sind die drei Entscheidungen
    aus P1.1 getroffen, und alles Weitere ist mit sinnvollen Werten vorbelegt.
    Ohne ihn erzwänge die Schrittfolge acht Stationen für einen Lauf, der mit
    drei auskommt.

    Auf dem Einstieg ist die ganze Leiste unsichtbar — dort gibt es kein
    «Weiter», sondern drei Wege. Im DOM bleibt sie trotzdem, siehe unten.
    """

    einstieg = is_entry(current)
    current = 0 if einstieg else current
    letzter = current >= FINAL
    # **Alle drei Knöpfe bleiben im DOM**, auch wo sie nichts zu tun haben — sie
    # werden nur ausgeblendet. Dash führt einen Callback gar nicht erst aus,
    # wenn auch nur *ein* Eingang fehlt: Auf Schritt 1 gab es «Direkt zum Start»
    # nicht, und damit war die ganze Navigation tot, «Weiter» eingeschlossen. Am
    # laufenden System aufgefallen — der Zähler blieb bei «Schritt 1 von 8», und
    # der Browser meldete «A nonexistent object was used in an Input».
    #
    # Dasselbe Muster wie bei den vier Viewport-Bereichen in `app.py`: im Layout
    # bleiben, Sichtbarkeit umschalten.
    return html.Div(
        [
            # **Auch auf dem ersten Schritt bedienbar.** Er führt dort auf den
            # Einstieg zurück — ohne das wäre die Schrittfolge eine Sackgasse,
            # aus der man nur über einen Neuladen wieder herauskommt. Auf dem
            # Einstieg selbst ist die ganze Leiste unsichtbar.
            ui.button("Zurück", id=BACK, variant="ghost"),
            # Die Begründung sitzt zwischen «Zurück» und dem nächsten Griff:
            # dort, wo der Blick ohnehin hinfällt, wenn der Knopf nicht reagiert.
            html.Div(
                id=GATE,
                className="af-wizard__gate",
                # Der Grund, warum «Weiter» nicht reagiert, gehört zu den
                # Dingen, die man **sofort** wissen muss — sonst drückt man
                # weiter auf einen Knopf, der nichts tut.
                **{"aria-live": "assertive"},
            ),
            html.Div(
                [
                    ui.button(
                        "Direkt zum Start",
                        id=SKIP,
                        variant="secondary",
                        icon_name="fast_forward",
                        # Auf schmaler Breite nur das Symbol: Drei ausgeschriebene
                        # Beschriftungen passen bei 375 px nicht nebeneinander, und
                        # die Leiste brach auf 133 px um (W5.5).
                        className="af-btn--symbol-schmal",
                        title="Direkt zum Start",
                        style=None if LAST_REQUIRED <= current < FINAL else {"display": "none"},
                    ),
                    ui.button(
                        "Weiter",
                        id=NEXT,
                        icon_name="arrow_forward",
                        style=None if not letzter else {"display": "none"},
                    ),
                    ui.button(
                        "Lauf starten",
                        id=START,
                        icon_name="play_arrow",
                        style=None if letzter else {"display": "none"},
                    ),
                ],
                className="flex items-center gap-3",
            ),
        ],
        className="af-wizard__nav",
        style=_HIDDEN if einstieg else _VISIBLE,
    )


def layout(draft: dict, current: int | None = ENTRY) -> html.Div:
    """Der Bereich «Einrichten» — Einstieg und Schrittfolge in einem Baum.

    **Beide stehen immer im DOM**, umgeschaltet wird nur die Sichtbarkeit. Die
    drei Wege des Einstiegs sind Eingänge desselben Callbacks wie «Weiter» und
    «Zurück»; ein Weg, den es auf Schritt 3 nicht gäbe, nähme die ganze
    Navigation mit — derselbe Fallstrick, der in P1.7 schon einmal «Weiter»
    stillgelegt hat. Dasselbe Muster wie bei den vier Viewport-Bereichen in
    `app.py`.
    """

    current = resolve(current)
    einstieg = is_entry(current)
    return html.Div(
        [
            html.Div(heading(current), id=HEAD_HOST),
            # Die Ansage steht **außerhalb** des Inhalts, der beim Wechsel
            # ausgetauscht wird — siehe `ANSAGE`.
            html.Div(
                id=ANSAGE,
                className="af-nur-vorlesen",
                **{"aria-live": "polite", "aria-atomic": "true"},
            ),
            # Statusmeldungen werden ebenfalls angesagt. `polite` und nicht
            # `assertive`: Sie melden, was gerade geschehen **ist** — sie
            # unterbrechen nicht, was jemand gerade tut.
            html.Div(id="cfg-status", className="mb-4", **{"aria-live": "polite"}),
            # Senke für den Sprung nach oben. Ein clientseitiger Callback braucht
            # einen Ausgang, hat hier aber nichts zu schreiben — er scrollt nur.
            dcc.Store(id=SCROLL_SINK),
            html.Div(
                [
                    html.Div(rail(current, _besucht_aus(None, current)), id=RAIL_HOST),
                    html.Div(
                        [
                            html.Div(
                                entry(draft),
                                id=ENTRY_HOST,
                                style=_VISIBLE if einstieg else _HIDDEN,
                            ),
                            html.Div(
                                content(draft, 0 if einstieg else current),
                                id=CONTENT_HOST,
                                style=_HIDDEN if einstieg else _VISIBLE,
                            ),
                            # Das Kleben sitzt am **Wirt**, nicht an der
                            # Navigation darin: Ein klebendes Element bewegt
                            # sich nur innerhalb seines Elternkastens, und der
                            # Wirt ist exakt so hoch wie sein Inhalt -- damit
                            # gaebe es null Spielraum. Am laufenden System
                            # gemessen: «Weiter» lag trotz `sticky` bei y=1361.
                            html.Div(
                                navigation(current),
                                id=NAV_HOST,
                                className="af-wizard__navhost",
                            ),
                        ],
                        className="af-wizard__main",
                    ),
                ],
                id=GRID,
                className=grid_class(current),
            ),
        ],
        className="af-pane af-pane--focus",
    )


# --- Callbacks -------------------------------------------------------------


def register_callbacks(app) -> None:
    @app.callback(
        Output(STEP_STORE, "data"),
        Output(STORE_ID, "data", allow_duplicate=True),
        Output(VISITED_STORE, "data"),
        Output(HISTORY_STORE, "data"),
        Input(BACK, "n_clicks"),
        Input(NEXT, "n_clicks"),
        Input(SKIP, "n_clicks"),
        Input(WAY_NEW, "n_clicks"),
        Input(WAY_SWEEP, "n_clicks"),
        Input(WAY_RESUME, "n_clicks"),
        Input({"type": JUMP, "index": ALL}, "n_clicks"),
        # Ein Hinweis im Prüfschritt führt zu seinem Schritt (P7.4-U4.4).
        Input({"type": start_flow.SPRUNG, "schritt": ALL}, "n_clicks"),
        State(STEP_STORE, "data"),
        State(STORE_ID, "data"),
        State(VISITED_STORE, "data"),
        State(HISTORY_STORE, "data"),
        prevent_initial_call=True,
    )
    def _navigate(
        _back, _next, _skip, _new, _sweep, _resume, _jump, _sprung, current, draft, besucht, verlauf
    ):
        """Alle Wege durch die Schrittfolge in einem Callback.

        Getrennte Callbacks müssten sich denselben Ausgang teilen und würden
        sich beim gleichzeitigen Feuern überschreiben — dieselbe Begründung wie
        bei den sechs Knöpfen der Zeitleiste.

        **Der zweite Ausgang ist die Ausnahme, nicht die Regel.** Werte fließen
        in dieser Oberfläche vom Feld in den Store und nicht zurück (Regel 2 der
        Architektur-Map). Die beiden Wege des Einstiegs schreiben trotzdem — sie
        *sind* die Entscheidung «ein Lauf» oder «alle Szenarien», und es gibt
        kein Feld, das sie träfe: Das Kästchen dafür liegt hinter der
        Feinabstimmung des zweiten Schritts. Geschrieben wird genau ein Feld,
        und nur, während der Einstieg auf dem Schirm steht — nie unter einem
        sichtbaren Eingabefeld hindurch.
        """

        jetzt = resolve(current)
        ausgeloest = ctx.triggered_id
        gesehen = _besucht_aus(besucht, jetzt)
        stapel = list(verlauf or [])

        def gehe(ziel, entwurf=no_update):
            """Ans Ziel — der verlassene Schritt gilt als besucht und kommt auf den Stapel.

            **Besucht wird der verlassene, nicht das Ziel.** Wer über die Liste
            auf Schritt 7 springt, hat 7 noch nicht gesehen; er sieht ihn im
            nächsten Augenblick. `_besucht_aus` nimmt den offenen Schritt beim
            Zeichnen ohnehin dazu — hier wäre es eine zweite, leicht
            auseinanderlaufende Buchführung.
            """

            return ziel, entwurf, sorted(gesehen), [*stapel, jetzt]

        def zurueck():
            """Dorthin, wo man hergekommen ist — und den Schritt vom Stapel nehmen.

            Ist der Stapel leer, führt «Zurück» auf den Einstieg. Das ist keine
            Notlösung, sondern die richtige Antwort: Wer keinen Weg hinter sich
            hat, steht am Anfang.
            """

            if not stapel:
                return ENTRY, no_update, sorted(gesehen), []
            return resolve(stapel[-1]), no_update, sorted(gesehen), stapel[:-1]

        if isinstance(ausgeloest, dict) and ausgeloest.get("type") == start_flow.SPRUNG:
            if not any(eintrag["value"] for eintrag in ctx.triggered if eintrag["value"]):
                return no_update, no_update, no_update, no_update
            ziel = next(
                (i for i, step in enumerate(STEPS) if step.key == ausgeloest.get("schritt")), None
            )
            if ziel is None:
                return no_update, no_update, no_update, no_update
            return gehe(ziel)

        if isinstance(ausgeloest, dict) and ausgeloest.get("type") == JUMP:
            # Nur ein wirklich gedrückter Knopf zählt: Beim Neuaufbau der Liste
            # feuert Dash alle Pattern-Eingänge mit `None`.
            if not any(eintrag["value"] for eintrag in ctx.triggered if eintrag["value"]):
                return no_update, no_update, no_update, no_update
            return gehe(clamp(ausgeloest.get("index")))

        # **Die drei Wege fangen neu an.** Besuchtes und Verlauf werden
        # zurückgesetzt: Wer vom Einstieg aus startet, trüge sonst Häkchen aus
        # dem vorigen Anlauf, und «Zurück» führte in einen Weg, den es nicht
        # mehr gibt. Der Stapel beginnt beim Einstieg, weil man von dort kommt.
        if ausgeloest == WAY_NEW:
            return 0, _with_sweeps(draft, False), [], [ENTRY]
        if ausgeloest == WAY_SWEEP:
            return FINAL, _with_sweeps(draft, True), [], [ENTRY]
        if ausgeloest == WAY_RESUME:
            # Weiterverwenden heißt anfassen lassen: kein Schreiben, nur der
            # Sprung ans Ende.
            return FINAL, no_update, [], [ENTRY]

        if ausgeloest == BACK:
            return zurueck()
        if ausgeloest == NEXT:
            return gehe(min(FINAL, (0 if jetzt is ENTRY else jetzt) + 1))
        if ausgeloest == SKIP:
            return gehe(FINAL)
        return no_update, no_update, no_update, no_update

    @app.callback(
        Output(CONTENT_HOST, "children"),
        Output(RAIL_HOST, "children"),
        Output(NAV_HOST, "children"),
        Output(HEAD_HOST, "children"),
        Output(ENTRY_HOST, "children"),
        Output(ENTRY_HOST, "style"),
        Output(CONTENT_HOST, "style"),
        Output(ANSAGE, "children"),
        Output(GRID, "className"),
        Input(STEP_STORE, "data"),
        Input("cfg-editor-refresh", "data"),
        State(STORE_ID, "data"),
        State(VISITED_STORE, "data"),
    )
    def _render(step, _refresh, draft: dict | None, besucht):
        """Den offenen Schritt zeichnen — Inhalt, Liste und Fußzeile in einem Zug.

        In **einem** Callback, weil alle drei denselben Stand zeigen: Getrennt
        könnten sie für einen Moment auseinanderlaufen und die Liste einen
        anderen Schritt hervorheben als den, der zu sehen ist.

        Nicht am Entwurf hängend: Der Schritt enthält Eingabefelder, und die
        dürfen nicht unter den Fingern ausgetauscht werden. Was sich laufend
        ändert, steht in den Slots, die `_live` füllt.

        **Den Sprung nach oben macht der Callback darunter**, clientseitig: Der
        Server hat dazu nichts beizutragen, und ein Rundlauf machte ihn träge.
        Ohne ihn stand man nach «Weiter» mitten im neuen Schritt — die
        Bildlaufhöhe des vorigen bleibt sonst erhalten, und gerade der lange
        vierte Schritt setzte einen weit unterhalb seiner Überschrift ab.
        """

        jetzt = resolve(step)
        data = draft or {}
        einstieg = is_entry(jetzt)
        return (
            content(data, 0 if einstieg else jetzt),
            rail(jetzt, _besucht_aus(besucht, jetzt)),
            navigation(jetzt),
            heading(jetzt),
            # Der Einstieg wird nur gebaut, wenn er zu sehen ist: `touched`
            # vergleicht gegen den Auslieferungszustand und liest dafür fünf
            # Config-Dateien. Das je Schrittwechsel zu tun wäre Arbeit für einen
            # Bildschirm, den niemand ansieht.
            entry(data) if einstieg else no_update,
            _VISIBLE if einstieg else _HIDDEN,
            _HIDDEN if einstieg else _VISIBLE,
            (
                "Einstieg: Womit möchten Sie anfangen?"
                if einstieg
                else f"Schritt {jetzt + 1} von {len(STEPS)}: {STEPS[jetzt].title}"
            ),
            grid_class(jetzt),
        )

    app.clientside_callback(
        """
        function (inhalt) {
            var pane = document.querySelector(".af-shell__main");
            if (pane) {
                var sanft = !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
                pane.scrollTo({ top: 0, behavior: sanft ? "smooth" : "auto" });
            }
            // **Der Fokus wandert mit** (P1.9-W5.3). Ohne das blieb er nach
            // «Weiter» auf dem Knopf, der gerade verschwunden war -- der
            // Browser setzt ihn dann auf den Seitenanfang zurueck, und wer mit
            // der Tastatur arbeitet, taste sich durch die halbe Seite bis zur
            // naechsten Frage. Der Titel des Schritts ist die Antwort auf die
            // Frage "wo bin ich jetzt".
            //
            // **An der Aenderung, nicht am Bildtakt** (P1.9-W5.3). Zwei
            // Anlaeufe davor haben nicht gegriffen, und beide aus demselben
            // Grund: Sie rieten, wann der neue Baum steht.
            //
            // Zuerst hing der Callback am Schritt-Store -- der aendert sich beim
            // Klick, der Inhalt kommt erst mit der Antwort des Servers. Dann am
            // Inhalt, aber der Fokus lief ueber requestAnimationFrame, und der
            // feuert in einem Tab, den niemand sieht, **gar nicht**: Am
            // laufenden System stand `visibilityState: "hidden"`, der Scroll
            // daneben lief (er ist synchron), und in drei Sekunden kam kein
            // einziges Bild. Ein Nutzer sieht seinen Tab meistens -- aber eine
            // Zusage, die von der Sichtbarkeit abhaengt, ist keine.
            //
            // Ein MutationObserver haengt an dem Ereignis, um das es geht: dass
            // der Inhalt ausgetauscht wurde. Er feuert auch ohne Zeichnen, und
            // er feuert genau dann, wenn es die neue Ueberschrift gibt.
            //
            // **Das Fenster ist bewusst weit, die Wache davor bewusst eng.** Mit
            // 600 ms sassen sechs der sieben Schritte -- "Pruefen & Starten"
            // nicht: Vorschau und Zeitschaetzung zeichnen dort nach, und der
            // letzte Austausch kam, als das Fenster schon zu war. Laenger zu
            // lauschen ist nur dann harmlos, wenn dabei niemandem etwas
            // weggenommen wird: Genommen wird der Fokus deshalb ausschliesslich,
            // wenn ihn **niemand haelt** -- BODY, gar nichts, oder ein Knoten,
            // den der Austausch gerade aus dem Dokument entfernt hat. Wer selbst
            // irgendwohin geklickt oder getabbt ist, behaelt seinen Platz, und
            // wer schon auf der Ueberschrift steht, wird nicht erneut angefasst.
            var wirt = document.getElementById("wizard-content-host");
            if (wirt) {
                var setzen = function () {
                    var aktiv = document.activeElement;
                    var frei = !aktiv || aktiv === document.body || !document.contains(aktiv);
                    if (!frei) { return; }
                    var titel = wirt.querySelector("h1");
                    if (titel) { titel.focus({ preventScroll: true }); }
                };
                var beob = new MutationObserver(setzen);
                beob.observe(wirt, { childList: true, subtree: true });
                window.setTimeout(function () { beob.disconnect(); }, 2500);
                // Falls der Baum schon steht, bevor dieser Callback laeuft.
                setzen();
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output(SCROLL_SINK, "data"),
        # **Am Inhalt, nicht am Schritt-Store** (P1.9-W5.3). Der Store ändert
        # sich, sobald jemand klickt — der neue Inhalt kommt erst mit der
        # Antwort des Servers. Am Store hängend fokussierte der Callback die
        # Überschrift des **alten** Schritts, die im selben Moment verschwand;
        # am laufenden System stand der Fokus danach auf `BODY`. Der Wirt des
        # Inhalts ändert sich genau dann, wenn es etwas zu fokussieren gibt.
        Input(CONTENT_HOST, "children"),
        prevent_initial_call=True,
    )
