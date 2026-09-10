"""SQL database tools and utilities for LangGraph agents."""

import re
import sqlite3
from typing import Any
from langchain_core.tools import tool, BaseTool

FORBIDDEN_SQL_KEYWORDS = [
    "DROP",
    "DELETE",
    "UPDATE",
    "INSERT",
    "ALTER",
    "TRUNCATE",
    "REPLACE",
    "EXEC",
    "GRANT",
    "REVOKE",
]


class SQLDatabase:
    """Manages SQLite database connections, schema introspection, and query execution."""

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def get_table_names(self) -> list[str]:
        """Return a list of non-internal table names in the database."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;"
        )
        return [row[0] for row in cursor.fetchall()]

    def get_table_schema(self, table_name: str) -> str:
        """Return the CREATE TABLE DDL statement for the specified table."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?;",
            (table_name,),
        )
        row = cursor.fetchone()
        if not row:
            return f"Error: Table '{table_name}' does not exist."
        return str(row[0])

    def get_all_schemas(self) -> str:
        """Return concatenated CREATE TABLE DDLs for all tables."""
        tables = self.get_table_names()
        if not tables:
            return "No tables found in database."
        return "\n\n".join(self.get_table_schema(t) for t in tables)

    def validate_query(self, query: str) -> tuple[bool, str | None]:
        """Validate query against guardrail policies (read-only SELECT, no DDL/DML)."""
        clean_query = query.strip()
        upper_query = clean_query.upper()

        # Check for forbidden keywords as standalone words
        for kw in FORBIDDEN_SQL_KEYWORDS:
            if re.search(rf"\b{kw}\b", upper_query):
                return False, f"Disallowed keyword detected: '{kw}'. Only read-only queries are permitted."

        # Ensure query starts with SELECT or WITH
        if not (upper_query.startswith("SELECT") or upper_query.startswith("WITH")):
            return False, "Query must begin with SELECT or WITH."

        return True, None

    def run_query(self, query: str, max_rows: int = 50) -> list[dict[str, Any]]:
        """
        Execute a SQL query safely and return rows as list of dicts.
        Raises sqlite3.Error on invalid syntax or execution failure.
        """
        is_valid, error = self.validate_query(query)
        if not is_valid:
            raise PermissionError(error)

        cursor = self.conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchmany(max_rows)
        return [dict(row) for row in rows]

    def close(self) -> None:
        """Close the underlying connection."""
        self.conn.close()


def create_sample_ecommerce_db() -> SQLDatabase:
    """Creates an in-memory SQLite database populated with sample eCommerce tables & data."""
    db = SQLDatabase(":memory:")
    cursor = db.conn.cursor()

    cursor.executescript("""
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            customer_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            country TEXT NOT NULL,
            total_spent REAL DEFAULT 0.0
        );

        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock_quantity INTEGER NOT NULL
        );

        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            order_date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
            FOREIGN KEY (product_id) REFERENCES products (product_id)
        );

        INSERT INTO customers (customer_id, customer_name, email, country, total_spent) VALUES
            (1, 'Alice Smith', 'alice@example.com', 'USA', 1450.50),
            (2, 'Bob Jones', 'bob@example.com', 'UK', 820.00),
            (3, 'Charlie Brown', 'charlie@example.com', 'USA', 2100.25),
            (4, 'Diana Prince', 'diana@example.com', 'Canada', 340.00),
            (5, 'Evan Wright', 'evan@example.com', 'Germany', 990.10);

        INSERT INTO products (product_id, product_name, category, price, stock_quantity) VALUES
            (1, 'Wireless Noise-Canceling Headphones', 'Electronics', 199.99, 45),
            (2, 'Ergonomic Mechanical Keyboard', 'Electronics', 129.50, 80),
            (3, 'Ultra-wide 4K Monitor', 'Electronics', 499.00, 20),
            (4, 'Adjustable Standing Desk', 'Furniture', 350.00, 15),
            (5, 'Mesh Ergonomic Office Chair', 'Furniture', 220.00, 25);

        INSERT INTO orders (order_id, customer_id, product_id, quantity, total_amount, order_date, status) VALUES
            (101, 1, 1, 2, 399.98, '2026-08-10', 'delivered'),
            (102, 1, 2, 1, 129.50, '2026-08-15', 'delivered'),
            (103, 3, 3, 2, 998.00, '2026-08-20', 'delivered'),
            (104, 3, 4, 1, 350.00, '2026-08-25', 'shipped'),
            (105, 2, 2, 2, 259.00, '2026-09-01', 'shipped'),
            (106, 4, 5, 1, 220.00, '2026-09-02', 'pending'),
            (107, 5, 1, 1, 199.99, '2026-09-03', 'delivered');
    """)
    db.conn.commit()
    return db


def create_sql_tools(db: SQLDatabase) -> list[BaseTool]:
    """Factory creating LangChain tools bound to a specific SQLDatabase instance."""

    @tool
    def list_tables() -> str:
        """List all table names available in the database."""
        tables = db.get_table_names()
        return ", ".join(tables) if tables else "No tables found."

    @tool
    def get_table_schema(table_name: str) -> str:
        """Get the CREATE TABLE schema and columns for a given table name."""
        return db.get_table_schema(table_name.strip())

    @tool
    def execute_sql(query: str) -> str:
        """Execute a read-only SQL query against the database and return results as string."""
        try:
            results = db.run_query(query)
            if not results:
                return "Query returned 0 rows."
            return str(results)
        except Exception as e:
            return f"Error executing query: {e}"

    return [list_tables, get_table_schema, execute_sql]
