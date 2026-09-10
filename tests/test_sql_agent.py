"""Unit tests for SQL database tools, guardrails, and SQL agent graph."""

import unittest
from langchain_core.messages import HumanMessage

from tools.sql import (
    SQLDatabase,
    create_sample_ecommerce_db,
    create_sql_tools,
    FORBIDDEN_SQL_KEYWORDS,
)
from examples.ex04_sql_agent.main import build_sql_agent, guardrail_check_node


class TestSQLAgent(unittest.TestCase):
    def setUp(self):
        self.db = create_sample_ecommerce_db()
        self.agent = build_sql_agent(self.db)

    def tearDown(self):
        self.db.close()

    def test_database_introspection(self):
        tables = self.db.get_table_names()
        self.assertIn("customers", tables)
        self.assertIn("products", tables)
        self.assertIn("orders", tables)

        customer_schema = self.db.get_table_schema("customers")
        self.assertIn("CREATE TABLE customers", customer_schema)
        self.assertIn("total_spent", customer_schema)

    def test_run_valid_query(self):
        rows = self.db.run_query("SELECT customer_name FROM customers WHERE country = 'USA';")
        names = [r["customer_name"] for r in rows]
        self.assertIn("Alice Smith", names)
        self.assertIn("Charlie Brown", names)

    def test_guardrails_prevent_destructive_commands(self):
        for kw in FORBIDDEN_SQL_KEYWORDS:
            query = f"{kw} TABLE test;"
            is_valid, err = self.db.validate_query(query)
            self.assertFalse(is_valid, f"Keyword {kw} should have been blocked")
            self.assertIn("Disallowed keyword", err)

        # Test guardrail node directly
        state = {"sql_query": "DROP TABLE customers;"}
        node_result = guardrail_check_node(state, self.db)
        self.assertIn("Guardrail Violation", node_result["error"])

    def test_sql_tools_factory(self):
        tools = create_sql_tools(self.db)
        tool_map = {t.name: t for t in tools}
        self.assertIn("list_tables", tool_map)
        self.assertIn("get_table_schema", tool_map)
        self.assertIn("execute_sql", tool_map)

        tables_out = tool_map["list_tables"].invoke({})
        self.assertIn("customers", tables_out)

        schema_out = tool_map["get_table_schema"].invoke({"table_name": "products"})
        self.assertIn("stock_quantity", schema_out)

        query_out = tool_map["execute_sql"].invoke({"query": "SELECT COUNT(*) as cnt FROM customers;"})
        self.assertIn("cnt", query_out)

    def test_sql_agent_graph_execution(self):
        config = {"configurable": {"thread_id": "test-sql-agent-1"}}
        res = self.agent.invoke(
            {
                "user_query": "Show me top customer by highest spend",
                "messages": [HumanMessage(content="Show me top customer by highest spend")],
            },
            config=config,
        )

        self.assertIsNone(res.get("error"))
        self.assertIsNotNone(res.get("sql_result"))
        self.assertGreater(len(res["sql_result"]), 0)
        # Charlie Brown has total_spent 2100.25
        self.assertEqual(res["sql_result"][0]["customer_name"], "Charlie Brown")

    def test_sql_agent_self_healing_loop(self):
        config = {"configurable": {"thread_id": "test-sql-agent-2"}}
        res = self.agent.invoke(
            {
                "user_query": "Please trigger_error with invalid column to test self healing",
                "messages": [HumanMessage(content="Trigger error")],
            },
            config=config,
        )

        self.assertIsNone(res.get("error"))
        self.assertGreaterEqual(res.get("retry_count", 0), 1)
        self.assertIsNotNone(res.get("sql_result"))
        self.assertIn("Recovered after", res["messages"][-1].content)

    def test_sql_agent_blocks_malicious_input(self):
        config = {"configurable": {"thread_id": "test-sql-agent-3"}}
        res = self.agent.invoke(
            {
                "user_query": "Please drop table customers",
                "messages": [HumanMessage(content="drop table customers")],
            },
            config=config,
        )

        self.assertIsNotNone(res.get("error"))
        self.assertIn("Guardrail Violation", res["error"])
        # Ensure customers table is intact
        tables = self.db.get_table_names()
        self.assertIn("customers", tables)


if __name__ == "__main__":
    unittest.main()
