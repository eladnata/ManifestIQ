from __future__ import annotations

import hashlib
from typing import Any


NON_CLAIMS = [
    "This packet does not certify compliance.",
    "This packet does not replace CISO, CTO, AppSec, Architecture, ITGC, SOX, Legal, Privacy, or Security review.",
    "This packet does not represent penetration testing completion.",
    "This packet does not grant production approval by itself.",
    "This packet is based only on deterministic local static analysis and available repository evidence.",
]

LIMITATIONS = [
    "The packet is derived from local deterministic scanner artifacts only.",
    "Unknown or missing evidence means the scanner did not find sufficient local repository evidence.",
    "The packet prepares expert review and does not assign approvals.",
]

EXCLUDED_CLAIMS = [
    "Certification of compliance",
    "SOX signoff",
    "Privacy approval",
    "Legal approval",
    "Penetration testing completion",
    "Production approval",
]

SEVERITY_RANK = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Info": 4}
IMPACT_RANK = {"Block": 0, "Mandatory Review": 1, "Conditional": 2, "Advisory": 3}
STATUS_BUCKETS = {
    "Blocked": "blocked_domains",
    "Mandatory Review": "mandatory_review_domains",
    "Conditional": "conditional_domains",
    "Accepted": "accepted_domains",
    "Insufficient Evidence": "insufficient_evidence_domains",
}


def _stable_id(prefix: str, parts: list[Any]) -> str:
    material = "|".join(str(part) for part in parts)
    return prefix + hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


def _dedupe_sorted(values: list[str]) -> list[str]:
    return sorted({value for value in values if value})


def _sort_material(item: dict) -> tuple[int, int, str, str]:
    return (
        SEVERITY_RANK.get(str(item.get("severity", "Info")), 5),
        IMPACT_RANK.get(str(item.get("decision_impact", "Advisory")), 4),
        str(item.get("rule_id") or ""),
        str(item.get("finding_id") or item.get("gap_id") or ""),
    )


def _top_risks(findings: list[dict]) -> list[dict]:
    material = [
        finding
        for finding in findings
        if finding.get("severity") in {"Critical", "High"}
        or finding.get("decision_impact") in {"Block", "Mandatory Review"}
    ]
    risks = []
    for finding in sorted(material, key=_sort_material):
        risks.append({
            "finding_id": finding.get("finding_id"),
            "rule_id": finding.get("rule_id"),
            "category": finding.get("category"),
            "severity": finding.get("severity"),
            "confidence": finding.get("confidence"),
            "title": finding.get("title"),
            "decision_impact": finding.get("decision_impact"),
            "evidence": {
                "file_path": finding.get("file_path"),
                "line_start": finding.get("line_start"),
            },
            "required_actions": finding.get("remediation", []),
        })
    return risks


def _material_gaps(gaps: list[dict]) -> list[dict]:
    material = [
        gap
        for gap in gaps
        if gap.get("severity") in {"Critical", "High"}
        or gap.get("decision_impact") in {"Block", "Mandatory Review"}
    ]
    return [
        {
            "gap_id": gap.get("gap_id"),
            "domain": gap.get("domain"),
            "severity": gap.get("severity"),
            "title": gap.get("title"),
            "decision_impact": gap.get("decision_impact"),
            "required_actions": gap.get("required_remediation", []),
            "related_findings": gap.get("related_findings", []),
            "related_rules": gap.get("related_rules", []),
        }
        for gap in sorted(material, key=_sort_material)
    ]


def _acceptance_summary(acceptance_matrix: dict) -> dict:
    summary = {
        "blocked_domains": [],
        "mandatory_review_domains": [],
        "conditional_domains": [],
        "accepted_domains": [],
        "insufficient_evidence_domains": [],
    }
    for row in acceptance_matrix.get("domains", []):
        bucket = STATUS_BUCKETS.get(row.get("status"))
        if bucket:
            summary[bucket].append(str(row.get("domain", "unknown")))
    return {key: sorted(values) for key, values in summary.items()}


