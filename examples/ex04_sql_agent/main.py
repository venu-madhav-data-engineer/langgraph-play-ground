"""04. SQL Agent Example with Self-Correction and Safety Guardrails.

Demonstrates a deterministic state machine with:
- Schema discovery
- SQL generation & guardrail validation (blocking DROP/DELETE/UPDATE)
- Execution against SQLite
- Self-healing loop when execution triggers database errors
- Result synthesis
"""

import re
import sqlite3
from functools import partial
from typing import Any, Literal
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from core.state import SQLAgentState
from tools.sql import SQLDatabase, create_sample_ecommerce_db


# --- Nodes ---

def fetch_schema_node(state: SQLAgentState, db: SQLDatabase) -> dict[str, Any]:
    """Inspects the database and populates schema context into state."""
    schemas = db.get_all_schemas()
    return {
        "schema_context": schemas,
        "retry_count": state.get("retry_count", 0),
        "max_retries": state.get("max_retries", 2),
        "error": None,
    }


def generate_sql_node(state: SQLAgentState) -> dict[str, Any]:
    """
    Generates SQL based on the user query and schema context.
    In production, this queries an LLM. Here we implement deterministic
    domain routing to simulate queries and test self-healing.
    """
    query = state.get("user_query", "").lower()

    if "top customer" in query or "highest spend" in query:
        sql = "SELECT customer_name, total_spent, country FROM customers ORDER BY total_spent DESC LIMIT 3;"
    elif "low stock" in query or "product stock" in query:
        sql = "SELECT product_name, category, price, stock_quantity FROM products ORDER BY stock_quantity ASC LIMIT 3;"
    elif "revenue" in query or "order count" in query or "total order" in query:
        sql = "SELECT COUNT(*) AS total_orders, ROUND(SUM(total_amount), 2) AS total_revenue FROM orders;"
    elif "from usa" in query or "american customer" in query:
        sql = "SELECT customer_name, email, country, total_spent FROM customers WHERE country = 'USA';"
    elif "trigger_error" in query or "invalid column" in query:
        # Intentionally faulty query to demonstrate the self-correction loop
        sql = "SELECT customer_name, non_existent_column FROM customers LIMIT 3;"
    elif "drop table" in query:
        # Malicious query to test guardrail rejection
        sql = "DROP TABLE customers;"
    else:
        # Generic query fallback
        sql = "SELECT * FROM customers LIMIT 3;"

    return {"sql_query": sql, "error": None}


def guardrail_check_node(state: SQLAgentState, db: SQLDatabase) -> dict[str, Any]:
    """Validates the generated SQL for safety (read-only, no destructive keywords)."""
    sql = state.get("sql_query") or ""
    is_valid, error_msg = db.validate_query(sql)
    if not is_valid:
        return {"error": f"Guardrail Violation: {error_msg}"}
    return {"error": None}


def execute_sql_node(state: SQLAgentState, db: SQLDatabase) -> dict[str, Any]:
    """Executes the validated SQL against the database, catching any runtime errors."""
    sql = state.get("sql_query") or ""
    try:
        results = db.run_query(sql)
        return {"sql_result": results, "error": None}
    except (sqlite3.Error, PermissionError) as exc:
        return {
            "sql_result": None,
            "error": f"Database Error: {exc}",
            "retry_count": state.get("retry_count", 0) + 1,
        }


def self_correct_node(state: SQLAgentState, db: SQLDatabase) -> dict[str, Any]:
    """
    Self-healing node: When execution encounters an error (e.g. invalid column),
    analyzes the error and schema context to produce a corrected SQL statement.
    """
    failed_sql = state.get("sql_query", "")
    error = state.get("error", "")

    # Self-healing logic: Replace non-existent column with a valid column from schema
    if "no such column: non_existent_column" in error.lower():
        corrected_sql = failed_sql.replace("non_existent_column", "total_spent")
    elif "no such column" in error.lower():
        corrected_sql = "SELECT customer_name, country, total_spent FROM customers LIMIT 3;"
    else:
        # Fallback to safe table select
        corrected_sql = "SELECT * FROM customers LIMIT 3;"

    return {
        "sql_query": corrected_sql,
        "error": None,
    }


def format_answer_node(state: SQLAgentState) -> dict[str, Any]:
    """Synthesizes the execution result or error into a human-readable AIMessage."""
    error = state.get("error")
    if error:
        content = f"Query Execution Failed: {error}"
    else:
        results = state.get("sql_result", [])
        sql = state.get("sql_query")
        retries = state.get("retry_count", 0)
        
        retry_note = f" (Recovered after {retries} retry)" if retries > 0 else ""
        content = f"SQL Executed{retry_note}:\n```sql\n{sql}\n```\n\nResults ({len(results)} rows):\n"
        for idx, row in enumerate(results, 1):
            content += f"{idx}. {row}\n"

    return {"messages": [AIMessage(content=content.strip())]}


