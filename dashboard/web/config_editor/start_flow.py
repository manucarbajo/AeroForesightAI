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
from dashboard.web.config_editor import compute_mode
from dashboard.web.config_editor import controls as c
from dashboard.web.state import draft_from_dict
from src.models.state_models import DEFAULT_SEED

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


def summary_sentence(draft: dict) -> str:
    """Was gleich passiert — in einem Satz, ohne Fachbegriffe."""

    if draft.get("run_all_sweeps"):
        count = len(list_sweep_presets())
        scope = f"**alle {count} hinterlegten Szenarien** nacheinander"
    else:
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


def _choice_label(title: str, description: str) -> html.Div:
    """Titel und ein Satz dazu — als Inhalt einer Karte im Raster.

    Untereinander war jede dieser Beschriftungen in einer schmalen Spalte gut
    100 px hoch; zehn davon ergaben drei Bildschirme. Nebeneinander sind es
    drei Reihen, und die Beschreibungen bleiben lesbar statt zu verschwinden.
    """

    return html.Div(
        [
            html.Span(title, className="font-body text-sm font-medium af-text"),
            html.Span(description, className=f"{ui.CAPTION} block mt-0.5 leading-relaxed"),
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
            {"label": _choice_label(preset.name, preset.description), "value": preset.id}
        )
    options.append(
        {
            "label": _choice_label(
                "Eigene Einstellungen",
                "Was weiter unten unter «Alle Einstellungen» eingestellt ist.",
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
        ui.note(
            "Das Szenario gilt **unverändert**: Faktorlage, Politik und Kosten kommen aus "
            f"`{preset.id}.json`, Ihre Einstellungen im Editor bleiben dafür außen vor. "
            f"Angelegt ist es auf **{preset.max_ticks} Ticks** — die Länge stellen Sie im "
            "nächsten Schritt selbst ein."
        )
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


def _tiles(draft: dict) -> list:
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

    if not draft.get("use_seed") and int(draft.get("run_count") or 1) > 1:
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
    if draft.get("scenario_mode") != "sweep" and not draft.get("apply_custom_overrides"):
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


def _step(number: int, title: str, lede: str, *children: object, actions: object = None):
    return ui.section(f"{number}. {title}", ui.lede(lede), *children, actions=actions)


def _scenario_step(draft: dict) -> object:
    return _step(
        1,
        "Was soll gerechnet werden?",
        "Die Annahmenwelt, von der der Lauf ausgeht. Ein vorbereitetes Szenario ist der "
        "schnellste Einstieg — es legt Faktorlage, Politik und Kosten in einem Zug fest.",
        ui.card(
            ui.radio(choice_options(), value=of(draft), id=FIELD_ID, cards=True),
            html.Div(scenario_details(draft), id=slot_id("scenario"), className="mt-5"),
        ),
        actions=ui.doc_link("presets"),
    )


def _scope_step(draft: dict) -> object:
    return _step(
        2,
        "Wie weit reicht der Lauf?",
        "Ein Tick ist eine Modellrunde, kein Kalenderzeitraum. Mehr Ticks heißt mehr "
        "Gelegenheiten für Rückkopplung zwischen Preis und Nachfrage.",
        ui.card(
            c.number(
                "rounds",
                int(draft.get("rounds") or 40),
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
                        int(draft.get("run_count") or 1),
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


def _mode_step(draft: dict) -> object:
    seed = draft.get("seed")
    return _step(
        3,
        "Womit wird gerechnet?",
        "Die Zahlen sind in allen drei Fällen dieselben — Preise, Buchungsraten und "
        "Faktorzustände berechnet immer das Rechenmodell. Die Auswahl bestimmt nur, wie "
        "viel dazu erzählt wird.",
        ui.card(
            ui.radio(compute_mode.OPTIONS, value=compute_mode.of(draft), id=compute_mode.FIELD_ID),
            html.Div(
                compute_mode.placeholder("start"),
                className="mt-5 pt-4 af-border-t af-border-subtle",
            ),
            ui.expert(
                ui.grid(
                    c.check("use_seed", bool(draft.get("use_seed")), detail=True),
                    c.number(
                        "seed", int(seed if seed is not None else DEFAULT_SEED), min=0, step=1
                    ),
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
            _scenario_step(draft),
            # `2xl` und nicht `xl`: Tailwinds Haltepunkte messen das **Fenster**,
            # der Inhalt steht aber in einer Zone, die schmaler ist als das
            # Fenster. Bei 1280 px teilte `xl` die 720 px des Viewports in zwei
            # 319-px-Spalten — genau die Enge, gegen die dieses Paket antritt.
            ui.grid(_scope_step(draft), _mode_step(draft), cols="2xl:grid-cols-2", gap="gap-8"),
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
