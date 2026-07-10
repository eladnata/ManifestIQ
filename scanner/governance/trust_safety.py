from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scanner.core.evidence import write_json


NON_CLAIMS = [
    "This trust safety review does not certify ManifestIQ.",
    "This trust safety review does not prove absence of vulnerabilities.",
    "This trust safety review does not replace expert architecture, security, legal, privacy, SOX, ITGC, or release review.",
    "This trust safety review is based only on deterministic local repository evidence available at generation time.",
    "This trust safety review does not approve a release.",
]

REQUIRED_DOMAINS = [
    "Trust Boundary",
    "Evidence Integrity",
    "Decision Semantics",
    "Failure Safety",
    "Non-Claims",
    "Local-Only Execution",
    "Raw Evidence Preservation",
    "Missing Evidence Handling",
    "Risk Acceptance Boundary",
    "Release Readiness Boundary",
    "Threat and Misuse Model",
    "Data Protection and Artifact Hygiene",
    "Secure Engineering",
    "Regulatory and Governance Alignment",
]

DOC_PATHS = {
    "README": Path("docs/internal/README.md"),
    "TRUST_SAFETY_DOCTRINE": Path("docs/internal/TRUST_SAFETY_DOCTRINE.md"),
    "EVIDENCE_INTEGRITY_STANDARD": Path("docs/internal/EVIDENCE_INTEGRITY_STANDARD.md"),
    "FAILURE_SAFETY_STANDARD": Path("docs/internal/FAILURE_SAFETY_STANDARD.md"),
    "DECISION_SEMANTICS_STANDARD": Path("docs/internal/DECISION_SEMANTICS_STANDARD.md"),
    "TRUST_BOUNDARY_AND_NON_CLAIMS": Path("docs/internal/TRUST_BOUNDARY_AND_NON_CLAIMS.md"),
    "THREAT_AND_MISUSE_MODEL": Path("docs/internal/THREAT_AND_MISUSE_MODEL.md"),
    "DATA_PROTECTION_AND_ARTIFACT_HYGIENE": Path("docs/internal/DATA_PROTECTION_AND_ARTIFACT_HYGIENE.md"),
    "SECURE_ENGINEERING_STANDARD": Path("docs/internal/SECURE_ENGINEERING_STANDARD.md"),
    "REGULATORY_AND_GOVERNANCE_ALIGNMENT": Path("docs/internal/REGULATORY_AND_GOVERNANCE_ALIGNMENT.md"),
}

