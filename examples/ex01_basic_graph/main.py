"""01. Basic Graph Example.

Demonstrates a simple linear StateGraph in LangGraph.
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class GreetingState(TypedDict):
    name: str
    greeting: str

def greet_node(state: GreetingState) -> dict[str, str]:
    return {"greeting": f"Hello, {state['name']}! Welcome to LangGraph Playground."}

def excitement_node(state: GreetingState) -> dict[str, str]:
    return {"greeting": f"{state['greeting']} Ready to build stateful AI workflows!"}

def build_graph():
    builder = StateGraph(GreetingState)
    builder.add_node("greeter", greet_node)
    builder.add_node("excitement", excitement_node)

    builder.add_edge(START, "greeter")
    builder.add_edge("greeter", "excitement")
    builder.add_edge("excitement", END)

    return builder.compile()

if __name__ == "__main__":
    graph = build_graph()
    initial_input: GreetingState = {"name": "Developer", "greeting": ""}
    print("Running 01_basic_graph:")
    result = graph.invoke(initial_input)
    print(f"Final output: {result}")
