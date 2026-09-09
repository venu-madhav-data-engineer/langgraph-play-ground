import unittest
from core.state import BaseAgentState, KeyValueState
from tools.calculator import calculator
from langchain_core.messages import HumanMessage
from examples.ex01_basic_graph.main import build_graph as build_ex01_graph
from examples.ex02_tool_calling_agent.main import build_graph as build_ex02_graph
from examples.ex03_memory_and_checkpoints.main import build_chat_graph as build_ex03_graph

class TestMonorepo(unittest.TestCase):
    def test_core_schemas(self):
        state: KeyValueState = {"input": "test", "step_count": 1}
        self.assertEqual(state["input"], "test")
        self.assertEqual(state["step_count"], 1)

    def test_tools_calculator(self):
        res = calculator.invoke({"expression": "10 * 5 + 2"})
        self.assertEqual(res, "52")

    def test_calculator_disallowed(self):
        with self.assertRaises(Exception):
            calculator.invoke({"expression": "__import__('os').system('ls')"})

    def test_example_01_graph(self):
        graph = build_ex01_graph()
        res = graph.invoke({"name": "Tester", "greeting": ""})
        self.assertIn("Hello, Tester!", res["greeting"])
        self.assertIn("Ready to build stateful AI workflows!", res["greeting"])

    def test_example_02_tool_agent(self):
        graph = build_ex02_graph()
        res = graph.invoke({
            "input": "calculate 20 + 30",
            "tool_name": None,
            "tool_input": None,
            "tool_output": None,
            "final_response": ""
        })
        self.assertIn("50", res["final_response"])

    def test_example_03_memory(self):
        graph = build_ex03_graph()
        cfg = {"configurable": {"thread_id": "test-session"}}

        out1 = graph.invoke({"messages": [HumanMessage(content="First message")]}, config=cfg)
        self.assertEqual(len(out1["messages"]), 2)

        out2 = graph.invoke({"messages": [HumanMessage(content="Second message")]}, config=cfg)
        self.assertEqual(len(out2["messages"]), 4)

if __name__ == "__main__":
    unittest.main()
