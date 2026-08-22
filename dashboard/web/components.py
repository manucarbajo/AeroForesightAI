"""Wiederverwendbare Bausteine im Landingpage-Stil.

Die Klassennamen sind Tailwind-Utilities — dieselbe Konfiguration, die
`aeroforesight-ai-landing-page/index.html` lädt. Damit bleibt die Optik ohne
zweites Design-System deckungsgleich; alles, was Utilities nicht abdecken
(Dropdowns, Tabs, Plotly-Modebar), steht in `assets/dashboard.css`.
"""

from __future__ import annotations

import json
from typing import Any, Iterable

from dash import dcc, html

# --- Klassenbausteine ------------------------------------------------------

CARD = "bg-white border border-slate-200 rounded-lg"
CARD_PAD = f"{CARD} p-5 sm:p-6"
LABEL = "block font-body text-sm font-medium text-slate-700 mb-1.5"
HINT = "font-body text-xs text-slate-500 mt-1.5 leading-relaxed"
CAPTION = "font-body text-xs text-slate-500"
H1 = "font-headline text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight"
H2 = "font-headline text-xl font-semibold text-slate-900 tracking-tight"
H3 = "font-headline text-base font-semibold text-slate-900"

_BUTTON_BASE = (
    "inline-flex items-center justify-center gap-2 px-5 py-2.5 font-body text-sm "
    "font-medium rounded transition-colors duration-200 border cursor-pointer "
    "disabled:opacity-50 disabled:cursor-not-allowed"
)
_BUTTON_VARIANTS = {
    "primary": "bg-navy-800 text-white border-navy-800 hover:bg-navy-700 shadow-sm",
    "secondary": "bg-white text-navy-800 border-slate-200 hover:bg-slate-50",
    "danger": "bg-white text-rose-800 border-rose-200 hover:bg-rose-50",
}

_ALERT_VARIANTS = {
    "info": ("bg-navy-50 border-navy-200 text-navy-900", "info"),
    "success": ("bg-teal-50 border-teal-200 text-teal-900", "check_circle"),
    "warning": ("bg-amber-50 border-amber-200 text-amber-900", "warning"),
    "error": ("bg-rose-50 border-rose-200 text-rose-900", "error"),
}


# --- Bausteine -------------------------------------------------------------


def icon(name: str, class_name: str = "text-base") -> html.Span:
    """Material-Symbol wie auf der Landingpage."""

    return html.Span(name, className=f"material-symbols-outlined {class_name}")


def card(*children: Any, class_name: str = "", pad: bool = True) -> html.Div:
    base = CARD_PAD if pad else CARD
    return html.Div(list(children), className=f"{base} {class_name}".strip())


def section(
    title: str | None,
    *children: Any,
    subtitle: str | None = None,
    actions: Any = None,
    class_name: str = "",
) -> html.Section:
    head: list[Any] = []
    if title or actions:
        head.append(
            html.Div(
                [
                    html.Div(
                        [
                            html.H2(title, className=H2) if title else None,
                            html.P(subtitle, className=f"{CAPTION} mt-1") if subtitle else None,
                        ]
                    ),
                    (
                        html.Div(actions, className="flex items-center gap-2 shrink-0")
                        if actions
                        else None
                    ),
                ],
                className="flex items-start justify-between gap-4 mb-4 flex-wrap",
            )
        )
    return html.Section(head + list(children), className=f"mb-8 {class_name}".strip())


def page_heading(title: str, subtitle: str | None = None) -> html.Div:
    return html.Div(
        [
            html.H1(title, className=H1),
            html.P(subtitle, className="font-body text-slate-600 mt-2") if subtitle else None,
        ],
        className="mb-6",
    )


def button(label: str, *, variant: str = "primary", icon_name: str | None = None, **kwargs: Any):
    children: list[Any] = [label]
    if icon_name:
        children.append(icon(icon_name, "text-sm"))
    class_name = f"{_BUTTON_BASE} {_BUTTON_VARIANTS.get(variant, _BUTTON_VARIANTS['primary'])}"
    extra = kwargs.pop("className", "")
    return html.Button(children, className=f"{class_name} {extra}".strip(), n_clicks=0, **kwargs)


def field(label: str, control: Any, *, hint: str | None = None, class_name: str = "") -> html.Div:
    return html.Div(
        [
            html.Label(label, className=LABEL),
            control,
            html.P(hint, className=HINT) if hint else None,
        ],
        className=class_name,
    )


