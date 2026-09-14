"""Der geführte Weg von «Was rechnen wir?» bis «Lauf läuft» (P1.1).

Drei Entscheidungen, mehr braucht niemand bis zum Start: **womit** gerechnet
wird (Standard-Ausgangslage, eines der Presets aus `configs/sweeps/`, oder die
eigenen Einstellungen aus dem Editor), **wie weit** der Lauf reicht, und
**wie** gerechnet wird. Alles andere liegt hinter «Feinabstimmung» oder unten
im Editor und ist mit sinnvollen Werten vorbelegt.

Bis P1.1 stand hier ein Editor mit sechs Tabs, in dem diese drei Fragen
zwischen rund sechzig anderen Feldern lagen. Die Presets — der schnellste Weg
zu einem sinnvollen Lauf — steckten in einem Auswahlfeld im ersten Tab, und die
Erklärungen zu jedem Parameter standen auf einer eigenen Dokumentationsseite,
also nicht dort, wo entschieden wird.

Zwei Dinge zur Mechanik:

* Die Felder hier tragen dieselben Pattern-Matching-IDs wie die im Editor und
  fließen durch denselben `_sync`-Callback in den Store. Ein Feld darf deshalb
  **nicht** doppelt gerendert werden — der geführte Block steht dauerhaft im
  DOM, der aktive Tab ebenfalls, und Dash quittiert doppelte IDs mit einem
  Fehler. Was hier steht, ist aus den Tabs entfernt.
* Was sich mit dem Entwurf ändern muss (die Beschreibung des gewählten
  Szenarios, der Preflight, die Feldfehler), steht in Slots, die ein Callback
  nachfüllt. Der Block selbst wird nicht neu gebaut.
"""

from __future__ import annotations

import re
from dataclasses import asdict

from dash import html

from dashboard.config_catalog import (
    PROPERTY_LABELS,
    issues_by_field,
    list_sweep_presets,
    rahmenszenarien,
    unfielded_issues,
    validate_draft,
)
from dashboard.web import components as ui
from dashboard.web import formate
from dashboard.web.config_editor import compute_mode, dauer
from dashboard.web.config_editor import controls as c
from dashboard.web.state import draft_from_dict
from src.config_loader import load_properties_config
from src.models.state_models import DEFAULT_SEED
from src.orchestration.scenario_sweeps import (
    SWEEP_SEED,
    SZENARIOTEXT_NUTZT_LLM,
    vorgegebene_felder,
)
from src.validation import horizontluecken

#: Die Szenario-Auswahl ist kein Draft-Feld: aus ihr folgen `scenario_mode` und
#: `sweep_id`. Dieselbe Übersetzung wie beim Rechenmodus, aus demselben Grund —
#: eine Entscheidung, zwei Felder.
FIELD = "scenario_choice"
FIELD_ID = {"type": c.CFG, "field": FIELD}

STANDARD = "basis"
CUSTOM = "custom"

#: Bereiche, die ein Callback nachfüllt, sobald sich der Entwurf ändert.
SLOT = "start-slot"

#: Der Klartext-Satz steht an zwei Stellen (geführter Block und Editor) und muss
#: an beiden mitlaufen — Pattern-Matching-ID, weil das Ziel fehlen darf.
SUMMARY = "cfg-summary"


def slot_id(name: str) -> dict:
    return {"type": SLOT, "slot": name}


def summary_id(slot: str) -> dict:
    return {"type": SUMMARY, "slot": slot}


#: Der Wirt des Auswahlfelds in Schritt 1 — neu gezeichnet, wenn jemand die
#: Stresstests ein- oder ausblendet (P7.4-U4.1).
LISTE = "start-szenarioliste"

#: Der Knopf «Stresstests zeigen». **Keine Konfigurationskennung**: Er schreibt
#: nichts in den Entwurf und ist damit keine vierte Entscheidung (P1.1).
STRESS_TOGGLE = "start-stresstests"


def liste_id(slot: str) -> dict:
    return {"type": LISTE, "slot": slot}


def stress_toggle_id(slot: str) -> dict:
    return {"type": STRESS_TOGGLE, "slot": slot}


# --- Auswahl ⇄ Entwurf -----------------------------------------------------


def of(draft: dict) -> str:
    """Aus dem Entwurf die aktuelle Auswahl ableiten."""

    if draft.get("scenario_mode") == "sweep" and draft.get("sweep_id"):
        return str(draft["sweep_id"])
    if draft.get("scenario_mode") == CUSTOM:
        return CUSTOM
    return STANDARD


def apply(draft: dict, choice: str | None) -> dict:
    """Auswahl zurück in `scenario_mode` und `sweep_id` schreiben.

    Die **Länge** wird hier bewusst nicht mitgezogen, obwohl jedes Preset eine
    mitbringt. Werte fließen in dieser Oberfläche in genau eine Richtung: vom
    Feld in den Store. Ein Feld von hier aus zu setzen hieße, dieselbe Zahl an
    zwei Stellen zu führen — der Eingabewert schriebe sie beim nächsten
    Abgleich sofort wieder zurück, und im Fenster stünde eine andere Zahl als
    im Lauf. Wie lange gerechnet wird, bleibt eine sichtbare Entscheidung des
    zweiten Schritts; die Länge, auf die ein Szenario angelegt ist, steht als
    Hinweis daneben.
    """

    if choice == CUSTOM:
        draft["scenario_mode"] = CUSTOM
        draft["apply_custom_overrides"] = True
    elif not choice or choice == STANDARD:
        draft["scenario_mode"] = "basis"
    else:
        draft["scenario_mode"] = "sweep"
        draft["sweep_id"] = choice
    draft.pop(FIELD, None)
    return draft


def normalise(draft: dict) -> dict:
    if FIELD not in draft:
        return draft
    return apply(draft, draft.get(FIELD))


# --- Der Satz in Klartext --------------------------------------------------

_MODE_PLAIN = {
    "basis": "der Standard-Ausgangslage des Modells",
    "sweep": "einem vorbereiteten Szenario",
    CUSTOM: "Ihren eigenen Einstellungen",
}


def ist_vergleich(draft: dict) -> bool:
    """Ob der Entwurf einen Szenario-Vergleich beschreibt statt eines Laufs.

    Eigene Funktion, weil daran seit P1.9-W1.3 mehrere Darstellungen hängen:
    Der Vergleich nimmt vom Entwurf **nichts** entgegen, und alles, was ihn
    beschreibt, muss deshalb aus einer anderen Quelle kommen.
    """

    return bool(draft.get("run_all_sweeps"))


