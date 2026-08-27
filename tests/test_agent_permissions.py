"""P0.5 — Faktor-Berechtigungen aus einer Quelle, geprüft an einer Stelle.

Das Abnahmekriterium steht in `TestJsonIstDieQuelle`: Eine Berechtigung, die
nur in `agent_profiles.json` ergänzt wird, muss **ohne Codeänderung** wirken.
Vor P0.5 hätte sie das nicht — die durchsetzende Quelle war ein hartcodiertes
Dict, das die JSON gar nicht las.
"""

from __future__ import annotations

import json

import pytest

from src.agents.agent_node import AgentNode
from src.agents.agent_permissions import (
    factor_permission_entry,
    may_propose_factor,
    parse_factor_permission,
    permitted_factor_ids,
)
from src.config_loader import build_initial_state
from src.market.factor_dynamics import validate_factor_proposals
from src.models.agent_models import AgentConfig, AgentProfile, StateChange
from src.models.enums import AgentType


def _regulator(state, may_propose: list[str] | None) -> AgentConfig:
    """Ersetzt den Regulator im State durch einen mit gegebener Berechtigung."""

    config = AgentConfig(
        id="regulator",
        name="Regulator",
        agent_type=AgentType.REGULATOR,
        description="Test",
        goals=[],
        profile=None if may_propose is None else AgentProfile(may_propose=may_propose),
    )
    state.agents = [config]
    return config


def _target_state(state, factor_id: str) -> str:
    """Ein Zustand des Faktors, der nicht der aktuelle ist."""

    factor = state.environment.factors[factor_id]
    return next(s for s in factor.possible_states if s != factor.current_state)


class TestGrammatik:
    """Die Schreibweise `factor_state F2` steht nur noch an einer Stelle."""

    def test_roundtrip(self) -> None:
        assert parse_factor_permission(factor_permission_entry("F2")) == "F2"

    def test_non_factor_entry_is_none(self) -> None:
        assert parse_factor_permission("events") is None

    def test_permitted_ids_ignore_non_factor_entries(self) -> None:
        profile = AgentProfile(may_propose=["events", "factor_state F2", "factor_state F6"])
        assert permitted_factor_ids(profile) == frozenset({"F2", "F6"})

    def test_no_profile_permits_nothing(self) -> None:
        """Vorher ließ der Parser ohne Profil alles durch, die Durchsetzung
        nichts. Für eine Berechtigungsregel ist nur eine Richtung vertretbar."""

        assert permitted_factor_ids(None) == frozenset()
        assert may_propose_factor(None, "F2") is False


class TestBeidePruefstellenStimmenUeberein:
    """Vor P0.5 prüften Parser und Durchsetzung unabhängig voneinander."""

    CASES = [
        (["factor_state F2"], "F2", True),
        (["factor_state F2"], "F6", False),
        (["events"], "F2", False),
        ([], "F2", False),
        (None, "F2", False),
    ]

    @pytest.mark.parametrize(("may_propose", "factor_id", "expected"), CASES)
    def test_parser_and_enforcement_agree(
        self, may_propose: list[str] | None, factor_id: str, expected: bool
    ) -> None:
        state = build_initial_state()
        config = _regulator(state, may_propose)
        target = _target_state(state, factor_id)

        node = AgentNode(config, llm=lambda _: "{}")
        parsed = node._parse_state_changes(
            [{"factor_id": factor_id, "proposed_state": target, "reasoning": "x"}],
            state,
        )
        assert bool(parsed) is expected

        gated = validate_factor_proposals(
            state,
            [StateChange(factor_id=factor_id, proposed_state=target, reasoning="x")],
            agent_id="regulator",
        )
        # Die Durchsetzung prüft zusätzlich gegen die Faktor-Regeln des Ticks;
        # verboten bleibt verboten, erlaubt darf trotzdem am Regelfilter hängen.
        if not expected:
            assert gated == []


