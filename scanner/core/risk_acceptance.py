from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

from scanner.core.evidence import build_manifest, write_json
from scanner.core.gaps import CATEGORY_DOMAIN


NON_CLAIMS = [
    "Risk acceptance coverage does not grant production approval by itself.",
    "Risk acceptance coverage does not change raw findings, raw score, or raw scanner decision.",
    "Risk acceptance coverage does not certify compliance or replace CISO, CTO, AppSec, ITGC, SOX, Legal, Privacy, or Security review.",
]

MATERIAL_SEVERITIES = {"Critical", "High"}
MATERIAL_IMPACTS = {"Block", "Mandatory Review"}
NON_APPROVED_STATUSES = {"draft", "rejected", "revoked"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    text = str(value)
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def _is_material(item: dict) -> bool:
    return item.get("severity") in MATERIAL_SEVERITIES or item.get("decision_impact") in MATERIAL_IMPACTS


def _finding_domain(finding: dict) -> str:
    return CATEGORY_DOMAIN.get(finding.get("category"), str(finding.get("category") or "Governance"))


def _source_path(summary: dict) -> str:
    metadata = summary.get("source_metadata", {})
    if isinstance(metadata, dict):
        return str(metadata.get("source_path") or metadata.get("repo_url") or "unknown")
    return "unknown"


def _list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if item]
    return []


def _scope(record: dict) -> dict:
    scope = record.get("scope", {})
    return scope if isinstance(scope, dict) else {}


def _has_scope_selector(scope: dict) -> bool:
    return any(_list(scope.get(key)) for key in ("rule_ids", "finding_ids", "gap_ids", "domains"))


def _scope_context_matches(scope: dict, summary: dict) -> bool:
    profiles = _list(scope.get("profiles"))
    source_paths = _list(scope.get("source_paths"))
    if profiles and str(summary.get("profile", "unknown")) not in profiles:
        return False
    if source_paths:
        current = _source_path(summary).replace("\\", "/").rstrip("/")
        normalized_scope = [item.replace("\\", "/").rstrip("/") for item in source_paths]
        if not any(current == item or current.endswith("/" + item) for item in normalized_scope):
            return False
    return True


def _finding_matches(record_scope: dict, finding: dict) -> bool:
    rule_ids = set(_list(record_scope.get("rule_ids")))
    finding_ids = set(_list(record_scope.get("finding_ids")))
    domains = set(_list(record_scope.get("domains")))
    finding_domain = _finding_domain(finding)
    candidates = {str(finding.get("category") or ""), finding_domain}
    return (
        str(finding.get("finding_id")) in finding_ids
        or str(finding.get("rule_id")) in rule_ids
        or bool(candidates & domains)
    )


def _gap_matches(record_scope: dict, gap: dict) -> bool:
    rule_ids = set(_list(record_scope.get("rule_ids")))
    gap_ids = set(_list(record_scope.get("gap_ids")))
    domains = set(_list(record_scope.get("domains")))
    return (
        str(gap.get("gap_id")) in gap_ids
        or bool(rule_ids & set(_list(gap.get("related_rules"))))
        or str(gap.get("domain") or "") in domains
    )


def _role_errors(record: dict, findings: list[dict], gaps: list[dict]) -> list[str]:
    role = str(record.get("approved_role") or "")
    errors = []
    for finding in findings:
        category = str(finding.get("category") or "")
        domain = _finding_domain(finding)
        rule_id = str(finding.get("rule_id") or "")
        if category == "Security" and finding.get("severity") == "Critical" and role not in {"CISO", "AppSec"}:
            errors.append("critical security findings require CISO or AppSec role")
        if (category == "SOX" or domain == "SOX / Finance" or rule_id.startswith("SOX-")) and role not in {"ITGC / SOX Reviewer", "CISO"}:
            errors.append("SOX/Finance findings require ITGC / SOX Reviewer or CISO")
        if (category == "AI Model Risk" or domain == "AI / Model Risk" or rule_id.startswith("AI-")) and role not in {"CISO", "Data Governance", "Security Architecture"}:
            errors.append("AI/model risk findings require CISO, Data Governance, or Security Architecture")
        if (category == "License Risk" or rule_id.startswith("LIC-")) and role not in {"Legal / Open Source Review", "CISO"}:
            errors.append("license findings require Legal / Open Source Review or CISO")
        if (category == "Architecture" or rule_id.startswith("ARCH-")) and role not in {"CTO / Enterprise Architecture", "Security Architecture"}:
            errors.append("architecture findings require CTO / Enterprise Architecture or Security Architecture")
        if (category == "Operations" or rule_id.startswith("OPS-")) and role not in {"DevOps / SRE", "Release Manager / Control Owner"}:
            errors.append("operational readiness findings require DevOps / SRE or Release Manager / Control Owner")
    for gap in gaps:
        domain = str(gap.get("domain") or "")
        if domain == "SOX / Finance" and role not in {"ITGC / SOX Reviewer", "CISO"}:
            errors.append("SOX/Finance findings require ITGC / SOX Reviewer or CISO")
        if domain == "AI / Model Risk" and role not in {"CISO", "Data Governance", "Security Architecture"}:
            errors.append("AI/model risk findings require CISO, Data Governance, or Security Architecture")
        if domain == "Architecture" and role not in {"CTO / Enterprise Architecture", "Security Architecture"}:
            errors.append("architecture findings require CTO / Enterprise Architecture or Security Architecture")
        if domain == "Operations" and role not in {"DevOps / SRE", "Release Manager / Control Owner"}:
            errors.append("operational readiness findings require DevOps / SRE or Release Manager / Control Owner")
    return sorted(set(errors))


