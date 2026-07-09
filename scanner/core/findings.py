from __future__ import annotations

from collections import defaultdict
import hashlib
from typing import Any

ALLOWED_CATEGORIES = {
    "AI Model Risk",
    "Architecture",
    "Security",
    "Supply Chain",
    "Configuration",
    "Documentation",
    "Governance",
    "License Risk",
    "Data Protection",
    "SOX",
    "Maintainability",
    "Operations",
    "Scan Integrity",
}
ALLOWED_CONFIDENCE = {"High", "Medium", "Low"}
ALLOWED_SEVERITY = {"Critical", "High", "Medium", "Low", "Info"}
CATEGORY_ALIASES = {
    "SOX / Finance": "SOX",
    "SOX/Finance": "SOX",
    "Operational Readiness": "Operations",
    "Scanner Reliability": "Scan Integrity",
}
DECISION_ALIASES = {
    "Blocks approval": "Block",
    "Not Approved": "Block",
}
REQUIRED_FINDING_FIELDS = {
    "finding_id",
    "rule_id",
    "baseline_rule",
    "category",
    "severity",
    "confidence",
    "title",
    "description",
    "file_path",
    "line_start",
    "line_end",
    "evidence_type",
    "evidence_snippet",
    "decision_impact",
    "owner_role",
    "requires_approval_from",
    "remediation",
    "status",
    "created_at",
    "profile",
}
DETERMINISTIC_CREATED_AT = "1970-01-01T00:00:00Z"


def normalize_category(category: Any) -> str:
    normalized = CATEGORY_ALIASES.get(str(category or "").strip(), str(category or "").strip())
    if normalized in ALLOWED_CATEGORIES:
        return normalized
    return "Scan Integrity"


def normalize_severity(severity: Any) -> str:
    normalized = str(severity or "").strip().title()
    if normalized in ALLOWED_SEVERITY:
        return normalized
    return "Medium"


def normalize_confidence(confidence: Any) -> str:
    normalized = str(confidence or "").strip().title()
    if normalized in ALLOWED_CONFIDENCE:
        return normalized
    return "Medium"


def normalize_remediation(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return [str(value)]


def _normalize_line(value: Any) -> int:
    if value in {None, ""}:
        return 0
    try:
        line = int(value)
    except (TypeError, ValueError):
        return 0
    return line if line > 0 else 0


def stable_finding_sort_key(finding: dict) -> tuple:
    return (
        finding.get("rule_id") or "",
        finding.get("category") or "",
        finding.get("severity") or "",
        finding.get("file_path") or "",
        finding.get("line_start") or 0,
        finding.get("line_end") or 0,
        finding.get("title") or "",
        finding.get("description") or "",
        finding.get("evidence_type") or "",
        finding.get("confidence") or "",
    )


def stable_finding_id(finding: dict) -> str:
    evidence = finding.get("evidence_value") or finding.get("evidence_snippet") or finding.get("title") or ""
    material = "|".join([
        str(finding.get("rule_id") or ""),
        str(finding.get("file_path") or ""),
        str(finding.get("line_start") or ""),
        str(evidence),
    ])
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:12]
    return f"{finding['rule_id']}-{digest}"


def normalize_decision(value: Any) -> str:
    normalized = str(value or "").strip()
    return DECISION_ALIASES.get(normalized, normalized or "Advisory")


def normalize_findings(findings: list[dict], rules: dict[str, dict], profile: str) -> list[dict]:
    normalized = []
    for finding in findings:
        rule_id = str(finding.get("rule_id") or "SCAN-001")
        rule = rules.get(rule_id, {})
        applies = rule.get("applies_to_profiles", ["all"])
        if "all" not in applies and profile not in applies:
            continue

        category = normalize_category(finding.get("category") or rule.get("category"))
        severity = normalize_severity(finding.get("severity") or rule.get("severity"))
        remediation = normalize_remediation(finding.get("remediation"))
        if not remediation:
            remediation = normalize_remediation(rule.get("remediation"))
        if not remediation:
            remediation = ["Review the finding, document the disposition, and re-run the scanner after remediation."]

        line_start = _normalize_line(finding.get("line_start"))
        line_end = _normalize_line(finding.get("line_end")) or line_start
        decision_impact = normalize_decision(finding.get("decision_impact") or rule.get("decision"))
        normalized.append({
            **finding,
            "finding_id": "",
            "rule_id": rule_id,
            "baseline_rule": bool(finding.get("baseline_rule", rule.get("baseline", False))),
            "category": category,
            "severity": severity,
            "title": str(finding.get("title") or rule.get("name") or "Readiness finding"),
            "description": str(finding.get("description") or rule.get("report_text") or "A readiness finding was detected."),
            "file_path": finding.get("file_path"),
            "line_start": line_start,
            "line_end": line_end,
            "evidence_type": str(finding.get("evidence_type") or "analysis"),
            "evidence_snippet": finding.get("evidence_snippet"),
            "confidence": normalize_confidence(finding.get("confidence")),
            "decision_impact": decision_impact,
            "profile": profile,
            "remediation": remediation,
            "owner_role": str(finding.get("owner_role") or rule.get("owner_role") or "Technical Owner"),
            "requires_approval_from": normalize_remediation(
                finding.get("requires_approval_from", rule.get("requires_approval_from", []))
            ),
            "status": str(finding.get("status") or "open"),
            "created_at": str(finding.get("created_at") or DETERMINISTIC_CREATED_AT),
            "score_impact": finding.get("score_impact", rule.get("score_impact", {})),
        })

    seen: defaultdict[str, int] = defaultdict(int)
    ordered = sorted(normalized, key=stable_finding_sort_key)
    for finding in ordered:
        finding_id = stable_finding_id(finding)
        seen[finding_id] += 1
        if seen[finding_id] > 1:
            finding_id = f"{finding_id}-{seen[finding_id]:02d}"
        finding["finding_id"] = finding_id
    return ordered
