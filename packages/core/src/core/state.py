from typing import Annotated, Sequence, TypedDict, Any
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class BaseAgentState(TypedDict):
    """
    Standard agent state with message history.
    Uses the add_messages reducer so new messages append automatically.
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]

class KeyValueState(TypedDict, total=False):
    """
    Flexible dictionary-based state for arbitrary key-value workflows.
    """
    input: str
    output: str
    context: dict[str, Any]
    step_count: int

class SQLAgentState(TypedDict, total=False):
    """
    State schema for SQL Agent workflows with error recovery and guardrails.
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_query: str
    schema_context: str
    sql_query: str | None
    sql_result: list[dict[str, Any]] | None
    error: str | None
    retry_count: int
    max_retries: int
