from __future__ import annotations

import hashlib


CATEGORY_DOMAIN = {
    "Architecture": "Architecture",
    "Configuration": "Platform",
    "Security": "Security",
    "Supply Chain": "Supply Chain",
    "License Risk": "Supply Chain",
    "Data Protection": "Data Protection",
    "SOX": "SOX / Finance",
    "AI Model Risk": "AI / Model Risk",
    "Operations": "Operations",
    "Documentation": "Delivery",
    "Maintainability": "Maintainability",
    "Governance": "Governance",
    "Scan Integrity": "Governance",
}


ENTERPRISE_IMPACT = {
    "Architecture": "Architecture uncertainty can prevent reliable ownership, deployment, and review boundaries.",
    "Platform": "Platform gaps can make runtime behavior difficult to reproduce or operate safely.",
    "Interfaces": "Interface gaps can obscure authentication, authorization, and integration requirements.",
    "Database and Storage": "Storage gaps can affect recovery, retention, and data governance obligations.",
    "External Egress": "External egress gaps can create unreviewed data transfer and vendor risk.",
    "Security": "Security gaps can expose credentials, unsafe code paths, or exploitable behavior.",
    "Supply Chain": "Supply chain gaps can affect dependency integrity, provenance, and legal review.",
    "Data Protection": "Data protection gaps can expose sensitive or regulated information.",
    "SOX / Finance": "Finance gaps can affect control reliance and SOX review requirements.",
    "AI / Model Risk": "AI/model gaps can create hidden provider, model, data-flow, and governance risk.",
    "Operations": "Operations gaps can reduce supportability, recovery, and production readiness.",
    "Delivery": "Delivery gaps can prevent repeatable handoff, deployment, and release review.",
    "Maintainability": "Maintainability gaps can increase change risk and long-term ownership cost.",
    "Governance": "Governance gaps can prevent accountable approval and risk acceptance.",
}


def _gap_id(finding: dict) -> str:
    material = "|".join([finding.get("finding_id", ""), finding.get("rule_id", ""), finding.get("title", "")])
    return "gap-" + hashlib.sha256(material.encode("utf-8")).hexdigest()[:12]


def _evidence_missing(finding: dict) -> list[str]:
    if finding.get("evidence_type") == "missing_file":
        return [str(finding.get("evidence_snippet") or finding.get("evidence_value") or "required evidence")]
    if finding.get("evidence_type") == "rule_evaluation" and "missing_signals" in str(finding.get("evidence_snippet")):
        return [str(finding.get("evidence_snippet"))]
    title = str(finding.get("title", "")).lower()
    if "missing" in title or "no " in title:
        return [finding.get("title", "required evidence")]
    return []


def build_gaps(findings: list[dict], rule_evaluations: dict) -> list[dict]:
    gaps = []
    material_findings = [
        finding
        for finding in findings
        if finding.get("severity") in {"Critical", "High"} or finding.get("decision_impact") in {"Block", "Mandatory Review", "Conditional"}
    ]
    for finding in material_findings:
        domain = CATEGORY_DOMAIN.get(finding.get("category"), "Governance")
        evidence_detected = []
        if finding.get("file_path"):
            evidence_detected.append({
                "file_path": finding.get("file_path"),
                "line_start": finding.get("line_start"),
                "evidence_type": finding.get("evidence_type"),
            })
        gaps.append({
            "gap_id": _gap_id(finding),
            "title": finding.get("title", "Enterprise assurance gap"),
            "domain": domain,
            "severity": finding.get("severity", "Medium"),
            "confidence": finding.get("confidence", "Medium"),
            "why_this_is_a_gap": f"This finding maps to {domain} assurance expectations and requires disposition before approval.",
            "evidence_detected": evidence_detected,
            "evidence_missing": _evidence_missing(finding),
            "enterprise_impact": ENTERPRISE_IMPACT.get(domain, "The gap can affect enterprise readiness review."),
            "required_remediation": finding.get("remediation", []),
            "related_findings": [finding.get("finding_id")],
            "related_rules": [finding.get("rule_id")],
            "decision_impact": finding.get("decision_impact", "Advisory"),
        })

    for evaluation in rule_evaluations.get("evaluations", []):
        if evaluation.get("missing_signals") and not any(evaluation["rule_id"] in gap["related_rules"] for gap in gaps):
            material = evaluation["rule_id"] + "|".join(evaluation["missing_signals"])
            gaps.append({
                "gap_id": "gap-" + hashlib.sha256(material.encode("utf-8")).hexdigest()[:12],
                "title": f"Required evidence missing for {evaluation['rule_id']}",
                "domain": "Governance",
                "severity": "Medium",
                "confidence": "High",
                "why_this_is_a_gap": "The rule contract required signals that were not produced by the local analyzer pipeline.",
                "evidence_detected": [],
                "evidence_missing": evaluation["missing_signals"],
                "enterprise_impact": ENTERPRISE_IMPACT["Governance"],
                "required_remediation": ["Provide evidence that produces the required signals or adjust the rule contract."],
                "related_findings": [],
                "related_rules": [evaluation["rule_id"]],
                "decision_impact": "Conditional",
            })

    deduped = {gap["gap_id"]: gap for gap in gaps}
    return [deduped[key] for key in sorted(deduped)]
