from __future__ import annotations

import json
from typing import Any
from urllib.parse import urlparse

from scanner import __version__
from scanner.core.capabilities import STRICT_PROFILES
from scanner.gui_server.runs import SOURCE_TYPES, RunManager, validate_preflight


def health_payload() -> dict[str, Any]:
    """
    Local-only health/capability metadata. No network egress, no telemetry,
    no cloud, no AI — this endpoint only reflects the running local process.
    """
    return {
        "schema": "manifestiq-health",
        "schema_version": "0.1",
        "status": "ok",
        "mode": "local-only",
        "network": "none",
        "telemetry": "none",
        "cloud": "none",
        "ai": "none",
        "version": __version__,
        "profiles": list(STRICT_PROFILES),
        "source_types": list(SOURCE_TYPES),
    }


def _parse_json_body(body: bytes | None) -> dict[str, Any]:
    if not body:
        return {}
    try:
        parsed = json.loads(body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


class ApiRouter:
    """
    Pure request dispatcher for the local GUI workbench API. Testable
    directly (no socket required); the HTTP server module wraps this in a
    BaseHTTPRequestHandler. Every route is same-origin, local-only, and
    read/derive-only over scanner functions that already exist — no scanner
    logic is duplicated or altered here.
    """

    def __init__(self, run_manager: RunManager):
        self.run_manager = run_manager

    def handle(self, method: str, path: str, body: bytes | None) -> tuple[int, dict[str, Any]]:
        parsed = urlparse(path)
        segments = [s for s in parsed.path.split("/") if s]

        if method == "GET" and segments == ["api", "health"]:
            return 200, health_payload()

        if method == "POST" and segments == ["api", "preflight"]:
            payload = _parse_json_body(body)
            result = validate_preflight(
                payload.get("source_type", ""),
                payload.get("source_value", ""),
                payload.get("profile", ""),
            )
            return 200, result

        if method == "POST" and segments == ["api", "runs"]:
            payload = _parse_json_body(body)
            result = self.run_manager.start_run(
                payload.get("source_type", ""),
                payload.get("source_value", ""),
                payload.get("profile", ""),
            )
            if "error" in result:
                return 400, result
            return 200, result["run"]

        if method == "GET" and len(segments) == 3 and segments[0] == "api" and segments[1] == "runs":
            run_id = segments[2]
            run = self.run_manager.get_run(run_id)
            if run is None:
                return 404, {"error": "run_not_found", "run_id": run_id}
            return 200, run

        if (
            method == "GET"
            and len(segments) == 4
            and segments[0] == "api"
            and segments[1] == "runs"
            and segments[3] == "board-verdict-data"
        ):
            run_id = segments[2]
            data = self.run_manager.get_board_verdict_data(run_id)
            if data is not None:
                return 200, data
            run = self.run_manager.get_run(run_id)
            if run is None:
                return 404, {"error": "run_not_found", "run_id": run_id}
            return 409, {"error": "not_sealed", "run_id": run_id, "status": run["status"]}

        return 404, {"error": "not_found", "path": parsed.path}
