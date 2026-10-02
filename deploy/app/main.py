"""HTTP wrapper around the module 04 agent.

    POST /ask   {"question": "..."}  ->  {"answer", "answer_found", "sources"}
    GET  /health

The key is read from the environment on the server. It never reaches the client.
No framework beyond the standard library, so the container stays small and there is
nothing to audit but this file.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, "/app")

from app.agent import Agent

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("agent")

MAX_BODY = 8192
agent: Agent | None = None


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._send(200, {"status": "ok", "chunks": len(agent.index) if agent else 0})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/ask":
            self._send(404, {"error": "not found"})
            return

        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0 or length > MAX_BODY:
            self._send(413, {"error": f"body must be 1 to {MAX_BODY} bytes"})
            return

        try:
            question = json.loads(self.rfile.read(length)).get("question", "").strip()
        except json.JSONDecodeError:
            self._send(400, {"error": "body must be JSON"})
            return

        if not question:
            self._send(400, {"error": "question is required"})
            return

        try:
            result = agent.ask(question)
        except Exception as exc:  # noqa: BLE001
            # Log the detail, return a generic message. Upstream errors can quote
            # request content, and this response goes to a client.
            log.exception("ask failed")
            self._send(502, {"error": "upstream inference request failed"})
            return

        self._send(200, result.model_dump())

    def log_message(self, fmt: str, *args) -> None:
        log.info("%s", fmt % args)


def main() -> None:
    global agent
    missing = [k for k in ("AKAMAI_BASE_URL", "AKAMAI_API_KEY") if not os.environ.get(k)]
    if missing:
        raise SystemExit(f"missing environment variables: {', '.join(missing)}")

    log.info("embedding the corpus")
    agent = Agent()
    log.info("index ready, %d chunks", len(agent.index))

    port = int(os.environ.get("PORT", "8000"))
    log.info("listening on 0.0.0.0:%d", port)
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
