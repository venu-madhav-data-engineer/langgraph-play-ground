"""03. Memory and Checkpoints Example.

Demonstrates conversational state persistence across turns using MemorySaver.
"""
from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def bot_node(state: ChatState) -> dict:
    """Echo/respond node that remembers earlier conversation."""
    last_msg = state["messages"][-1]
    history_count = len(state["messages"])
    reply = f"Echoing back: '{last_msg.content}'. (Total turns remembered: {history_count})"
    return {"messages": [AIMessage(content=reply)]}

def build_chat_graph():
    builder = StateGraph(ChatState)
    builder.add_node("bot", bot_node)
    builder.add_edge(START, "bot")
    builder.add_edge("bot", END)

    # In-memory checkpointer to persist state across thread_id
    memory = MemorySaver()
    return builder.compile(checkpointer=memory)

if __name__ == "__main__":
    graph = build_chat_graph()
    config = {"configurable": {"thread_id": "session-42"}}

    print("--- Turn 1 ---")
    out1 = graph.invoke({"messages": [HumanMessage(content="Hello, my name is Alice.")]}, config=config)
    print(out1["messages"][-1].content)

    print("\n--- Turn 2 ---")
    out2 = graph.invoke({"messages": [HumanMessage(content="What did I just tell you?")]}, config=config)
    print(out2["messages"][-1].content)
    print(f"\nTotal messages stored in thread session-42: {len(out2['messages'])}")
