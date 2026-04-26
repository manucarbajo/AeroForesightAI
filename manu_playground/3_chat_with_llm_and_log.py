import os
from datetime import datetime
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver

#Log File festlegen
LOG_FILE = "chat_log.txt"

#Logging-Funktion
def log_to_file(user_msg, ai_msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}]\n")
        f.write(f"USER: {user_msg}\n")
        f.write(f"AI  : {ai_msg}\n")
        f.write("-" * 30 + "\n")

class State(TypedDict):
    messages: Annotated[list, add_messages]

#LLM initialisieren
llm = ChatOllama(
    model="llama3.1:8b",
    temperature=0.7,
)

#Knoten definieren
def chatbot(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

#Langgraph bauen
graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()

#Memory für Gedächtnis des LLM (mehrere Antworten möglich)
memory = MemorySaver()
#Übergabe des memory-Objekts für den Graphen
graph = graph_builder.compile(checkpointer=memory)

# Konfiguration für Thread (Chatsitzung)
config = {"configurable": {"thread_id": "1"}}

print("Chatbot gestartet! (Tippe 'exit' um zu beenden)")
print("-" * 50)

# Die Endlos-Schleife für die Konsole
while True:
    # Input Nutzer
    user_input = input("\nDu: ")
    
    # Wann Abbruch?
    if user_input.lower() in ["exit"]:
        print("Chat beendet.")
        break

    # Graph starten -> config mitgeben, damit Memory gefunden wird
    result = graph.invoke({"messages": [("user", user_input)]}, config)

    # Output auslesen
    ai_response = result["messages"][-1].content

    # Output LLM
    print("\nOllama:", ai_response)
    print("-" * 50)

    # Log speichern
    log_to_file(user_input, ai_response)