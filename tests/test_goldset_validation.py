import json
from pathlib import Path

from scanner.core.evidence import write_json
from scanner.validation.goldset import compare_goldset
from scanner.validation.matching import match_findings


def test_goldset_schema_example_exists():
    assert Path("validation/gold_sets/schemas/goldset.schema.json").exists()
    assert Path("validation/gold_sets/examples/sample-goldset.json").exists()


def test_reviewer_worksheet_schema_example_exists():
    assert Path("validation/gold_sets/schemas/reviewer_worksheet.schema.json").exists()
    assert Path("validation/gold_sets/examples/sample-reviewer-worksheet.json").exists()


def test_comparison_report_schema_exists():
    assert Path("validation/gold_sets/schemas/comparison_report.schema.json").exists()


def test_deterministic_matching_by_rule_id():
    human = [{
        "human_finding_id": "H1",
        "domain": "Security",
        "rule_id": "SEC-001",
        "severity": "Critical",
        "title": "Hardcoded secret",
        "file_path": "app.py",
        "decision_impact": "Block",
    }]
    scanner = [{
        "finding_id": "S1",
        "category": "Security",
        "rule_id": "SEC-001",
        "severity": "Critical",
        "title": "Potential hardcoded secret detected",
        "file_path": "app.py",
        "decision_impact": "Block",
    }]
    matches = match_findings(human, scanner)
    assert matches[0]["scanner_finding_id"] == "S1"
    assert matches[0]["match_confidence"] == "High"
    assert "rule_id matched" in matches[0]["match_reasons"]


def test_matching_fallback_by_domain_severity_title_and_file_path():
    human = [{
        "human_finding_id": "H1",
        "domain": "Operations",
        "rule_id": None,
        "severity": "High",
        "title": "No monitoring evidence",
        "file_path": "README.md",
        "decision_impact": "Conditional",
    }]
    scanner = [{
        "finding_id": "S1",
        "category": "Operations",
        "rule_id": "OPS-003",
        "severity": "High",
        "title": "No monitoring evidence detected",
        "file_path": "README.md",
        "decision_impact": "Conditional",
    }]
    matches = match_findings(human, scanner)
    assert matches[0]["scanner_finding_id"] == "S1"
    assert matches[0]["match_confidence"] in {"High", "Medium"}
    assert "domain matched" in matches[0]["match_reasons"]
    assert "file_path matched" in matches[0]["match_reasons"]


def _write_scan_output(path: Path, findings: list[dict]):
    path.mkdir(parents=True)
    write_json(path / "scan-summary.json", {"scan_id": "scan-test", "profile": "enterprise"})
    write_json(path / "findings.json", findings)


def _write_goldset(path: Path):
    write_json(path, {
        "schema": "enterprise-whitebox-goldset",
        "schema_version": "0.1",
        "repo_id": "unit-goldset",
        "repo_description": "Unit test gold set",
        "profile": "enterprise",
        "review_date": "2026-07-09",
        "reviewers": [{"reviewer_id": "r1", "role": "AppSec"}],
        "human_ground_truth_findings": [
            {
                "human_finding_id": "H1",
                "domain": "Security",
                "rule_id": "SEC-001",
                "severity": "Critical",
                "title": "Hardcoded secret in source",
                "description": "Detectable by static scanner.",
                "file_path": "app.py",
                "evidence_hint": "secret assignment",
                "decision_impact": "Block",
                "materiality": "material",
                "expected_scanner_detectable": True,
            },
            {
                "human_finding_id": "H2",
                "domain": "Business Risk",
                "rule_id": None,
                "severity": "High",
                "title": "Unapproved business owner risk acceptance",
                "description": "Requires business context outside repository.",
                "file_path": None,
                "evidence_hint": None,
                "decision_impact": "Mandatory Review",
                "materiality": "material",
                "expected_scanner_detectable": False,
            },
            {
                "human_finding_id": "H3",
                "domain": "Security",
                "rule_id": "SEC-002",
                "severity": "Critical",
                "title": "Unsafe dynamic execution",
                "description": "Detectable but intentionally missed in this unit case.",
                "file_path": "app.py",
                "evidence_hint": "eval",
                "decision_impact": "Block",
                "materiality": "material",
                "expected_scanner_detectable": True,
            },
        ],
        "human_top_blockers": [
            {
                "blocker_id": "B1",
                "title": "Hardcoded secret blocks approval",
                "domain": "Security",
                "severity": "Critical",
                "decision_impact": "Block",
            }
        ],
        "required_human_reviews": ["AppSec"],
        "manual_review_time_minutes": 100,
        "notes": [],
    })


