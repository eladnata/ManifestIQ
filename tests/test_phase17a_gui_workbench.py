import json
import re
import threading
import time
import urllib.request
from pathlib import Path

import pytest

from scanner import __version__
from scanner.app.cli import app
from scanner.core.orchestrator import run_scan
from scanner.core.workspace import prepare_folder_workspace
from scanner.gui_server.api import health_payload
from scanner.gui_server.runs import RunManager, validate_preflight

SAMPLE_PROJECT = Path("tests/sample_projects/insecure-python")

FORBIDDEN_CLAIM_TERMS = [
    "Approved",
    "Certified",
    "Compliant",
    "Safe",
    "Production Ready",
    "SOX Approved",
    "Privacy Approved",
    "Legally Approved",
    "Fully Secure",
]


def _assert_no_bare_positive_claim(payload_str: str, *, context: str) -> None:
    for term in FORBIDDEN_CLAIM_TERMS:
        # Word-boundary match only: "Safe" must not match inside "trust-safety-review.json".
        pattern = r"\b" + re.escape(term) + r"\b"
        for match in re.finditer(pattern, payload_str, re.IGNORECASE):
            start = max(0, match.start() - 12)
            preceding = payload_str[start : match.start()].lower()
            assert "not " in preceding or "no " in preceding, (
                f"[{context}] forbidden term '{term}' appears without a preceding negation: "
                f"...{payload_str[start:match.end() + 12]}..."
            )


def _wait_for_completion(manager: RunManager, run_id: str, timeout: float = 60.0) -> dict:
    deadline = time.time() + timeout
    run = None
    while time.time() < deadline:
        run = manager.get_run(run_id)
        if run["status"] in ("sealed", "failed"):
            return run
        time.sleep(0.1)
    raise AssertionError(f"Run {run_id} did not complete within {timeout}s: {run}")


# ---------------------------------------------------------------------------
# 1. `python -m scanner gui` command exists.
# ---------------------------------------------------------------------------


def test_gui_cli_command_registered():
    from typer.main import get_command

    click_command = get_command(app)
    assert "gui" in click_command.commands


# ---------------------------------------------------------------------------
# 2. API health endpoint returns local-only metadata.
# ---------------------------------------------------------------------------


def test_api_health_endpoint_local_only_metadata_via_live_server(tmp_path):
    from scanner.gui_server.server import create_httpd

    static_dir = tmp_path / "static"
    static_dir.mkdir()
    (static_dir / "index.html").write_text("<html></html>", encoding="utf-8")

    httpd = create_httpd("127.0.0.1", 0, tmp_path / "gui-runs", static_dir)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health", timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        assert data["status"] == "ok"
        assert data["mode"] == "local-only"
        assert data["network"] == "none"
        assert data["telemetry"] == "none"
        assert data["cloud"] == "none"
        assert data["ai"] == "none"
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_health_payload_function_directly():
    data = health_payload()
    assert data["schema"] == "manifestiq-health"
    assert data["mode"] == "local-only"


# ---------------------------------------------------------------------------
# 3. Preflight fails closed on missing source.
# ---------------------------------------------------------------------------


def test_preflight_fails_closed_on_missing_folder():
    result = validate_preflight("folder", "does/not/exist/anywhere", "enterprise")
    assert result["state"] == "cannot_run"
    assert any("not found" in b.lower() for b in result["blockers"])


def test_preflight_fails_closed_on_empty_source_value():
    result = validate_preflight("folder", "", "enterprise")
    assert result["state"] == "cannot_run"
    assert result["blockers"]


def test_preflight_fails_closed_on_unknown_profile():
    result = validate_preflight("folder", str(SAMPLE_PROJECT), "not-a-real-profile")
    assert result["state"] == "cannot_run"
    assert any("profile" in b.lower() for b in result["blockers"])


# ---------------------------------------------------------------------------
# 4. Preflight succeeds for the sample project folder.
# ---------------------------------------------------------------------------


