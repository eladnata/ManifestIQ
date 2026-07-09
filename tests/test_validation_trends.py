import json
from pathlib import Path

from typer.testing import CliRunner

from scanner.app.cli import app
from scanner.core.evidence import write_json
from scanner.validation.trends import compare_trend, compute_metric_deltas


def test_trend_manifest_schema_example_exists():
    assert Path("validation/trends/schemas/trend_manifest.schema.json").exists()
    assert Path("validation/trends/examples/sample-trend-manifest.json").exists()


def test_validation_gate_policy_example_exists():
    assert Path("validation/trends/schemas/validation_gate_policy.schema.json").exists()
    assert Path("validation/trends/examples/sample-validation-gate-policy.json").exists()


def test_trend_report_schema_exists():
    assert Path("validation/trends/schemas/trend_report.schema.json").exists()


def _portfolio_report(**overrides):
    summary = {
        "repositories_count": 2,
        "profiles": ["enterprise"],
        "detectable_human_findings_count": 10,
        "matched_findings_count": 9,
        "missed_detectable_findings_count": 1,
        "scanner_only_findings_count": 10,
        "triaged_scanner_only_findings_count": 5,
        "detectable_recall": 0.9,
        "material_precision_after_triage": 0.9,
        "critical_miss_rate": 0.0,
        "top_blocker_agreement": 0.9,
        "evidence_traceability": 1.0,
        "average_review_preparation_acceleration": 0.5,
    }
    summary.update(overrides)
    return {
        "schema": "enterprise-whitebox-portfolio-validation-report",
        "schema_version": "0.1",
        "portfolio_id": "portfolio",
        "scanner_version": "test",
        "ruleset_version": "rules",
        "summary": summary,
        "by_domain": [
            {"domain": "Security", "detectable_recall": summary.get("domain_security_recall", summary["detectable_recall"])},
            {"domain": "Operations", "detectable_recall": 0.9},
        ],
        "by_rule_family": [
            {"rule_family": "SEC", "detectable_recall": summary.get("rule_sec_recall", summary["detectable_recall"])},
            {"rule_family": "OPS", "detectable_recall": 0.9},
        ],
        "by_profile": [{"profile": "enterprise", "detectable_recall": summary["detectable_recall"]}],
        "confidence_calibration": {},
        "scanner_only_triage_summary": {
            "scanner_only_findings_count": summary["scanner_only_findings_count"],
            "triage_rate": summary.get("triage_rate", 0.5),
            "valid_scanner_only_material_finding_rate": summary.get("valid_scanner_only_material_finding_rate", 0.25),
            "false_positive_rate_after_triage": summary.get("false_positive_rate_after_triage", 0.1),
        },
        "reviewer_agreement_summary": {},
        "recommendations": [],
        "limitations": [],
    }


def _write_trend_inputs(tmp_path: Path, baseline: dict, candidate: dict):
    write_json(tmp_path / "baseline.json", baseline)
    write_json(tmp_path / "candidate.json", candidate)
    write_json(tmp_path / "policy.json", json.loads(Path("validation/trends/examples/sample-validation-gate-policy.json").read_text(encoding="utf-8")))
    write_json(tmp_path / "manifest.json", {
        "schema": "enterprise-whitebox-validation-trend-manifest",
        "schema_version": "0.1",
        "trend_id": "unit-trend",
        "description": "Unit trend",
        "baseline_report_path": "baseline.json",
        "candidate_report_path": "candidate.json",
        "comparison_mode": "baseline_vs_candidate",
        "created_at": "2026-07-09",
    })
    return tmp_path / "manifest.json", tmp_path / "policy.json"


def test_trend_comparison_computes_metric_deltas():
    baseline = _portfolio_report(detectable_recall=0.9)
    candidate = _portfolio_report(detectable_recall=0.85)
    deltas = compute_metric_deltas(baseline, candidate)
    assert deltas["detectable_recall"]["baseline"] == 0.9
    assert deltas["detectable_recall"]["candidate"] == 0.85
    assert deltas["detectable_recall"]["delta"] == -0.05


def test_no_regression_produces_passed(tmp_path):
    manifest, policy = _write_trend_inputs(tmp_path, _portfolio_report(), _portfolio_report())
    report = compare_trend(manifest, policy, tmp_path / "out")
    assert report["summary"]["gate_status"] == "Passed"
    assert report["blocking_regressions"] == []
    assert report["warnings"] == []


