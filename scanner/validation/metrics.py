from __future__ import annotations

from typing import Any


MATERIAL_SEVERITIES = {"Critical", "High"}
MATERIAL_IMPACTS = {"Block", "Mandatory Review"}


def _safe_ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 1.0
    return round(numerator / denominator, 4)


def expected_matches_finding(expected: dict[str, Any], finding: dict[str, Any]) -> bool:
    if expected.get("rule_id") != finding.get("rule_id"):
        return False
    if expected.get("severity") and expected.get("severity") != finding.get("severity"):
        return False
    if expected.get("decision_impact") and expected.get("decision_impact") != finding.get("decision_impact"):
        return False
    file_contains = expected.get("file_contains")
    if file_contains and file_contains not in str(finding.get("file_path") or ""):
        return False
    title_contains = expected.get("title_contains")
    if title_contains and title_contains.lower() not in str(finding.get("title") or "").lower():
        return False
    return True


def material_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        finding
        for finding in findings
        if finding.get("severity") in MATERIAL_SEVERITIES or finding.get("decision_impact") in MATERIAL_IMPACTS
    ]


def has_traceability(finding: dict[str, Any]) -> bool:
    if not finding.get("finding_id") or not finding.get("rule_id") or not finding.get("evidence_type"):
        return False
    if finding.get("evidence_type") in {"missing_file", "rule_evaluation", "metadata"}:
        return bool(finding.get("evidence_snippet") or finding.get("title"))
    return bool(finding.get("file_path") or finding.get("evidence_snippet") or finding.get("title"))


def calculate_validation_metrics(expected: list[dict[str, Any]], findings: list[dict[str, Any]], determinism_passed: bool) -> dict[str, Any]:
    detected_expected = []
    missed_expected = []
    matched_finding_ids = set()

    for item in expected:
        match = next((finding for finding in findings if expected_matches_finding(item, finding)), None)
        if match:
            detected = {**item, "detected_finding_id": match.get("finding_id")}
            detected_expected.append(detected)
            matched_finding_ids.add(match.get("finding_id"))
        else:
            missed_expected.append(item)

    material = material_findings(findings)
    unexpected = [
        {
            "finding_id": finding.get("finding_id"),
            "rule_id": finding.get("rule_id"),
            "severity": finding.get("severity"),
            "decision_impact": finding.get("decision_impact"),
            "title": finding.get("title"),
        }
        for finding in material
        if finding.get("finding_id") not in matched_finding_ids
    ]

    critical_expected = [item for item in expected if item.get("critical") or item.get("severity") == "Critical"]
    missed_critical = [
        item
        for item in missed_expected
        if item.get("critical") or item.get("severity") == "Critical"
    ]
    traceable_material = [finding for finding in material if has_traceability(finding)]
    precision = _safe_ratio(len(detected_expected), len(detected_expected) + len(unexpected))
    recall = _safe_ratio(len(detected_expected), len(expected))
    critical_miss_rate = _safe_ratio(len(missed_critical), len(critical_expected))
    evidence_traceability = _safe_ratio(len(traceable_material), len(material))

    status = "Passed"
    if missed_critical or not determinism_passed or evidence_traceability < 1.0:
        status = "Failed"

    return {
        "total_expected_findings": len(expected),
        "detected_expected_findings": len(detected_expected),
        "detected_expected": detected_expected,
        "missed_expected_findings": missed_expected,
        "unexpected_findings": unexpected,
        "precision": precision,
        "recall": recall,
        "critical_miss_rate": critical_miss_rate,
        "evidence_traceability": evidence_traceability,
        "determinism_passed": determinism_passed,
        "status": status,
    }

