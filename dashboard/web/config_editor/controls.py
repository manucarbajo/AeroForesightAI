"""Eingabefelder des Config-Editors und der Weg ihrer Werte in den Store.

Streamlit las Widget-Werte einfach von oben nach unten ab. Dash braucht dafür
Callbacks — bei rund sechzig Feldern wäre einer pro Feld unhaltbar. Stattdessen
trägt jedes Feld eine Pattern-Matching-ID mit dem Pfad, an dem sein Wert im
Draft steht (`market_feedback_edit.damping`, `factor_states.F3`, …), und **ein**
Callback schreibt alle sichtbaren Felder auf einmal an ihren Platz.

Damit bleibt der Editor deklarativ: eine neue Einstellung ist ein Feld mit
einem Pfad, kein zusätzlicher Callback.
"""

from __future__ import annotations

from typing import Any, Iterable

from dash import dcc, html

from dashboard.web import components as ui

#: Skalare Felder (Zahl, Text, Auswahl, Schieberegler).
CFG = "cfg"
#: Checkboxen — ihr Wert ist eine Liste, deshalb ein eigener Typ.
CFG_BOOL = "cfg-bool"
#: Schaltflächen, die den Entwurf strukturell ändern (Preset übernehmen,
#: Property anlegen, speichern …).
ACTION = "cfg-action"
#: Freie Eingaben, die *nicht* im Draft landen (neue Property-ID, Preset-Name).
FREE = "cfg-free"

# Aktions- und Freitext-IDs sind bewusst Pattern-Matching-IDs: die zugehörigen
# Elemente stehen jeweils nur in einem Tab. Ein Callback auf eine feste ID, die
# gerade nicht im DOM liegt, quittiert Dash im Browser mit einer Fehlermeldung —
# bei Pattern-Matching ist eine leere Treffermenge dagegen der Normalfall.


def cfg_id(field: str, kind: str = CFG) -> dict:
    return {"type": kind, "field": field}


def action_id(name: str) -> dict:
    return {"type": ACTION, "action": name}


def free_id(name: str) -> dict:
    return {"type": FREE, "name": name}


def free_value(states: list, name: str, default: str = "") -> str:
    """Wert einer Freitext-Eingabe aus `ctx.states_list` herausfischen."""

    for entry in states or []:
        if (entry.get("id") or {}).get("name") == name:
            return entry.get("value") or default
    return default


# --- Pfad-Zugriff ----------------------------------------------------------


def get_path(data: dict, path: str, default: Any = None) -> Any:
    """`market_feedback_edit.damping` aus dem Store-Dict lesen."""

    current: Any = data
    for part in path.split("."):
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, list):
            try:
                current = current[int(part)]
            except (ValueError, IndexError):
                return default
        else:
            return default
        if current is None:
            return default
    return current


def set_path(data: dict, path: str, value: Any) -> None:
    """Wert an einem Punktpfad setzen; fehlende Zwischenebenen entstehen als Dict."""

    parts = path.split(".")
    current: Any = data
    for part in parts[:-1]:
        if isinstance(current, list):
            try:
                current = current[int(part)]
                continue
            except (ValueError, IndexError):
                return
        if not isinstance(current, dict):
            return
        if part not in current or not isinstance(current[part], (dict, list)):
            current[part] = {}
        current = current[part]

    last = parts[-1]
    if isinstance(current, list):
        try:
            current[int(last)] = value
        except (ValueError, IndexError):
            return
    elif isinstance(current, dict):
        current[last] = value


def apply_inputs(data: dict, entries: Iterable[tuple[dict, Any]]) -> dict:
    """Alle sichtbaren Feldwerte in eine Kopie des Drafts schreiben."""

    updated = dict(data)
    for identifier, value in entries:
        field = (identifier or {}).get("field")
        if not field:
            continue
        if identifier.get("type") == CFG_BOOL:
            value = bool(value)
        set_path(updated, field, value)
    return updated


# --- Felder ----------------------------------------------------------------


def number(
    label: str,
    field: str,
    value: Any,
    *,
    min: float | None = None,
    max: float | None = None,
    step: float | None = None,
    hint: str | None = None,
    class_name: str = "",
) -> html.Div:
    return ui.field(
        label,
        dcc.Input(
            id=cfg_id(field),
            type="number",
            value=value,
            min=min,
            max=max,
            step=step,
            className="af-input",
            debounce=True,
        ),
        hint=hint,
        class_name=class_name,
    )


def text(
    label: str,
    field: str,
    value: Any,
    *,
    placeholder: str = "",
    hint: str | None = None,
    class_name: str = "",
) -> html.Div:
    return ui.field(
        label,
        dcc.Input(
            id=cfg_id(field),
            type="text",
            value=value or "",
            placeholder=placeholder,
            className="af-input",
            debounce=True,
        ),
        hint=hint,
        class_name=class_name,
    )


def textarea(
    label: str, field: str, value: Any, *, hint: str | None = None, class_name: str = ""
) -> html.Div:
    return ui.field(
        label,
        # dcc.Textarea kennt kein `debounce` — der Wert läuft pro Tastendruck
        # in den Store. Bei einem Beschreibungsfeld ist das verkraftbar.
        dcc.Textarea(id=cfg_id(field), value=value or "", className="af-input"),
        hint=hint,
        class_name=class_name,
    )


def select(
    label: str,
    field: str,
    value: Any,
    options: list[dict],
    *,
    hint: str | None = None,
    clearable: bool = False,
    class_name: str = "",
) -> html.Div:
    return ui.field(
        label,
        dcc.Dropdown(
            id=cfg_id(field),
            options=options,
            value=value,
            clearable=clearable,
            className="af-dropdown",
        ),
        hint=hint,
        class_name=class_name,
    )


def slider(
    label: str,
    field: str,
    value: float,
    *,
    min: float = 0.0,
    max: float = 1.0,
    step: float = 0.05,
    hint: str | None = None,
    class_name: str = "",
) -> html.Div:
    marks = {min: f"{min:g}", max: f"{max:g}"}
    return ui.field(
        label,
        html.Div(
            dcc.Slider(
                id=cfg_id(field),
                min=min,
                max=max,
                step=step,
                value=value,
                marks=marks,
                tooltip={"placement": "bottom", "always_visible": True},
                className="af-slider",
            ),
            className="pt-1",
        ),
        hint=hint,
        class_name=class_name,
    )


def check(label: str, field: str, value: bool, *, hint: str | None = None) -> html.Div:
    return ui.checkbox(label, value=bool(value), id=cfg_id(field, CFG_BOOL), hint=hint)
