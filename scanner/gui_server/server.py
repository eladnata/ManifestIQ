from __future__ import annotations

import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from scanner.gui_server.api import ApiRouter
from scanner.gui_server.runs import RunManager


def _make_handler(router: ApiRouter, static_root: Path) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        server_version = "ManifestIQLocalGUI/1.0"

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A002 - stdlib signature
            # Quiet by default; this is a local instrument, not a diagnostic console.
            pass

        def _send_json(self, status: int, payload: dict[str, Any]) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _serve_static(self) -> None:
            rel = self.path.split("?", 1)[0].lstrip("/")
            if rel == "":
                rel = "index.html"
            candidate = (static_root / rel).resolve()
            # Directory traversal guard: never serve outside the built static root.
            if not str(candidate).startswith(str(static_root)) or not candidate.is_file():
                candidate = static_root / "index.html"
                if not candidate.is_file():
                    self.send_response(404)
                    self.end_headers()
                    return
            content_type, _ = mimetypes.guess_type(str(candidate))
            data = candidate.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type or "application/octet-stream")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self) -> None:  # noqa: N802 - stdlib method name
            if self.path.split("?", 1)[0].startswith("/api/"):
                status, payload = router.handle("GET", self.path, None)
                self._send_json(status, payload)
                return
            self._serve_static()

        def do_POST(self) -> None:  # noqa: N802 - stdlib method name
            length = int(self.headers.get("Content-Length", 0) or 0)
            body = self.rfile.read(length) if length else b""
            if self.path.split("?", 1)[0].startswith("/api/"):
                status, payload = router.handle("POST", self.path, body)
                self._send_json(status, payload)
                return
            self.send_response(404)
            self.end_headers()

    return Handler


def create_httpd(host: str, port: int, runs_dir: Path, static_dir: Path) -> ThreadingHTTPServer:
    """
    Build (but do not start) the local GUI workbench HTTP server. Binds only
    to the given host/port (default 127.0.0.1) and serves exactly two things:
    the built static frontend, and the same-origin local-only JSON API.
    """
    run_manager = RunManager(runs_dir)
    router = ApiRouter(run_manager)
    handler_cls = _make_handler(router, Path(static_dir).resolve())
    return ThreadingHTTPServer((host, port), handler_cls)


def run_server(host: str, port: int, runs_dir: Path, static_dir: Path) -> None:
    if not Path(static_dir).is_dir():
        raise SystemExit(
            f"GUI static assets not found at {static_dir}. Build the frontend first:\n"
            f"  cd apps/gui && npm install && npm run build"
        )
    httpd = create_httpd(host, port, Path(runs_dir), Path(static_dir))
    bound_port = httpd.server_address[1]
    print(f"ManifestIQ local GUI workbench: http://{host}:{bound_port}  (local-only — no network egress, no telemetry)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
