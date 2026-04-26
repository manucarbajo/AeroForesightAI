from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama

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

#Input des Users
#user_input = "Wenn du ein Mensch wärst, was für einen Namen würdest du dir geben?"
user_input = "Was ist die Hauptstadt von Deutschland? Antworte ausschließlich in Emojis."
initial_state = {"messages": [("user", user_input)]}

#Ausgabe des Modells
result = graph.invoke(initial_state)

#Ausgabe Konsole
print("\n--- Ollama Antwort ---")
print(result["messages"][-1].content)