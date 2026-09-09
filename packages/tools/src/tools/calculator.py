import math
from langchain_core.tools import tool

@tool
def calculator(expression: str) -> str:
    """Evaluates a basic math expression safely. Supports standard arithmetic and math module functions."""
    allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
    allowed_names.update({"abs": abs, "round": round, "min": min, "max": max})

    # Basic input sanitation
    code = compile(expression, "<string>", "eval")
    for name in code.co_names:
        if name not in allowed_names:
            raise ValueError(f"Use of '{name}' is not allowed in calculator")

    result = eval(code, {"__builtins__": {}}, allowed_names)
    return str(result)