def test_goldset_metrics_exclude_non_detectable_from_recall_and_calculate_critical_miss(tmp_path):
    scan_output = tmp_path / "scan"
    goldset_path = tmp_path / "goldset.json"
    output = tmp_path / "out"
    _write_scan_output(scan_output, [{
        "finding_id": "S1",
        "rule_id": "SEC-001",
        "category": "Security",
        "severity": "Critical",
        "title": "Potential hardcoded secret detected",
        "file_path": "app.py",
        "evidence_type": "pattern_match",
        "decision_impact": "Block",
    }])
    _write_goldset(goldset_path)

    report = compare_goldset(scan_output, goldset_path, output)
    assert report["summary"]["human_findings_count"] == 3
    assert report["summary"]["detectable_human_findings_count"] == 2
    assert report["summary"]["matched_findings_count"] == 1
    assert report["summary"]["recall_detectable"] == 0.5
    assert report["summary"]["critical_miss_rate"] == 0.5
    assert len(report["non_detectable_human_findings"]) == 1


def test_scanner_only_findings_are_triage_required_not_automatic_false_positives(tmp_path):
    scan_output = tmp_path / "scan"
    goldset_path = tmp_path / "goldset.json"
    output = tmp_path / "out"
    _write_scan_output(scan_output, [
        {
            "finding_id": "S1",
            "rule_id": "SEC-001",
            "category": "Security",
            "severity": "Critical",
            "title": "Potential hardcoded secret detected",
            "file_path": "app.py",
            "evidence_type": "pattern_match",
            "decision_impact": "Block",
        },
        {
            "finding_id": "S2",
            "rule_id": "OPS-003",
            "category": "Operations",
            "severity": "High",
            "title": "No monitoring evidence detected",
            "file_path": None,
            "evidence_type": "missing_file",
            "evidence_snippet": "monitoring evidence",
            "decision_impact": "Conditional",
        },
    ])
    _write_goldset(goldset_path)

    report = compare_goldset(scan_output, goldset_path, output)
    assert any(item["finding_id"] == "S2" for item in report["scanner_only_findings"])
    assert any(item["finding_id"] == "S2" for item in report["triage_required"])
    assert report["summary"]["material_precision"] == 1.0


def test_top_blocker_agreement_calculated(tmp_path):
    scan_output = tmp_path / "scan"
    goldset_path = tmp_path / "goldset.json"
    output = tmp_path / "out"
    _write_scan_output(scan_output, [{
        "finding_id": "S1",
        "rule_id": "SEC-001",
        "category": "Security",
        "severity": "Critical",
        "title": "Potential hardcoded secret detected",
        "file_path": "app.py",
        "evidence_type": "pattern_match",
        "decision_impact": "Block",
    }])
    _write_goldset(goldset_path)
    report = compare_goldset(scan_output, goldset_path, output)
    assert report["summary"]["top_blocker_agreement"] == 1.0


def test_goldset_comparison_report_generated(tmp_path):
    scan_output = tmp_path / "scan"
    goldset_path = tmp_path / "goldset.json"
    output = tmp_path / "out"
    _write_scan_output(scan_output, [{
        "finding_id": "S1",
        "rule_id": "SEC-001",
        "category": "Security",
        "severity": "Critical",
        "title": "Potential hardcoded secret detected",
        "file_path": "app.py",
        "evidence_type": "pattern_match",
        "decision_impact": "Block",
    }])
    _write_goldset(goldset_path)
    report = compare_goldset(scan_output, goldset_path, output)
    report_path = output / "goldset-comparison-report.json"
    assert report_path.exists()
    on_disk = json.loads(report_path.read_text(encoding="utf-8"))
    assert on_disk["schema"] == "enterprise-whitebox-goldset-comparison-report"
    assert on_disk["summary"] == report["summary"]