def _overall_confidence(confidence_summary: dict) -> str:
    counts = confidence_summary.get("confidence_counts", {})
    if confidence_summary.get("low_confidence_domains") or counts.get("Low", 0) > 0:
        return "Low"
    if counts.get("Medium", 0) > 0:
        return "Medium"
    return "High"


def _technical_summary(system_dossier: dict, control_context: dict) -> dict:
    technical = system_dossier.get("technical_summary", {})
    return {
        "system_type": str(control_context.get("system_type") or "unknown"),
        "architecture_style": str(control_context.get("architecture_style") or "unknown"),
        "languages": sorted(technical.get("languages", {}).keys()) if isinstance(technical.get("languages"), dict) else sorted(control_context.get("languages", [])),
        "frameworks": sorted(control_context.get("frameworks", [])),
        "databases_detected": sorted(control_context.get("databases_detected", [])),
        "external_egress_detected": bool(control_context.get("external_egress_detected", False)),
        "ai_model_usage_detected": bool(control_context.get("ai_model_usage_detected", False)),
        "financial_indicators_detected": bool(control_context.get("financial_indicators_detected", False)),
        "sensitive_data_indicators_detected": bool(control_context.get("sensitive_data_indicators_detected", False)),
    }


def _reviewers(findings: list[dict], gaps: list[dict], control_context: dict) -> list[str]:
    reviewers: set[str] = set()
    for finding in findings:
        category = finding.get("category")
        rule_id = str(finding.get("rule_id", ""))
        severity = finding.get("severity")
        impact = finding.get("decision_impact")
        if severity == "Critical":
            reviewers.add("CISO")
        if category == "Security" or rule_id.startswith("SEC-"):
            reviewers.add("AppSec")
            if severity == "Critical" or impact == "Block":
                reviewers.add("CISO")
        if category == "AI Model Risk" or rule_id.startswith("AI-"):
            reviewers.update({"CISO", "Data Governance", "Security Architecture"})
        if category == "SOX" or rule_id.startswith("SOX-"):
            reviewers.add("ITGC / SOX Reviewer")
        if category == "Data Protection" or rule_id.startswith("DATA-"):
            reviewers.update({"AppSec", "Data Governance"})
        if category == "License Risk" or rule_id.startswith("LIC-"):
            reviewers.add("Legal / Open Source Review")
        if category == "Supply Chain":
            reviewers.add("Security Architecture")
        if category == "Operations" or rule_id.startswith("OPS-"):
            reviewers.add("DevOps / SRE")
        if category == "Architecture" or rule_id.startswith("ARCH-"):
            reviewers.add("CTO / Enterprise Architecture")
        if category in {"Governance", "Scan Integrity"} or rule_id.startswith("GOV-"):
            reviewers.add("Release Manager / Control Owner")

    for gap in gaps:
        domain = gap.get("domain")
        if domain == "Operations":
            reviewers.add("DevOps / SRE")
        elif domain == "Architecture":
            reviewers.add("CTO / Enterprise Architecture")
        elif domain == "Governance":
            reviewers.add("Release Manager / Control Owner")
        elif domain == "SOX / Finance":
            reviewers.add("ITGC / SOX Reviewer")
        elif domain in {"External Egress", "AI / Model Risk"}:
            reviewers.update({"Security Architecture", "Data Governance"})

    if control_context.get("external_egress_detected"):
        reviewers.update({"Security Architecture", "Data Governance"})
    if control_context.get("ai_model_usage_detected"):
        reviewers.update({"CISO", "Data Governance", "Security Architecture"})
    if control_context.get("financial_indicators_detected") or control_context.get("sox_review_required"):
        reviewers.add("ITGC / SOX Reviewer")
    if control_context.get("sensitive_data_indicators_detected") or control_context.get("data_governance_review_required"):
        reviewers.add("Data Governance")
    if control_context.get("security_architecture_review_required"):
        reviewers.add("Security Architecture")

    return sorted(reviewers)


