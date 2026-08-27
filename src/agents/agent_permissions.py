"""Wer darf welchen Faktor vorschlagen — eine Quelle, eine Prüfung (P0.5).

Bis P0.5 gab es beides doppelt. Die Quellen: ein hartcodiertes Dict
``AGENT_FACTOR_PERMISSIONS`` in `market.factor_dynamics` und ``may_propose`` in
`configs/agent_profiles.json`. Die Prüfungen: `agents.agent_node` filterte beim
Parsen gegen das Profil, `market.factor_dynamics.validate_factor_proposals`
später noch einmal gegen das Dict. Beide stimmten überein — aber nichts hielt
sie synchron, und die durchsetzende war die hartcodierte. Eine neue
Berechtigung in der JSON wäre still ins Leere gelaufen.

Das greift Invariante 2 direkt an, deshalb ist der Zuschnitt hier eng:
`configs/agent_profiles.json` ist die Quelle, `may_propose_factor` ist die
Prüfung, und beide Aufrufer benutzen sie.

**Ohne Profil ist nichts erlaubt.** Auch das war vorher uneinheitlich: Der
Parser ließ ohne Profil alles durch, die Durchsetzung ließ ohne Eintrag nichts
durch. Für eine Berechtigungsregel ist nur eine Richtung vertretbar — wer nicht
ausdrücklich darf, darf nicht.
"""

from __future__ import annotations

from src.models.agent_models import AgentProfile

#: Präfix, mit dem ein ``may_propose``-Eintrag eine Faktor-Berechtigung
#: ausdrückt. Stand nach P0.4 an drei Stellen als Zeichenkette im Code —
#: Parser, Durchsetzung und Validierung. Jetzt einmal hier.
FACTOR_PERMISSION_PREFIX = "factor_state "


def factor_permission_entry(factor_id: str) -> str:
    """Die ``may_propose``-Schreibweise für einen Faktor."""

    return f"{FACTOR_PERMISSION_PREFIX}{factor_id}"


def parse_factor_permission(entry: str) -> str | None:
    """Faktor-ID aus einem ``may_propose``-Eintrag — oder ``None``.

    ``None`` heißt: Der Eintrag ist keine Faktor-Berechtigung (z. B. ``events``).
    """

    if not entry.startswith(FACTOR_PERMISSION_PREFIX):
        return None
    return entry.removeprefix(FACTOR_PERMISSION_PREFIX).strip()


def permitted_factor_ids(profile: AgentProfile | None) -> frozenset[str]:
    """Alle Faktoren, die dieses Profil vorschlagen darf."""

    if profile is None:
        return frozenset()
    return frozenset(
        factor_id
        for factor_id in (parse_factor_permission(entry) for entry in profile.may_propose)
        if factor_id
    )


def may_propose_factor(profile: AgentProfile | None, factor_id: str) -> bool:
    """Die eine Prüfung. Beide Aufrufer rufen sie, keiner prüft selbst."""

    return factor_id in permitted_factor_ids(profile)
