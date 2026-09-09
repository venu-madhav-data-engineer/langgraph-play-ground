from typing import Any
from langgraph.graph.state import CompiledStateGraph

def print_ascii_graph(graph: CompiledStateGraph) -> None:
    """Prints an ASCII diagram of the compiled graph if supported."""
    try:
        print(graph.get_graph().draw_ascii())
    except Exception as e:
        print(f"Could not render ASCII graph: {e}")

def format_messages(messages: list[Any]) -> str:
    """Format message list for readable CLI / terminal output."""
    output = []
    for msg in messages:
        sender = getattr(msg, "type", "unknown")
        content = getattr(msg, "content", str(msg))
        output.append(f"[{sender.upper()}]: {content}")
    return "\n".join(output)
