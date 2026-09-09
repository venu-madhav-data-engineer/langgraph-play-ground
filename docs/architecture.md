# Monorepo Architecture & Guidelines

## Overview

The `langgraph-play-ground` monorepo organizes applications, shared libraries, and experiments for developing LangGraph-based AI agents.

```
langgraph-play-ground/
├── apps/                         # Deployable services and applications
│   ├── api/                      # LangGraph HTTP API service
│   └── cli/                      # Interactive terminal agent runner
├── packages/                     # Reusable shared packages
│   ├── core/                     # Shared state schemas, graph base logic, utilities
│   └── tools/                    # Shared agent tools (calculator, custom tools)
├── examples/                     # Standalone runnable workflow examples
│   ├── 01_basic_graph/           # Linear stateful graph
│   ├── 02_tool_calling_agent/    # Conditional branching & tools
│   └── 03_memory_and_checkpoints/# Multi-turn conversational persistence
├── notebooks/                    # Jupyter notebooks for exploratory research
├── docs/                         # Architecture documentation and guides
└── tests/                        # Test suites across monorepo packages
```

## Adding a New Package

1. Create a directory inside `packages/<new_package>/`
2. Add a `pyproject.toml` declaring dependencies and setuptools package discovery:
   ```toml
   [build-system]
   requires = ["setuptools>=61.0"]
   build-backend = "setuptools.build_meta"

   [project]
   name = "langgraph-<new_package>"
   version = "0.1.0"
   dependencies = [...]

   [tool.setuptools.packages.find]
   where = ["src"]
   ```
3. Implement code in `packages/<new_package>/src/<new_package>/`
4. Install in editable mode:
   ```bash
   pip install -e packages/<new_package>
   ```

## Adding a New Application

1. Create a folder inside `apps/<app_name>/`
2. Import from `core` and `tools` packages
3. Provide entrypoints in `apps/<app_name>/src/<app_name>/main.py`