def _vergleich_satz() -> str:
    """Was bei einem Szenario-Vergleich wirklich passiert.

    Bis P1.9 stand hier derselbe Satz wie für einen Einzellauf, mit den Werten
    des Entwurfs darin — «ausgehend von der Standard-Ausgangslage aus `configs/`,
    ohne Sprachmodell; die Zahlen stimmen, die Agenten-Texte sind Platzhalter».
    Drei Aussagen, drei Mal falsch: Die Ausgangslage ist je Szenario eine andere,
    Agenten-Texte gibt es überhaupt keine, und ein Sprachmodell wird für den
    Abschlusstext sehr wohl gerufen.
    """

    # **Nicht `list_sweep_presets()`** (P2.2): Verglichen werden die
    # Rahmenszenarien, nicht die Stresstests der Engine. Der Satz nannte bis
    # dahin acht und meinte damit auch «Totaler Wahnsinn (Alle Parameter)».
    count = len(rahmenszenarien())
    satz = (
        f"Sie starten **alle {count} Rahmenszenarien** nacheinander — jedes "
        "aus seiner eigenen Datei und **in seiner eigenen Länge**, ohne Agenten-Dialog. "
        "Am Ende liegen sie zum Vergleich nebeneinander. Die hinterlegten Stresstests "
        "der Engine sind nicht dabei; sie behaupten kein Weltbild."
    )
    if SZENARIOTEXT_NUTZT_LLM:
        satz += (
            " Für den abschließenden Szenariotext wird das Sprachmodell befragt — "
            "auch dann, wenn Sie oben «ohne Sprachmodell» gewählt haben."
        )
    return satz


def summary_sentence(draft: dict) -> str:
    """Was gleich passiert — in einem Satz, ohne Fachbegriffe."""

    if ist_vergleich(draft):
        return _vergleich_satz()

    runs = int(draft.get("run_count") or 1)
    scope = f"**{runs} Läufe**" if runs > 1 else "**einen Lauf**"

    basis = _MODE_PLAIN.get(draft.get("scenario_mode", "basis"), "der Standard-Ausgangslage")
    if draft.get("scenario_mode") == "sweep" and draft.get("sweep_id"):
        preset = next((s for s in list_sweep_presets() if s.id == draft["sweep_id"]), None)
        if preset is not None:
            basis = f"dem Szenario **«{preset.name}»**"
    ticks = draft.get("rounds", "?")

    if draft.get("deterministic_only"):
        mode = "nur mit den berechneten Zahlen, ohne Agenten-Dialog"
    elif draft.get("mock_llm"):
        mode = "ohne Sprachmodell; die Zahlen stimmen, die Agenten-Texte sind Platzhalter"
    else:
        mode = f"mit dem Sprachmodell «{draft.get('model', '?')}» für die Agenten-Narrative"

    return (
        f"Sie starten {scope} über **{formate.ticks_mit_modellzeit(ticks)}**, "
        f"ausgehend von {basis}, {mode}."
    )


# --- Schritt 1: Was soll gerechnet werden? ---------------------------------


def _kennzahl(preset) -> str:
    """Was man über ein Szenario wissen muss, um es zu **wählen**.

    Zwei Angaben, beide immer da: **wie lang** es angelegt ist, und **wie stark**
    es eingreift (Systemgrößen plus Faktoren). Meilensteine stehen bewusst nicht
    dabei — vier der acht Szenarien haben keine, und «0 Meilensteine» ist keine
    Auskunft, sondern Rauschen.
    """

    eingriffe = len(preset.property_overrides) + len(preset.factor_overrides)
    wort = "Änderung" if eingriffe == 1 else "Änderungen"
    kennzahl = f"{formate.ticks_mit_modellzeit(preset.max_ticks)} · {eingriffe} {wort}"

    # **Seit P2.2 steht die Art vorneweg**, und zwar nur bei den Stresstests:
    # Ein Rahmen ist der Normalfall und braucht keine Marke, ein Belastungstest
    # der Engine schon — er stand bis dahin gleichrangig neben «Business as
    # Usual» und wurde als Zukunft angeboten.
    if preset.art != "rahmen":
        return f"Stresstest · {kennzahl}"
    return kennzahl


def _choice_label(title: str, kennzahl: str | None = None) -> html.Div:
    """Ein Eintrag der Liste: **Name und Kennzahl, kein Satz** (P7.4-U4.1).

    Seit P1.9-W3.4 trug jede Kachel zwei Zeilen Beschreibung, abgeschnitten mit
    Auslassung — gemessen stand der Satz meist mitten im Gedanken still (E2).
    **Jetzt steht die Beschreibung nur noch in den Einzelheiten daneben**, voll,
    und nur für das eine Szenario, das zur Debatte steht. Die Kennzahl macht die
    Einträge vergleichbar.
    """

    return html.Div(
        [
            html.Span(title, className=f"font-body {ui.BESCHRIFTUNG} font-medium af-text block"),
            (html.Span(kennzahl, className="af-choice__meta") if kennzahl else None),
        ],
        className="min-w-0",
    )


def choice_options(*, stresstests: bool = False, gewaehlt: str | None = None) -> list[dict]:
    """Standard, die Rahmen, auf Wunsch die Stresstests, und die eigenen Einstellungen.

    **Stresstests sind ausgeblendet** (P7.4-U4.1, von Haiko entschieden am
    2026-09-14): Sie standen alphabetisch zwischen den Rahmen und waren nur an
    einem kleinen Zusatz zu erkennen (E2). **Ein gewählter Stresstest bleibt
    sichtbar** — sonst stünde eine Auswahl da, die niemand sieht.
    """

    options: list[dict] = [{"label": _choice_label("Standard-Ausgangslage"), "value": STANDARD}]
    for preset in list_sweep_presets():
        if preset.art != "rahmen" and not stresstests and preset.id != gewaehlt:
            continue
        options.append({"label": _choice_label(preset.name, _kennzahl(preset)), "value": preset.id})
    options.append({"label": _choice_label("Eigene Einstellungen"), "value": CUSTOM})
    return options


def stresstest_anzahl() -> int:
    return sum(1 for preset in list_sweep_presets() if preset.art != "rahmen")


