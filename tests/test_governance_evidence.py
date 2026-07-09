import json
from pathlib import Path

from typer.testing import CliRunner

from scanner.app.cli import app
from scanner.governance.checks import run_governance_checks
from scanner.governance.release_evidence import generate_release_evidence


TEMPLATES = [
    "governance/templates/CHANGE_REQUEST_TEMPLATE.md",
    "governance/templates/RELEASE_CHECKLIST_TEMPLATE.md",
    "governance/templates/CALIBRATION_DECISION_TEMPLATE.md",
    "governance/templates/ADR_TEMPLATE.md",
]

SCHEMAS = [
    "governance/schemas/change_request.schema.json",
    "governance/schemas/release_checklist.schema.json",
    "governance/schemas/release_evidence.schema.json",
]


def test_governance_templates_exist():
    for template in TEMPLATES:
        assert Path(template).exists(), template


def test_governance_schemas_exist():
    for schema in SCHEMAS:
        assert Path(schema).exists(), schema


def test_governance_evidence_packet_spec_exists():
    assert Path("docs/governance/GOVERNANCE_EVIDENCE_PACKET_SPEC.md").exists()


def test_governance_check_module_returns_status():
    report = run_governance_checks()
    assert report["schema"] == "enterprise-whitebox-governance-check-report"
    assert report["status"] in {"Passed", "Warning", "Failed"}
    assert report["checks"]
    assert "warnings" in report
    assert "failures" in report


def test_governance_check_report_is_generated(tmp_path):
    report = run_governance_checks(output_dir=tmp_path)
    report_path = tmp_path / "governance-check-report.json"
    assert report_path.exists()
    saved = json.loads(report_path.read_text(encoding="utf-8"))
    assert saved["status"] == report["status"]


def test_release_evidence_file_is_generated_without_fake_test_results(tmp_path):
    governance_report = run_governance_checks(output_dir=tmp_path)
    evidence = generate_release_evidence(governance_report=governance_report, output_dir=tmp_path)
    evidence_path = tmp_path / "release-evidence.json"
    assert evidence_path.exists()
    assert evidence["schema"] == "enterprise-whitebox-release-evidence"
    assert evidence["test_status"] == "unknown"
    assert evidence["validation_status"] == "unknown"
    assert evidence["release_gate_status"] == "Not Evaluated"
    assert evidence["release_decision"] == "Not Requested"


def test_cli_governance_check_generates_governance_output(tmp_path):
    runner = CliRunner()
    result = runner.invoke(app, ["governance-check", "--output", str(tmp_path / "governance-output")])
    assert result.exit_code == 0
    report_path = tmp_path / "governance-output" / "governance-check-report.json"
    evidence_path = tmp_path / "governance-output" / "release-evidence.json"
    assert report_path.exists()
    assert evidence_path.exists()
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["test_status"] == "unknown"
