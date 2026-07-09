import json
from pathlib import Path

import pytest

from scanner.validation.metrics import calculate_validation_metrics
from scanner.validation.runner import run_validation_suite


@pytest.fixture(scope="module")
def adversarial_report(tmp_path_factory):
    output = tmp_path_factory.mktemp("validation") / "out"
    report = run_validation_suite(suite="adversarial", output_dir=output)
    return report, output / "validation-report.json"


def _detected_rule(report: dict, fixture: str, rule_id: str) -> bool:
    return any(
        item.get("fixture") == fixture and item.get("rule_id") == rule_id
        for item in report["detected_expected"]
    )


def test_validation_metrics_can_be_calculated():
    expected = [{"rule_id": "SEC-001", "severity": "Critical", "critical": True}]
    findings = [{
        "finding_id": "SEC-001-test",
        "rule_id": "SEC-001",
        "severity": "Critical",
        "decision_impact": "Block",
        "evidence_type": "pattern_match",
        "file_path": "app.py",
        "title": "Potential hardcoded secret detected",
    }]
    report = calculate_validation_metrics(expected, findings, determinism_passed=True)
    assert report["precision"] == 1.0
    assert report["recall"] == 1.0
    assert report["critical_miss_rate"] == 0.0
    assert report["evidence_traceability"] == 1.0
    assert report["status"] == "Passed"


def test_validation_report_is_generated(adversarial_report):
    report, report_path = adversarial_report
    assert report_path.exists()
    on_disk = json.loads(report_path.read_text(encoding="utf-8"))
    assert on_disk["suite"] == "adversarial-v0.1"
    assert on_disk["total_expected_findings"] >= 10
    assert on_disk["status"] == report["status"]


def test_seeded_expected_findings_are_detected(adversarial_report):
    report, _report_path = adversarial_report
    assert report["detected_expected_findings"] == report["total_expected_findings"]
    assert report["missed_expected_findings"] == []


def test_critical_seeded_findings_are_not_missed(adversarial_report):
    report, _report_path = adversarial_report
    assert report["critical_miss_rate"] == 0.0
    assert report["status"] == "Passed"


def test_validation_deterministic_rerun(adversarial_report):
    report, _report_path = adversarial_report
    assert report["determinism_passed"] is True


def test_evidence_traceability_exists_for_material_findings(adversarial_report):
    report, _report_path = adversarial_report
    assert report["evidence_traceability"] == 1.0


def test_misleading_docs_do_not_suppress_real_gaps(adversarial_report):
    report, _report_path = adversarial_report
    assert _detected_rule(report, "adversarial-docs", "DEL-003")
    assert _detected_rule(report, "adversarial-docs", "OPS-001")


def test_hidden_ai_indicators_are_detected(adversarial_report):
    report, _report_path = adversarial_report
    assert _detected_rule(report, "adversarial-hidden-ai", "AI-001")
    assert _detected_rule(report, "adversarial-hidden-ai", "AI-002")
    assert _detected_rule(report, "adversarial-hidden-ai", "AI-003")


def test_external_egress_indicators_are_detected(adversarial_report):
    report, _report_path = adversarial_report
    assert _detected_rule(report, "adversarial-egress", "OPS-011")


def test_validation_report_schema(adversarial_report):
    report, _report_path = adversarial_report
    required = {
        "suite",
        "total_expected_findings",
        "detected_expected_findings",
        "missed_expected_findings",
        "unexpected_findings",
        "precision",
        "recall",
        "critical_miss_rate",
        "evidence_traceability",
        "determinism_passed",
        "status",
    }
    assert required <= report.keys()
