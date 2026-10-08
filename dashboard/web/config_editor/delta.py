"""Was am Entwurf vom Auslieferungszustand abweicht (P1.9-W4.2).

Der Prüfschritt zeigte einen Satz und sechs Kacheln — aber nicht, **was man
geändert hat**. Bei über hundert Eingabefeldern über sieben Schritte und einen
Modell-Bereich ist das die einzige Frage, die vor einem Start wirklich zählt,
und die einzige, auf die es ohne diese Ansicht keine Antwort gab. Der einzige
Umkehrmechanismus war «Auf Standard zurücksetzen», und der wirft alles weg.

**Verglichen wird gegen den Auslieferungszustand**, nicht gegen «vorher»: Ein
Entwurf hat keine Geschichte, er hat einen Ausgangspunkt. Dieselbe Quelle wie
`touched()` — `initial_draft_dict()`.

**Verschachteltes wird gezählt, nicht aufgezählt.** Dreizehn Systemgrößen mit je
Startwert, Regeln und Schalter ergäben Dutzende Zeilen und keinen Überblick. Wer
wissen will, *welche* Größe sich geändert hat, sieht im Modell nach; hier zählt,
**dass** etwas abweicht und wie viel.
"""

from __future__ import annotations

from dataclasses import dataclass

from dash import html

from dashboard.web import components as ui
from dashboard.web.config_editor import glossary

#: Eine Rücknahme. Pattern-ID, weil es je Abweichung eine gibt.
REVERT = "cfg-revert"


def revert_id(feld: str) -> dict:
    return {"type": REVERT, "feld": feld}


@dataclass(frozen=True)
class Abweichung:
    """Ein Unterschied zum Auslieferungszustand, in Klartext."""

    feld: str
    was: str
    vorher: str
    jetzt: str


#: Felder, die **den Startpfad wählen** statt ihn zu parametrisieren. Sie stehen
#: nicht in der Liste: «Sie haben den Szenario-Vergleich gewählt» ist keine
#: Abweichung, sondern der Satz, der ohnehin über der Liste steht.
PFADWAHL = {"run_all_sweeps", "scenario_mode", "sweep_id", "resume_from"}

#: Verschachtelte Strukturen. Je Eintrag: wie sie in Klartext heißen und wie ihre
#: Anzahl zu benennen ist.
VERSCHACHTELT = {
    "property_edits": ("Systemgrößen", "geändert"),
    "abweichungen": ("Verläufe", "geändert"),
    "modellannahmen": ("Modellannahmen", "geändert"),
    "population_edits": ("Bevölkerungssegmente", "geändert"),
    "market_feedback_edit": ("Preisbildung", "geändert"),
    "saturation_edit": ("Sättigung", "geändert"),
}


#: **Der Rechenmodus ist eine Wahl aus zwei Schaltern** — und steht deshalb als
#: eine Abweichung da, mit dem gewählten Modus beim Namen (Abnahme V6,
#: 2026-09-30). Bis dahin stand jeder Schalter für sich, mit seinem eigenen
#: Namen: Wer «Mit Sprachmodell» wählte, schaltete `mock_llm` aus und las in der
#: Liste «Rechenmodus ‹Ohne Sprachmodell›» — das Gegenteil seiner Wahl.
RECHENMODUS = "rechenmodus"
RECHENMODUS_FELDER = ("mock_llm", "deterministic_only")


def rechenmodus(werte: dict) -> str:
    """Wie der Rechenmodus eines Entwurfs heißt — dieselben drei Namen wie in Schritt 5."""

    if werte.get("deterministic_only"):
        return "Nur Zahlen"
    if werte.get("mock_llm"):
        return "Ohne Sprachmodell"
    return "Mit Sprachmodell"


def _klartext(wert: object) -> str:
    if wert is None or wert == "":
        return "—"
    if wert is True:
        return "an"
    if wert is False:
        return "aus"
    return str(wert)


def _name(feld: str) -> str:
    param = glossary.get(feld)
    return param.full_label() if param else feld


