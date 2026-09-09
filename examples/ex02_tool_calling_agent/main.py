"""02. Tool Calling Agent Example.

Demonstrates conditional routing with tools in LangGraph.
"""
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict):
    input: str
    tool_name: str | None
    tool_input: str | None
    tool_output: str | None
    final_response: str

def planner_node(state: AgentState) -> dict:
    """Mock planner that decides whether a tool is required."""
    user_input = state["input"]
    if "calculate" in user_input.lower() or any(char in user_input for char in "+-*/"):
        # Simple extraction for demo purposes
        expr = "".join(c for c in user_input if c in "0123456789+-*/. ")
        return {
            "tool_name": "calculator",
            "tool_input": expr.strip(),
            "final_response": "",
        }
    return {
        "tool_name": None,
        "tool_input": None,
        "final_response": f"I can answer directly: {user_input}",
    }

def tool_node(state: AgentState) -> dict:
    """Executes the tool requested by the planner."""
    tool_name = state["tool_name"]
    tool_input = state["tool_input"] or ""

    if tool_name == "calculator":
        try:
            # Safe evaluation
            result = str(eval(tool_input, {"__builtins__": {}}, {}))
        except Exception as e:
            result = f"Calculation error: {e}"
        return {
            "tool_output": result,
            "final_response": f"The answer to '{tool_input}' is {result}.",
        }

    return {"tool_output": "Unknown tool", "final_response": "Could not execute tool."}

def route_decision(state: AgentState) -> Literal["call_tool", "end"]:
    """Conditional edge router."""
    if state.get("tool_name"):
        return "call_tool"
    return "end"

def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("planner", planner_node)
    builder.add_node("tool_node", tool_node)

    builder.add_edge(START, "planner")
    builder.add_conditional_edges(
        "planner",
        route_decision,
        {
            "call_tool": "tool_node",
            "end": END,
        }
    )
    builder.add_edge("tool_node", END)

    return builder.compile()

if __name__ == "__main__":
    graph = build_graph()
    queries = [
        "What is 45 * 12 + 10?",
        "Tell me what LangGraph is useful for.",
    ]

    for q in queries:
        print(f"\n--- Query: {q} ---")
        res = graph.invoke({"input": q, "tool_name": None, "tool_input": None, "tool_output": None, "final_response": ""})
        print(f"Result: {res['final_response']}")
