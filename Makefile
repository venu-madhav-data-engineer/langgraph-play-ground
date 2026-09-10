.PHONY: help install install-editable test lint run-basic run-tools run-memory run-sql run-sql-interactive run-cli run-api

PYTHON ?= ./myenv/bin/python
PIP ?= PIP_PREFIX="" ./myenv/bin/pip

help:
	@echo "Available commands:"
	@echo "  make install          Install local packages (packages/core, packages/tools) in editable mode"
	@echo "  make test             Run test suite"
	@echo "  make run-basic        Run the basic graph example"
	@echo "  make run-tools        Run the tool calling agent example"
	@echo "  make run-memory       Run the memory checkpointer example"
	@echo "  make run-sql          Run the self-healing SQL agent example (demo suite)"
	@echo "  make run-sql-interactive Run the interactive SQL agent CLI"
	@echo "  make run-cli          Launch interactive playground CLI (math + SQL)"
	@echo "  make run-api          Start API server"

install:
	$(PIP) install -e packages/core
	$(PIP) install -e packages/tools

install-editable: install

test:
	$(PYTHON) -m unittest discover tests

run-basic:
	$(PYTHON) examples/ex01_basic_graph/main.py

run-tools:
	$(PYTHON) examples/ex02_tool_calling_agent/main.py

run-memory:
	$(PYTHON) examples/ex03_memory_and_checkpoints/main.py

run-sql:
	$(PYTHON) examples/ex04_sql_agent/main.py

run-sql-interactive:
	$(PYTHON) examples/ex04_sql_agent/main.py -i

run-cli:
	$(PYTHON) apps/cli/src/cli/main.py

run-api:
	$(PYTHON) apps/api/src/api/main.py
