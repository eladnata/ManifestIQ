import json
from pathlib import Path

from typer.testing import CliRunner

from scanner.app.cli import app
from scanner.core.evidence import write_json
from scanner.validation.portfolio import aggregate_portfolio


def test_portfolio_manifest_schema_example_exists():
    assert Path("validation/portfolio/schemas/portfolio_manifest.schema.json").exists()
    assert Path("validation/portfolio/examples/sample-portfolio-manifest.json").exists()


def test_scanner_only_triage_schema_example_exists():
    assert Path("validation/portfolio/schemas/scanner_only_triage.schema.json").exists()
    assert Path("validation/portfolio/examples/sample-scanner-only-triage.json").exists()


def test_calibration_log_schema_example_exists():
    assert Path("validation/portfolio/schemas/calibration_log.schema.json").exists()
    assert Path("validation/portfolio/examples/sample-calibration-log.json").exists()


def test_portfolio_report_schema_exists():
    assert Path("validation/portfolio/schemas/portfolio_report.schema.json").exists()


def _comparison_report_one() -> dict:
    return {
        "schema": "enterprise-whitebox-goldset-comparison-report",
        "schema_version": "0.1",
        "repo_id": "repo-one",
        "profile": "enterprise",
        "scanner_run_id": "scan-one",
        "summary": {
            "human_findings_count": 3,
            "scanner_findings_count": 4,
            "detectable_human_findings_count": 2,
            "matched_findings_count": 1,
            "missed_detectable_findings_count": 1,
            "scanner_only_findings_count": 2,
            "critical_miss_rate": 0.5,
            "recall_detectable": 0.5,
            "material_precision": 1.0,
            "top_blocker_agreement": 0.5,
            "evidence_traceability": 1.0,
            "confidence_calibration": {"status": "Worksheet Provided", "evidence_quality_score": 4},
            "review_preparation_acceleration": {"status": "Worksheet Provided", "acceleration": 0.5},
        },
        "matched_findings": [
            {
                "human_finding_id": "H1",
                "scanner_finding_id": "S1",
                "human_rule_id": "SEC-001",
                "scanner_rule_id": "SEC-001",
                "human_domain": "Security",
                "human_severity": "Critical",
                "human_materiality": "material",
                "match_confidence": "High",
                "match_reasons": ["rule_id matched"],
            }
        ],
        "missed_detectable_findings": [
            {
                "human_finding_id": "H2",
                "rule_id": "SEC-002",
                "domain": "Security",
                "severity": "Critical",
                "decision_impact": "Block",
                "title": "Unsafe dynamic execution",
                "expected_scanner_detectable": True,
                "materiality": "material",
            }
        ],
        "non_detectable_human_findings": [
            {
                "human_finding_id": "H3",
                "rule_id": None,
                "domain": "Business Risk",
                "severity": "High",
                "expected_scanner_detectable": False,
            }
        ],
        "scanner_only_findings": [
            {"finding_id": "S2", "rule_id": "OPS-003", "category": "Operations", "severity": "High", "decision_impact": "Conditional", "title": "No monitoring evidence"},
            {"finding_id": "S3", "rule_id": "DOC-001", "category": "Documentation", "severity": "Medium", "decision_impact": "Conditional", "title": "Missing documentation"},
        ],
        "triage_required": [],
        "recommendations": [],
    }


def _comparison_report_two() -> dict:
    return {
        "schema": "enterprise-whitebox-goldset-comparison-report",
        "schema_version": "0.1",
        "repo_id": "repo-two",
        "profile": "finance-sox",
        "scanner_run_id": "scan-two",
        "summary": {
            "human_findings_count": 1,
            "scanner_findings_count": 2,
            "detectable_human_findings_count": 1,
            "matched_findings_count": 1,
            "missed_detectable_findings_count": 0,
            "scanner_only_findings_count": 1,
            "critical_miss_rate": 0.0,
            "recall_detectable": 1.0,
            "material_precision": 1.0,
            "top_blocker_agreement": 1.0,
            "evidence_traceability": 1.0,
            "confidence_calibration": {"status": "Worksheet Provided", "evidence_quality_score": 5},
            "review_preparation_acceleration": {"status": "Worksheet Provided", "acceleration": 0.75},
        },
        "matched_findings": [
            {
                "human_finding_id": "H4",
                "scanner_finding_id": "S4",
                "human_rule_id": "OPS-003",
                "scanner_rule_id": "OPS-003",
                "human_domain": "Operations",
                "human_severity": "High",
                "human_materiality": "material",
                "match_confidence": "High",
                "match_reasons": ["rule_id matched"],
            }
        ],
        "missed_detectable_findings": [],
        "non_detectable_human_findings": [],
        "scanner_only_findings": [
            {"finding_id": "S5", "rule_id": "LIC-003", "category": "License Risk", "severity": "High", "decision_impact": "Mandatory Review", "title": "Dependency missing license"},
        ],
        "triage_required": [],
        "recommendations": [],
    }


