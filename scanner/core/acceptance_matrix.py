from __future__ import annotations

from scanner.core.gaps import CATEGORY_DOMAIN


DOMAINS = [
    "Architecture",
    "Platform",
    "Interfaces",
    "Database and Storage",
    "External Egress",
    "Security",
    "Supply Chain",
    "Data Protection",
    "SOX / Finance",
    "AI / Model Risk",
    "Operations",
    "Delivery",
    "Maintainability",
    "Governance",
]


def _status(findings: list[dict]) -> str:
    if any(f.get("decision_impact") == "Block" or f.get("severity") == "Critical" for f in findings):
        return "Blocked"
    if any(f.get("decision_impact") == "Mandatory Review" for f in findings):
        return "Mandatory Review"
    if any(f.get("decision_impact") == "Conditional" or f.get("severity") == "High" for f in findings):
        return "Conditional"
    if findings:
        return "Conditional"
    return "Passed"


def build_acceptance_matrix(findings: list[dict], gaps: list[dict], confidence_summary: dict, scoring: dict) -> dict:
    rows = []
    for domain in DOMAINS:
        domain_findings = [finding for finding in findings if CATEGORY_DOMAIN.get(finding.get("category"), "Governance") == domain]
        domain_gaps = [gap for gap in gaps if gap.get("domain") == domain]
        status = _status(domain_findings)
        if domain_gaps and status == "Passed":
            status = "Conditional"
        confidence = "High" if status == "Passed" else "Medium"
        if not domain_findings and not domain_gaps and domain in {"Interfaces", "External Egress", "Database and Storage"}:
            status = "Unknown"
            confidence = "Low"
        reason = "No material findings or gaps were identified for this domain."
        if domain_findings:
            reason = f"{len(domain_findings)} finding(s) affect this domain."
        elif domain_gaps:
            reason = f"{len(domain_gaps)} gap(s) affect this domain."
        rows.append({
            "domain": domain,
            "status": status,
            "confidence": confidence,
            "reason": reason,
            "blocking_findings": [
                finding["finding_id"]
                for finding in domain_findings
                if finding.get("decision_impact") in {"Block", "Mandatory Review"} or finding.get("severity") == "Critical"
            ],
            "related_gaps": [gap["gap_id"] for gap in domain_gaps],
            "required_remediation": sorted({item for finding in domain_findings for item in finding.get("remediation", [])}),
        })

    if scoring.get("decision") == "Not Approved" and not any(row["status"] == "Blocked" for row in rows):
        rows.append({
            "domain": "Governance",
            "status": "Blocked",
            "confidence": "High",
            "reason": "Final decision is Not Approved because a blocking gate was produced.",
            "blocking_findings": [],
            "related_gaps": [],
            "required_remediation": ["Review blocking gates in scan-summary.json."],
        })

    return {
        "schema": "enterprise-whitebox-acceptance-matrix",
        "schema_version": "0.1",
        "final_decision": scoring.get("decision"),
        "score": scoring.get("score"),
        "domains": rows,
        "confidence_summary": {
            "confidence_counts": confidence_summary.get("confidence_counts", {}),
            "low_confidence_domains": confidence_summary.get("low_confidence_domains", []),
        },
    }