def test_preflight_succeeds_for_sample_project():
    result = validate_preflight("folder", str(SAMPLE_PROJECT), "finance-sox")
    assert result["state"] == "ready"
    assert result["blockers"] == []


def test_preflight_git_source_flags_outbound_fetch_but_does_not_block():
    result = validate_preflight("git", "https://example.invalid/repo.git", "enterprise")
    assert result["state"] == "needs_attention"
    assert result["blockers"] == []
    ids = [c["id"] for c in result["checks"]]
    assert "git_outbound_fetch" in ids


# ---------------------------------------------------------------------------
# 5 & 6 & 7. Run can start, writes an evidence package, produces
# board-verdict-data.json.
# ---------------------------------------------------------------------------


def test_run_starts_completes_writes_evidence_and_board_verdict_data(tmp_path):
    manager = RunManager(tmp_path / "gui-runs")
    result = manager.start_run("folder", str(SAMPLE_PROJECT), "finance-sox")
    assert "run" in result
    run_id = result["run"]["run_id"]

    run = _wait_for_completion(manager, run_id)
    assert run["status"] == "sealed", run.get("error")

    evidence_dir = Path(run["evidence_dir"])
    assert (evidence_dir / "manifest.json").is_file()
    assert (evidence_dir / "sha256.txt").is_file()
    assert (evidence_dir / "decision-packet.json").is_file()
    assert (evidence_dir / "findings.json").is_file()

    run_dir = Path(run["run_dir"])
    assert (run_dir / "board-verdict-data.json").is_file()
    assert (run_dir / "preflight.json").is_file()
    assert (run_dir / "source-metadata.json").is_file()

    for stage in run["stages"]:
        assert stage["state"] == "complete", stage

    assert run["integrity"]["state"] == "Verified"
    assert run["manifest_hash"]


# ---------------------------------------------------------------------------
# 8. Board Verdict uses real run data after scan (not stale sample data).
# ---------------------------------------------------------------------------


def test_board_verdict_data_reflects_the_real_run_not_stale_sample(tmp_path):
    manager = RunManager(tmp_path / "gui-runs")
    result = manager.start_run("folder", str(SAMPLE_PROJECT), "finance-sox")
    run_id = result["run"]["run_id"]
    run = _wait_for_completion(manager, run_id)
    assert run["status"] == "sealed"

    data = manager.get_board_verdict_data(run_id)
    assert data is not None
    assert data["schema"] == "manifestiq-board-verdict-data"
    # The contract must point at THIS run's own evidence directory.
    assert run_id in data["evidence_package"] or str(Path(run["evidence_dir"])) == data["evidence_package"]
    assert data["manifest_hash"] == run["manifest_hash"]


def test_board_verdict_data_unavailable_before_sealed(tmp_path):
    manager = RunManager(tmp_path / "gui-runs")
    result = manager.start_run("folder", str(SAMPLE_PROJECT), "finance-sox")
    run_id = result["run"]["run_id"]
    # Immediately after starting, the run is very unlikely to be sealed yet;
    # regardless of timing, get_board_verdict_data must never fabricate data
    # for a run that has not sealed.
    data = manager.get_board_verdict_data(run_id)
    if data is None:
        assert True
    else:
        # If the background thread finished exceptionally fast, it must be sealed.
        run = manager.get_run(run_id)
        assert run["status"] == "sealed"
    _wait_for_completion(manager, run_id)


def test_run_not_found_returns_none(tmp_path):
    manager = RunManager(tmp_path / "gui-runs")
    assert manager.get_run("run_does_not_exist") is None
    assert manager.get_board_verdict_data("run_does_not_exist") is None


# ---------------------------------------------------------------------------
# 9. API never returns approval-bearing claims.
# ---------------------------------------------------------------------------