FORBIDDEN_TERMS = [
    "Approved",
    "Certified",
    "Compliant",
    "Safe",
    "Production Ready",
    "SOX Approved",
    "Privacy Approved",
    "Legally Approved",
    "Fully Secure",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _domain(domain: str, refs: list[str]) -> dict[str, Any]:
    return {
        "domain": domain,
        "status": "passed",
        "evidence_references": refs,
        "findings": [],
        "required_actions": [],
    }


def _mark(domain: dict[str, Any], status: str, finding: str, action: str) -> None:
    current = domain["status"]
    ranking = {"failed": 3, "warning": 2, "unknown": 1, "passed": 0}
    if ranking[status] > ranking[current]:
        domain["status"] = status
    domain["findings"].append(finding)
    domain["required_actions"].append(action)


def _contains_all(text: str, phrases: list[str]) -> list[str]:
    normalized = _normalize_text(text)
    return [phrase for phrase in phrases if phrase.lower() not in normalized]


def _normalize_text(text: str) -> str:
    normalized = text.lower().replace("*", "").replace("`", "")
    return " ".join(normalized.split())


def _missing_groups(text: str, groups: list[tuple[str, list[str]]]) -> list[str]:
    normalized = _normalize_text(text)
    missing: list[str] = []
    for label, options in groups:
        if not any(option.lower() in normalized for option in options):
            missing.append(label)
    return missing


def _line_allows_term(line: str, term: str, section_heading: str) -> bool:
    lowered = line.lower()
    heading_lower = section_heading.lower()
    term_lower = term.lower()
    if "forbidden" in lowered or "forbidden" in heading_lower:
        return True
    if "allowed conservative language" in heading_lower:
        return True
    if "must not" in lowered or "does not" in lowered or "not " + term_lower in lowered:
        return True
    if "no artifact implied" in lowered or "must not be represented as" in lowered:
        return True
    if f"`{term}`".lower() in lowered or f'"{term}"'.lower() in lowered:
        return True
    if "quoted forbidden terms" in lowered or "non-claims" in lowered or "denied claims" in lowered:
        return True
    if term_lower == "approved" and "not approved" in lowered:
        return True
    return False


def _find_forbidden_claims(paths: list[Path]) -> list[str]:
    findings: list[str] = []
    for path in paths:
        if not path.is_file():
            continue
        current_heading = ""
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("#"):
                current_heading = stripped
            for term in FORBIDDEN_TERMS:
                pattern = r"\b" + re.escape(term.lower()) + r"\b"
                if re.search(pattern, stripped.lower()) is None:
                    continue
                if _line_allows_term(stripped, term, current_heading):
                    continue
                findings.append(f"{path.as_posix()}:{lineno} uses unsupported positive claim language: {term}")
    return findings


def _check_repo_docs(repo_root: Path, domains: dict[str, dict[str, Any]]) -> tuple[list[str], list[str], list[str]]:
    blocking_gaps: list[str] = []
    warnings: list[str] = []
    limitations: list[str] = []

    texts = {name: _read_text(repo_root / rel_path) for name, rel_path in DOC_PATHS.items()}
    paths = {name: repo_root / rel_path for name, rel_path in DOC_PATHS.items()}

    missing_docs = [name for name, path in paths.items() if not path.is_file()]
    for name in missing_docs:
        message = f"Critical doctrine document missing: {DOC_PATHS[name].as_posix()}"
        blocking_gaps.append(message)
        _mark(domains["Trust Boundary"], "failed", message, "Restore the missing doctrine document.")

    readme = texts["README"]
    if "trust_safety_doctrine.md" not in readme.lower() or "top-level doctrine" not in readme.lower():
        message = "Internal README does not identify TRUST_SAFETY_DOCTRINE.md as the top-level doctrine."
        blocking_gaps.append(message)
        _mark(domains["Trust Boundary"], "failed", message, "Update docs/internal/README.md to point to the top-level doctrine.")

    trust_boundary_missing = _missing_groups(texts["TRUST_BOUNDARY_AND_NON_CLAIMS"], [
        ("must not transmit source code", ["must not transmit source code", "must not transmit source code, evidence"]),
        ("must not perform external enrichment", ["must not perform external enrichment"]),
        ("must not emit telemetry", ["must not emit telemetry"]),
        ("must not perform silent or background network calls", ["must not perform silent or background network calls"]),
        ("dependency responsibility", ["dependency responsibility", "hold transitively through all dependencies"]),
    ])
    for phrase in trust_boundary_missing:
        message = f"Critical trust-boundary phrase missing from TRUST_BOUNDARY_AND_NON_CLAIMS.md: {phrase}"
        blocking_gaps.append(message)
        _mark(domains["Trust Boundary"], "failed", message, "Restore the missing trust-boundary requirement.")

    integrity_missing = _missing_groups(texts["EVIDENCE_INTEGRITY_STANDARD"], [
        ("content integrity value", ["content integrity value"]),
        ("every run must produce a manifest", ["every run must produce a manifest", "every run must produce a manifest recording"]),
        ("traceable", ["traceable", "traceability"]),
        ("stale", ["stale"]),
        ("corrupted", ["corrupted"]),
        ("deterministic regeneration", ["deterministic regeneration"]),
    ])
    for phrase in integrity_missing:
        message = f"Critical evidence-integrity phrase missing from EVIDENCE_INTEGRITY_STANDARD.md: {phrase}"
        blocking_gaps.append(message)
        _mark(domains["Evidence Integrity"], "failed", message, "Restore the missing evidence-integrity requirement.")

    decision_missing = _missing_groups(texts["DECISION_SEMANTICS_STANDARD"], [
        ("raw scanner decision", ["raw scanner decision"]),
        ("ready for review is not approval", ["ready for review is not approval", "ready for review must not be treated as approval"]),
        ("risk acceptance is not remediation or approval", ["risk acceptance is not remediation or approval", "exceptions are not remediation", "risk acceptance must not be treated as remediation or approval"]),
        ("release readiness is not release approval", ["release readiness is not release approval"]),
        ("status laundering", ["status laundering"]),
        ("exception misuse", ["exception misuse", "exception abuse"]),
    ])
    for phrase in decision_missing:
        message = f"Critical decision-semantics phrase missing from DECISION_SEMANTICS_STANDARD.md: {phrase}"
        blocking_gaps.append(message)
        _mark(domains["Decision Semantics"], "failed", message, "Restore the missing decision-semantics requirement.")

    threat_text = texts["THREAT_AND_MISUSE_MODEL"]
    threat_missing = _contains_all(threat_text, [
        "a1",
        "a2",
        "a3",
        "a4",
        "a5",
        "a6",
        "m1",
        "m2",
        "m3",
        "m4",
        "m5",
        "m6",
        "m7",
    ])
    for phrase in threat_missing:
        message = f"Critical threat-model item missing from THREAT_AND_MISUSE_MODEL.md: {phrase.upper()}"
        blocking_gaps.append(message)
        _mark(domains["Threat and Misuse Model"], "failed", message, "Restore the missing adversary or misuse scenario.")

    data_missing = _missing_groups(texts["DATA_PROTECTION_AND_ARTIFACT_HYGIENE"], [
        ("remain within the local environment", ["remain within the local environment", "all scanned source and all evidence must remain within the local environment"]),
        ("secrets, credentials", ["secrets, credentials"]),
        ("personal data", ["personal data"]),
        ("redaction", ["redaction"]),
        ("sensitivity classification", ["sensitivity classification"]),
        ("must not imply", ["must not imply", "must not be represented as safe to distribute"]),
    ])
    for phrase in data_missing:
        message = f"Critical data-protection phrase missing from DATA_PROTECTION_AND_ARTIFACT_HYGIENE.md: {phrase}"
        blocking_gaps.append(message)
        _mark(domains["Data Protection and Artifact Hygiene"], "failed", message, "Restore the missing data-protection requirement.")

    engineering_missing = _missing_groups(texts["SECURE_ENGINEERING_STANDARD"], [
        ("dependencies must be minimal", ["dependencies must be minimal", "manifestiq's dependencies must be minimal"]),
        ("secure defaults", ["secure defaults"]),
        ("must not depend on any component that introduces ai inference", ["must not depend on any component that introduces ai inference"]),
        ("no-transmission, no-telemetry", ["no-transmission, no-telemetry"]),
        ("test coverage", ["test coverage"]),
    ])
    for phrase in engineering_missing:
        message = f"Critical secure-engineering phrase missing from SECURE_ENGINEERING_STANDARD.md: {phrase}"
        blocking_gaps.append(message)
        _mark(domains["Secure Engineering"], "failed", message, "Restore the missing secure-engineering requirement.")

    regulatory_missing = _missing_groups(texts["REGULATORY_AND_GOVERNANCE_ALIGNMENT"], [
        ("asdlc / secure sdlc", ["asdlc / secure sdlc"]),
        ("sox / itgc", ["sox / itgc"]),
        ("privacy / legal", ["privacy / legal"]),
        ("release governance", ["release governance"]),
        ("must not claim certification", ["must not claim certification", "without claiming compliance, certification, or approval", "manifestiq must not claim certification"]),
    ])
    for phrase in regulatory_missing:
        message = f"Critical governance-alignment phrase missing from REGULATORY_AND_GOVERNANCE_ALIGNMENT.md: {phrase}"
        blocking_gaps.append(message)
        _mark(domains["Regulatory and Governance Alignment"], "failed", message, "Restore the missing governance-alignment requirement.")

    non_claim_docs = [
        texts["TRUST_SAFETY_DOCTRINE"],
        texts["TRUST_BOUNDARY_AND_NON_CLAIMS"],
        texts["REGULATORY_AND_GOVERNANCE_ALIGNMENT"],
    ]
    if not any("must not claim" in _normalize_text(text) or "does not approve a release" in _normalize_text(text) or "must not claim, imply, or state as a positive fact" in _normalize_text(text) for text in non_claim_docs):
        message = "Internal doctrine does not state non-claims explicitly."
        blocking_gaps.append(message)
        _mark(domains["Non-Claims"], "failed", message, "Add explicit non-claims to the internal doctrine set.")

    forbidden_hits = _find_forbidden_claims([paths[name] for name in DOC_PATHS])
    for hit in forbidden_hits:
        blocking_gaps.append(hit)
        _mark(domains["Non-Claims"], "failed", hit, "Remove unsupported positive claim language or reframe it as a denial or forbidden-term example.")

    raw_evidence_checks = _missing_groups(texts["EVIDENCE_INTEGRITY_STANDARD"], [
        ("must not hide, suppress, delete, downgrade, or mutate raw findings", ["must not hide, suppress, delete, downgrade, or mutate raw findings"]),
        ("raw findings must be retained verbatim", ["raw findings must be retained verbatim"]),
    ])
    for phrase in raw_evidence_checks:
        message = f"Critical raw-evidence preservation phrase missing from EVIDENCE_INTEGRITY_STANDARD.md: {phrase}"
        blocking_gaps.append(message)
        _mark(domains["Raw Evidence Preservation"], "failed", message, "Restore raw-evidence preservation language.")

    for phrase in _missing_groups(texts["EVIDENCE_INTEGRITY_STANDARD"], [
        ("missing evidence must be an explicit", ["missing evidence must be an explicit", "missing evidence must be an explicit, first-class finding or limitation"]),
        ("must not present missing evidence as acceptable", ["must not present missing evidence as acceptable"]),
    ]):
        message = f"Critical missing-evidence phrase missing from EVIDENCE_INTEGRITY_STANDARD.md: {phrase}"
        blocking_gaps.append(message)
        _mark(domains["Missing Evidence Handling"], "failed", message, "Restore missing-evidence handling language.")

    for phrase in _missing_groups(texts["DECISION_SEMANTICS_STANDARD"], [
        ("risk acceptance", ["risk acceptance"]),
        ("not remediation or approval", ["not remediation or approval", "exceptions are not remediation"]),
    ]):
        message = f"Critical risk-acceptance boundary phrase missing from DECISION_SEMANTICS_STANDARD.md: {phrase}"
        blocking_gaps.append(message)
        _mark(domains["Risk Acceptance Boundary"], "failed", message, "Restore risk-acceptance boundary language.")

    for phrase in _contains_all(texts["DECISION_SEMANTICS_STANDARD"], ["ready for review", "release readiness is not release approval"]):
        message = f"Critical release-readiness boundary phrase missing from DECISION_SEMANTICS_STANDARD.md: {phrase}"
        blocking_gaps.append(message)
        _mark(domains["Release Readiness Boundary"], "failed", message, "Restore release-readiness boundary language.")

    for phrase in _contains_all(texts["FAILURE_SAFETY_STANDARD"], ["fail closed, never fail open"]):
        message = f"Critical failure-safety phrase missing from FAILURE_SAFETY_STANDARD.md: {phrase}"
        blocking_gaps.append(message)
        _mark(domains["Failure Safety"], "failed", message, "Restore the fail-closed rule.")

    for phrase in _contains_all(texts["TRUST_SAFETY_DOCTRINE"], ["local-first", "deterministic", "non-ai", "non-cloud"]):
        message = f"Critical local-only execution phrase missing from TRUST_SAFETY_DOCTRINE.md: {phrase}"
        blocking_gaps.append(message)
        _mark(domains["Local-Only Execution"], "failed", message, "Restore the local-only execution doctrine.")

    if not texts["FAILURE_SAFETY_STANDARD"]:
        limitations.append("Failure-safety doctrine could not be evaluated because its source document is missing.")

    return blocking_gaps, warnings, limitations


def _check_evidence_package(evidence_package: Path, domains: dict[str, dict[str, Any]]) -> tuple[list[str], list[str], list[str]]:
    blocking_gaps: list[str] = []
    warnings: list[str] = []
    limitations: list[str] = []

    manifest_path = evidence_package / "manifest.json"
    manifest = _read_json(manifest_path)
    if not manifest_path.is_file():
        warnings.append("Evidence package manifest.json is missing.")
        _mark(domains["Evidence Integrity"], "warning", "Evidence package manifest.json is missing.", "Provide a manifest.json for the evidence package.")
        return blocking_gaps, warnings, limitations

    files = manifest.get("files")
    if not isinstance(files, list):
        warnings.append("Evidence package manifest.json does not expose a files list.")
        _mark(domains["Evidence Integrity"], "warning", "Evidence package manifest.json does not expose a files list.", "Use the existing manifest format with explicit files entries.")
        return blocking_gaps, warnings, limitations

    for item in files:
        if not isinstance(item, dict):
            continue
        rel_path = str(item.get("path", ""))
        if not rel_path:
            warnings.append("Manifest entry missing path.")
            _mark(domains["Evidence Integrity"], "warning", "Manifest entry missing path.", "Record a path for every manifest entry.")
            continue
        target = evidence_package / rel_path
        if not target.is_file():
            message = f"Manifest entry refers to missing local file: {rel_path}"
            blocking_gaps.append(message)
            _mark(domains["Evidence Integrity"], "failed", message, "Restore or regenerate the missing artifact.")
        if "sha256" not in item:
            warning = f"Manifest entry missing hash field for artifact: {rel_path}"
            warnings.append(warning)
            _mark(domains["Evidence Integrity"], "warning", warning, "Add hash values when the manifest format supports them.")

    decision_packet = _read_json(evidence_package / "decision-packet.json")
    if decision_packet is None:
        warnings.append("Decision packet missing from evidence package.")
        _mark(domains["Decision Semantics"], "warning", "Decision packet missing from evidence package.", "Provide decision-packet.json for evidence-package trust checks.")
    else:
        for field in ["raw_decision", "raw_score"]:
            if field not in decision_packet:
                message = f"Decision packet does not preserve {field}."
                blocking_gaps.append(message)
                _mark(domains["Decision Semantics"], "failed", message, "Preserve raw_decision and raw_score in decision-packet.json.")

    risk_review = _read_json(evidence_package / "risk-acceptance-review.json")
    if risk_review is not None:
        for field in ["raw_decision", "raw_score"]:
            if field not in risk_review:
                message = f"Risk acceptance review does not preserve {field}."
                blocking_gaps.append(message)
                _mark(domains["Risk Acceptance Boundary"], "failed", message, "Preserve raw_decision and raw_score in risk-acceptance-review.json.")

    release_candidate = _read_json(evidence_package / "release-candidate-summary.json")
    if release_candidate is not None:
        non_claims = release_candidate.get("non_claims", [])
        if not isinstance(non_claims, list) or not any("does not approve a release" in str(item).lower() for item in non_claims):
            message = "Release candidate summary does not state that it does not approve a release."
            blocking_gaps.append(message)
            _mark(domains["Release Readiness Boundary"], "failed", message, "Preserve explicit non-approval language in release-candidate-summary.json.")

    return blocking_gaps, warnings, limitations


def render_trust_safety_markdown(review: dict[str, Any]) -> str:
    lines = [
        "# ManifestIQ Trust Safety Review",
        "",
        f"- Review status: {review['review_status']}",
        "",
        "## Domains",
    ]
    lines.extend(f"- {domain['domain']}: {domain['status']}" for domain in review["domains"])
    lines.extend(["", "## Blocking Gaps"])
    lines.extend(f"- {item}" for item in review["blocking_gaps"] or ["None."])
    lines.extend(["", "## Warnings"])
    lines.extend(f"- {item}" for item in review["warnings"] or ["None."])
    lines.extend(["", "## Non-Claims"])
    lines.extend(f"- {item}" for item in review["non_claims"])
    lines.append("")
    return "\n".join(lines)


def build_trust_safety_review(repo_root: Path | str, evidence_package: Path | str | None = None) -> dict[str, Any]:
    root = Path(repo_root)
    domain_map = {
        "Trust Boundary": _domain("Trust Boundary", [str(DOC_PATHS["TRUST_BOUNDARY_AND_NON_CLAIMS"].as_posix())]),
        "Evidence Integrity": _domain("Evidence Integrity", [str(DOC_PATHS["EVIDENCE_INTEGRITY_STANDARD"].as_posix())]),
        "Decision Semantics": _domain("Decision Semantics", [str(DOC_PATHS["DECISION_SEMANTICS_STANDARD"].as_posix())]),
        "Failure Safety": _domain("Failure Safety", [str(DOC_PATHS["FAILURE_SAFETY_STANDARD"].as_posix())]),
        "Non-Claims": _domain("Non-Claims", [str(DOC_PATHS["TRUST_BOUNDARY_AND_NON_CLAIMS"].as_posix())]),
        "Local-Only Execution": _domain("Local-Only Execution", [str(DOC_PATHS["TRUST_SAFETY_DOCTRINE"].as_posix()), str(DOC_PATHS["TRUST_BOUNDARY_AND_NON_CLAIMS"].as_posix())]),
        "Raw Evidence Preservation": _domain("Raw Evidence Preservation", [str(DOC_PATHS["EVIDENCE_INTEGRITY_STANDARD"].as_posix())]),
        "Missing Evidence Handling": _domain("Missing Evidence Handling", [str(DOC_PATHS["EVIDENCE_INTEGRITY_STANDARD"].as_posix()), str(DOC_PATHS["FAILURE_SAFETY_STANDARD"].as_posix())]),
        "Risk Acceptance Boundary": _domain("Risk Acceptance Boundary", [str(DOC_PATHS["DECISION_SEMANTICS_STANDARD"].as_posix())]),
        "Release Readiness Boundary": _domain("Release Readiness Boundary", [str(DOC_PATHS["DECISION_SEMANTICS_STANDARD"].as_posix()), str(DOC_PATHS["REGULATORY_AND_GOVERNANCE_ALIGNMENT"].as_posix())]),
        "Threat and Misuse Model": _domain("Threat and Misuse Model", [str(DOC_PATHS["THREAT_AND_MISUSE_MODEL"].as_posix())]),
        "Data Protection and Artifact Hygiene": _domain("Data Protection and Artifact Hygiene", [str(DOC_PATHS["DATA_PROTECTION_AND_ARTIFACT_HYGIENE"].as_posix())]),
        "Secure Engineering": _domain("Secure Engineering", [str(DOC_PATHS["SECURE_ENGINEERING_STANDARD"].as_posix())]),
        "Regulatory and Governance Alignment": _domain("Regulatory and Governance Alignment", [str(DOC_PATHS["REGULATORY_AND_GOVERNANCE_ALIGNMENT"].as_posix())]),
    }

    blocking_gaps, warnings, limitations = _check_repo_docs(root, domain_map)
    if evidence_package is not None:
        e_blocking, e_warnings, e_limitations = _check_evidence_package(Path(evidence_package), domain_map)
        blocking_gaps.extend(e_blocking)
        warnings.extend(e_warnings)
        limitations.extend(e_limitations)

    domains = [domain_map[name] for name in REQUIRED_DOMAINS]
    if blocking_gaps:
        review_status = "Failed"
    elif warnings:
        review_status = "Warning"
    elif all(domain["status"] == "passed" for domain in domains):
        review_status = "Passed"
    else:
        review_status = "Not Evaluated"

    return {
        "schema": "manifestiq-trust-safety-review",
        "schema_version": "0.1",
        "generated_at": _now_iso(),
        "review_status": review_status,
        "domains": domains,
        "blocking_gaps": sorted(set(blocking_gaps)),
        "warnings": sorted(set(warnings)),
        "limitations": sorted(set(limitations)),
        "non_claims": NON_CLAIMS,
    }


def collect_trust_safety_review(
    *,
    repo_root: Path | str,
    output_dir: Path | str,
    evidence_package: Path | str | None = None,
) -> dict[str, Any]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    review = build_trust_safety_review(repo_root=repo_root, evidence_package=evidence_package)
    write_json(output / "trust-safety-review.json", review)
    (output / "trust-safety-review.md").write_text(render_trust_safety_markdown(review), encoding="utf-8")
    return review