def stresstest_knopftext(gezeigt: bool) -> str:
    """Was der Knopf sagt — was ein Klick als Nächstes tut."""

    return "Stresstests verbergen" if gezeigt else f"Stresstests zeigen ({stresstest_anzahl()})"


def szenario_radio(draft: dict, *, stresstests: bool) -> object:
    """Das eine Auswahlfeld des Schritts — mit oder ohne Stresstests."""

    return ui.radio(
        choice_options(stresstests=stresstests, gewaehlt=of(draft)),
        value=of(draft),
        id=FIELD_ID,
        cards=True,
        legend="Was soll gerechnet werden? Die Annahmenwelt des Laufs.",
    )


def _eigene_werte_wirken(draft: dict) -> bool:
    """Ob die eigenen Werte des Entwurfs in den Lauf eingehen.

    Lag bis P2.0-C in `config_editor/factors.py`, zusammen mit dem Schalter.
    """

    return bool(draft.get("apply_custom_overrides")) or of(draft) == CUSTOM


#: Wie viele Sätze der Begründung offen stehen (D3, entschieden am 2026-09-12).
#:
#: **Zwei**, und die Zahl ist die Entscheidung: Vorher stand die ganze
#: Begründung da — je Szenario 1163 bis 2429 Zeichen zusammen mit der These,
#: und beim Standardrahmen 2261 Zeichen allein aus Begründung und Vorbehalt. Das
#: ist die Tonlage eines Projektplans, nicht die eines Produkts. **Die
#: Ehrlichkeit bleibt vollständig erreichbar**, sie stört nur nicht mehr die
#: Entscheidung: Der Rest steht einen Klick tiefer.
SAETZE_OFFEN = 2

#: Satzende: Punkt, Frage- oder Ausrufezeichen, gefolgt von Weißraum.
#:
#: **Nachgemessen tragfähig, nicht angenommen** (2026-09-12): In keiner der
#: fünf Kohärenzbegründungen steht eine Abkürzung («z. B.», «bzw.», «ca.»,
#: «vgl.», «Nr.») oder eine Dezimalzahl, an der dieses Muster falsch schneiden
#: würde. `test_web_start_flow.py` misst das an den ausgelieferten Dateien —
#: wer eine Begründung mit einer Abkürzung schreibt, bekommt Bescheid, bevor
#: ein Leser einen halben Satz sieht.
_SATZENDE = re.compile(r"(?<=[.!?])\s+")


def satzanfang(text: str, saetze: int = SAETZE_OFFEN) -> tuple[str, str]:
    """Die ersten `saetze` Sätze und der Rest — beide bereits beschnitten.

    Öffentlich, weil der Wächter dieselbe Trennung nachrechnet, die die
    Oberfläche zeigt. Zwei Implementierungen wären die zweite Quelle, an der
    sie auseinanderlaufen.
    """

    teile = _SATZENDE.split(text.strip())
    return " ".join(teile[:saetze]).strip(), " ".join(teile[saetze:]).strip()


def _kohaerenz_block(kohaerenz, *, vorspann=None) -> html.Div:
    """Die Kohärenzbegründung eines Rahmens — **eine Stelle für alle Rahmen**.

    Sie steht offen da und nicht hinter «Fachliches»: Sie ist die einzige
    Absicherung, die ein Rahmenszenario hat — es gibt keinen Algorithmus, der
    seine Stimmigkeit prüft (Variante C, P2.2), und das soll man sehen statt
    aufklappen müssen. Quellen und Vorbehalt liegen darunter, weil sie beim
    Nachprüfen gebraucht werden und nicht beim Auswählen.

    **Gemeinsam für Preset und Standard seit A1** (2026-09-03): Vorher gab es
    diesen Block nur für Presets, und der Standard — der meistgenutzte Rahmen —
    zeigte gar nichts. Zwei Renderer für dieselbe Sache wären die zweite Quelle
    gewesen, an der sie auseinanderlaufen.
    """

    if kohaerenz is None:
        return html.Div()

    offen, rest = satzanfang(kohaerenz.begruendung)
    kinder: list = [vorspann] if vorspann is not None else []
    kinder += [
        # **These und zwei Sätze in Fließtextgröße** (D3). Vorher trug die These
        # `af-md--betont` (14 px) und die Begründung `af-md--caption` (12 px) —
        # zwei Größen in einem Leseblock, und genau daran ist U1.2 beim ersten
        # Anlauf gescheitert: Ein Deckel in Pixeln kann die Zusage «höchstens 75
        # Zeichen je Zeile» nicht für zwei Schriftgrößen halten (608 px tragen
        # bei 15 px 66 Zeichen, bei 12 px 106). **Ein Leseblock hat eine
        # Textgröße** — das ist die Regel, die aus dem Fehlschlag folgt.
        #
        # **Markdown, nicht `html.P`** (P7.1-U1.4): Die Begründungen in
        # `configs/` sind mit `**fett**` und `` `avia_paoc` `` geschrieben, und
        # im Browser standen die Zeichen roh da.
        ui.markdown(kohaerenz.these, class_name="af-md--tight af-md--these mb-2"),
        ui.markdown(offen, class_name="af-md--tight"),
        ui.expert(
            html.Div(
                [
                    # Der Rest der Begründung — er stand bis D3 offen da.
                    (
                        ui.markdown(rest, class_name="af-md--tight af-md--caption mb-3")
                        if rest
                        else None
                    ),
                    # **Als Markdown-Liste**, weil die Quellen Tabellen in
                    # Backticks nennen. Eine Quelle ist die längste Zeile, die
                    # eine Oberfläche zu bieten hat — Titel, Autor, Jahr,
                    # Fundstelle in einer Zeile —, und sie läuft seit der
                    # Rücknahme von E3 über die volle Breite.
                    ui.markdown(
                        "\n".join(f"- {quelle}" for quelle in kohaerenz.quellen),
                        class_name="af-md--tight af-md--caption mb-3",
                    ),
                    ui.markdown(kohaerenz.vorbehalt, class_name="af-md--tight af-md--caption"),
                ]
            ),
            # **Eine Klappe für alles, was belegt** (D3). Vorher hieß sie
            # «Quellen und was davon nicht belegt ist» und trug nur zwei der
            # vier Texte; die Begründung stand darüber offen.
            title="Begründung und Quellen",
        ),
    ]
    # **Gar kein Deckel mehr** (Rücknahme von E3 am 2026-09-12). Der Weg
    # hierher in drei Stufen, und jede war eine Messung: Zuerst trug jeder Text
    # sein eigenes `af-mass` in `ch`, also bekam jeder eine andere Breite
    # (These 424 px, Begründung 363, Quellenliste verschachtelt 341) — vier
    # Breiten in einem Block, der Befund, mit dem das UI/UX-Audit angefangen
    # hat. Dann saß mit U1.2 ein Deckel in `rem` am Block, und die Texte
    # endeten an einer Kante — bei 512 px von 760. Jetzt endet die Kante dort,
    # wo der Block endet.
    #
    # **Was von D3 bleibt, ist die Regel dahinter:** Ein Leseblock hat eine
    # Textgröße. Sie galt unabhängig vom Deckel.
    return html.Div(kinder, className="mb-4")