def _zaehle_unterschiede(vorher: object, jetzt: object) -> int:
    """Wie viele Einträge einer verschachtelten Struktur abweichen."""

    if isinstance(vorher, dict) and isinstance(jetzt, dict):
        schluessel = set(vorher) | set(jetzt)
        return sum(1 for k in schluessel if vorher.get(k) != jetzt.get(k))
    if isinstance(vorher, list) and isinstance(jetzt, list):
        if len(vorher) != len(jetzt):
            return abs(len(vorher) - len(jetzt)) + sum(1 for a, b in zip(vorher, jetzt) if a != b)
        return sum(1 for a, b in zip(vorher, jetzt) if a != b)
    return 1


def unterschiede(draft: dict) -> list[Abweichung]:
    """Alle Abweichungen vom Auslieferungszustand."""

    from dashboard.web.state import initial_draft_dict

    standard = initial_draft_dict()
    gefunden: list[Abweichung] = []

    for feld in sorted(set(standard) | set(draft or {})):
        if feld in PFADWAHL or feld in RECHENMODUS_FELDER:
            continue
        alt, neu = standard.get(feld), (draft or {}).get(feld)
        if alt == neu:
            continue

        if feld in VERSCHACHTELT:
            wort, verb = VERSCHACHTELT[feld]
            anzahl = _zaehle_unterschiede(alt, neu)
            gefunden.append(
                Abweichung(
                    feld,
                    wort,
                    "wie ausgeliefert",
                    f"{anzahl} {verb}" if anzahl != 1 else f"1 {verb.rstrip('t')}t",
                )
            )
            continue

        gefunden.append(Abweichung(feld, _name(feld), _klartext(alt), _klartext(neu)))

    vorher, jetzt = rechenmodus(standard), rechenmodus(draft or {})
    if vorher != jetzt:
        gefunden.append(Abweichung(RECHENMODUS, "Rechenmodus", vorher, jetzt))

    return sorted(gefunden, key=lambda abweichung: abweichung.feld)


def _zeile(abweichung: Abweichung) -> html.Div:
    return html.Div(
        [
            html.Div(
                [
                    html.Span(abweichung.was, className="af-delta__was"),
                    html.Span(
                        f"{abweichung.vorher} → {abweichung.jetzt}",
                        className="af-delta__wert",
                    ),
                ],
                className="min-w-0",
            ),
            ui.button(
                "Zurücknehmen",
                id=revert_id(abweichung.feld),
                variant="ghost",
                className=f"!px-2 !py-1 {ui.KLEIN} shrink-0",
            ),
        ],
        className="af-delta__zeile",
    )


def layout(draft: dict) -> object:
    """Die Liste — oder ein Satz, wenn nichts abweicht.

    Sie steht hinter einer Klappe: Im Normalfall hat man ein oder zwei Dinge
    geändert und weiß es; die Zahl im Deckel genügt dann. Wer nach vier Wochen
    einen Entwurf aus der Sitzung wiederfindet, klappt auf.
    """

    abweichungen = unterschiede(draft)
    if not abweichungen:
        return ui.hinweis(
            "Der Lauf verwendet durchgehend die ausgelieferten Werte — es gibt nichts, "
            "was Sie beim Vergleich mit einem anderen Lauf berücksichtigen müssten.",
            "kontext",
            icon_name="check_circle",
        )

    return ui.expert(
        html.Div([_zeile(a) for a in abweichungen], className="af-delta"),
        count=len(abweichungen),
        einheit=("Abweichung", "Abweichungen"),
        title="Was von der Auslieferung abweicht",
        names=", ".join(a.was for a in abweichungen[:4]) + (" …" if len(abweichungen) > 4 else ""),
    )


def zuruecknehmen(draft: dict, feld: str) -> dict:
    """Ein Feld auf den Auslieferungszustand zurücksetzen — nur dieses eine.

    Der Gegenentwurf zu «Auf Standard zurücksetzen», das alles verwirft. Wer
    eine einzelne Änderung rückgängig machen wollte, musste bis hierher wissen,
    welcher Wert vorher dort stand.
    """

    from dashboard.web.state import initial_draft_dict

    standard = initial_draft_dict()
    if feld == RECHENMODUS:
        for schalter in RECHENMODUS_FELDER:
            draft[schalter] = standard[schalter]
    elif feld in standard:
        draft[feld] = standard[feld]
    else:
        draft.pop(feld, None)
    return draft
