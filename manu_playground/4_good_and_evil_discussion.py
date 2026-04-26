import os
from datetime import datetime
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama

# Konfiguration
LOG_FILE = "4_chat_log.txt"
MAX_RUNDEN = 3 

# Logging
def log_to_file(user_msg, agent_messages):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}]\n")
        f.write(f"THEMA: {user_msg}\n")
        f.write("-" * 20 + "\n")
        for msg in agent_messages:
            f.write(f"{msg.content}\n\n")
        f.write("=" * 50 + "\n")

class State(TypedDict):
    messages: Annotated[list, add_messages]

# LLM initialisieren
llm = ChatOllama(
    #model="llama3.1:8b",
    model="dolphin-llama3",
    temperature=0.7,
)

# Hilfsfunktion, damit Agenten History wissen.
def format_history(messages):
    return "\n".join([msg.content for msg in messages])


# Knoten
# Dummy-Knoten für  parallele Steuerung (verteilt nur)
def start_round_node(state: State):
    return {}

# Sammelt die Antworten
def parallel_collector_node(state: State):
    return {} 

# 1. Optimist
def optimist_node(state: State):
    print(" Optimist...") 
    history = format_history(state["messages"])
    prompt = f"""Du bist der Optimist in einer moderierten Debatte.

Bisheriger Verlauf:
{history}

Deine Aufgabe:
Beziehe dich direkt auf die ALLERLETZTE Nachricht (die Eingangsfrage des Nutzers oder die letzte Frage des Orchestrators).
Antworte darauf aus positiver Sicht. 
Antworte in MAXIMAL 2 kurzen Sätzen.
Beginne deine Antwort IMMER mit '[Optimist]: '"""
    
    response = llm.invoke(prompt)
    return {"messages": [response]}

# 2. Pessimist
def pessimist_node(state: State):
    print(" Pessimist...") 
    history = format_history(state["messages"])
    prompt = f"""Du bist der Pessimist in einer moderierten Debatte.

Bisheriger Verlauf:
{history}

Deine Aufgabe:
Beziehe dich direkt auf die ALLERLETZTE Nachricht (die Eingangsfrage des Nutzers oder die letzte Frage des Orchestrators).
Antworte darauf aus kritischer Sicht und betone die Risiken/Gefahren.
Antworte in MAXIMAL 2 kurzen Sätzen.
Beginne deine Antwort IMMER mit '[Pessimist]: '"""
    
    response = llm.invoke(prompt)
    return {"messages": [response]}

# 3. Orchestrator (Zusammenfassung Runde)
def orchestrator_summary_node(state: State):
    print(" Orchestrator fasst zusammen und fragt weiter...") 
    history = format_history(state["messages"])
    prompt = f"""Du bist der neutrale Orchestrator.

Bisheriger Verlauf:
{history}

Deine Aufgabe:
Lies die beiden gerade abgegebenen Argumente von Optimist und Pessimist.
Fasse die Punkte in 1 Satz neutral zusammen und stelle dann eine neue, vertiefende Frage an die beiden, um die Debatte voranzutreiben.
Beginne deine Antwort IMMER  mit '[Zusammenfassung]: '"""
    
    response = llm.invoke(prompt)
    return {"messages": [response]}

# 4. Orchestrator (Finales Urteil)
def orchestrator_decider_node(state: State):
    print(" Orchestrator fällt das finale Urteil...\n") 
    history = format_history(state["messages"])
    prompt = f"""Du bist der neutrale Schiedsrichter. Die Debatte ist beendet.

Kompletter Verlauf:
{history}

Deine Aufgabe:
Bestimme EINEN KLAREN GEWINNER basierend auf den vorgebrachten Argumenten. Kein Unentschieden!

Antworte EXAKT nach diesem Muster (keine anderen Worte davor oder danach!):
GEWINNER: <Schreibe hier nur "Optimist" oder "Pessimist">
BEGRÜNDUNG: <Schreibe hier in 2-3 Sätzen, warum diese Seite gewonnen hat>"""
    
    response = llm.invoke(prompt)
    return {"messages": [response]}


# Weichenfunktionen
def route_after_parallel(state: State) -> Literal["orchestrator_summary", "orchestrator_decider"]:
    messages = state["messages"]
    
    # Runden berechnen
    expected_messages = 1 + (MAX_RUNDEN * 2) + (MAX_RUNDEN - 1)
    
    if len(messages) >= expected_messages:
        # Maximale Anzahl erreicht?
        return "orchestrator_decider"
        
    #  Nein? Weiter machen
    return "orchestrator_summary"


# Graph bauen
graph_builder = StateGraph(State)

graph_builder.add_node("start_round", start_round_node)
graph_builder.add_node("optimist", optimist_node)
graph_builder.add_node("pessimist", pessimist_node)
graph_builder.add_node("parallel_collector", parallel_collector_node)
graph_builder.add_node("orchestrator_summary", orchestrator_summary_node)
graph_builder.add_node("orchestrator_decider", orchestrator_decider_node)

# Ablauf
# Start geht in den Runden-Verteiler
graph_builder.add_edge(START, "start_round")

# Vom Verteiler geht es PARALLEL an beide
graph_builder.add_edge("start_round", "optimist")
graph_builder.add_edge("start_round", "pessimist")

# Beide fließen nach ihrer Antwort im Sammler zusammen
graph_builder.add_edge("optimist", "parallel_collector")
graph_builder.add_edge("pessimist", "parallel_collector")

# Vom Sammler wird geprüft, ob es weitergeht oder zu Ende ist
graph_builder.add_conditional_edges(
    "parallel_collector", 
    route_after_parallel,
    {"orchestrator_summary": "orchestrator_summary", "orchestrator_decider": "orchestrator_decider"}
)

# Nach der Zusammenfassung beginnt die nächste Runde
graph_builder.add_edge("orchestrator_summary", "start_round")

# Nach dem finalen Urteil ist Schluss
graph_builder.add_edge("orchestrator_decider", END)

graph = graph_builder.compile()


# Durchlauf
if __name__ == "__main__":
    print("-" * 50)
    user_input = input(f"Dein Thema:")

    if user_input.strip():
        print(f"\nStart Debatte ...\n")

        result = graph.invoke({"messages": [("user", user_input)]})
        agent_messages = result["messages"][1:]
        
        print("=" * 50)
        for msg in agent_messages[:-1]:
            # Ignoriere leere Nachrichten von Dummy-Knoten beim Printen
            if msg.content.strip(): 
                print(msg.content)
                print("-" * 50)

        print("\n" + "-" * 30)
        print("       URTEIL DES ORCHESTRATORS")
        print("-" * 30 + "\n")
        print(agent_messages[-1].content)
        print("\n" + "=" * 50)

        # Filtere leere Dummy-Nachrichten aus dem Log
        clean_messages = [m for m in agent_messages if m.content.strip()]
        log_to_file(user_input, clean_messages)
        print(f"(Die Diskussion wurde in '{LOG_FILE}' gespeichert.)")