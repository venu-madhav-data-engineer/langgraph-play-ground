# API Service (`apps/api`)

HTTP API service exposing endpoints to invoke LangGraph graphs.

## Endpoints

- `GET /health` - Healthcheck endpoint.
- `POST /invoke` - Run graph with JSON body `{"input": "..."}`.

## Run

```bash
python apps/api/src/api/main.py
```
