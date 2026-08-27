"""Die eine Auswertung einer ``when``-Klausel (P0.4).

Bis P0.4 gab es diese Auswertung **dreimal**: in `factor_dynamics.rule_matches`
für die Faktor-Regeln, in `population_sampler._rule_matches` für die
Shift-Regeln und ein drittes Mal in `simulation_functions` für die Aktivierung
der regulatorischen Kostentreiber. Die drei kannten unterschiedlich viele
Bedingungen, und wer eine Regel schrieb, die eine der Stellen nicht verstand,
bekam keinen Fehler — die Regel griff einfach nie.

Deshalb zwei Grundsätze in diesem Modul:

1. **Eine Klausel, eine Bedeutung.** Alle Regelarten werden von derselben
   Funktion ausgewertet, mit demselben Vokabular.
2. **Struktureller Unsinn schlägt laut fehl.** Ein unbekannter Schlüssel, ein
   Vergleich ohne Bezugsgröße oder ein ``factor`` ohne ``state`` wirft
   `UnknownRuleConditionError`, statt still `False` zu liefern.

Bewusst **nicht** hier geprüft werden Namen: ob es die Metrik `booking_rate`
oder die Systemgröße `carbon_tax_level` überhaupt gibt, entscheidet
`src/validation.py` beim Laden der Config — dort sind die Vokabulare bekannt,
und dort ist ein Tippfehler auch vor dem ersten Tick sichtbar. Zur Laufzeit
heißt "Wert nicht da" schlicht: Bedingung nicht erfüllt. Das ist ein normaler
Zustand, kein Fehler (`booking_rate` existiert im ersten Tick noch nicht).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, fields
from typing import Any

from src.models.state_models import FactorState


class UnknownRuleConditionError(ValueError):
    """Eine ``when``-Klausel ist strukturell nicht auswertbar."""


@dataclass(frozen=True)
class RuntimeMetrics:
    """Momentaufnahme des Tick-Kontexts für die Regelauswertung.

    Liegt hier und nicht bei den Marktfunktionen, damit `validation.py` das
    Vokabular der Metriknamen kennt, ohne das halbe Marktpaket zu importieren.
    Gebaut wird die Momentaufnahme in `market.factor_dynamics`, weil sie den
    `SimulationState` braucht.
    """

    tick: int
    booking_rate: float | None
    prior_booking_rate: float | None
    cost_pressure: float | None
    cost_index: float | None
    ticket_price: float | None
    demand_level: float | None
    carbon_tax_level: float | None
    saf_mandate_share: float | None
    fuel_price_change: float | None
    oil_price_index: float | None

    def as_mapping(self) -> dict[str, float | None]:
        return {field.name: getattr(self, field.name) for field in fields(self)}


#: Namen, die in ``{"metric": ...}`` stehen dürfen.
KNOWN_METRICS: frozenset[str] = frozenset(field.name for field in fields(RuntimeMetrics))

#: Bezugsgrößen einer Klausel. ``tick`` ist die Kurzform für
#: ``{"metric": "tick", "eq": N}`` und die einzige, die ihren Wert direkt trägt.
NUMERIC_SUBJECTS: frozenset[str] = frozenset({"tick", "metric", "system_property"})

#: Vergleiche. ``gte``/``lte`` sind die Altnamen von ``at_least``/``at_most``
#: und bleiben erlaubt, damit bestehende Klauseln nicht umgeschrieben werden
#: müssen.
OPERATORS: frozenset[str] = frozenset({"above", "below", "at_least", "at_most", "eq", "gte", "lte"})

KNOWN_KEYS: frozenset[str] = NUMERIC_SUBJECTS | OPERATORS | frozenset({"factor", "state"})


@dataclass(frozen=True)
class RuleContext:
    """Alles, wogegen eine Klausel in einem Tick geprüft wird."""

    tick: int
    factors: Mapping[str, FactorState]
    metrics: Mapping[str, float | None]
    system_properties: Mapping[str, float]

    @classmethod
    def from_metrics(
        cls,
        metrics: RuntimeMetrics,
        *,
        factors: Mapping[str, FactorState],
        system_properties: Mapping[str, float],
    ) -> RuleContext:
        return cls(
            tick=metrics.tick,
            factors=factors,
            metrics=metrics.as_mapping(),
            system_properties=system_properties,
        )


def _fail(rule_id: str, message: str) -> None:
    where = f"Regel '{rule_id}': " if rule_id else ""
    raise UnknownRuleConditionError(f"{where}{message}")


def _numeric_subject(when: Mapping[str, Any], rule_id: str) -> str | None:
    """Die eine numerische Bezugsgröße der Klausel — oder keine."""

    present = sorted(key for key in NUMERIC_SUBJECTS if key in when)
    if len(present) > 1:
        _fail(
            rule_id,
            f"mehrere Bezugsgrößen in einer Klausel ({', '.join(present)}). "
            "Ein Vergleich ließe sich dann keiner davon zuordnen — "
            "bitte auf mehrere Regeln aufteilen.",
        )
    return present[0] if present else None


def _resolve_numeric(
    when: Mapping[str, Any],
    subject: str,
    context: RuleContext,
    rule_id: str,
) -> float | None:
    if subject == "tick":
        return float(context.tick)
    name = str(when[subject])
    if subject == "metric":
        return context.metrics.get(name)
    value = context.system_properties.get(name)
    return None if value is None else float(value)


def _compare(value: float, when: Mapping[str, Any]) -> bool:
    if "above" in when and value <= float(when["above"]):
        return False
    if "below" in when and value >= float(when["below"]):
        return False
    if "at_least" in when and value < float(when["at_least"]):
        return False
    if "gte" in when and value < float(when["gte"]):
        return False
    if "at_most" in when and value > float(when["at_most"]):
        return False
    if "lte" in when and value > float(when["lte"]):
        return False
    if "eq" in when and value != float(when["eq"]):
        return False
    return True


def check_when(when: Mapping[str, Any] | None, *, rule_id: str = "") -> None:
    """Prüft eine Klausel auf strukturelle Auswertbarkeit — ohne Kontext.

    Wird von `rule_matches` benutzt und von `validation.py`, damit ein Fehler
    schon beim Laden der Config auffällt und nicht erst in dem Tick, in dem die
    Regel greifen sollte.
    """

    if not when:
        return

    unknown = sorted(set(when) - KNOWN_KEYS)
    if unknown:
        _fail(
            rule_id,
            f"unbekannte Bedingung(en) {', '.join(repr(key) for key in unknown)}. "
            f"Erlaubt sind: {', '.join(sorted(KNOWN_KEYS))}.",
        )

    subject = _numeric_subject(when, rule_id)
    operators = sorted(key for key in OPERATORS if key in when)

    if subject == "tick" and operators:
        _fail(
            rule_id,
            f"'tick' trägt seinen Wert bereits ({when['tick']!r}) und verträgt sich "
            f"nicht mit {', '.join(operators)}. Für einen Bereich "
            "{'metric': 'tick', 'at_least': N} schreiben.",
        )

    if operators and subject is None:
        _fail(
            rule_id,
            f"Vergleich {', '.join(operators)} ohne Bezugsgröße. "
            "'metric', 'system_property' oder 'tick' fehlt.",
        )

    if subject in {"metric", "system_property"} and not operators:
        _fail(
            rule_id,
            f"'{subject}' ohne Vergleich. "
            f"Erwartet wird einer von: {', '.join(sorted(OPERATORS))}.",
        )

    if "factor" in when:
        # Bewusst nicht `str(when.get("state", ""))`: `str(None)` ist "None" und
        # damit wahrheitswertig. Ein `"state": null` kam so durch die Prüfung und
        # wurde danach gegen den Zustand "None" verglichen — der Regel fehlte
        # nichts Sichtbares, sie traf nur nie zu. Genau die stille
        # Wirkungslosigkeit, gegen die P0.4 angetreten ist; der Leerstring
        # daneben wurde längst abgewiesen. Gefunden 2026-08-27.
        state = when.get("state")
        if not isinstance(state, str) or not state.strip():
            _fail(
                rule_id,
                f"'factor': {when['factor']!r} braucht ein 'state' als nicht leeren "
                f"Text, nicht {state!r}. Ohne Zielzustand könnte die Bedingung nie "
                "zutreffen.",
            )

    if "state" in when and "factor" not in when:
        _fail(rule_id, "'state' ohne 'factor'.")

    for key in operators + (["tick"] if subject == "tick" else []):
        try:
            value = float(when[key])
        except (TypeError, ValueError):
            _fail(rule_id, f"'{key}': {when[key]!r} ist keine Zahl.")
            return
        # Ein Tick ist ein Tick (Invariante 5). `rule_matches` vergleicht über
        # `int(...)`, das eine Nachkommastelle stillschweigend abschneidet:
        # `{"tick": 3.7}` griff in Tick 3. Ein Zahlendreher sah damit aus wie
        # eine Regel, die einfach woanders greift. Gefunden 2026-08-27.
        if key == "tick" and value != int(value):
            _fail(
                rule_id,
                f"'tick': {when[key]!r} ist keine ganze Zahl. Ticks sind ganzzahlig — "
                "für einen Bereich {'metric': 'tick', 'at_least': N} schreiben.",
            )


def rule_matches(
    when: Mapping[str, Any] | None,
    context: RuleContext,
    *,
    rule_id: str = "",
) -> bool:
    """Trifft die Klausel im gegebenen Kontext zu?

    Eine leere Klausel schränkt nichts ein und trifft damit zu. Ob eine Regel
    *ohne* Bedingung fachlich zulässig ist, entscheidet nicht dieses Modul:
    `regulatory_influences` dürfen unbedingt gelten, `factor_rules` und
    `shift_rules` weist `validation.py` ab.
    """

    check_when(when, rule_id=rule_id)
    if not when:
        return True

    if "factor" in when:
        factor = context.factors.get(str(when["factor"]))
        if factor is None or factor.current_state != str(when["state"]):
            return False

    subject = _numeric_subject(when, rule_id)
    if subject is None:
        return True

    if subject == "tick":
        return context.tick == int(when["tick"])

    value = _resolve_numeric(when, subject, context, rule_id)
    if value is None:
        return False
    return _compare(value, when)


_OPERATOR_LABELS = {
    "above": ">",
    "below": "<",
    "at_least": "≥",
    "gte": "≥",
    "at_most": "≤",
    "lte": "≤",
    "eq": "=",
}


def _number(value: Any) -> str:
    try:
        return f"{float(value):g}"
    except (TypeError, ValueError):
        return str(value)


def describe_when(when: Mapping[str, Any] | None) -> str:
    """Die Klausel als Fließtext — für Protokoll und Handbuch.

    Bewusst dieselbe Quelle wie `rule_matches`: Der Protokollgenerator hatte
    seine eigene, unvollständige Beschreibung und nannte eine Regel ohne
    Bedingung "immer", während der Code sie nie greifen ließ.
    """

    if not when:
        return "immer"

    parts: list[str] = []
    if "factor" in when:
        parts.append(f"Faktor {when['factor']} = {when.get('state', '?')}")

    if "tick" in when:
        parts.append(f"Tick = {when['tick']}")
    elif "metric" in when or "system_property" in when:
        subject = "metric" if "metric" in when else "system_property"
        label = f"`{when[subject]}`"
        comparisons = [
            f"{label} {_OPERATOR_LABELS[key]} {_number(when[key])}"
            for key in ("above", "below", "at_least", "gte", "at_most", "lte", "eq")
            if key in when
        ]
        parts.extend(comparisons or [label])

    return ", ".join(parts) if parts else "immer"
