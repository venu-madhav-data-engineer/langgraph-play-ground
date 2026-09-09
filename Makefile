.PHONY: help install install-editable test lint run-basic run-tools run-memory run-cli run-api

PYTHON ?= ./myenv/bin/python
PIP ?= PIP_PREFIX="" ./myenv/bin/pip

help:
	@echo "Available commands:"
	@echo "  make install          Install local packages (packages/core, packages/tools) in editable mode"
	@echo "  make test             Run test suite"
	@echo "  make run-basic        Run the basic graph example"
	@echo "  make run-tools        Run the tool calling agent example"
	@echo "  make run-memory       Run the memory checkpointer example"
	@echo "  make run-cli          Launch interactive CLI runner"
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

run-cli:
	$(PYTHON) apps/cli/src/cli/main.py

run-api:
	$(PYTHON) apps/api/src/api/main.py
