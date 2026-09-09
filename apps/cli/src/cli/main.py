"""Interactive CLI Runner for LangGraph Agents."""
import sys
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from core.state import KeyValueState
from tools.calculator import calculator

class InteractiveState(TypedDict):
    query: str
    response: str

def agent_node(state: InteractiveState) -> dict:
    query = state["query"].strip()
    # Check if this is a calculation query
    if any(char in query for char in "+-*/"):
        try:
            expr = "".join(c for c in query if c in "0123456789+-*/.() ")
            calc_res = calculator.invoke({"expression": expr.strip()})
            return {"response": f"Calculation Result: {calc_res}"}
        except Exception as e:
            return {"response": f"Error calculating: {e}"}
    return {"response": f"Agent processed query: '{query}'"}

def build_cli_graph():
    builder = StateGraph(InteractiveState)
    builder.add_node("agent", agent_node)
    builder.add_edge(START, "agent")
    builder.add_edge("agent", END)
    return builder.compile()

def main():
    print("=" * 60)
    print(" LangGraph Playground - Interactive Agent CLI")
    print(" Type your message/expression below. Type 'exit' or 'quit' to exit.")
    print("=" * 60)

    graph = build_cli_graph()

    while True:
        try:
            user_input = input("\nYou > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("Exiting playground CLI. Bye!")
                break

            result = graph.invoke({"query": user_input, "response": ""})
            print(f"Agent > {result['response']}")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting playground CLI. Bye!")
            break

if __name__ == "__main__":
    main()
