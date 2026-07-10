from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scanner.core.evidence import write_json


EXPECTED_ARTIFACTS = {
    "manifest": "manifest.json",
    "scan_summary": "scan-summary.json",
    "decision_packet": "decision-packet.json",
    "system_dossier": "system-dossier.json",
    "evidence_graph": "evidence-graph.json",
    "acceptance_matrix": "enterprise-acceptance-matrix.json",
}

NON_CLAIMS = [
    "This self-assurance summary does not certify ManifestIQ.",
    "This self-assurance summary does not approve a release.",
    "This self-assurance summary is based only on a local deterministic self-scan evidence package.",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _artifact_status(evidence_package: Path, filename: str) -> str:
    return "present" if (evidence_package / filename).is_file() else "missing"


def _counts(scan_summary: dict[str, Any]) -> dict[str, int]:
    counts = scan_summary.get("finding_counts", {})
    if not isinstance(counts, dict):
        counts = {}
    return {
        "critical": int(counts.get("Critical", counts.get("critical", 0)) or 0),
        "high": int(counts.get("High", counts.get("high", 0)) or 0),
        "medium": int(counts.get("Medium", counts.get("medium", 0)) or 0),
        "low": int(counts.get("Low", counts.get("low", 0)) or 0),
    }


def _source_path(scan_summary: dict[str, Any], evidence_package: Path) -> str:
    metadata = scan_summary.get("source_metadata", {})
    if isinstance(metadata, dict) and metadata.get("source_path"):
        return str(metadata["source_path"])
    return str(evidence_package)


def build_self_assurance_summary(evidence_package: Path | str) -> dict[str, Any]:
    package = Path(evidence_package)
    scan_summary = _read_json(package / "scan-summary.json") or {}
    artifact_statuses = {
        key: _artifact_status(package, filename)
        for key, filename in EXPECTED_ARTIFACTS.items()
    }
    counts = _counts(scan_summary)
    blocking_reasons: list[str] = []
    warnings: list[str] = []

    if artifact_statuses["scan_summary"] == "missing":
        blocking_reasons.append("Self-scan summary is missing.")
    for key, status in artifact_statuses.items():
        if status == "missing" and key != "scan_summary":
            blocking_reasons.append(f"Self-scan artifact is missing: {EXPECTED_ARTIFACTS[key]}")

    decision = str(scan_summary.get("decision", "Unknown"))
    if decision in {"Not Approved", "Rejected"}:
        blocking_reasons.append(f"Self-scan decision is {decision}.")
    elif decision not in {"Approved", "Conditional Approval", "Pilot Only", "Remediation Required", "Mandatory Review"}:
        warnings.append("Self-scan decision is unknown.")
    if counts["critical"] > 0:
        blocking_reasons.append("Self-scan produced critical findings.")
    if counts["high"] > 0 and not blocking_reasons:
        warnings.append("Self-scan produced high findings requiring review.")

    if blocking_reasons:
        status = "failed"
    elif warnings:
        status = "warning"
    elif artifact_statuses["scan_summary"] == "present":
        status = "passed"
    else:
        status = "unknown"

    return {
        "schema": "manifestiq-self-assurance-summary",
        "schema_version": "0.1",
        "generated_at": _now_iso(),
        "self_scan": {
            "source_path": _source_path(scan_summary, package),
            "profile": str(scan_summary.get("profile", "unknown")),
            "decision": decision,
            "score": int(scan_summary.get("score", 0) or 0),
            **counts,
            "evidence_package_path": str(package) if package.exists() else None,
            "decision_packet_path": str(package / "decision-packet.json") if (package / "decision-packet.json").is_file() else None,
            "risk_acceptance_review_path": str(package / "risk-acceptance-review.json") if (package / "risk-acceptance-review.json").is_file() else None,
        },
        "expected_artifacts": artifact_statuses,
        "self_assurance_status": status,
        "blocking_reasons": blocking_reasons,
        "warnings": warnings,
        "limitations": [
            "Self-assurance summarizes a local static scan of ManifestIQ and does not certify release readiness.",
            "Recursive output folders should be ignored or excluded when self-scanning the repository.",
        ],
        "non_claims": NON_CLAIMS,
    }


def collect_self_assurance(evidence_package: Path | str, output_dir: Path | str) -> dict[str, Any]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    summary = build_self_assurance_summary(evidence_package)
    write_json(output / "self-assurance-summary.json", summary)
    return summary
