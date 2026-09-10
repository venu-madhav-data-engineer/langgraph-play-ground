"""Interactive CLI Runner for LangGraph Agents."""
import sys
from pathlib import Path

# Ensure repository root is on sys.path
_repo_root = str(Path(__file__).resolve().parents[4])
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from core.state import KeyValueState
from tools.calculator import calculator
from tools.sql import SQLDatabase, create_sample_ecommerce_db
from examples.ex04_sql_agent.main import build_sql_agent
from langchain_core.messages import HumanMessage

class InteractiveState(TypedDict):
    query: str
    response: str

# Shared SQL agent instance
_sql_db = create_sample_ecommerce_db()
_sql_agent = build_sql_agent(_sql_db)

SQL_KEYWORDS = (
    "sql", "select", "table", "schema", "customer", "product",
    "order", "revenue", "spend", "database", "stock", "drop"
)

def agent_node(state: InteractiveState) -> dict:
    query = state["query"].strip()
    lower_query = query.lower()

    # 1. SQL Query routing (explicit prefix or domain keywords)
    if lower_query.startswith("/sql") or any(kw in lower_query for kw in SQL_KEYWORDS):
        clean_q = query[4:].strip() if lower_query.startswith("/sql") else query
        try:
            cfg = {"configurable": {"thread_id": "cli-session"}}
            sql_res = _sql_agent.invoke(
                {"user_query": clean_q, "messages": [HumanMessage(content=clean_q)]},
                config=cfg,
            )
            return {"response": f"\n{sql_res['messages'][-1].content}"}
        except Exception as e:
            return {"response": f"SQL Agent Error: {e}"}

    # 2. Math calculation query
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
