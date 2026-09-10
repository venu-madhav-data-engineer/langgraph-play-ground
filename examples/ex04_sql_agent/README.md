# 04 - Self-Healing SQL Agent

Demonstrates a stateful, guardrail-protected SQL agent in LangGraph:
- Dynamic schema introspection against SQLite.
- SQL query formulation with guardrails (blocking `DROP`, `DELETE`, `UPDATE`).
- Automated error recovery and self-healing loop (re-prompting/rewriting queries on SQL syntax or schema errors).
- Clean result synthesis into natural language `AIMessage`.

## Architecture

```mermaid
flowchart TD
    START([START]) --> fetch_schema["fetch_schema"]
    fetch_schema --> generate_sql["generate_sql"]
    generate_sql --> guardrail_check{"guardrail_check"}
    guardrail_check -- "Safe" --> execute_sql["execute_sql"]
    guardrail_check -- "Disallowed Keyword" --> format_answer["format_answer"]
    execute_sql --> eval{"eval_execution"}
    eval -- "Success" --> format_answer
    eval -- "Error & Retries < Max" --> self_correct["self_correct"]
    eval -- "Retries Exceeded" --> format_answer
    self_correct --> guardrail_check
    format_answer --> END([END])
```

## Run

```bash
python -m examples.ex04_sql_agent.main
```
or
```bash
make run-sql
```
