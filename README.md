# LangGraph Playground Monorepo

A modular monorepo environment for experimenting, building, and deploying stateful, multi-actor AI agents and workflows using **LangGraph**.

---

## Repository Structure

```
langgraph-play-ground/
├── .env.example              # Environment variables template (API keys, tracing, etc.)
├── .gitignore                # Comprehensive gitignore for Python, AI/LangGraph, and IDEs
├── Makefile                  # Developer workflow shortcuts
├── pyproject.toml            # Root workspace configuration & dependency definitions
├── README.md                 # Project documentation
│
├── apps/                     # Deployable applications & services
│   ├── api/                  # HTTP API server scaffold for invoking graphs
│   └── cli/                  # Interactive terminal REPL agent runner
│
├── packages/                 # Shared libraries & modules (editable packages)
│   ├── core/                 # Shared state schemas, graph base logic, utilities
│   └── tools/                # Shared agent tools (calculator, custom tools)
│
├── examples/                 # Ready-to-run pattern examples
│   ├── ex01_basic_graph/     # Linear stateful graph demonstration
│   ├── ex02_tool_calling_agent/ # Conditional branching & tool invocation
│   ├── ex03_memory_and_checkpoints/ # Conversational persistence with MemorySaver
│   └── ex04_sql_agent/       # Self-healing SQL agent with guardrails
│
├── notebooks/                # Jupyter notebooks for interactive experimentation
├── docs/                     # Architecture guides & documentation
└── tests/                    # Integration & unit test suite (13 passing tests)
```

---

## Quickstart

### 1. Environment Setup

If not already created, set up the virtual environment:

```bash
python3 -m venv myenv
source myenv/bin/activate
pip install -U langgraph
```

Copy the example environment configuration:
```bash
cp .env.example .env
```

### 2. Install Monorepo Packages (Editable Mode)

Install the shared packages (`core` and `tools`) in editable mode so changes immediately reflect across all apps and examples:

```bash
make install
```
*(or manually: `pip install -e packages/core -e packages/tools`)*

---

## Running Examples & Applications

| Command | Description |
| :--- | :--- |
| `make test` | Run the complete monorepo test suite |
| `make run-basic` | Run the linear stateful graph example (`ex01_basic_graph`) |
| `make run-tools` | Run the tool-calling conditional agent (`ex02_tool_calling_agent`) |
| `make run-memory` | Run the conversational memory persistence example (`ex03_memory_and_checkpoints`) |
| `make run-sql` | Run the self-healing SQL agent example (`ex04_sql_agent`) |
| `make run-cli` | Launch the interactive agent CLI runner |
| `make run-api` | Start the local HTTP API service on `http://0.0.0.0:8000` |

---

## Shared Packages

### `packages/core`
- **State Schemas**: `BaseAgentState` (with `add_messages` reducer), `KeyValueState`, `SQLAgentState`.
- **Utilities**: `print_ascii_graph`, `format_messages`.

### `packages/tools`
- **Calculator**: Safe mathematical expression evaluation tool (`calculator.invoke(...)`).
- **SQL Tools**: `SQLDatabase`, `create_sql_tools`, `create_sample_ecommerce_db`, guardrail query validation (`FORBIDDEN_SQL_KEYWORDS`).
- **Tool Helpers**: Extraction and schema utilities (`get_tool_names`).

---

## Running Tests

Run the test suite via the Makefile or directly:

```bash
make test
```
or
```bash
./myenv/bin/python -m unittest discover tests
```

---

## Architecture & Development Guide

For details on how to add new packages, applications, or graph workflows, refer to [docs/architecture.md](docs/architecture.md).