def scenario_details(draft: dict) -> html.Div:
    """Was zur aktuellen Auswahl gehört — Begründung und der Weg in den Editor."""

    choice = of(draft)
    if choice == CUSTOM:
        # **Für eigene Werte gibt es keine Begründung, und das ist keine Lücke.**
        # Ein selbst zusammengestellter Rahmen ist genau so stimmig, wie der
        # Nutzer ihn macht; ihm eine Kohärenzbehauptung unterzuschieben wäre eine
        # Aussage, die niemand getroffen hat.
        return html.Div(
            ui.hinweis(
                "Für eine eigene Zusammenstellung gibt es **keine hinterlegte "
                "Begründung** — die Rahmenszenarien tragen je eine, weil jemand sie "
                "aufgeschrieben und belegt hat. Wer eigene Verläufe nach außen "
                "zitiert, begründet ihre Stimmigkeit selbst.",
                "kontext",
            )
        )
    if choice == STANDARD:
        # **Auch der Standard ist ein Rahmen** (P2.0-B), und seit A1 trägt er
        # seine Begründung wie jeder andere. Sie stand als einzige nicht da —
        # ausgerechnet beim meistgenutzten Weltbild, das jeder Lauf ohne
        # Preset-Wahl benutzt.
        return _kohaerenz_block(
            load_properties_config().kohaerenz,
            # **Eine Zeile, kein Kasten** (P7.4-U4.1): Als Kasten kostete sie bei
            # 1440 × 900 128 px in der schmalen rechten Spalte.
            vorspann=ui.satz(
                "Der Lauf rechnet mit den **hinterlegten Verläufen des Modells** — eigenen "
                "Annahmen über Politik, Kosten und Konjunktur, begründet wie jedes Szenario.",
                class_name=f"{ui.CAPTION} mb-2",
            ),
        )

    preset = next((s for s in list_sweep_presets() if s.id == choice), None)
    if preset is None:
        return html.Div(ui.hinweis(f"Das Szenario «{choice}» ist nicht hinterlegt.", "warnung"))

    children: list = [
        # **Der volle Beschreibungstext steht hier**, seit die Kachel ihn auf
        # zwei Zeilen klemmt (W3.4). Er ist nicht verschwunden, er steht nur
        # dort, wo er gebraucht wird: bei dem einen Szenario, das zur Debatte
        # steht, statt zehnmal im Raster.
        html.P(preset.description, className=f"{ui.CAPTION} mb-4"),
        ui.hinweis(
            "Das Szenario gilt **unverändert**: Politik, Kosten und Nachfrageumfeld kommen aus "
            f"`{preset.id}.json`, Ihre Einstellungen im Editor bleiben dafür außen vor. "
            f"Angelegt ist es auf **{formate.ticks_mit_modellzeit(preset.max_ticks)}** — die Länge stellen Sie im "
            "nächsten Schritt selbst ein.",
            "kontext",
        ),
    ]
    # **Die Kohärenzbegründung (P2.2, Variante C).** Sie steht offen da und
    # nicht hinter «Fachliches»: Sie ist die einzige Absicherung, die ein
    # Rahmenszenario hat — es gibt keinen Algorithmus, der seine Stimmigkeit
    # prüft, und das soll man sehen statt aufklappen müssen.
    if preset.kohaerenz is not None:
        children.append(_kohaerenz_block(preset.kohaerenz))
    elif preset.art != "rahmen":
        children.append(
            ui.hinweis(
                "Dies ist ein **Stresstest der Engine**, kein begründetes Weltbild. Die "
                "Verläufe sind auf Sichtbarkeit und Belastung gebaut, nicht auf "
                "Plausibilität — die Zahlen taugen zum Prüfen der Mechanik, nicht als "
                "Aussage über die Zukunft. Ein Szenario-Vergleich lässt ihn deshalb aus.",
                "warnung",
            )
        )

    if preset.rationale:
        children.append(
            ui.expert(ui.markdown(preset.rationale), title="Warum dieses Szenario so aufgebaut ist")
        )
    children.append(
        html.Div(
            [
                ui.button(
                    "Werte übernehmen und selbst anpassen",
                    id=c.action_id("apply-sweep"),
                    variant="secondary",
                    icon_name="download",
                ),
                html.P(
                    "Schreibt die Werte des Szenarios in den Editor und schaltet auf "
                    "«Eigene Einstellungen» um.",
                    className=f"{ui.CAPTION} mt-2",
                ),
            ],
            className="mt-4",
        )
    )
    return html.Div(children)


# --- Preflight -------------------------------------------------------------


def schritttitel(key: str) -> str:
    """Der Titel eines Schritts — aus `wizard.STEPS`, nie hingeschrieben (P7.2-U2.2).

    Zwei Texte verwiesen auf Schritte, die es so nicht mehr gab: «Schritten 4
    bis 7» (die Schrittfolge hat seit P2.0-C sechs) und Schritt «Ausgangslage»
    (mit P2.0-C entfallen). Beide waren beim Schreiben richtig. Eine Nummer oder
    ein Titel als Literal weiß nichts davon, dass die Schrittfolge sich ändert —
    `tests/test_web_schrittverweise.py` meldet jedes.

    Der Import steht in der Funktion, weil `wizard` dieses Modul importiert.
    """

    from dashboard.web.config_editor import wizard

    return next(step.title for step in wizard.STEPS if step.key == key)