def _write_portfolio_inputs(tmp_path: Path) -> Path:
    write_json(tmp_path / "reports" / "one.json", _comparison_report_one())
    write_json(tmp_path / "reports" / "two.json", _comparison_report_two())
    write_json(tmp_path / "triage-one.json", {
        "schema": "enterprise-whitebox-scanner-only-triage",
        "schema_version": "0.1",
        "repo_id": "repo-one",
        "scanner_run_id": "scan-one",
        "triaged_by": [{"reviewer_id": "r1", "role": "AppSec"}],
        "triage_items": [
            {"scanner_finding_id": "S2", "rule_id": "OPS-003", "domain": "Operations", "severity": "High", "label": "false_positive", "reason": "Synthetic false positive", "confidence": "High"},
            {"scanner_finding_id": "S3", "rule_id": "DOC-001", "domain": "Documentation", "severity": "Medium", "label": "valid_material", "reason": "Valid scanner-only finding", "confidence": "Medium"},
        ],
    })
    write_json(tmp_path / "calibration.json", {
        "schema": "enterprise-whitebox-calibration-log",
        "schema_version": "0.1",
        "calibration_id": "CAL-TEST",
        "date": "2026-07-09",
        "ruleset_version_before": "before",
        "ruleset_version_after": None,
        "reason": "Unit test calibration log",
        "evidence": [{"repo_id": "repo-one", "finding_id": "S2", "metric": "false_positive_rate_after_triage", "observation": "Synthetic observation"}],
        "decision": {"change_type": "no_change", "description": "No change in unit test", "approved_by_role": "AppSec"},
    })
    manifest = {
        "schema": "enterprise-whitebox-validation-portfolio",
        "schema_version": "0.1",
        "portfolio_id": "unit-portfolio",
        "description": "Unit test portfolio",
        "created_at": "2026-07-09",
        "scanner_version": "test",
        "ruleset_version": "ruleset-test",
        "comparison_reports": [
            {"repo_id": "repo-one", "profile": "enterprise", "comparison_report_path": "reports/one.json", "worksheet_path": None, "triage_path": "triage-one.json"},
            {"repo_id": "repo-two", "profile": "finance-sox", "comparison_report_path": "reports/two.json", "worksheet_path": None, "triage_path": None},
        ],
    }
    write_json(tmp_path / "portfolio.json", manifest)
    return tmp_path / "portfolio.json"


def test_portfolio_aggregation_across_multiple_comparison_reports(tmp_path):
    manifest = _write_portfolio_inputs(tmp_path)
    report = aggregate_portfolio(manifest, tmp_path / "out", calibration_log_paths=[tmp_path / "calibration.json"])
    assert report["summary"]["repositories_count"] == 2
    assert report["summary"]["detectable_human_findings_count"] == 3
    assert report["summary"]["matched_findings_count"] == 2
    assert report["summary"]["missed_detectable_findings_count"] == 1
    assert report["summary"]["detectable_recall"] == 0.6667


def test_untriaged_scanner_only_findings_are_not_false_positives(tmp_path):
    manifest = _write_portfolio_inputs(tmp_path)
    report = aggregate_portfolio(manifest, tmp_path / "out")
    triage = report["scanner_only_triage_summary"]
    assert triage["scanner_only_findings_count"] == 3
    assert triage["triaged_scanner_only_findings_count"] == 2
    assert triage["untriaged_scanner_only_findings_count"] == 1
    assert triage["false_positive_count"] == 1


def test_triaged_false_positives_affect_material_precision(tmp_path):
    manifest = _write_portfolio_inputs(tmp_path)
    report = aggregate_portfolio(manifest, tmp_path / "out")
    assert report["summary"]["material_precision_after_triage"] == 0.6667


def test_triaged_valid_material_affects_scanner_only_value_metric(tmp_path):
    manifest = _write_portfolio_inputs(tmp_path)
    report = aggregate_portfolio(manifest, tmp_path / "out")
    assert report["scanner_only_triage_summary"]["valid_material_count"] == 1
    assert report["scanner_only_triage_summary"]["valid_scanner_only_material_finding_rate"] == 0.5


def test_non_detectable_human_findings_remain_excluded_from_recall(tmp_path):
    manifest = _write_portfolio_inputs(tmp_path)
    report = aggregate_portfolio(manifest, tmp_path / "out")
    assert report["summary"]["detectable_human_findings_count"] == 3
    assert report["summary"]["detectable_recall"] == 0.6667


def test_critical_miss_rate_aggregates_correctly(tmp_path):
    manifest = _write_portfolio_inputs(tmp_path)
    report = aggregate_portfolio(manifest, tmp_path / "out")
    assert report["summary"]["critical_miss_rate"] == 0.5


def test_domain_rule_family_and_profile_metrics_are_generated(tmp_path):
    manifest = _write_portfolio_inputs(tmp_path)
    report = aggregate_portfolio(manifest, tmp_path / "out")
    assert any(item["domain"] == "Security" for item in report["by_domain"])
    assert any(item["rule_family"] == "SEC" for item in report["by_rule_family"])
    assert any(item["profile"] == "enterprise" for item in report["by_profile"])


def test_cli_generates_portfolio_validation_report(tmp_path):
    manifest = _write_portfolio_inputs(tmp_path)
    runner = CliRunner()
    result = runner.invoke(app, ["validate-portfolio", "--manifest", str(manifest), "--output", str(tmp_path / "cli-out")])
    assert result.exit_code == 0
    report_path = tmp_path / "cli-out" / "portfolio-validation-report.json"
    assert report_path.exists()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["schema"] == "enterprise-whitebox-portfolio-validation-report"
