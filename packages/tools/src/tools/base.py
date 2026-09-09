"""Base tool utilities and helpers."""
from typing import Callable, Any
from langchain_core.tools import BaseTool

def get_tool_names(tools: list[BaseTool | Callable[..., Any]]) -> list[str]:
    """Extract names from tools."""
    names = []
    for t in tools:
        if hasattr(t, "name"):
            names.append(t.name)
        elif hasattr(t, "__name__"):
            names.append(t.__name__)
    return names
