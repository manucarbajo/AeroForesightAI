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

from dash import html

from dashboard.config_catalog import (
    issues_by_field,
    list_sweep_presets,
    unfielded_issues,
    validate_draft,
)
from dashboard.web import components as ui
from dashboard.web.config_editor import compute_mode, dauer
from dashboard.web.config_editor import controls as c
from dashboard.web.state import draft_from_dict
from src.models.state_models import DEFAULT_SEED
from src.orchestration.scenario_sweeps import (
    SWEEP_SEED,
    SZENARIOTEXT_NUTZT_LLM,
    vorgegebene_felder,
)

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
    "basis": "der Standard-Ausgangslage aus `configs/`",
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

    count = len(list_sweep_presets())
    satz = (
        f"Sie starten **alle {count} hinterlegten Szenarien** nacheinander — jedes "
        "aus seiner eigenen Datei und **in seiner eigenen Länge**, ohne Agenten-Dialog. "
        "Am Ende liegen sie zum Vergleich nebeneinander."
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

    return f"Sie starten {scope} über **{ticks} Ticks**, ausgehend von {basis}, {mode}."


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
    return f"{preset.max_ticks} Ticks · {eingriffe} {wort}"


def _choice_label(title: str, description: str, kennzahl: str | None = None) -> html.Div:
    """Eine Kachel im Raster: Name, Kennzahl, zwei Zeilen Beschreibung (P1.9-W3.4).

    Vorher trug jede Kachel ihre **vollständige** Beschreibung — zwischen einer
    und sechs Zeilen, je nach Szenario. Gemessen waren die zehn Kacheln damit
    zwischen 88 und 264 px hoch, das Raster 5 Reihen, und Schritt 1 brauchte
    1,92 Bildschirme: der zweithöchste Wert der ganzen Schrittfolge.

    Ein Raster, dessen Zeilen unterschiedlich hoch sind, lässt sich außerdem
    nicht überfliegen — man liest zehn Absätze, statt zehn Möglichkeiten zu
    vergleichen. Die Beschreibung ist deshalb auf zwei Zeilen geklemmt, und die
    **Kennzahl** darüber macht die Kacheln erst vergleichbar.

    Der vollständige Text geht dabei nicht verloren: Er steht unter dem Raster,
    sobald ein Szenario gewählt ist (`scenario_details`) — dort, wo man ihn
    braucht, und nur für das eine, das zur Debatte steht.
    """

    return html.Div(
        [
            html.Span(title, className="font-body text-sm font-medium af-text block"),
            (html.Span(kennzahl, className="af-choice__meta") if kennzahl else None),
            html.Span(description, className=f"{ui.CAPTION} af-choice__text"),
        ],
        className="min-w-0",
    )


def choice_options() -> list[dict]:
    """Standard, jedes Preset, und der Weg zu den eigenen Einstellungen."""

    options: list[dict] = [
        {
            "label": _choice_label(
                "Standard-Ausgangslage",
                "Die hinterlegten Werte aus `configs/` — der neutrale Ausgangspunkt.",
            ),
            "value": STANDARD,
        }
    ]
    for preset in list_sweep_presets():
        options.append(
            {
                "label": _choice_label(preset.name, preset.description, _kennzahl(preset)),
                "value": preset.id,
            }
        )
    options.append(
        {
            "label": _choice_label(
                "Eigene Einstellungen",
                "Was Sie in den Schritten 4 bis 7 selbst eingestellt haben.",
            ),
            "value": CUSTOM,
        }
    )
    return options


def scenario_details(draft: dict) -> html.Div:
    """Was zur aktuellen Auswahl gehört — Begründung und der Weg in den Editor."""

    choice = of(draft)
    if choice in {STANDARD, CUSTOM}:
        return html.Div()

    preset = next((s for s in list_sweep_presets() if s.id == choice), None)
    if preset is None:
        return html.Div(
            ui.alert(f"Preset `{choice}` liegt nicht unter `configs/sweeps/`.", "warning")
        )

    children: list = [
        # **Der volle Beschreibungstext steht hier**, seit die Kachel ihn auf
        # zwei Zeilen klemmt (W3.4). Er ist nicht verschwunden, er steht nur
        # dort, wo er gebraucht wird: bei dem einen Szenario, das zur Debatte
        # steht, statt zehnmal im Raster.
        html.P(preset.description, className=f"{ui.CAPTION} mb-4 max-w-prose"),
        ui.note(
            "Das Szenario gilt **unverändert**: Faktorlage, Politik und Kosten kommen aus "
            f"`{preset.id}.json`, Ihre Einstellungen im Editor bleiben dafür außen vor. "
            f"Angelegt ist es auf **{preset.max_ticks} Ticks** — die Länge stellen Sie im "
            "nächsten Schritt selbst ein."
        ),
    ]
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
            className="mt-5",
        )
    )
    return html.Div(children)