def _required_actions(findings: list[dict], gaps: list[dict]) -> list[str]:
    actions = []
    for risk in _top_risks(findings):
        actions.extend(risk.get("required_actions", []))
    for gap in _material_gaps(gaps):
        actions.extend(gap.get("required_actions", []))
    return _dedupe_sorted([str(action) for action in actions])


def _rationale(summary: dict, findings: list[dict], gaps: list[dict], acceptance_matrix: dict, confidence_summary: dict) -> dict:
    blocking = [
        f"{gate.get('rule_id')}: {gate.get('title')}"
        for gate in summary.get("blocking_gates", [])
        if gate.get("decision_impact") == "Block" or gate.get("severity") == "Critical"
    ]
    mandatory = [
        f"{finding.get('rule_id')}: {finding.get('title')}"
        for finding in findings
        if finding.get("decision_impact") == "Mandatory Review"
    ]
    conditional = [
        f"{gap.get('gap_id')}: {gap.get('title')}"
        for gap in gaps
        if gap.get("decision_impact") == "Conditional"
    ]
    rationale = []
    if blocking:
        rationale.append(f"{len(blocking)} blocking reason(s) were identified.")
    if mandatory:
        rationale.append(f"{len(mandatory)} mandatory-review finding(s) require expert disposition.")
    material_gap_count = len(_material_gaps(gaps))
    if material_gap_count:
        rationale.append(f"{material_gap_count} material gap(s) require remediation or review.")
    blocked_domains = [
        row.get("domain")
        for row in acceptance_matrix.get("domains", [])
        if row.get("status") in {"Blocked", "Mandatory Review", "Conditional"}
    ]
    if blocked_domains:
        rationale.append("Acceptance matrix flagged review domains: " + ", ".join(sorted(str(domain) for domain in blocked_domains)) + ".")
    for limitation in confidence_summary.get("limitations", []):
        rationale.append(str(limitation))
    return {
        "rationale": rationale,
        "blocking_reasons": sorted(blocking),
        "mandatory_review_reasons": sorted(set(mandatory)),
        "conditional_reasons": sorted(set(conditional)),
    }


def _evidence_references(
    *,
    findings: list[dict],
    gaps: list[dict],
    manifest: dict | None,
) -> list[dict]:
    refs = []
    if manifest:
        for item in manifest.get("files", []):
            refs.append({
                "type": "artifact",
                "path": item.get("path"),
                "sha256": item.get("sha256"),
            })
        if manifest.get("package_sha256"):
            refs.append({"type": "manifest_hash", "sha256": manifest["package_sha256"]})
    for finding in findings:
        if finding.get("finding_id"):
            refs.append({
                "type": "finding",
                "finding_id": finding.get("finding_id"),
                "rule_id": finding.get("rule_id"),
                "file_path": finding.get("file_path"),
            })
    for gap in gaps:
        if gap.get("gap_id"):
            refs.append({
                "type": "gap",
                "gap_id": gap.get("gap_id"),
                "related_rules": gap.get("related_rules", []),
            })
    return refs


