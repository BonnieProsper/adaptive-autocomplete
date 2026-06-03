"""
aac serve: a minimal JSON API server for integrating adaptive-autocomplete
into any application. Zero dependencies beyond the standard library.

Endpoints
---------
GET  /suggest?q=<prefix>[&limit=N]       -> {"suggestions": [...]}
GET  /explain?q=<prefix>[&limit=N]       -> {"explanations": [...]}
GET  /health                             -> {"status": "ok", "preset": "..."}
POST /record?q=<prefix>&value=<word>     -> {"recorded": true}

All responses are JSON. Errors return {"error": "<message>"} with an
appropriate HTTP status code.

The server is single-threaded (BaseHTTPRequestHandler is synchronous).
For concurrent workloads, run multiple processes behind a reverse proxy,
or use the library's async API directly (engine.suggest_async()).
"""
from __future__ import annotations

import json
import socket
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import TYPE_CHECKING
from urllib.parse import parse_qs, urlparse

if TYPE_CHECKING:
    from aac.engine.engine import AutocompleteEngine


# ---------------------------------------------------------------------------
# Request handler
# ---------------------------------------------------------------------------

def _make_handler(engine: AutocompleteEngine, preset: str) -> type[BaseHTTPRequestHandler]:

    class ServeHandler(BaseHTTPRequestHandler):
        _engine = engine
        _preset = preset

        # suppress per-request logs; caller controls verbosity via --quiet
        def log_message(self, fmt: str, *args: object) -> None:
            pass

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            path = parsed.path
            qs = parse_qs(parsed.query)

            if path == "/suggest":
                self._handle_suggest(qs)
            elif path == "/explain":
                self._handle_explain(qs)
            elif path == "/health":
                self._send_json({"status": "ok", "preset": self._preset})
            else:
                self._send_error(404, f"Unknown endpoint: {path!r}. "
                                 "Available: /suggest, /explain, /health, /record")

        def do_POST(self) -> None:
            parsed = urlparse(self.path)
            path = parsed.path
            qs = parse_qs(parsed.query)

            # Accept body params too (application/x-www-form-urlencoded or query string)
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length > 0:
                body = self.rfile.read(content_length).decode("utf-8", errors="replace")
                body_qs = parse_qs(body)
                qs = {**qs, **body_qs}

            if path == "/record":
                self._handle_record(qs)
            else:
                self._send_error(405, f"POST not supported for {path!r}. "
                                 "POST is only accepted at /record.")

        def do_OPTIONS(self) -> None:
            """CORS preflight - allows browser clients to call the API directly."""
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()

        # ----------------------------------------------------------------
        # Endpoint handlers
        # ----------------------------------------------------------------

        def _handle_suggest(self, qs: dict[str, list[str]]) -> None:
            q = qs.get("q", [""])[0].strip()
            if not q:
                self._send_error(400, "Missing required parameter: q")
                return
            limit = _parse_int(qs, "limit", default=10, min_val=1, max_val=100)
            suggestions = self._engine.suggest(q, limit=limit)
            self._send_json({"suggestions": suggestions})

        def _handle_explain(self, qs: dict[str, list[str]]) -> None:
            q = qs.get("q", [""])[0].strip()
            if not q:
                self._send_error(400, "Missing required parameter: q")
                return
            limit = _parse_int(qs, "limit", default=10, min_val=1, max_val=100)
            explanations = self._engine.explain(q, limit=limit)
            self._send_json({
                "explanations": [
                    {
                        "value": e.value,
                        "base_score": round(e.base_score, 5),
                        "history_boost": round(e.history_boost, 5),
                        "final_score": round(e.final_score, 5),
                        "source": e.source,
                        "base_components": {
                            k: round(v, 5) for k, v in e.base_components.items()
                        },
                        "history_components": {
                            k: round(v, 5) for k, v in e.history_components.items()
                        },
                        "contribution_pct": {
                            k: round(v, 4) for k, v in e.contribution_pct.items()
                        },
                    }
                    for e in explanations
                ]
            })

        def _handle_record(self, qs: dict[str, list[str]]) -> None:
            q = qs.get("q", [""])[0].strip()
            value = qs.get("value", [""])[0].strip()
            if not q or not value:
                self._send_error(400, "Missing required parameters: q and value")
                return
            self._engine.record_selection(q, value)
            self._send_json({"recorded": True})

        # ----------------------------------------------------------------
        # Response helpers
        # ----------------------------------------------------------------

        def _send_json(self, data: object, status: int = 200) -> None:
            body = json.dumps(data).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)

        def _send_error(self, status: int, message: str) -> None:
            self._send_json({"error": message}, status=status)

    return ServeHandler


def _parse_int(
    qs: dict[str, list[str]],
    key: str,
    *,
    default: int,
    min_val: int,
    max_val: int,
) -> int:
    try:
        return min(max(int(qs.get(key, [str(default)])[0]), min_val), max_val)
    except (ValueError, TypeError):
        return default


def _find_free_port(preferred: int, host: str) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((host, preferred))
            return preferred
        except OSError:
            s.bind((host, 0))
            return int(s.getsockname()[1])


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run(
    *,
    engine: AutocompleteEngine,
    host: str = "127.0.0.1",
    port: int = 8420,
    preset: str = "production",
    quiet: bool = False,
) -> None:
    """
    Start the JSON API server. Blocks until interrupted (Ctrl-C).

    Parameters
    ----------
    engine:
        The AutocompleteEngine instance to serve.
    host:
        Interface to bind to. Use ``"0.0.0.0"`` inside Docker so the port
        is reachable from the host machine.
    port:
        Port to listen on. Falls back to a random free port if occupied.
    preset:
        Preset name reported in /health responses. No functional effect.
    quiet:
        Suppress startup banner.
    """
    port = _find_free_port(port, host)
    handler_class = _make_handler(engine, preset)
    server = HTTPServer((host, port), handler_class)

    if not quiet:
        print(f"aac serve  http://{host}:{port}  (preset: {preset})", file=sys.stderr)
        print("  GET  /suggest?q=prog[&limit=10]", file=sys.stderr)
        print("  GET  /explain?q=prog[&limit=10]", file=sys.stderr)
        print("  POST /record?q=prog&value=programming", file=sys.stderr)
        print("  GET  /health", file=sys.stderr)
        print("Press Ctrl-C to stop.", file=sys.stderr)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        if not quiet:
            print("\nShutting down.", file=sys.stderr)
        server.shutdown()