def _base_normalized_record(record: dict) -> dict:
    return {
        "exception_id": str(record.get("exception_id") or ""),
        "status": "invalid",
        "title": str(record.get("title") or ""),
        "covered_rule_ids": [],
        "covered_finding_ids": [],
        "covered_gap_ids": [],
        "covered_domains": [],
        "validation_errors": [],
        "validation_warnings": [],
        "expires_at": record.get("expires_at"),
        "approved_role": record.get("approved_role"),
        "owner": record.get("owner"),
    }


def _validate_record(
    record: dict,
    *,
    summary: dict,
    material_findings: list[dict],
    material_gaps: list[dict],
    now: datetime,
) -> dict:
    normalized = _base_normalized_record(record)
    status = str(record.get("status") or "").lower()
    scope = _scope(record)
    errors: list[str] = []

    for field in ("exception_id", "reason", "risk_statement", "owner", "approved_by", "approved_role", "approved_at", "expires_at"):
        if not record.get(field):
            errors.append(f"{field} is required")
    if not _has_scope_selector(scope):
        errors.append("at least one scope selector is required")

    expires_at = _parse_datetime(record.get("expires_at"))
    if record.get("expires_at") and expires_at is None:
        errors.append("expires_at must be a valid ISO-8601 datetime")
    if status != "approved":
        normalized["status"] = status if status in NON_APPROVED_STATUSES or status == "expired" else "invalid"
        normalized["validation_errors"] = sorted(errors)
        return normalized
    if expires_at and expires_at < now:
        normalized["status"] = "expired"
        normalized["validation_errors"] = sorted(errors)
        return normalized
    if errors:
        normalized["status"] = "invalid"
        normalized["validation_errors"] = sorted(errors)
        return normalized
    if not _scope_context_matches(scope, summary):
        normalized["status"] = "scope_mismatch"
        return normalized

    matched_findings = [finding for finding in material_findings if _finding_matches(scope, finding)]
    matched_gaps = [gap for gap in material_gaps if _gap_matches(scope, gap)]
    if not matched_findings and not matched_gaps:
        normalized["status"] = "scope_mismatch"
        return normalized

    role_errors = _role_errors(record, matched_findings, matched_gaps)
    if role_errors:
        normalized["status"] = "invalid"
        normalized["validation_errors"] = role_errors
        return normalized

    normalized["status"] = "valid"
    normalized["covered_rule_ids"] = sorted({
        str(finding.get("rule_id"))
        for finding in matched_findings
        if finding.get("rule_id")
    } | {
        rule_id
        for gap in matched_gaps
        for rule_id in _list(gap.get("related_rules"))
    })
    normalized["covered_finding_ids"] = sorted(str(finding.get("finding_id")) for finding in matched_findings if finding.get("finding_id"))
    normalized["covered_gap_ids"] = sorted(str(gap.get("gap_id")) for gap in matched_gaps if gap.get("gap_id"))
    normalized["covered_domains"] = sorted({
        _finding_domain(finding)
        for finding in matched_findings
    } | {
        str(gap.get("domain"))
        for gap in matched_gaps
        if gap.get("domain")
    })
    return normalized


def _review_status(
    *,
    register_provided: bool,
    invalid_or_expired_count: int,
    covered_total: int,
    uncovered_total: int,
    material_total: int,
) -> str:
    if not register_provided:
        return "No Exceptions Provided"
    if invalid_or_expired_count > 0:
        return "Expired Or Invalid Exceptions Present"
    if covered_total == 0:
        return "No Valid Coverage"
    if uncovered_total > 0:
        return "Partially Covered"
    if material_total > 0 and uncovered_total == 0:
        return "Covered With Active Exceptions"
    return "No Valid Coverage"


