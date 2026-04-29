from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver

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

# 6. Konfiguration für Thread (Chatsitzung)
config = {"configurable": {"thread_id": "1"}}

print("Chatbot gestartet! (Tippe 'exit' um zu beenden)")
print("-" * 50)

# 7. Die Endlos-Schleife für die Konsole
while True:
    # Input Nutzer
    user_input = input("\nDu: ")
    
    # Wann Abbruch?
    if user_input.lower() in ["exit"]:
        print("Chat beendet.")
        break

    # Graph starten -> config mitgeben, damit Memory gefunden wird
    result = graph.invoke({"messages": [("user", user_input)]}, config)

    # Output LLM
    print("\nOllama:", result["messages"][-1].content)
    print("-" * 50)