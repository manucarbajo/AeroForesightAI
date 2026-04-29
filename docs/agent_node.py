import json
import logging
from typing import Dict, Any, List

# --- Annahme: Die Modelle kommen aus AP1 ---
# from src.models import AgentResponse, EventLogEntry 

# Dummy-Klassen für die Unabhängigkeit dieses Snippets (kann durch AP1-Imports ersetzt werden)
class AgentResponse:
    def __init__(self, reasoning: str, action_type: str, action_details: Dict[str, Any]):
        self.reasoning = reasoning
        self.action_type = action_type
        self.action_details = action_details

class EventLogEntry:
    def __init__(self, agent_id: str, event_type: str, description: str):
        self.agent_id = agent_id
        self.event_type = event_type
        self.description = description

logger = logging.getLogger(__name__)

class AgentNode:
    """
    Knoten für die Agentenlogik. Nimmt den Mock/State entgegen, baut den Prompt, 
    parsed die LLM-Antwort und erzeugt die entsprechenden AP1-Datenmodelle.
    """
    def __init__(self, agent_id: str, prompt_template_path: str):
        self.agent_id = agent_id
        self.prompt_template = self._load_prompt(prompt_template_path)

    def _load_prompt(self, path: str) -> str:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Prompt template {path} not found.")
            return "{market_state} {agent_state}"

    def _build_prompt(self, market_state: Dict[str, Any], agent_state: Dict[str, Any]) -> str:
        """
        Setzt die States in das Template Pattern ein.
        """
        market_str = json.dumps(market_state, indent=2)
        agent_str = json.dumps(agent_state, indent=2)
        
        return self.prompt_template.format(
            market_state=market_str,
            agent_state=agent_str
        )

    def _parse_response(self, raw_llm_response: str) -> AgentResponse:
        """
        Wandelt rohe LLM-Antwort in eine AgentResponse um. 
        Implementiert Fallback-Logik bei Parsing-Fehlern.
        """
        # Vorverarbeitung, falls das LLM Markdown-Ticks ignoriert hat und doch mitschickt
        cleaned_response = raw_llm_response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]

        try:
            data = json.loads(cleaned_response)
            return AgentResponse(
                reasoning=data.get("reasoning", "Keine Begründung geliefert."),
                action_type=data.get("action_type", "WARTEN"),
                action_details=data.get("action_details", {})
            )
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM response for {self.agent_id}: {e}")
            # Fallback Default-Response
            return AgentResponse(
                reasoning="Fallback: JSON konnte nicht geparst werden.",
                action_type="WARTEN",
                action_details={}
            )

    def _create_event_entries(self, raw_llm_response: str) -> List[EventLogEntry]:
        """
        Extrahiert die EventLog-Rohdaten aus der Antwort.
        """
        events = []
        try:
            cleaned = raw_llm_response.strip().removeprefix("```json").removesuffix("```").strip()
            data = json.loads(cleaned)
            logs = data.get("event_logs", [])
            for log in logs:
                events.append(EventLogEntry(
                    agent_id=self.agent_id,
                    event_type=log.get("event_type", "UNKNOWN"),
                    description=log.get("description", "Keine Beschreibung")
                ))
        except Exception as e:
            logger.warning(f"Fehler bei Event-Extraktion für {self.agent_id}: {e}")
            events.append(EventLogEntry(
                agent_id=self.agent_id,
                event_type="ERROR",
                description="Konnte EventLogs nicht auslesen"
            ))
        return events

# --- Mock Testing für den Developer (wird beim Import ignoriert) ---
if __name__ == "__main__":
    # Teste den Node mit Mock-State
    mock_market = {"current_price_wheat": 5.0, "demand": "high"}
    mock_agent = {"inventory_wheat": 10, "budget": 100}
    
    # Simuliere einen Consumer
    node = AgentNode("consumer_1", "src/prompts/consumer.md")
    prompt = node._build_prompt(mock_market, mock_agent)
    
    # Simuliere die (rohe) Antwort eines LLMs
    mock_llm_response = """
    {
      "reasoning": "Der Preis ist gut, ich kaufe Weizen.",
      "action_type": "KAUFEN",
      "action_details": {"target": "market", "amount": 5, "price": 5.0},
      "event_logs": [{"event_type": "DECISION", "description": "Kaufentscheidung getroffen."}]
    }
    """
    
    response_obj = node._parse_response(mock_llm_response)
    events = node._create_event_entries(mock_llm_response)
    
    print(f"Parsed Action: {response_obj.action_type}")
    print(f"Parsed Reasoning: {response_obj.reasoning}")
    print(f"Extracted Events Count: {len(events)}")