def _vergleich_tiles() -> list:
    """Kacheln, die den Vergleich beschreiben — nicht den Entwurf.

    Die sechs Kacheln des Einzellaufs zeigen Ziel-Auslastung, Segmente und
    aktive Systemgrößen aus dem Entwurf. Beim Vergleich gilt davon nichts:
    Jedes Szenario bringt seine eigenen Werte mit. Sie dort anzuzeigen hieße,
    Zahlen zu nennen, mit denen nicht gerechnet wird.
    """

    # **Die Rahmen, nicht der ganze Ordner** (P7.2-U2.1). Bis zum 2026-09-11
    # zählte diese Kachel `list_sweep_presets()` — acht, samt der Stresstests —,
    # während der Satz darüber «alle vier Rahmenszenarien» sagte. Auch die
    # Längenspanne kam aus den Stresstests: «40–120 Ticks» für einen Vergleich,
    # dessen Szenarien alle 120 Ticks lang sind.
    rahmen = rahmenszenarien()
    laengen = sorted({p.max_ticks for p in rahmen}) or [0]
    laenge = (
        formate.ticks_mit_modellzeit(laengen[0])
        if len(laengen) == 1
        else f"{min(laengen)}–{max(laengen)} Ticks"
    )

    return [
        ui.kachel("Rahmenszenarien", len(rahmen)),
        ui.kachel(
            "Länge",
            laenge,
            hint=(
                "Je Szenario so, wie es angelegt ist — nicht die Länge aus "
                f"«{schritttitel('umfang')}»."
            ),
            variante="text",
        ),
        ui.kachel(
            "Rechenmodus",
            "Nur Zahlen",
            hint="Vom Vergleich vorgegeben, damit die Szenarien vergleichbar bleiben.",
            variante="text",
        ),
        ui.kachel(
            "Zufallsstartwert",
            f"{SWEEP_SEED} (vorgegeben)",
            hint="Für alle Szenarien derselbe — sonst zeigt ein Unterschied die Ziehung.",
            variante="text",
        ),
    ]


def vorgaben_hinweis(draft: dict) -> object:
    """Welche Antworten der Vergleich nicht verwendet — und warum.

    **Der Text kommt aus dem Vertrag des Sweeps** (`FESTLEGUNGEN`/`UNBEACHTET`),
    nicht aus dieser Datei. Damit kann die Oberfläche nicht behaupten, ein Feld
    sei vorgegeben, das in Wahrheit wirkt, und ebenso wenig eines verschweigen:
    `tests/test_web_wirkung.py` hält beide Richtungen fest.
    """

    if not ist_vergleich(draft):
        return None

    vorgaben = vorgegebene_felder()
    # Nur, was der Assistent überhaupt fragt — ein Feld, das nirgends
    # eingestellt werden kann, muss man auch nicht als vorgegeben ausweisen.
    sichtbar = [
        "rounds",
        "apply_custom_overrides",
        "deterministic_only",
        "mock_llm",
        "use_seed",
        "seed",
        "base_price",
        "checkpoint_interval",
    ]
    zeilen = [f"- {vorgaben[feld].grund}" for feld in sichtbar if feld in vorgaben]

    return ui.expert(
        ui.markdown("\n".join(zeilen)),
        title="Was der Vergleich vorgibt — und Ihre Einstellungen dafür nicht verwendet",
    )


def _tiles(draft: dict) -> list:
    if ist_vergleich(draft):
        return _vergleich_tiles()

    # **Drei Werte, die vor dem Start zählen** (P7.4-U4.4). Ziel-Auslastung,
    # Segmente und aktive Systemgrößen sind Modellinterna; sie stehen seither
    # hinter «Technische Details» (`_modell_kacheln`). Das Bedienfeld zeigt die
    # ersten drei — und damit jetzt, was «Die erste Simulation» schon lange sagt.
    return [
        ui.kachel("Länge", formate.ticks_mit_modellzeit(draft.get("rounds", "?"))),
        ui.kachel(
            "Wiederholungen",
            "alle Szenarien" if draft.get("run_all_sweeps") else draft.get("run_count", 1),
        ),
        ui.kachel(
            "Zufallsstartwert",
            draft.get("seed", "—") if draft.get("use_seed") else f"{DEFAULT_SEED} (Standard)",
            hint="Ohne eigenen Startwert rechnet der Lauf mit dem Standardwert.",
        ),
    ]


def _modell_kacheln(draft: dict) -> list:
    """Kennzahlen des Modells — für wen nachsehen will, nicht für die Entscheidung.

    **Ziel-Auslastung und Segmente kommen aus der Datei, nicht aus dem Entwurf**
    (P7.13-U13.5). Preisbildung und Bevölkerung aus dem Bereich «Modell» wirken
    nur gespeichert; gemessen erreichte eine eingetragene Ziel-Auslastung von 0,61
    keinen Lauf, und diese Kachel zeigte sie trotzdem an. Die aktiven Systemgrößen
    stammen weiter aus dem Entwurf, weil sie mit «Eigene Werte anwenden» ankommen.
    """

    from dashboard.config_catalog import (
        extract_market_feedback_from_file,
        extract_population_edits_from_file,
    )

    datei = draft.get("properties_file") or "properties.json"
    feedback = asdict(extract_market_feedback_from_file(datei))
    segments = [s for s in extract_population_edits_from_file(datei) if s.type == "boolean"]
    active_properties = [
        key
        for key, edit in (draft.get("property_edits") or {}).items()
        if isinstance(edit, dict) and edit.get("is_active", True)
    ]
    return [
        ui.kachel(
            "Ziel-Auslastung",
            (
                f"{float(feedback.get('target_booking_rate', 0.37)):.0%}"
                if feedback.get("enabled", True)
                else "Preis fix"
            ),
        ),
        ui.kachel("Segmente", len(segments)),
        ui.kachel("Aktive Systemgrößen", len(active_properties)),
    ]


