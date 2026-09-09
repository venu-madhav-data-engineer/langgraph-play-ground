"""LangGraph API Server Scaffold.

Provides HTTP interface for invoking LangGraph workflows.
"""
from typing import Any
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
from langgraph.graph import StateGraph, START, END
from core.state import KeyValueState

def process_request(state: KeyValueState) -> dict:
    inp = state.get("input", "")
    return {
        "output": f"Processed: {inp}",
        "step_count": state.get("step_count", 0) + 1,
    }

builder = StateGraph(KeyValueState)
builder.add_node("process", process_request)
builder.add_edge(START, "process")
builder.add_edge("process", END)
graph = builder.compile()

class SimpleAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "service": "langgraph-api"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/invoke":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode()) if body else {}

            input_text = data.get("input", "")
            result = graph.invoke({"input": input_text, "step_count": 0})

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        else:
            self.send_response(404)
            self.end_headers()

def run_server(host: str = "0.0.0.0", port: int = 8000):
    server_address = (host, port)
    httpd = HTTPServer(server_address, SimpleAPIHandler)
    print(f"LangGraph API Server running on http://{host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()

if __name__ == "__main__":
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")
    run_server(host=host, port=port)