def build_risk_acceptance_review(
    *,
    exception_register: dict | None,
    summary: dict,
    findings: list[dict],
    gaps: list[dict],
    now: datetime | None = None,
) -> tuple[dict, dict]:
    now = now or datetime.now(timezone.utc)
    material_findings = [finding for finding in findings if _is_material(finding)]
    material_gaps = [gap for gap in gaps if _is_material(gap)]
    records = exception_register.get("records", []) if exception_register else []
    if not isinstance(records, list):
        records = []

    normalized_records = [
        _validate_record(record if isinstance(record, dict) else {}, summary=summary, material_findings=material_findings, material_gaps=material_gaps, now=now)
        for record in records
    ]
    valid_records = [record for record in normalized_records if record["status"] == "valid"]
    covered_finding_ids = {finding_id for record in valid_records for finding_id in record["covered_finding_ids"]}
    covered_gap_ids = {gap_id for record in valid_records for gap_id in record["covered_gap_ids"]}
    covered_findings = [finding for finding in material_findings if finding.get("finding_id") in covered_finding_ids]
    uncovered_findings = [finding for finding in material_findings if finding.get("finding_id") not in covered_finding_ids]
    covered_gaps = [gap for gap in material_gaps if gap.get("gap_id") in covered_gap_ids]
    uncovered_gaps = [gap for gap in material_gaps if gap.get("gap_id") not in covered_gap_ids]
    expired_records = [record for record in normalized_records if record["status"] == "expired"]
    invalid_records = [
        record
        for record in normalized_records
        if record["status"] in {"invalid", "draft", "rejected", "revoked"}
    ]
    expired_or_invalid = expired_records + invalid_records
    uncovered_total = len(uncovered_findings) + len(uncovered_gaps)
    required_follow_up = []
    if uncovered_findings:
        required_follow_up.append("Disposition uncovered material findings before relying on risk acceptance coverage.")
    if uncovered_gaps:
        required_follow_up.append("Disposition uncovered material gaps before relying on risk acceptance coverage.")
    if expired_or_invalid:
        required_follow_up.append("Resolve expired, invalid, draft, rejected, or revoked exception records.")

    normalized = {
        "schema": "manifestiq-normalized-exception-register",
        "schema_version": "0.1",
        "register_id": str((exception_register or {}).get("register_id") or "none"),
        "records": normalized_records,
    }
    review = {
        "schema": "manifestiq-risk-acceptance-review",
        "schema_version": "0.1",
        "generated_at": _now_iso(),
        "source": {
            "profile": str(summary.get("profile", "unknown")),
            "source_path": _source_path(summary),
            "scan_id": summary.get("scan_id"),
        },
        "raw_decision": str(summary.get("decision", "Unknown")),
        "raw_score": int(summary.get("score", 0)),
        "coverage_summary": {
            "material_findings_total": len(material_findings),
            "material_findings_covered": len(covered_findings),
            "material_findings_uncovered": len(uncovered_findings),
            "material_gaps_total": len(material_gaps),
            "material_gaps_covered": len(covered_gaps),
            "material_gaps_uncovered": len(uncovered_gaps),
            "expired_exceptions": len(expired_records),
            "invalid_exceptions": len(invalid_records),
        },
        "review_status": _review_status(
            register_provided=exception_register is not None,
            invalid_or_expired_count=len(expired_or_invalid),
            covered_total=len(covered_findings) + len(covered_gaps),
            uncovered_total=uncovered_total,
            material_total=len(material_findings) + len(material_gaps),
        ),
        "covered_findings": covered_findings,
        "uncovered_findings": uncovered_findings,
        "covered_gaps": covered_gaps,
        "uncovered_gaps": uncovered_gaps,
        "expired_or_invalid_exceptions": expired_or_invalid,
        "required_follow_up": required_follow_up,
        "non_claims": NON_CLAIMS,
    }
    return normalized, review


