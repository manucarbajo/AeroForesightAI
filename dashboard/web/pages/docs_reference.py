"""Referenzkapitel des Handbuchs — aus Code und Konfiguration erzeugt.

Alles hier wird zur Laufzeit aus `glossary.py` und den Dateien unter
`configs/` gelesen. Eine neue Systemgröße, ein neues Preset oder ein neuer
Parameter erscheint dadurch von selbst im Handbuch, und kein Wert kann von
dem abweichen, mit dem tatsächlich gerechnet wird.

Jede Funktion liefert Markdown-Quelltext, keine Dash-Komponenten — damit
laufen erzeugte und geschriebene Kapitel durch dieselbe Darstellung und
landen gemeinsam im Suchindex.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from dashboard.config_catalog import EINHEITEN, configs_dir, list_sweep_presets, load_config_file
from dashboard.web import formate
from dashboard.web.config_editor import glossary

#: Rollenbezeichnungen für `agent_profiles.json`.
AGENT_LABELS = {
    "consumer": "Consumer — die Nachfrageseite",
    "provider": "Provider — die Airline",
    "regulator": "Regulator — die Politik",
}

#: Einheiten aus `properties.json` in lesbare Form — die Langform aus
#: `config_catalog.EINHEITEN`, der einen Quelle (P7.1-U1.5).
UNIT_LABELS = {kennung: lang for kennung, (_, lang) in EINHEITEN.items()}


def _escape(text: Any) -> str:
    """Pipe-Zeichen maskieren, damit sie keine Tabellenspalte aufreißen."""

    return str(text if text is not None else "").replace("|", "\\|").strip()


def _number(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


# --- Parameter -------------------------------------------------------------


def parameter() -> str:
    lines = [
        "Alle Einstellungen des Konfigurations-Editors, nach Themen geordnet. Die letzte "
        "Spalte nennt das Feld in den Dateien unter `configs/` — dort steht derselbe Wert, "
        "wenn Sie ihn außerhalb der Oberfläche nachsehen wollen.",
        "",
    ]
    for group in glossary.GROUPS:
        lines += [f"## {group.title}", "", group.intro, ""]
        lines += ["| Einstellung | Bedeutung | Einheit | Feld in `configs/` |", "|---|---|---|---|"]
        for path in group.paths:
            param = glossary.get(path)
            if param is None:
                continue
            lines.append(
                f"| **{_escape(param.label)}** "
                f"| {_escape(param.detail or param.short)} "
                f"| {_escape(param.unit) or '—'} "
                f"| {'`' + _escape(param.technical) + '`' if param.technical else '—'} |"
            )
        lines.append("")
    return "\n".join(lines)


# --- Faktoren --------------------------------------------------------------


def faktoren() -> str:
    payload = load_config_file("factors.json")
    lines = [
        "Die sieben Faktoren beschreiben die Welt, in der ein Lauf stattfindet. Jeder hat "
        "genau zwei mögliche Zustände. **Sie stellen sie nicht ein** — der Lauf erzeugt "
        "sie aus den exogenen Größen des gewählten Rahmenszenarios.",
        "",
        "Zu einer Kombination aller sieben Zustände kann die eingefrorene Matrix einen "
        "Konsistenzwert ausrechnen. **Er misst Polarität, nicht Plausibilität** — wie "
        "einheitlich gepolt eine Lage ist, nicht wie wahrscheinlich sie eintritt. Deshalb "
        "heißt er im Artefakt «Widerspruchsfreiheit» und nicht mehr «Plausibilität».",
        "",
    ]
    for key in sorted(payload):
        factor = payload[key]
        if not isinstance(factor, dict) or not factor.get("name"):
            continue
        lines += [
            f"## {key} · {_escape(factor.get('name'))}",
            "",
            _escape(factor.get("description")),
            "",
            "| Zustand | Bedeutung |",
            "|---|---|",
        ]
        for state, description in (factor.get("possible_states") or {}).items():
            lines.append(f"| `{_escape(state)}` | {_escape(description)} |")
        lines.append("")
    return "\n".join(lines)


# --- Systemgrößen ----------------------------------------------------------


def systemgroessen() -> str:
    payload = load_config_file("properties.json")
    system = [item for item in payload.get("system_properties", []) if isinstance(item, dict)]
    individual = [
        item for item in payload.get("individual_properties", []) if isinstance(item, dict)
    ]

    lines = [
        "Systemgrößen sind die Zahlen hinter den Faktoren: Politik, Kosten, Konjunktur. "
        "Jede hat einen Startwert und kann sich über Regeln im Lauf verändern. "
        "Zu bearbeiten im Bereich «Modell», Abschnitt «Rahmenbedingungen».",
        "",
        "## Größen des Systems",
        "",
        "| Größe | Bedeutung | Einheit | Bereich |",
        "|---|---|---|---|",
    ]
    for item in system:
        low, high = item.get("min_value"), item.get("max_value")
        span = "—" if low is None and high is None else f"{_number(low)} – {_number(high)}"
        unit = UNIT_LABELS.get(item.get("unit", ""), item.get("unit") or "—")
        lines.append(
            f"| `{_escape(item.get('id'))}` "
            f"| {_escape(item.get('description')) or '—'} "
            f"| {_escape(unit)} "
            f"| {_escape(span)} |"
        )

    lines += [
        "",
        "## Eigenschaften einer Person",
        "",
        "Diese Merkmale trägt jede simulierte Person. Aus ihnen entsteht die "
        "Kaufentscheidung. Anteile und Verteilungen legen Sie im Bereich "
        "«Modell» fest, Abschnitt «Nachfrage & Preisbildung».",
        "",
        "| Merkmal | Art | Bedeutung |",
        "|---|---|---|",
    ]
    for item in individual:
        kind = "Zugehörigkeit (ja/nein)" if item.get("type") == "boolean" else "Verteilung"
        lines.append(
            f"| `{_escape(item.get('id'))}` "
            f"| {kind} "
            f"| {_escape(item.get('description')) or '—'} |"
        )
    lines.append("")
    return "\n".join(lines)


# --- Presets ---------------------------------------------------------------


def presets() -> str:
    sweeps = list_sweep_presets()
    lines = [
        "Fertige Annahmenwelten. Ein Preset legt Politik, Kosten und Konjunktur in einem "
        "Zug fest und ist der schnellste Einstieg in einen Lauf; die Faktorlage "
        "entsteht daraus im Lauf. Auswahl im Bereich «Einrichten», erster Schritt; "
        "über «Werte übernehmen und selbst anpassen» wandern die Einstellungen in "
        "Ihren Entwurf und lassen sich einzeln verändern.",
        "",
    ]
    if not sweeps:
        return "\n".join(lines + ["Keine Presets unter `configs/sweeps/` gefunden."])

    for sweep in sweeps:
        lines += [
            f"## {_escape(sweep.name)}",
            "",
            f"`{_escape(sweep.id)}` · {formate.ticks_mit_modellzeit(sweep.max_ticks)}",
            "",
            _escape(sweep.description),
            "",
        ]
        if getattr(sweep, "rationale", ""):
            lines += [sweep.rationale.strip(), ""]

        milestones = _milestones(sweep.id)
        if milestones:
            lines += [
                "Erwarteter Verlauf:",
                "",
                "| Ab Tick | Was gelten sollte |",
                "|---|---|",
            ]
            for tick, description in milestones:
                lines.append(f"| {tick} | {_escape(description)} |")
            lines.append("")
    return "\n".join(lines)


def _milestones(sweep_id: str) -> list[tuple[Any, str]]:
    """Meilensteine eines Presets lesen — sie stehen nur in der Datei, nicht im Modell."""

    path = Path(configs_dir()) / "sweeps" / f"{sweep_id}.json"
    if not path.is_file():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return [
        (item.get("tick", "?"), item.get("description", ""))
        for item in payload.get("milestones", [])
        if isinstance(item, dict)
    ]


# --- Akteure ---------------------------------------------------------------


def akteure() -> str:
    payload = load_config_file("agent_profiles.json")
    lines = [
        "Die drei Akteure sind informationsbeschränkt: Jeder sieht nur, was sein Profil "
        "erlaubt, und darf nur vorschlagen, was dort steht. Das ist keine Empfehlung, "
        "sondern wird in Python geprüft — ein Agent, der eine Kennzahl nennen wollte, "
        "kommt damit nicht durch.",
        "",
    ]
    for key, profile in payload.items():
        if not isinstance(profile, dict):
            continue
        lines += [
            f"## {AGENT_LABELS.get(key, key.title())}",
            "",
            "| | |",
            "|---|---|",
            f"| Sieht | {_escape(', '.join(profile.get('observes') or [])) or '—'} |",
            f"| Darf vorschlagen | {_escape(', '.join(profile.get('may_propose') or [])) or 'nichts'} |",
            f"| Darf nie ausgeben | {_escape(', '.join(profile.get('must_not_output') or [])) or '—'} |",
            f"| Hängt ab von | {_escape(', '.join(profile.get('depends_on') or [])) or '—'} |",
            "",
        ]
    return "\n".join(lines)