def test_api_payloads_never_contain_bare_positive_approval_claims(tmp_path):
    _assert_no_bare_positive_claim(json.dumps(health_payload()), context="health")

    preflight_ready = validate_preflight("folder", str(SAMPLE_PROJECT), "finance-sox")
    _assert_no_bare_positive_claim(json.dumps(preflight_ready), context="preflight-ready")

    preflight_blocked = validate_preflight("folder", "does/not/exist", "enterprise")
    _assert_no_bare_positive_claim(json.dumps(preflight_blocked), context="preflight-blocked")

    manager = RunManager(tmp_path / "gui-runs")
    result = manager.start_run("folder", str(SAMPLE_PROJECT), "finance-sox")
    run_id = result["run"]["run_id"]
    run = _wait_for_completion(manager, run_id)
    _assert_no_bare_positive_claim(json.dumps(run), context="run-status")

    data = manager.get_board_verdict_data(run_id)
    _assert_no_bare_positive_claim(json.dumps(data), context="board-verdict-data")


def test_api_router_dispatch_never_leaks_approval_claim(tmp_path):
    from scanner.gui_server.api import ApiRouter

    manager = RunManager(tmp_path / "gui-runs")
    router = ApiRouter(manager)

    status, payload = router.handle("GET", "/api/health", None)
    assert status == 200
    _assert_no_bare_positive_claim(json.dumps(payload), context="router-health")

    body = json.dumps({"source_type": "folder", "source_value": str(SAMPLE_PROJECT), "profile": "finance-sox"}).encode()
    status, payload = router.handle("POST", "/api/preflight", body)
    assert status == 200
    _assert_no_bare_positive_claim(json.dumps(payload), context="router-preflight")

    status, payload = router.handle("POST", "/api/runs", body)
    assert status == 200
    run_id = payload["run_id"]

    _wait_for_completion(manager, run_id)
    status, payload = router.handle("GET", f"/api/runs/{run_id}", None)
    assert status == 200
    _assert_no_bare_positive_claim(json.dumps(payload), context="router-run-status")

    status, payload = router.handle("GET", f"/api/runs/{run_id}/board-verdict-data", None)
    assert status == 200
    _assert_no_bare_positive_claim(json.dumps(payload), context="router-board-verdict-data")


def test_api_router_returns_404_for_unknown_run(tmp_path):
    manager = RunManager(tmp_path / "gui-runs")
    from scanner.gui_server.api import ApiRouter

    router = ApiRouter(manager)
    status, payload = router.handle("GET", "/api/runs/does-not-exist", None)
    assert status == 404


def test_api_router_fails_closed_when_preflight_blocks_run_creation(tmp_path):
    from scanner.gui_server.api import ApiRouter

    manager = RunManager(tmp_path / "gui-runs")
    router = ApiRouter(manager)
    body = json.dumps({"source_type": "folder", "source_value": "does/not/exist", "profile": "enterprise"}).encode()
    status, payload = router.handle("POST", "/api/runs", body)
    assert status == 400
    assert payload["error"] == "preflight_failed"


# ---------------------------------------------------------------------------
# 10. No scanner scoring/rules changed: the GUI-triggered run must produce an
# identical deterministic decision/score/finding-count to a direct scan.
# ---------------------------------------------------------------------------


def test_gui_run_produces_identical_decision_to_direct_scan(tmp_path):
    direct_output = tmp_path / "direct-scan"
    direct_workspace = prepare_folder_workspace(SAMPLE_PROJECT, direct_output)
    direct_summary = run_scan(workspace=direct_workspace, profile="finance-sox", scanner_version=__version__)

    manager = RunManager(tmp_path / "gui-runs")
    result = manager.start_run("folder", str(SAMPLE_PROJECT), "finance-sox")
    run_id = result["run"]["run_id"]
    run = _wait_for_completion(manager, run_id)
    assert run["status"] == "sealed"

    gui_summary = json.loads((Path(run["evidence_dir"]) / "scan-summary.json").read_text(encoding="utf-8"))

    assert gui_summary["decision"] == direct_summary["decision"]
    assert gui_summary["score"] == direct_summary["score"]
    assert gui_summary["finding_counts"] == direct_summary["finding_counts"]
    assert gui_summary["category_scores"] == direct_summary["category_scores"]