def load_exception_register(path: Path | str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def render_risk_acceptance_markdown(review: dict) -> str:
    summary = review.get("coverage_summary", {})
    lines = [
        "# ManifestIQ Risk Acceptance Review",
        "",
        "## Review Status",
        f"- Status: {review.get('review_status')}",
        f"- Raw decision: {review.get('raw_decision')}",
        f"- Raw score: {review.get('raw_score')}",
        "",
        "## Coverage Summary",
        f"- Material findings covered: {summary.get('material_findings_covered', 0)}",
        f"- Material findings uncovered: {summary.get('material_findings_uncovered', 0)}",
        f"- Material gaps covered: {summary.get('material_gaps_covered', 0)}",
        f"- Material gaps uncovered: {summary.get('material_gaps_uncovered', 0)}",
        f"- Expired exceptions: {summary.get('expired_exceptions', 0)}",
        f"- Invalid exceptions: {summary.get('invalid_exceptions', 0)}",
        "",
        "## Required Follow-Up",
    ]
    lines.extend(f"- {item}" for item in review.get("required_follow_up", []) or ["No follow-up was generated by the exception review."])
    lines.extend(["", "## Non-Claims"])
    lines.extend(f"- {item}" for item in review.get("non_claims", []))
    lines.append("")
    return "\n".join(lines)


def risk_acceptance_summary(review: dict | None) -> dict | None:
    if not review:
        return None
    summary = review.get("coverage_summary", {})
    return {
        "review_status": review.get("review_status"),
        "material_findings_covered": summary.get("material_findings_covered", 0),
        "material_findings_uncovered": summary.get("material_findings_uncovered", 0),
        "material_gaps_covered": summary.get("material_gaps_covered", 0),
        "material_gaps_uncovered": summary.get("material_gaps_uncovered", 0),
        "expired_or_invalid_exceptions": [
            record.get("exception_id")
            for record in review.get("expired_or_invalid_exceptions", [])
            if record.get("exception_id")
        ],
        "non_claim": "Risk acceptance coverage does not grant production approval by itself.",
    }


def _risk_acceptance_html(review: dict) -> str:
    summary = review.get("coverage_summary", {})
    return (
        "\n  <h2>Risk Acceptance</h2>\n"
        "  <table>\n"
        f"    <tr><th>Review status</th><td>{escape(str(review.get('review_status', 'Unknown')))}</td></tr>\n"
        f"    <tr><th>Covered material findings</th><td>{summary.get('material_findings_covered', 0)}</td></tr>\n"
        f"    <tr><th>Uncovered material findings</th><td>{summary.get('material_findings_uncovered', 0)}</td></tr>\n"
        f"    <tr><th>Covered material gaps</th><td>{summary.get('material_gaps_covered', 0)}</td></tr>\n"
        f"    <tr><th>Uncovered material gaps</th><td>{summary.get('material_gaps_uncovered', 0)}</td></tr>\n"
        f"    <tr><th>Expired/invalid exception count</th><td>{len(review.get('expired_or_invalid_exceptions', []))}</td></tr>\n"
        "    <tr><th>Review artifact</th><td><code>risk-acceptance-review.json</code></td></tr>\n"
        "  </table>\n"
    )


def inject_risk_acceptance_into_report(report_path: Path, review: dict) -> None:
    html = report_path.read_text(encoding="utf-8")
    if "risk-acceptance-review.json" in html:
        return
    section = _risk_acceptance_html(review)
    marker = "  <h2>Blocking Gates</h2>"
    if marker in html:
        html = html.replace(marker, section + "\n" + marker, 1)
    else:
        html = html.replace("</body>", section + "</body>", 1)
    report_path.write_text(html, encoding="utf-8")


def apply_exception_register_to_evidence_package(
    evidence_package: Path | str,
    exception_register: Path | str,
    output_dir: Path | str,
) -> dict:
    evidence = Path(evidence_package)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    summary = json.loads((evidence / "scan-summary.json").read_text(encoding="utf-8"))
    findings = json.loads((evidence / "findings.json").read_text(encoding="utf-8"))
    gaps = json.loads((evidence / "gaps.json").read_text(encoding="utf-8"))
    register = load_exception_register(exception_register)
    normalized, review = build_risk_acceptance_review(exception_register=register, summary=summary, findings=findings, gaps=gaps)
    write_json(output / "exception-register-normalized.json", normalized)
    write_json(output / "risk-acceptance-review.json", review)
    (output / "risk-acceptance-review.md").write_text(render_risk_acceptance_markdown(review), encoding="utf-8")

    packet_path = output / "decision-packet.json"
    if packet_path.exists():
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        packet["risk_acceptance"] = risk_acceptance_summary(review)
        write_json(packet_path, packet)

    report_path = output / "final-report.html"
    if report_path.exists():
        inject_risk_acceptance_into_report(report_path, review)

    manifest = build_manifest(output)
    return {"normalized": normalized, "review": review, "manifest": manifest}
