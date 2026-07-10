import importlib
import json
from pathlib import Path

from typer.testing import CliRunner

from scanner.app.cli import app
from scanner.core.evidence import write_json
from scanner.governance.release_go_no_go import build_release_go_no_go_report


SCAN_COMMAND = "python -m scanner scan-folder --path tests/sample_projects/insecure-python --output output --profile finance-sox"


def _sample_module():
    return importlib.import_module("scanner.governance.sample_scan_evidence")


def _write_evidence_package(path: Path, *, include_manifest: bool = True, include_summary: bool = True, include_report: bool = True) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    if include_summary:
        write_json(path / "scan-summary.json", {
            "profile": "finance-sox",
            "source_metadata": {"source_path": "tests/sample_projects/insecure-python"},
            "decision": "Not Approved",
            "score": 0,
            "finding_counts": {
                "Critical": 1,
                "High": 2,
                "Medium": 3,
                "Low": 4,
            },
            "report_path": str(path / "final-report.html"),
        })
    if include_report:
        (path / "final-report.html").write_text("<html><body>sample</body></html>", encoding="utf-8")
    if include_manifest:
        write_json(path / "manifest.json", {
            "files": [
                {"path": "scan-summary.json", "sha256": "sample"},
                {"path": "final-report.html", "sha256": "sample"},
            ],
            "package_sha256": "sample",
        })
    return path


def test_sample_scan_evidence_module_exists():
    assert Path("scanner/governance/sample_scan_evidence.py").exists()


def test_valid_evidence_package_generates_sample_scan_summary(tmp_path):
    package = _write_evidence_package(tmp_path / "evidence-package")
    out = tmp_path / "governance-output"
    summary = _sample_module().collect_sample_scan_evidence(package, SCAN_COMMAND, out)

    summary_path = out / "sample_scan_summary.json"
    assert summary_path.exists()
    saved = json.loads(summary_path.read_text(encoding="utf-8"))
    assert saved == summary
    assert summary["schema"] == "enterprise-whitebox-sample-scan-summary"
    assert summary["schema_version"] == "0.1"
    assert summary["command"] == SCAN_COMMAND
    assert summary["profile"] == "finance-sox"
    assert summary["scan_target"] == "tests/sample_projects/insecure-python"
    assert summary["decision"] == "Not Approved"
    assert summary["score"] == 0
    assert summary["critical"] == 1
    assert summary["high"] == 2
    assert summary["medium"] == 3
    assert summary["low"] == 4
    assert summary["findings_total"] == 10
    assert summary["manifest_status"] == "present"
    assert summary["report_status"] == "present"
    assert summary["status"] == "passed"
    assert summary["notes"] == []


def test_missing_evidence_package_returns_unknown_with_note(tmp_path):
    summary = _sample_module().build_sample_scan_summary(tmp_path / "missing-package", SCAN_COMMAND)

    assert summary["status"] == "unknown"
    assert summary["evidence_package_path"] is None
    assert summary["manifest_path"] is None
    assert summary["report_path"] is None
    assert summary["manifest_status"] == "unknown"
    assert summary["report_status"] == "unknown"
    assert summary["decision"] == "Unknown"
    assert summary["notes"]


def test_missing_manifest_is_handled_conservatively(tmp_path):
    package = _write_evidence_package(tmp_path / "evidence-package", include_manifest=False)
    summary = _sample_module().build_sample_scan_summary(package, SCAN_COMMAND)

    assert summary["status"] == "failed"
    assert summary["manifest_status"] == "missing"
    assert summary["report_status"] == "present"
    assert summary["decision"] == "Not Approved"
    assert any("manifest" in note.lower() for note in summary["notes"])


def test_missing_scan_summary_is_handled_conservatively(tmp_path):
    package = _write_evidence_package(tmp_path / "evidence-package", include_summary=False)
    summary = _sample_module().build_sample_scan_summary(package, SCAN_COMMAND)

    assert summary["status"] == "failed"
    assert summary["manifest_status"] == "present"
    assert summary["decision"] == "Unknown"
    assert summary["score"] == 0
    assert summary["findings_total"] == 0
    assert any("scan summary" in note.lower() for note in summary["notes"])


def test_final_report_presence_is_recorded(tmp_path):
    package = _write_evidence_package(tmp_path / "evidence-package", include_report=False)
    summary = _sample_module().build_sample_scan_summary(package, SCAN_COMMAND)

    assert summary["status"] == "passed"
    assert summary["report_status"] == "missing"
    assert summary["report_path"] is None
    assert any("final html report" in note.lower() for note in summary["notes"])


def test_cli_generates_sample_scan_summary(tmp_path):
    package = _write_evidence_package(tmp_path / "evidence-package")
    out = tmp_path / "governance-output"
    runner = CliRunner()
    result = runner.invoke(app, [
        "collect-scan-evidence",
        "--evidence-package",
        str(package),
        "--command",
        SCAN_COMMAND,
        "--output",
        str(out),
    ])

    assert result.exit_code == 0
    summary_path = out / "sample_scan_summary.json"
    assert summary_path.exists()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["status"] == "passed"
    assert summary["decision"] == "Not Approved"


def test_sample_release_manifest_can_reference_generated_summary(tmp_path):
    package = _write_evidence_package(tmp_path / "evidence-package")
    out = tmp_path / "governance-output"
    _sample_module().collect_sample_scan_evidence(package, SCAN_COMMAND, out)
    write_json(tmp_path / "governance.json", {
        "schema": "enterprise-whitebox-governance-check-report",
        "schema_version": "0.1",
        "status": "Passed",
        "checks": [],
        "warnings": [],
        "failures": [],
        "limitations": [],
    })
    write_json(tmp_path / "tests.json", {
        "schema": "enterprise-whitebox-test-result-summary",
        "schema_version": "0.1",
        "command": "python -m pytest",
        "status": "passed",
        "tests_passed": 1,
        "tests_failed": 0,
        "tests_skipped": 0,
        "tests_total": 1,
        "duration_seconds": 1,
        "generated_at": "2026-07-09T00:00:00Z",
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
            "test_result_summary": "tests.json",
            "sample_scan_summary": "governance-output/sample_scan_summary.json",
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
    assert report["summary"]["sample_scan_status"] == "passed"