def build_decision_packet(
    *,
    summary: dict,
    findings: list[dict],
    gaps: list[dict],
    confidence_summary: dict,
    acceptance_matrix: dict,
    system_dossier: dict,
    control_context: dict,
    manifest: dict | None,
    risk_acceptance: dict | None = None,
) -> dict:
    source_metadata = summary.get("source_metadata", {})
    rationale = _rationale(summary, findings, gaps, acceptance_matrix, confidence_summary)
    packet = {
        "schema": "manifestiq-decision-packet",
        "schema_version": "0.1",
        "packet_id": _stable_id("decision-packet-", [
            summary.get("scan_id", "unknown"),
            source_metadata.get("source_path", "unknown"),
            summary.get("profile", "unknown"),
            summary.get("decision", "Unknown"),
            summary.get("score", 0),
        ]),
        "generated_at": str(summary.get("generated_at") or summary.get("scan_id") or "unknown"),
        "source": {
            "source_type": str(source_metadata.get("source_type", "unknown")),
            "source_path": str(source_metadata.get("source_path") or source_metadata.get("repo_url") or "unknown"),
            "profile": str(summary.get("profile", "unknown")),
            "scanner_version": str(summary.get("scanner_version", "unknown")),
            "ruleset_version": summary.get("ruleset_version"),
            "ruleset_sha256": summary.get("ruleset_version"),
        },
        "decision": {
            "value": str(summary.get("decision", "Unknown")),
            "score": int(summary.get("score", 0)),
            **rationale,
        },
        "executive_technical_summary": _technical_summary(system_dossier, control_context),
        "top_risks": _top_risks(findings),
        "material_gaps": _material_gaps(gaps),
        "acceptance_summary": _acceptance_summary(acceptance_matrix),
        "confidence_summary": {
            "overall_confidence": _overall_confidence(confidence_summary),
            "low_confidence_areas": sorted(confidence_summary.get("low_confidence_domains", [])),
            "limitations": confidence_summary.get("limitations", []),
        },
        "required_actions": _required_actions(findings, gaps),
        "required_reviewers": _reviewers(findings, gaps, control_context),
        "evidence_references": _evidence_references(findings=findings, gaps=gaps, manifest=manifest),
        "excluded_claims": EXCLUDED_CLAIMS,
        "limitations": _dedupe_sorted([*system_dossier.get("limitations", []), *confidence_summary.get("limitations", []), *LIMITATIONS]),
        "non_claims": NON_CLAIMS,
    }
    if risk_acceptance:
        packet["risk_acceptance"] = risk_acceptance
    return packet


def render_decision_packet_markdown(packet: dict) -> str:
    lines = [
        "# ManifestIQ Decision Packet",
        "",
        "## Decision",
        f"- Decision: {packet['decision']['value']}",
        f"- Score: {packet['decision']['score']}",
        f"- Packet ID: {packet['packet_id']}",
        "",
        "## Why This Decision",
    ]
    lines.extend(f"- {item}" for item in packet["decision"].get("rationale", []) or ["No material rationale was generated."])
    lines.extend(["", "## Top Risks"])
    lines.extend(
        f"- {risk.get('severity')} {risk.get('rule_id')}: {risk.get('title')} ({risk.get('decision_impact')})"
        for risk in packet.get("top_risks", [])
    )
    if not packet.get("top_risks"):
        lines.append("- No top risks were identified.")
    lines.extend(["", "## Material Gaps"])
    lines.extend(
        f"- {gap.get('severity')} {gap.get('gap_id')}: {gap.get('title')} ({gap.get('decision_impact')})"
        for gap in packet.get("material_gaps", [])
    )
    if not packet.get("material_gaps"):
        lines.append("- No material gaps were identified.")
    lines.extend(["", "## Acceptance Summary"])
    for key, values in packet.get("acceptance_summary", {}).items():
        lines.append(f"- {key}: {', '.join(values) if values else 'None'}")
    lines.extend(["", "## Confidence and Limitations"])
    lines.append(f"- Overall confidence: {packet['confidence_summary']['overall_confidence']}")
    lines.extend(f"- {item}" for item in packet["confidence_summary"].get("limitations", []))
    lines.extend(["", "## Required Actions"])
    lines.extend(f"- {item}" for item in packet.get("required_actions", []) or ["No required actions were generated."])
    lines.extend(["", "## Required Reviewers"])
    lines.extend(f"- {item}" for item in packet.get("required_reviewers", []) or ["No required reviewers were derived."])
    lines.extend(["", "## Evidence References"])
    for ref in packet.get("evidence_references", [])[:25]:
        label = ref.get("path") or ref.get("finding_id") or ref.get("gap_id") or ref.get("sha256")
        lines.append(f"- {ref.get('type')}: {label}")
    lines.extend(["", "## Non-Claims"])
    lines.extend(f"- {item}" for item in packet.get("non_claims", []))
    lines.append("")
    return "\n".join(lines)
