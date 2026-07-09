import json
from pathlib import Path

from typer.testing import CliRunner

from scanner.app.cli import app
from scanner.core.evidence import write_json
from scanner.governance.release_go_no_go import build_release_go_no_go_report, prepare_release_evidence


RELEASE_SCHEMAS = [
    "governance/schemas/release_manifest.schema.json",
    "governance/schemas/test_result_summary.schema.json",
    "governance/schemas/sample_scan_summary.schema.json",
    "governance/schemas/accepted_warning.schema.json",
    "governance/schemas/approval_record.schema.json",
    "governance/schemas/release_go_no_go_report.schema.json",
]

RELEASE_EXAMPLES = [
    "governance/examples/sample-release-manifest.json",
    "governance/examples/sample-test-result-summary.json",
    "governance/examples/sample-scan-summary.json",
    "governance/examples/sample-accepted-warning.json",
    "governance/examples/sample-approval-record.json",
]


def test_release_intake_schemas_exist():
    for schema in RELEASE_SCHEMAS:
        assert Path(schema).exists(), schema


def test_sample_release_examples_exist():
    for example in RELEASE_EXAMPLES:
        assert Path(example).exists(), example


def _write_release_fixture(
    tmp_path: Path,
    *,
    test_status: str = "passed",
    sample_status: str = "passed",
    governance_status: str = "Passed",
    trend_status: str = "Passed",
    approval_decision: str | None = "Approved for pilot",
    accepted_warning_source: str | None = None,
    include_goldset: bool = True,
    include_portfolio: bool = True,
    known_limitations: list[str] | None = None,
) -> Path:
    write_json(tmp_path / "governance.json", {
        "schema": "enterprise-whitebox-governance-check-report",
        "schema_version": "0.1",
        "status": governance_status,
        "checks": [],
        "warnings": [],
        "failures": [],
        "limitations": [],
    })
    write_json(tmp_path / "tests.json", {
        "schema": "enterprise-whitebox-test-result-summary",
        "schema_version": "0.1",
        "command": "python -m pytest",
        "status": test_status,
        "tests_passed": 1 if test_status == "passed" else 0,
        "tests_failed": 1 if test_status == "failed" else 0,
        "duration_seconds": 1,
        "generated_at": "2026-07-09T00:00:00Z",
        "notes": [],
    })
    write_json(tmp_path / "scan.json", {
        "schema": "enterprise-whitebox-sample-scan-summary",
        "schema_version": "0.1",
        "command": "sample",
        "profile": "enterprise",
        "decision": "Conditional",
        "score": 80,
        "critical": 0,
        "high": 0,
        "evidence_package_path": None,
        "manifest_path": None,
        "status": sample_status,
        "notes": [],
    })
    write_json(tmp_path / "adversarial.json", {"status": "passed"})
    if include_goldset:
        write_json(tmp_path / "goldset.json", {"status": "passed"})
    if include_portfolio:
        write_json(tmp_path / "portfolio.json", {"status": "passed"})
    write_json(tmp_path / "trend.json", {
        "schema": "enterprise-whitebox-validation-trend-report",
        "schema_version": "0.1",
        "summary": {"gate_status": trend_status},
    })
    accepted_warnings = []
    if accepted_warning_source:
        write_json(tmp_path / "accepted-warning.json", {
            "schema": "enterprise-whitebox-accepted-warning",
            "schema_version": "0.1",
            "warning_id": "WARN-1",
            "source": accepted_warning_source,
            "description": "Accepted warning",
            "reason_accepted": "Accepted for test",
            "accepted_by_role": "Release Manager",
            "expires_at": None,
        })
        accepted_warnings.append("accepted-warning.json")
    approval_record = None
    if approval_decision:
        write_json(tmp_path / "approval.json", {
            "schema": "enterprise-whitebox-approval-record",
            "schema_version": "0.1",
            "release_id": "unit-release",
            "decision": approval_decision,
            "approved_by_role": "Release Manager",
            "approval_date": "2026-07-09",
            "conditions": ["Condition accepted"] if known_limitations else [],
            "notes": [],
        })
        approval_record = "approval.json"

    write_json(tmp_path / "manifest.json", {
        "schema": "enterprise-whitebox-release-manifest",
        "schema_version": "0.1",
        "release_id": "unit-release",
        "scanner_version": "unit",
        "ruleset_version": "rules",
        "ruleset_sha256": "hash",
        "created_at": "2026-07-09",
        "evidence_inputs": {
            "governance_check_report": "governance.json",
            "test_result_summary": "tests.json",
            "sample_scan_summary": "scan.json",
            "adversarial_validation_report": "adversarial.json",
            "goldset_comparison_report": "goldset.json" if include_goldset else None,
            "portfolio_validation_report": "portfolio.json" if include_portfolio else None,
            "validation_trend_report": "trend.json",
            "accepted_warnings": accepted_warnings,
            "approval_record": approval_record,
        },
        "known_limitations": known_limitations or [],
        "release_notes": [],
    })
    return tmp_path / "manifest.json"


