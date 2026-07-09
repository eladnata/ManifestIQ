from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scanner.core.evidence import write_json
from scanner.validation.matching import match_findings, scanner_blocking_findings
from scanner.validation.metrics import _safe_ratio, has_traceability, material_findings
from scanner.validation.reviewer_metrics import (
    confidence_calibration,
    load_reviewer_worksheet,
    review_preparation_acceleration,
    worksheet_false_positive_ids,
    worksheet_top_blocker_agreement,
    worksheet_valid_scanner_only_ids,
)


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _finding_summary(finding: dict[str, Any]) -> dict[str, Any]:
    return {
        "finding_id": finding.get("finding_id"),
        "rule_id": finding.get("rule_id"),
        "category": finding.get("category"),
        "severity": finding.get("severity"),
        "decision_impact": finding.get("decision_impact"),
        "title": finding.get("title"),
        "file_path": finding.get("file_path"),
    }


def _human_summary(finding: dict[str, Any]) -> dict[str, Any]:
    return {
        "human_finding_id": finding.get("human_finding_id"),
        "rule_id": finding.get("rule_id"),
        "domain": finding.get("domain"),
        "severity": finding.get("severity"),
        "decision_impact": finding.get("decision_impact"),
        "title": finding.get("title"),
        "file_path": finding.get("file_path"),
        "expected_scanner_detectable": finding.get("expected_scanner_detectable"),
        "materiality": finding.get("materiality"),
    }


def _top_blocker_agreement(goldset: dict[str, Any], scanner_findings: list[dict[str, Any]], worksheet: dict[str, Any] | None) -> float:
    worksheet_score = worksheet_top_blocker_agreement(worksheet)
    if worksheet_score is not None:
        return worksheet_score
    human_blockers = [
        {
            "human_finding_id": blocker.get("blocker_id"),
            "rule_id": None,
            "domain": blocker.get("domain"),
            "severity": blocker.get("severity"),
            "title": blocker.get("title"),
            "file_path": None,
            "decision_impact": blocker.get("decision_impact"),
        }
        for blocker in goldset.get("human_top_blockers", [])
    ]
    if not human_blockers:
        return 1.0
    matches = match_findings(human_blockers, scanner_blocking_findings(scanner_findings))
    return _safe_ratio(len(matches), len(human_blockers))


def compare_goldset(
    scan_output: Path | str,
    goldset_path: Path | str,
    output_dir: Path | str,
    worksheet_path: Path | str | None = None,
) -> dict[str, Any]:
    scan_output = Path(scan_output)
    goldset_path = Path(goldset_path)
    output_dir = Path(output_dir)
    worksheet = load_reviewer_worksheet(Path(worksheet_path)) if worksheet_path else None

    goldset = _read_json(goldset_path)
    scanner_findings = _read_json(scan_output / "findings.json")
    scan_summary_path = scan_output / "scan-summary.json"
    scan_summary = _read_json(scan_summary_path) if scan_summary_path.exists() else {}
    scanner_run_id = scan_summary.get("scan_id", scan_output.name)
    profile = goldset.get("profile") or scan_summary.get("profile", "unknown")

    human_findings = goldset.get("human_ground_truth_findings", [])
    detectable = [finding for finding in human_findings if finding.get("expected_scanner_detectable") is True]
    non_detectable = [finding for finding in human_findings if finding.get("expected_scanner_detectable") is not True]
    matches = match_findings(detectable, scanner_findings)
    matched_human_ids = {match["human_finding_id"] for match in matches}
    matched_scanner_ids = {match["scanner_finding_id"] for match in matches}
    missed_detectable = [finding for finding in detectable if finding.get("human_finding_id") not in matched_human_ids]

    material_scanner = material_findings(scanner_findings)
    false_positive_ids = worksheet_false_positive_ids(worksheet)
    valid_scanner_only_ids = worksheet_valid_scanner_only_ids(worksheet)
    scanner_only = [
        finding
        for finding in material_scanner
        if finding.get("finding_id") not in matched_scanner_ids
    ]
    triage_required = [
        _finding_summary(finding)
        for finding in scanner_only
        if finding.get("finding_id") not in false_positive_ids
        and finding.get("finding_id") not in valid_scanner_only_ids
    ]

    critical_detectable = [finding for finding in detectable if finding.get("severity") == "Critical"]
    missed_critical = [finding for finding in missed_detectable if finding.get("severity") == "Critical"]
    traceable_material = [finding for finding in material_scanner if has_traceability(finding)]
    matched_material = [
        match
        for match in matches
        if next((finding for finding in detectable if finding.get("human_finding_id") == match["human_finding_id"]), {}).get("materiality") == "material"
    ]

    material_precision_denominator = len(matched_material) + len(false_positive_ids)
    recommendations = []
    if missed_detectable:
        recommendations.append("Review missed detectable human findings and calibrate analyzers or rules.")
    if triage_required:
        recommendations.append("Triage scanner-only material findings before counting them as false positives.")
    if non_detectable:
        recommendations.append("Keep non-detectable human findings outside scanner recall metrics.")
    if not recommendations:
        recommendations.append("Continue gold set validation after major analyzer or ruleset changes.")

    report = {
        "schema": "enterprise-whitebox-goldset-comparison-report",
        "schema_version": "0.1",
        "repo_id": goldset.get("repo_id"),
        "profile": profile,
        "scanner_run_id": scanner_run_id,
        "summary": {
            "human_findings_count": len(human_findings),
            "scanner_findings_count": len(scanner_findings),
            "detectable_human_findings_count": len(detectable),
            "matched_findings_count": len(matches),
            "missed_detectable_findings_count": len(missed_detectable),
            "scanner_only_findings_count": len(scanner_only),
            "critical_miss_rate": _safe_ratio(len(missed_critical), len(critical_detectable)),
            "recall_detectable": _safe_ratio(len(matches), len(detectable)),
            "material_precision": _safe_ratio(len(matched_material), material_precision_denominator),
            "top_blocker_agreement": _top_blocker_agreement(goldset, scanner_findings, worksheet),
            "evidence_traceability": _safe_ratio(len(traceable_material), len(material_scanner)),
            "confidence_calibration": confidence_calibration(worksheet),
            "review_preparation_acceleration": review_preparation_acceleration(goldset, worksheet),
        },
        "matched_findings": matches,
        "missed_detectable_findings": [_human_summary(finding) for finding in missed_detectable],
        "non_detectable_human_findings": [_human_summary(finding) for finding in non_detectable],
        "scanner_only_findings": [_finding_summary(finding) for finding in scanner_only],
        "triage_required": triage_required,
        "recommendations": recommendations,
    }
    write_json(output_dir / "goldset-comparison-report.json", report)
    return report
