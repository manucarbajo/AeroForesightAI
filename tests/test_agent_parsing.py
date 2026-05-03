import pytest
from src.models.agent_models import AgentResponse, StateChange
from src.models.enums import AgentType


def _make_valid_response(**kwargs) -> AgentResponse:
    defaults = {
        "agent_id": "consumer",
        "round_number": 1,
        "reasoning": "Test reasoning",
        "actions": ["test_action"],
        "state_changes": [],
        "segment_analysis": {},
        "raw_output": "",
    }
    defaults.update(kwargs)
    return AgentResponse(**defaults)


def test_agent_response_valid():
    response = _make_valid_response()
    assert response.agent_id == "consumer"
    assert response.round_number == 1
    assert response.reasoning == "Test reasoning"
    assert response.actions == ["test_action"]


def test_agent_response_default_fields():
    response = _make_valid_response()
    assert response.state_changes == []
    assert response.segment_analysis == {}
    assert response.raw_output == ""


def test_agent_response_with_state_changes():
    state_change = StateChange(
        factor_id="F1",
        proposed_state="F1.2",
        reasoning="Test reasoning"
    )
    response = _make_valid_response(state_changes=[state_change])
    assert len(response.state_changes) == 1
    assert response.state_changes[0].factor_id == "F1"
    assert response.state_changes[0].proposed_state == "F1.2"


def test_agent_response_with_segment_analysis():
    segment_analysis = {
        "leisure_price_sensitive": "Nachfrage sinkt stark",
        "business_traveler": "Kaum Auswirkungen",
    }
    response = _make_valid_response(
        agent_id="consumer",
        segment_analysis=segment_analysis
    )
    assert "leisure_price_sensitive" in response.segment_analysis
    assert "business_traveler" in response.segment_analysis


def test_agent_response_multiple_actions():
    response = _make_valid_response(actions=["action_1", "action_2", "action_3"])
    assert len(response.actions) == 3


def test_state_change_valid():
    change = StateChange(
        factor_id="F2",
        proposed_state="F2.2",
        reasoning="Regulierung verschärft"
    )
    assert change.factor_id == "F2"
    assert change.proposed_state == "F2.2"
    assert change.reasoning != ""


def test_agent_response_missing_required_fields():
    with pytest.raises(Exception):
        AgentResponse(
            agent_id="consumer",
            # round_number fehlt
            reasoning="Test",
            actions=[],
        )


def test_agent_response_all_agent_types():
    for agent_id in ["consumer", "provider", "regulator"]:
        response = _make_valid_response(agent_id=agent_id)
        assert response.agent_id == agent_id