def herkunft(draft: dict) -> object:
    """Woran ein Lauf später wiederzuerkennen ist — **vor** dem Start (P1.9-W4.2/W4.4).

    P0.6 hat dafür gesorgt, dass ein Lauf festhält, wie er entstanden ist: Seed,
    Rechenmodus, Codestand und ein Fingerabdruck jeder gelesenen
    Konfigurationsdatei. Das stand bis hierher aber erst **danach** im Artefakt.

    Wer zwei Läufe vergleichen will, braucht die Angaben vorher: Ein Lauf mit
    anderem Codestand oder anderem Config-Fingerabdruck gehört nicht neben einen
    anderen — und das merkt man besser vor der halben Stunde Rechenzeit als
    danach.

    **Dieselbe Quelle wie das Artefakt** (`output_writer.provenance`), nicht eine
    zweite Berechnung daneben: Sonst stünde vorher etwas anderes als hinterher,
    und genau die Drift hat P0.6 an anderer Stelle gekostet.
    """

    from src.reporting.output_writer.provenance import code_version, config_fingerprint

    zeilen: list = []

    stand = code_version()
    if stand:
        kurz = str(stand.get("commit", "?"))[:12]
        zweig = stand.get("branch") or "?"
        schmutzig = " · nicht eingecheckte Änderungen" if stand.get("dirty") else ""
        zeilen.append(("Codestand", f"{kurz} ({zweig}){schmutzig}"))

    try:
        abdruck = config_fingerprint(_zustand(draft))
    except Exception:  # noqa: BLE001 - eine kaputte Config meldet schon der Preflight
        abdruck = None
    if abdruck is not None:
        zeilen.append(("Konfiguration", abdruck.simulation_config + " / " + abdruck.properties))

    if not zeilen:
        return None

    # **Zeilen, keine eigene Klappe** (P7.4-U4.4): Sie stehen in «Technische
    # Details», und eine Klappe in der Klappe verbietet die Regel zum Aufklappen.
    return html.Div(
        [
            html.Div(
                [
                    html.Span(name, className="af-delta__was"),
                    html.Span(wert, className="af-delta__wert"),
                ],
                className="af-delta__zeile",
            )
            for name, wert in zeilen
        ],
        className="af-delta",
    )


def technische_details(draft: dict) -> object:
    """Woran der Lauf später wiederzuerkennen ist, und die Kennzahlen des Modells (P7.4-U4.4).

    **Eine Klappe am Ende des Prüfschritts.** Bis dahin stand die Herkunft als
    eigene Klappe mitten im Preflight und daneben sechs Kacheln, drei davon
    Modellinterna — gemessen bei 1440 × 900 zusammen fast 300 px für Angaben, die
    man zum Nachsehen braucht und nicht zum Starten (E9).
    """

    teile: list = [herkunft(draft)]
    if not ist_vergleich(draft):
        teile.append(
            html.Div(
                ui.grid(*_modell_kacheln(draft), cols="sm:grid-cols-2 lg:grid-cols-3", gap="gap-4"),
                className="mt-4",
            )
        )
    teile = [teil for teil in teile if teil is not None]
    if not teile:
        return None
    return ui.expert(
        *teile,
        title="Technische Details",
        names="Codestand, Konfiguration, Kennzahlen des Modells",
    )


def _zustand(draft: dict):
    """Den Zustand bauen, den der Lauf bekäme — für den Fingerabdruck."""

    from dashboard.config_catalog import prepare_simulation_state

    return prepare_simulation_state(draft_from_dict(draft))


#: Der Knopf unter einem Hinweis, der zum Schritt führt, in dem er sich beheben
#: lässt (P7.4-U4.4). **Eigene Kennung**, nicht die der Schrittliste: Dieselbe
#: Kennung zweimal im DOM wäre für Dash ein Laufzeitfehler.
SPRUNG = "wizard-hinweis-sprung"


def sprung_id(schritt: str) -> dict:
    return {"type": SPRUNG, "schritt": schritt}


def _mit_sprung(hinweis: object, schritt: str, sprung: bool) -> object:
    """Ein Hinweis mit Knopf zum Schritt — **nur im Prüfschritt** (*sprung*).

    Im Bedienfeld steht man im Leitstand; ein Sprung schaltete dort einen
    Schritt des Einrichtens um, den niemand sieht.
    """

    if not sprung:
        return hinweis
    return html.Div(
        [
            hinweis,
            ui.button(
                f"Zu «{schritttitel(schritt)}»",
                id=sprung_id(schritt),
                variant="ghost",
                className="mt-1",
            ),
        ]
    )


def _warnings(draft: dict, errors: list[str], *, sprung: bool = False) -> list:
    """Was den Start verhindert, und was später enttäuscht — getrennt gehalten.

    Fehler zuerst und sichtbar abgesetzt: Die Hinweise darunter sind Ratschläge,
    das hier verhindert den Start. Beides in einem Topf zu zeigen, würde genau
    die Unterscheidung verwischen, auf die es ankommt.
    """

    warnings: list = []

    ohne_feld = unfielded_issues(errors)
    am_feld = len(errors) - len(ohne_feld)
    if errors:
        text = "**Der Lauf kann so nicht starten.**"
        if ohne_feld:
            text += " " + " · ".join(f"`{error}`" for error in ohne_feld)
        if am_feld:
            steht = "steht ein Hinweis" if am_feld == 1 else f"stehen {am_feld} Hinweise"
            text += f" Dazu {steht} direkt am betroffenen Feld."
        warnings.append(ui.hinweis(text, "fehler"))

    # Zwei der Hinweise unten gelten nur für einen Lauf: Der Vergleich hat einen
    # vorgegebenen Startwert und wendet eigene Werte ohnehin nicht an. Sie dort
    # zu zeigen hieße, zu einer Einstellung zu raten, die nicht wirkt.
    vergleich = ist_vergleich(draft)

    if not vergleich and not draft.get("use_seed") and int(draft.get("run_count") or 1) > 1:
        warnings.append(
            _mit_sprung(
                ui.hinweis(
                    "Mehrere Wiederholungen ohne festen Zufallsstartwert: Die Läufe werden sich "
                    "unterscheiden. Das ist gewollt, wenn Sie die Streuung sehen wollen — für "
                    "einen sauberen A/B-Vergleich setzen Sie den Startwert unter «Feinabstimmung».",
                    "info",
                ),
                "modus",
                sprung,
            )
        )
    if draft.get("no_scenarios"):
        warnings.append(
            _mit_sprung(
                ui.hinweis(
                    "«Keine Szenarien erzeugen» ist aktiv — der Tab «Szenario» bleibt nach dem "
                    "Lauf leer, obwohl er die Hauptansicht ist.",
                    "warnung",
                ),
                "technik",
                sprung,
            )
        )
    if (
        not vergleich
        and draft.get("scenario_mode") != "sweep"
        and not draft.get("apply_custom_overrides")
    ):
        warnings.append(
            _mit_sprung(
                ui.hinweis(
                    "«Eigene Werte anwenden» ist aus — Änderungen an den Systemgrößen "
                    "wirken in diesem Lauf nicht.",
                    "warnung",
                ),
                "szenario",
                sprung,
            )
        )

    # **Wie weit die Vorgaben reichen** (P2.8, Restposition). Ein Lauf über den
    # letzten Stützpunkt hinaus ist zulässig — die Kurve hält dort ihren letzten
    # Wert, und bei einer CO₂-Abgabe am Endwert ist genau das gemeint. Er soll es
    # nur **sagen**: Bis dahin rechnete ein Standardlauf ein Viertel seiner Länge
    # mit einer fortgeschriebenen Bevölkerung, ohne dass irgendwo etwas stand.
    warnings.extend(_horizont_hinweis(draft))
    return warnings