def checkbox(label: str, *, value: bool, hint: str | None = None, **kwargs: Any) -> html.Div:
    """Einzelne Checkbox mit Beschriftung — ersetzt ``st.checkbox``."""

    return html.Div(
        [
            dcc.Checklist(
                options=[{"label": label, "value": "on"}],
                value=["on"] if value else [],
                className="af-check",
                inputClassName="af-check__input",
                labelClassName="af-check__label",
                **kwargs,
            ),
            html.P(hint, className=f"{HINT} ml-6") if hint else None,
        ]
    )


def metric_tile(label: str, value: Any, hint: str | None = None) -> html.Div:
    return html.Div(
        [
            html.Div(label.upper(), className="font-body text-xs tracking-wider text-slate-500"),
            html.Div(
                str(value),
                className="font-headline text-2xl font-bold text-navy-800 mt-1 tracking-tight",
            ),
            html.Div(hint, className=f"{CAPTION} mt-1") if hint else None,
        ],
        className=f"{CARD} p-4",
    )


def alert(text: Any, kind: str = "info", *, class_name: str = "") -> html.Div:
    classes, icon_name = _ALERT_VARIANTS.get(kind, _ALERT_VARIANTS["info"])
    body = dcc.Markdown(text, className="af-md") if isinstance(text, str) else text
    return html.Div(
        [
            icon(icon_name, "text-lg shrink-0 mt-0.5"),
            html.Div(body, className="font-body text-sm leading-relaxed min-w-0"),
        ],
        className=f"flex items-start gap-3 border rounded px-4 py-3 {classes} {class_name}".strip(),
    )


def empty_state(text: str, *, hint: str | None = None, icon_name: str = "inbox") -> html.Div:
    return html.Div(
        [
            icon(icon_name, "text-3xl text-slate-300"),
            html.P(text, className="font-body text-sm text-slate-600 mt-3"),
            html.P(hint, className=f"{CAPTION} mt-1 max-w-md") if hint else None,
        ],
        className=f"{CARD} flex flex-col items-center justify-center text-center px-6 py-12",
    )


def accordion(title: Any, *children: Any, open: bool = False, badge: str | None = None):
    """Aufklappbarer Block — ersetzt ``st.expander`` ohne eigenen Callback."""

    summary = html.Summary(
        [
            icon("chevron_right", "af-acc__chevron text-lg text-slate-400"),
            html.Span(title, className="font-body text-sm font-medium text-slate-800 flex-1"),
            (
                html.Span(
                    badge,
                    className="font-body text-xs text-navy-700 bg-navy-50 border border-navy-100 rounded-full px-2 py-0.5",
                )
                if badge
                else None
            ),
        ],
        className="af-acc__summary flex items-center gap-2 cursor-pointer select-none px-4 py-3",
    )
    return html.Details(
        [summary, html.Div(list(children), className="px-4 pb-4 pt-1")],
        open=open,
        className=f"af-acc {CARD} mb-2",
    )


def code_block(text: str, *, max_height: str = "24rem") -> html.Pre:
    return html.Pre(
        text,
        className="af-code font-mono text-xs text-slate-700 bg-slate-50 border border-slate-200 "
        "rounded p-4 overflow-auto whitespace-pre",
        style={"maxHeight": max_height},
    )


def json_view(payload: Any, *, max_height: str = "24rem") -> html.Pre:
    try:
        text = json.dumps(payload, indent=2, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        text = str(payload)
    return code_block(text, max_height=max_height)


def markdown(text: str, *, class_name: str = "") -> dcc.Markdown:
    """Markdown mit den Typo-Regeln aus `assets/dashboard.css`."""

    return dcc.Markdown(text or "", className=f"af-md {class_name}".strip(), link_target="_blank")


def tabs(tab_id: str, items: Iterable[tuple[str, str]], value: str) -> dcc.Tabs:
    """Tab-Leiste im Landingpage-Stil (Unterstrich, Navy aktiv)."""

    return dcc.Tabs(
        id=tab_id,
        value=value,
        parent_className="af-tabs",
        className="af-tabs__list",
        content_className="af-tabs__content",
        children=[
            dcc.Tab(
                label=label,
                value=val,
                className="af-tab",
                selected_className="af-tab--selected",
            )
            for label, val in items
        ],
    )


def grid(*children: Any, cols: str = "md:grid-cols-2", gap: str = "gap-4") -> html.Div:
    return html.Div(list(children), className=f"grid grid-cols-1 {cols} {gap}")


def divider(class_name: str = "my-6") -> html.Hr:
    return html.Hr(className=f"border-slate-200 {class_name}")
