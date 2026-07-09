import json
from pathlib import Path

from typer.testing import CliRunner

from scanner.app.cli import app
from scanner.core.evidence import write_json
from scanner.governance.release_go_no_go import build_release_go_no_go_report
from scanner.governance.test_evidence import parse_junit_xml


def _write_xml(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def test_junit_xml_parser_handles_passing_tests(tmp_path):
    junit = _write_xml(tmp_path / "pytest.xml", '<testsuite tests="3" failures="0" errors="0" skipped="0" time="1.2"></testsuite>')
    summary = parse_junit_xml(junit, "python -m pytest")
    assert summary["status"] == "passed"
    assert summary["tests_total"] == 3
    assert summary["tests_passed"] == 3
    assert summary["tests_failed"] == 0
    assert summary["duration_seconds"] == 1.2


def test_junit_xml_parser_handles_failures_and_errors(tmp_path):
    junit = _write_xml(tmp_path / "pytest.xml", '<testsuite tests="4" failures="1" errors="1" skipped="0" time="2.5"></testsuite>')
    summary = parse_junit_xml(junit, "python -m pytest")
    assert summary["status"] == "failed"
    assert summary["tests_total"] == 4
    assert summary["tests_failed"] == 2
    assert summary["tests_passed"] == 2


def test_junit_xml_parser_handles_skipped_tests(tmp_path):
    junit = _write_xml(tmp_path / "pytest.xml", '<testsuite tests="5" failures="0" errors="0" skipped="2" time="3"></testsuite>')
    summary = parse_junit_xml(junit, "python -m pytest")
    assert summary["status"] == "passed"
    assert summary["tests_total"] == 5
    assert summary["tests_skipped"] == 2
    assert summary["tests_passed"] == 3


def test_missing_junit_xml_produces_unknown_status_with_note(tmp_path):
    summary = parse_junit_xml(tmp_path / "missing.xml", "python -m pytest")
    assert summary["status"] == "unknown"
    assert summary["tests_total"] == 0
    assert summary["notes"]


def test_invalid_junit_xml_produces_unknown_status_with_note(tmp_path):
    junit = _write_xml(tmp_path / "pytest.xml", "<not-xml")
    summary = parse_junit_xml(junit, "python -m pytest")
    assert summary["status"] == "unknown"
    assert summary["notes"]


def test_cli_generates_test_result_summary(tmp_path):
    junit = _write_xml(tmp_path / "pytest.xml", '<testsuite tests="2" failures="0" errors="0" skipped="0" time="0.5"></testsuite>')
    runner = CliRunner()
    result = runner.invoke(app, [
        "collect-test-evidence",
        "--junit",
        str(junit),
        "--command",
        "python -m pytest --junitxml pytest.xml",
        "--output",
        str(tmp_path / "out"),
    ])
    assert result.exit_code == 0
    summary_path = tmp_path / "out" / "test_result_summary.json"
    assert summary_path.exists()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["status"] == "passed"
    assert summary["source"] == "junit_xml"


def test_generated_summary_can_be_referenced_by_release_manifest_logic(tmp_path):
    junit = _write_xml(tmp_path / "pytest.xml", '<testsuite tests="2" failures="0" errors="0" skipped="0" time="0.5"></testsuite>')
    runner = CliRunner()
    result = runner.invoke(app, [
        "collect-test-evidence",
        "--junit",
        str(junit),
        "--command",
        "python -m pytest --junitxml pytest.xml",
        "--output",
        str(tmp_path),
    ])
    assert result.exit_code == 0
    write_json(tmp_path / "governance.json", {
        "schema": "enterprise-whitebox-governance-check-report",
        "schema_version": "0.1",
        "status": "Passed",
        "checks": [],
        "warnings": [],
        "failures": [],
        "limitations": [],
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
        "status": "passed",
        "notes": [],
    })
    write_json(tmp_path / "trend.json", {
        "schema": "enterprise-whitebox-validation-trend-report",
        "schema_version": "0.1",
        "summary": {"gate_status": "Passed"},
    })
    write_json(tmp_path / "approval.json", {
        "schema": "enterprise-whitebox-approval-record",
        "schema_version": "0.1",
        "release_id": "unit-release",
        "decision": "Approved for pilot",
        "approved_by_role": "Release Manager",
        "approval_date": "2026-07-09",
        "conditions": [],
        "notes": [],
    })
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
            "test_result_summary": "test_result_summary.json",
            "sample_scan_summary": "scan.json",
            "adversarial_validation_report": None,
            "goldset_comparison_report": None,
            "portfolio_validation_report": None,
            "validation_trend_report": "trend.json",
            "accepted_warnings": [],
            "approval_record": "approval.json",
        },
        "known_limitations": [],
        "release_notes": [],
    })
    report = build_release_go_no_go_report(tmp_path / "manifest.json")
    assert report["summary"]["test_status"] == "passed"