# --- Preflight -------------------------------------------------------------


def _vergleich_tiles() -> list:
    """Kacheln, die den Vergleich beschreiben — nicht den Entwurf.

    Die sechs Kacheln des Einzellaufs zeigen Ziel-Auslastung, Segmente und
    aktive Systemgrößen aus dem Entwurf. Beim Vergleich gilt davon nichts:
    Jedes Szenario bringt seine eigenen Werte mit. Sie dort anzuzeigen hieße,
    Zahlen zu nennen, mit denen nicht gerechnet wird.
    """

    presets = list_sweep_presets()
    laengen = sorted({p.max_ticks for p in presets})
    laenge = f"{laengen[0]} Ticks" if len(laengen) == 1 else f"{min(laengen)}–{max(laengen)} Ticks"

    return [
        ui.metric_tile("Szenarien", len(presets)),
        ui.metric_tile(
            "Länge",
            laenge,
            hint="Je Szenario so, wie es angelegt ist — nicht die Länge aus Schritt 2.",
            prose=True,
        ),
        ui.metric_tile(
            "Rechenmodus",
            "Nur Zahlen",
            hint="Vom Vergleich vorgegeben, damit die Szenarien vergleichbar bleiben.",
            prose=True,
        ),
        ui.metric_tile(
            "Zufallsstartwert",
            f"{SWEEP_SEED} (vorgegeben)",
            hint="Für alle Szenarien derselbe — sonst zeigte ein Unterschied die "
            "Ziehung statt des Szenarios.",
            prose=True,
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

    feedback = draft.get("market_feedback_edit") or {}
    segments = [s for s in (draft.get("population_edits") or []) if s.get("type") == "boolean"]
    active_properties = [
        key
        for key, edit in (draft.get("property_edits") or {}).items()
        if isinstance(edit, dict) and edit.get("is_active", True)
    ]

    return [
        ui.metric_tile("Länge", f"{draft.get('rounds', '?')} Ticks"),
        ui.metric_tile(
            "Wiederholungen",
            "alle Szenarien" if draft.get("run_all_sweeps") else draft.get("run_count", 1),
        ),
        ui.metric_tile(
            "Ziel-Auslastung",
            (
                f"{float(feedback.get('target_booking_rate', 0.37)):.0%}"
                if feedback.get("enabled", True)
                else "Preis fix"
            ),
        ),
        ui.metric_tile("Segmente", len(segments)),
        ui.metric_tile("Aktive Systemgrößen", len(active_properties)),
        ui.metric_tile(
            "Zufallsstartwert",
            draft.get("seed", "—") if draft.get("use_seed") else f"{DEFAULT_SEED} (Standard)",
            hint="Ohne eigenen Startwert rechnet der Lauf mit dem Standardwert.",
        ),
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

    return ui.expert(
        html.Div(
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
        ),
        count=len(zeilen),
        title="Woran dieser Lauf später wiederzuerkennen ist",
        names="Codestand, Fingerabdruck der Konfiguration",
    )


def _zustand(draft: dict):
    """Den Zustand bauen, den der Lauf bekäme — für den Fingerabdruck."""

    from dashboard.config_catalog import prepare_simulation_state

    return prepare_simulation_state(draft_from_dict(draft))


def _warnings(draft: dict, errors: list[str]) -> list:
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
        warnings.append(ui.alert(text, "error"))

    # Zwei der Hinweise unten gelten nur für einen Lauf: Der Vergleich hat einen
    # vorgegebenen Startwert und wendet eigene Werte ohnehin nicht an. Sie dort
    # zu zeigen hieße, zu einer Einstellung zu raten, die nicht wirkt.
    vergleich = ist_vergleich(draft)

    if not vergleich and not draft.get("use_seed") and int(draft.get("run_count") or 1) > 1:
        warnings.append(
            ui.alert(
                "Mehrere Wiederholungen ohne festen Zufallsstartwert: Die Läufe werden sich "
                "unterscheiden. Das ist gewollt, wenn Sie die Streuung sehen wollen — für "
                "einen sauberen A/B-Vergleich setzen Sie den Startwert unter «Feinabstimmung».",
                "info",
            )
        )
    if draft.get("no_scenarios"):
        warnings.append(
            ui.alert(
                "«Keine Szenarien erzeugen» ist aktiv — der Tab «Szenario» bleibt nach dem "
                "Lauf leer, obwohl er die Hauptansicht ist.",
                "warning",
            )
        )
    if (
        not vergleich
        and draft.get("scenario_mode") != "sweep"
        and not draft.get("apply_custom_overrides")
    ):
        warnings.append(
            ui.alert(
                "«Eigene Werte anwenden» ist aus — Änderungen an Faktoren und Systemgrößen "
                "wirken in diesem Lauf nicht.",
                "warning",
            )
        )
    return warnings


#: Was im Bedienfeld von den sechs Kacheln übrig bleibt. Die drei, die vor dem
#: Start wirklich zählen; der Rest steht im Bereich «Einrichten», wo er
#: eingestellt wird.
_COMPACT_TILES = 3


def preflight(
    draft: dict, errors: list[str], *, slot: str = "setup", compact: bool = False
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
    return html.Div(
        [
            ui.card(html.Div(ui.markdown(summary_sentence(draft)), id=summary_id(slot))),
            html.Div(_warnings(draft, errors), className="space-y-2 mt-4"),
            html.Div(vorgaben_hinweis(draft), className="mt-4"),
            html.Div(dauer.hinweis(draft), className="mt-4"),
            html.Div(herkunft(draft) if not compact else None, className="mt-4"),
            html.Div(
                ui.grid(
                    *(tiles[:_COMPACT_TILES] if compact else tiles),
                    cols="grid-cols-1" if compact else "sm:grid-cols-2 lg:grid-cols-3",
                    gap="gap-2" if compact else "gap-4",
                ),
                className="mt-4",
            ),
        ]
    )


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
        "schnellste Einstieg — es legt Faktorlage, Politik und Kosten in einem Zug fest.",
        ui.card(
            ui.radio(
                choice_options(),
                value=of(draft),
                id=FIELD_ID,
                cards=True,
                legend="Was soll gerechnet werden? Die Annahmenwelt des Laufs.",
            ),
            html.Div(scenario_details(draft), id=slot_id("scenario"), className="mt-5"),
        ),
        actions=ui.doc_link("presets"),
    )


def scope_step(draft: dict, number: int | None = 2) -> object:
    return _step(
        number,
        "Wie weit reicht der Lauf?",
        "Ein Tick ist eine Modellrunde, kein Kalenderzeitraum. Mehr Ticks heißt mehr "
        "Gelegenheiten für Rückkopplung zwischen Preis und Nachfrage.",
        ui.card(
            c.number(
                "rounds",
                draft.get("rounds"),
                min=1,
                max=500,
                step=1,
                detail=True,
                class_name="max-w-xs",
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
                        className="pt-7",
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
                className="mt-5 pt-4 af-border-t af-border-subtle",
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