def _horizont_hinweis(draft: dict) -> list:
    """Ein Satz, keine Liste — sonst steht der Preflight voller Selbstverständlichkeiten.

    Genannt wird der **früheste** Horizont und wie viele Verläufe betroffen sind;
    welche es im Einzelnen sind, steht im Modell-Bereich, wo man sie auch ändern
    kann.
    """

    ticks = int(draft.get("rounds") or 0)
    if ticks <= 0:
        return []

    luecken = horizontluecken(load_properties_config(), max_ticks=ticks)
    if not luecken:
        return []

    frueheste = luecken[0]
    wie_viele = "Ein Verlauf endet" if len(luecken) == 1 else f"{len(luecken)} Verläufe enden"
    return [
        ui.hinweis(
            f"{wie_viele} vor dem Ende des Laufs — der früheste ist "
            f"«{PROPERTY_LABELS.get(frueheste.property_id, frueheste.property_id)}» "
            f"bei Tick {frueheste.letzter_stuetzpunkt}. "
            f"Danach hält er seinen letzten Wert; die letzten "
            f"{frueheste.ticks_darueber} Ticks rechnen also mit einer "
            "fortgeschriebenen Vorgabe. Das ist zulässig — gemeint ist es nicht "
            "immer.",
            "info",
        )
    ]


#: Was im Bedienfeld von den sechs Kacheln übrig bleibt. Die drei, die vor dem
#: Start wirklich zählen; der Rest steht im Bereich «Einrichten», wo er
#: eingestellt wird.
_COMPACT_TILES = 3


def preflight(
    draft: dict,
    errors: list[str],
    *,
    slot: str = "setup",
    compact: bool = False,
    abweichungen: object = None,
) -> html.Div:
    """Der letzte Blick vor dem Start.

    *slot* benennt den Platzhalter für den Klartext-Satz. Er ist ein Parameter,
    weil derselbe Satz an mehreren Stellen stehen darf — dieselbe ID zweimal
    wäre dagegen ein Laufzeitfehler im Browser.

    *compact* ist die Fassung für das Bedienfeld: drei Kacheln statt sechs,
    einspaltig. Seit P1.6 steht der Preflight dort, direkt über dem Knopf, den
    er absichert.
    """

    tiles = _tiles(draft)
    if compact:
        return html.Div(
            [
                ui.card(html.Div(ui.markdown(summary_sentence(draft)), id=summary_id(slot))),
                html.Div(_warnings(draft, errors), className="space-y-2 mt-4"),
                html.Div(vorgaben_hinweis(draft), className="mt-4"),
                html.Div(dauer.hinweis(draft), className="mt-4"),
                html.Div(
                    ui.grid(*tiles[:_COMPACT_TILES], cols="grid-cols-1", gap="gap-2"),
                    className="mt-4",
                ),
            ]
        )

    # **Die feste Reihenfolge des Prüfschritts** (P7.4-U4.4): was läuft und wie
    # lange, die Werte, was abweicht, was zu beachten ist, zuletzt die Details.
    # Bis dahin standen die Abweichungen ganz unten und zwischen Satz und Kacheln
    # Hinweise, Dauer und Herkunft (E9) — gemessen 1,42 Schirme bei 1440 × 900.
    satz = dauer.schaetzung(draft)
    teile: list = [
        ui.card(
            html.Div(
                [
                    html.Div(ui.markdown(summary_sentence(draft)), id=summary_id(slot)),
                    ui.satz(satz, class_name=f"{ui.CAPTION} mt-2") if satz else None,
                ]
            )
        ),
        html.Div(
            ui.grid(*tiles, cols="sm:grid-cols-2 lg:grid-cols-3", gap="gap-4"),
            className="mt-4",
        ),
    ]
    if abweichungen is not None:
        teile.append(html.Div(abweichungen, className="mt-4"))
    hinweise = _warnings(draft, errors, sprung=True)
    if hinweise:
        teile.append(html.Div(hinweise, className="space-y-2 mt-4"))
    for teil in (vorgaben_hinweis(draft), technische_details(draft)):
        if teil is not None:
            teile.append(html.Div(teil, className="mt-4"))
    return html.Div(teile)


# --- Aufbau ----------------------------------------------------------------


def _step(number: int | None, title: str, lede: str, *children: object, actions: object = None):
    """Ein Schritt mit Überschrift — oder ohne.

    `number=None` lässt Titel und Nummer weg. Das braucht die Schrittfolge aus
    P1.7: Sie schreibt «Schritt 1 von 7» und den Titel selbst über den Inhalt,
    und darunter stand die Überschrift danach ein zweites Mal.

    **Seit P1.9-W3.5 fällt auch die Einleitung weg**, aus demselben Grund: Die
    Schrittfolge schreibt bereits `Step.lede` unter den Titel, und darunter stand
    hier ein zweiter, längerer Satz mit derselben Aussage — der Schritt-Lede war
    wörtlich sein erster Satz. Zwei Einleitungen übereinander kosteten auf jedem
    der drei Entscheidungsschritte rund 60 px und sagten einmal zu viel.

    Der ausführlichere Text ist nicht verloren: Er steht jetzt als `Step.lede` in
    `wizard.STEPS` und damit an der Stelle, an der die Schrittfolge ihn ohnehin
    zeigt.
    """

    if number is None:
        return ui.section(None, *children, actions=actions)
    return ui.section(f"{number}. {title}", ui.lede(lede), *children, actions=actions)