# --- Routing Conditions ---

def route_guardrail(state: SQLAgentState) -> Literal["execute_sql", "format_answer"]:
    """If guardrail check failed, skip execution and format rejection answer."""
    if state.get("error"):
        return "format_answer"
    return "execute_sql"


def route_execution(state: SQLAgentState) -> Literal["self_correct", "format_answer"]:
    """If execution failed and retries remain, attempt self-correction."""
    if state.get("error"):
        if state.get("retry_count", 0) <= state.get("max_retries", 2):
            return "self_correct"
        return "format_answer"
    return "format_answer"


# --- Graph Builder ---

def build_sql_agent(db: SQLDatabase | None = None, checkpointer=None):
    """Assembles and compiles the self-healing SQL agent graph."""
    if db is None:
        db = create_sample_ecommerce_db()

    builder = StateGraph(SQLAgentState)

    # 1. Register nodes
    builder.add_node("fetch_schema", partial(fetch_schema_node, db=db))
    builder.add_node("generate_sql", generate_sql_node)
    builder.add_node("guardrail_check", partial(guardrail_check_node, db=db))
    builder.add_node("execute_sql", partial(execute_sql_node, db=db))
    builder.add_node("self_correct", partial(self_correct_node, db=db))
    builder.add_node("format_answer", format_answer_node)

    # 2. Add edges
    builder.add_edge(START, "fetch_schema")
    builder.add_edge("fetch_schema", "generate_sql")
    builder.add_edge("generate_sql", "guardrail_check")

    # 3. Conditional routing
    builder.add_conditional_edges(
        "guardrail_check",
        route_guardrail,
        {
            "execute_sql": "execute_sql",
            "format_answer": "format_answer",
        },
    )

    builder.add_conditional_edges(
        "execute_sql",
        route_execution,
        {
            "self_correct": "self_correct",
            "format_answer": "format_answer",
        },
    )

    # From self-correction, loop back to guardrail check
    builder.add_edge("self_correct", "guardrail_check")
    builder.add_edge("format_answer", END)

    if checkpointer is None:
        checkpointer = MemorySaver()

    return builder.compile(checkpointer=checkpointer)


if __name__ == "__main__":
    import sys

    db = create_sample_ecommerce_db()
    agent = build_sql_agent(db)

    args = sys.argv[1:]

    # Case 1: Interactive REPL CLI
    if args and args[0] in ("-i", "--interactive", "interactive"):
        print("=" * 60)
        print(" LangGraph SQL Agent - Interactive CLI")
        print(" Ask questions about customers, orders, products, or revenue.")
        print(" Type 'exit' or 'quit' to quit.")
        print("=" * 60)
        session_count = 1
        while True:
            try:
                user_q = input("\nsql-agent > ").strip()
                if not user_q:
                    continue
                if user_q.lower() in ("exit", "quit", "q"):
                    print("Exiting SQL Agent CLI. Goodbye!")
                    break
                cfg = {"configurable": {"thread_id": f"cli-session-{session_count}"}}
                res = agent.invoke(
                    {
                        "user_query": user_q,
                        "messages": [HumanMessage(content=user_q)],
                    },
                    config=cfg,
                )
                print(f"\n{res['messages'][-1].content}")
                session_count += 1
            except (KeyboardInterrupt, EOFError):
                print("\nExiting SQL Agent CLI. Goodbye!")
                break

    # Case 2: One-shot CLI query from command-line arguments
    elif args and args[0] not in ("--demo", "-d"):
        user_q = " ".join(args)
        cfg = {"configurable": {"thread_id": "cli-oneshot-1"}}
        res = agent.invoke(
            {
                "user_query": user_q,
                "messages": [HumanMessage(content=user_q)],
            },
            config=cfg,
        )
        print(res["messages"][-1].content)

    # Case 3: Default demonstration suite
    else:
        queries = [
            "Show me top customers by highest spend",
            "What is our total revenue and order count?",
            "Please trigger_error with invalid column (demonstrate self-healing)",
            "Can you DROP TABLE customers?",
        ]

        for idx, q in enumerate(queries, 1):
            print(f"\n{'=' * 60}")
            print(f"Test Query {idx}: {q}")
            print(f"{'=' * 60}")

            cfg = {"configurable": {"thread_id": f"session-{idx}"}}
            res = agent.invoke(
                {
                    "user_query": q,
                    "messages": [HumanMessage(content=q)],
                },
                config=cfg,
            )

            last_msg = res["messages"][-1]
            print(last_msg.content)