class TestJsonIstDieQuelle:
    """Das Abnahmekriterium: Eine Änderung in der JSON wirkt ohne Codeänderung."""

    def test_shipped_profiles_match_the_removed_hardcoded_dict(self) -> None:
        """Das gelöschte Dict sagte regulator={F2,F6}, provider/consumer leer.
        Genau das muss die JSON jetzt allein liefern."""

        state = build_initial_state()
        by_id = {agent.id: agent for agent in state.agents}
        assert permitted_factor_ids(by_id["regulator"].profile) == frozenset({"F2", "F6"})
        assert permitted_factor_ids(by_id["provider"].profile) == frozenset()
        assert permitted_factor_ids(by_id["consumer"].profile) == frozenset()

    def test_new_permission_in_json_reaches_enforcement(self, tmp_path, monkeypatch) -> None:
        """Der eigentliche Nachweis: Eine Berechtigung, die **nur** in
        `agent_profiles.json` ergänzt wird, wirkt bis in die Durchsetzung —
        ohne dass F4 für den Regulator irgendwo im Code vorkommt.

        Gebaut wird dafür ein Konfigurationsverzeichnis, in dem genau diese eine
        Zeile mehr steht. Alles andere ist identisch, und der einzige
        Unterschied zwischen den beiden Läufen unten ist das Profil.
        """

        from src import config_loader

        state = build_initial_state()
        # F4 steht auf F4.1, und eine Faktor-Regel erlaubt bei hohem Kostendruck
        # den Wechsel auf F4.2. Damit hängt der Vorschlag nur noch an der
        # Berechtigung — genau das soll geprüft werden.
        state.environment.factors["F4"].current_state = "F4.1"
        state.market_metrics = {"cost_pressure": 150.0}
        proposal = [StateChange(factor_id="F4", proposed_state="F4.2", reasoning="x")]

        assert (
            validate_factor_proposals(state, proposal, agent_id="regulator") == []
        ), "F4 ist in der ausgelieferten JSON nicht erlaubt — sonst prüft dieser Test nichts"

        source = config_loader.CONFIGS_DIR
        for name in ("agents.json", "agent_profiles.json"):
            (tmp_path / name).write_text(
                (source / name).read_text(encoding="utf-8"), encoding="utf-8"
            )
        profiles = json.loads((tmp_path / "agent_profiles.json").read_text(encoding="utf-8"))
        profiles["regulator"]["may_propose"].append(factor_permission_entry("F4"))
        (tmp_path / "agent_profiles.json").write_text(
            json.dumps(profiles, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        monkeypatch.setattr(config_loader, "CONFIGS_DIR", tmp_path)
        state.agents = config_loader.load_agents(tmp_path / "agents.json")

        gated = validate_factor_proposals(state, proposal, agent_id="regulator")
        assert [change.factor_id for change in gated] == ["F4"]

    def test_provider_still_may_not_propose_factors(self) -> None:
        """Invariante 2: Provider und Consumer schlagen nur Events vor."""

        state = build_initial_state()
        provider = next(agent for agent in state.agents if agent.id == "provider")
        target = _target_state(state, "F2")

        gated = validate_factor_proposals(
            state,
            [StateChange(factor_id="F2", proposed_state=target, reasoning="x")],
            agent_id="provider",
        )
        assert gated == []
        assert permitted_factor_ids(provider.profile) == frozenset()


class TestDasDictIstWeg:
    def test_hardcoded_permissions_are_gone(self) -> None:
        """Regression: Solange das Dict existiert, kann es wieder auseinanderlaufen."""

        import src.market.factor_dynamics as factor_dynamics

        assert not hasattr(factor_dynamics, "AGENT_FACTOR_PERMISSIONS")

    def test_package_no_longer_exports_it(self) -> None:
        import src.market as market

        assert "AGENT_FACTOR_PERMISSIONS" not in market.__all__