def scenario_step(draft: dict, number: int | None = 1) -> object:
    return _step(
        number,
        "Was soll gerechnet werden?",
        "Die Annahmenwelt, von der der Lauf ausgeht. Ein vorbereitetes Szenario ist der "
        "schnellste Einstieg — es legt Politik, Kosten und Nachfrageumfeld in einem Zug fest.",
        ui.card(
            # **Links die Liste, rechts die Einzelheiten** (P7.4-U4.1, von Haiko
            # entschieden am 2026-09-14). Gemessen bei 1440 × 900 standen zehn
            # Karten 539 px hoch und die Einzelheiten 317 px darunter. Unter
            # 1280 px stehen beide untereinander (`.af-szenariowahl`).
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                szenario_radio(draft, stresstests=False),
                                id=liste_id("scenario"),
                            ),
                            # **Außerhalb des Wirts**: Neu gezeichnet setzte er seinen
                            # Klickzähler zurück, und der Knopf wüsste nicht mehr, was er
                            # zeigt.
                            (
                                ui.button(
                                    stresstest_knopftext(False),
                                    id=stress_toggle_id("scenario"),
                                    variant="ghost",
                                    className="mt-2",
                                )
                                if stresstest_anzahl()
                                else None
                            ),
                            # **Hinter «Feinabstimmung» und mit `detail=True`**, nicht auf
                            # der Entscheidungsfläche: «gelten meine Werte» ist kein vierter
                            # Schritt zum Lauf (der Wächter aus P1.1 hat den ersten Anlauf
                            # gemeldet). Der Schalter stand bis P2.0-C im Schritt
                            # «Ausgangslage». **Links unter der Liste seit P7.4-U4.1**:
                            # Unter beiden Spalten kostete er die letzte Zeile über einem
                            # Bildschirm bei 1440 × 900.
                            ui.expert(
                                c.check(
                                    "apply_custom_overrides",
                                    _eigene_werte_wirken(draft),
                                    detail=True,
                                ),
                                title="Feinabstimmung",
                            ),
                        ]
                    ),
                    html.Div(scenario_details(draft), id=slot_id("scenario")),
                ],
                className="af-szenariowahl",
            ),
        ),
        actions=ui.doc_link("presets"),
    )


def scope_step(draft: dict, number: int | None = 2) -> object:
    return _step(
        number,
        "Wie weit reicht der Lauf?",
        "Ein Tick ist ein Monat, vierzig sind gut drei Jahre — in den Zahlen steht "
        "trotzdem kein Datum. Mehr Ticks heißt vor allem mehr Gelegenheiten für "
        "Rückkopplung zwischen Preis und Nachfrage.",
        ui.card(
            c.number(
                "rounds",
                draft.get("rounds"),
                min=1,
                max=500,
                step=1,
                detail=True,
                breite="feld",
            ),
            ui.expert(
                ui.grid(
                    c.number(
                        "run_count",
                        draft.get("run_count"),
                        min=1,
                        max=20,
                        step=1,
                        detail=True,
                    ),
                    html.Div(
                        c.check("run_all_sweeps", bool(draft.get("run_all_sweeps")), detail=True),
                        className="af-neben-feld",
                    ),
                    cols="md:grid-cols-2",
                ),
                count=2,
                names="Wiederholungen, alle Szenarien vergleichen",
            ),
        ),
        actions=ui.doc_link("tick-und-lauf"),
    )


def mode_step(draft: dict, number: int | None = 3) -> object:
    return _step(
        number,
        "Womit wird gerechnet?",
        "Die Zahlen sind in allen drei Fällen dieselben — Preise, Buchungsraten und "
        "Faktorzustände berechnet immer das Rechenmodell. Die Auswahl bestimmt nur, wie "
        "viel dazu erzählt wird.",
        ui.card(
            ui.radio(
                compute_mode.OPTIONS,
                value=compute_mode.of(draft),
                id=compute_mode.FIELD_ID,
                legend="Womit wird gerechnet? Ob und wie die Agenten den Lauf deuten.",
            ),
            html.Div(
                compute_mode.placeholder("start"),
                className="mt-4 pt-4 af-border-t af-border-subtle",
            ),
            ui.expert(
                ui.grid(
                    c.check("use_seed", bool(draft.get("use_seed")), detail=True),
                    c.number("seed", draft.get("seed"), min=0, step=1),
                    cols="sm:grid-cols-2",
                ),
                count=2,
                title="Zufallsstartwert",
                names="Ohne Angabe rechnet der Lauf reproduzierbar mit dem Standardwert.",
            ),
        ),
        actions=ui.doc_link("zahlen-und-sprache"),
    )


def layout(draft: dict) -> html.Div:
    """Die drei Entscheidungen — seit P1.6 im Bereich «Einrichten».

    Schritt 1 steht über die volle Breite (die Presets brauchen sie als
    Raster), Schritt 2 und 3 teilen sich darunter eine Reihe. Der Preflight
    steht **nicht** mehr hier: Er gehört neben den Start-Knopf, und der sitzt
    im Bedienfeld links.
    """

    return html.Div(
        [
            scenario_step(draft),
            # `2xl` und nicht `xl`: Tailwinds Haltepunkte messen das **Fenster**,
            # der Inhalt steht aber in einer Zone, die schmaler ist als das
            # Fenster. Bei 1280 px teilte `xl` die 720 px des Viewports in zwei
            # 319-px-Spalten — genau die Enge, gegen die dieses Paket antritt.
            ui.grid(scope_step(draft), mode_step(draft), cols="2xl:grid-cols-2", gap="gap-8"),
        ]
    )


def errors_for(draft: dict) -> list[str]:
    try:
        return validate_draft(draft_from_dict(draft))
    except Exception as exc:  # noqa: BLE001 - eine kaputte Config ist ein Befund, kein Absturz
        return [f"Konfiguration konnte nicht geladen werden: {exc}"]


def live_state(draft: dict) -> tuple[dict, dict]:
    """Alles, was ein Callback nach einer Änderung nachfüllt.

    In einem Zug, weil die Prüfung den ganzen Simulationszustand aufbaut — sie
    soll pro Änderung **einmal** laufen, nicht je Ausgabefeld. Zurück kommen die
    Slot-Inhalte und die Befunde je Feld.
    """

    errors = errors_for(draft)
    slots = {
        "scenario": scenario_details(draft),
        # Der Preflight-Slot liegt seit P1.6 im Bedienfeld, nicht mehr in
        # `layout()`. Die Zuordnung bleibt dieselbe — nur der Ort hat sich
        # geändert, und `_live` findet ihn über die Pattern-ID trotzdem.
        "preflight": preflight(draft, errors, slot="rail", compact=True),
    }
    return slots, issues_by_field(errors)