def test_critical_miss_increase_produces_failed(tmp_path):
    manifest, policy = _write_trend_inputs(tmp_path, _portfolio_report(), _portfolio_report(critical_miss_rate=0.1))
    report = compare_trend(manifest, policy, tmp_path / "out")
    assert report["summary"]["gate_status"] == "Failed"
    assert any(item["type"] == "critical_miss_rate_above_threshold" for item in report["blocking_regressions"])


def test_evidence_traceability_drop_produces_failed(tmp_path):
    manifest, policy = _write_trend_inputs(tmp_path, _portfolio_report(), _portfolio_report(evidence_traceability=0.95))
    report = compare_trend(manifest, policy, tmp_path / "out")
    assert report["summary"]["gate_status"] == "Failed"
    assert any(item["type"] == "evidence_traceability_below_threshold" for item in report["blocking_regressions"])


def test_recall_drop_beyond_threshold_produces_failed(tmp_path):
    manifest, policy = _write_trend_inputs(tmp_path, _portfolio_report(detectable_recall=0.9), _portfolio_report(detectable_recall=0.7))
    report = compare_trend(manifest, policy, tmp_path / "out")
    assert report["summary"]["gate_status"] == "Failed"
    assert any(item["type"] in {"detectable_recall_below_threshold", "detectable_recall_drop"} for item in report["blocking_regressions"])


def test_top_blocker_agreement_drop_produces_warning(tmp_path):
    manifest, policy = _write_trend_inputs(tmp_path, _portfolio_report(top_blocker_agreement=0.9), _portfolio_report(top_blocker_agreement=0.8))
    report = compare_trend(manifest, policy, tmp_path / "out")
    assert report["summary"]["gate_status"] == "Warning"
    assert any(item["type"] == "top_blocker_agreement_drop" for item in report["warnings"])


def test_material_precision_drop_produces_warning(tmp_path):
    manifest, policy = _write_trend_inputs(tmp_path, _portfolio_report(material_precision_after_triage=0.95), _portfolio_report(material_precision_after_triage=0.8))
    report = compare_trend(manifest, policy, tmp_path / "out")
    assert report["summary"]["gate_status"] == "Warning"
    assert any(item["type"] == "material_precision_drop" for item in report["warnings"])


def test_scanner_only_triage_growth_produces_warning(tmp_path):
    manifest, policy = _write_trend_inputs(tmp_path, _portfolio_report(scanner_only_findings_count=10), _portfolio_report(scanner_only_findings_count=20))
    report = compare_trend(manifest, policy, tmp_path / "out")
    assert report["summary"]["gate_status"] == "Warning"
    assert any(item["type"] == "scanner_only_triage_growth" for item in report["warnings"])


def test_domain_level_regression_is_detected(tmp_path):
    manifest, policy = _write_trend_inputs(tmp_path, _portfolio_report(domain_security_recall=0.9), _portfolio_report(domain_security_recall=0.7))
    report = compare_trend(manifest, policy, tmp_path / "out")
    assert any(item["type"] == "domain_regression" for item in report["warnings"])
    assert any(item["domain"] == "Security" and item["delta"] == -0.2 for item in report["by_domain_deltas"])


def test_rule_family_regression_is_detected(tmp_path):
    manifest, policy = _write_trend_inputs(tmp_path, _portfolio_report(rule_sec_recall=0.9), _portfolio_report(rule_sec_recall=0.7))
    report = compare_trend(manifest, policy, tmp_path / "out")
    assert any(item["type"] == "rule_family_regression" for item in report["warnings"])
    assert any(item["rule_family"] == "SEC" and item["delta"] == -0.2 for item in report["by_rule_family_deltas"])


def test_cli_generates_validation_trend_report(tmp_path):
    manifest, policy = _write_trend_inputs(tmp_path, _portfolio_report(), _portfolio_report())
    runner = CliRunner()
    result = runner.invoke(app, ["validate-trend", "--manifest", str(manifest), "--gate-policy", str(policy), "--output", str(tmp_path / "trend-out")])
    assert result.exit_code == 0
    report_path = tmp_path / "trend-out" / "validation-trend-report.json"
    assert report_path.exists()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["schema"] == "enterprise-whitebox-validation-trend-report"