def test_release_evidence_generation_with_provided_inputs(tmp_path):
    manifest = _write_release_fixture(tmp_path)
    release_evidence, report = prepare_release_evidence(manifest, tmp_path / "out")
    assert report["status"] == "Go"
    assert release_evidence["test_status"] == "passed"
    assert release_evidence["release_gate_status"] == "Passed"
    assert (tmp_path / "out" / "release-evidence.json").exists()
    assert (tmp_path / "out" / "release-go-no-go-report.json").exists()


def test_missing_evidence_is_marked_missing_or_unknown(tmp_path):
    manifest = _write_release_fixture(tmp_path, include_goldset=False, include_portfolio=False, approval_decision=None)
    report = build_release_go_no_go_report(manifest)
    assert report["summary"]["goldset_status"] == "missing"
    assert report["summary"]["portfolio_status"] == "missing"
    assert report["summary"]["approval_decision"] == "Not Requested"
    assert report["status"] == "Not Evaluated"


def test_failed_tests_produce_no_go(tmp_path):
    manifest = _write_release_fixture(tmp_path, test_status="failed")
    report = build_release_go_no_go_report(manifest)
    assert report["status"] == "No-Go"
    assert any("Test result" in reason for reason in report["blocking_reasons"])


def test_failed_trend_gate_produces_no_go(tmp_path):
    manifest = _write_release_fixture(tmp_path, trend_status="Failed")
    report = build_release_go_no_go_report(manifest)
    assert report["status"] == "No-Go"
    assert any("trend" in reason.lower() for reason in report["blocking_reasons"])


def test_accepted_warning_can_produce_conditional_go(tmp_path):
    manifest = _write_release_fixture(tmp_path, trend_status="Warning", accepted_warning_source="trend_gate")
    report = build_release_go_no_go_report(manifest)
    assert report["status"] == "Conditional Go"
    assert report["summary"]["accepted_warnings_count"] == 1


def test_approval_record_is_required_for_go(tmp_path):
    manifest = _write_release_fixture(tmp_path, approval_decision=None)
    report = build_release_go_no_go_report(manifest)
    assert report["status"] == "Not Evaluated"
    assert report["summary"]["approval_decision"] == "Not Requested"


def test_command_does_not_fake_test_results_when_missing(tmp_path):
    manifest = _write_release_fixture(tmp_path, approval_decision=None)
    data = json.loads(manifest.read_text(encoding="utf-8"))
    data["evidence_inputs"]["test_result_summary"] = None
    write_json(manifest, data)
    release_evidence, report = prepare_release_evidence(manifest, tmp_path / "out")
    assert report["summary"]["test_status"] == "missing"
    assert release_evidence["test_status"] == "missing"


def test_cli_generates_release_evidence_and_go_no_go_report(tmp_path):
    manifest = _write_release_fixture(tmp_path)
    runner = CliRunner()
    result = runner.invoke(app, ["prepare-release-evidence", "--manifest", str(manifest), "--output", str(tmp_path / "release-out")])
    assert result.exit_code == 0
    assert (tmp_path / "release-out" / "release-evidence.json").exists()
    assert (tmp_path / "release-out" / "release-go-no-go-report.json").exists()
