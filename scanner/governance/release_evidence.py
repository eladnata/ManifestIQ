from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scanner import __version__
from scanner.core.evidence import write_json
from scanner.core.rules_engine import rulebook_summary


def build_release_evidence(governance_report: dict, output_dir: Path | None = None) -> dict:
    try:
        ruleset_version = rulebook_summary()["ruleset_hash"]
    except Exception:
        ruleset_version = "unknown"

    evidence_files = ["governance-check-report.json", "release-evidence.json"]
    if output_dir is not None:
        existing_files = [
            path.name
            for path in sorted(output_dir.glob("*.json"))
            if path.name != "release-evidence.json"
        ]
        evidence_files = sorted(set(existing_files + ["release-evidence.json"]))

    return {
        "schema": "enterprise-whitebox-release-evidence",
        "schema_version": "0.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scanner_version": __version__ or "unknown",
        "ruleset_version": ruleset_version or "unknown",
        "governance_check_status": governance_report["status"],
        "test_status": "unknown",
        "validation_status": "unknown",
        "release_gate_status": "Not Evaluated",
        "release_decision": "Not Requested",
        "evidence_files": evidence_files,
        "known_limitations": [
            "This command does not run tests; test_status remains unknown.",
            "This command does not run sample scans or validation suites; validation_status remains unknown.",
            "Release gates are not fully evaluated without test, scan, validation, documentation, and approval evidence.",
        ],
        "recommendations": [
            "Run python -m pytest before release decision.",
            "Run sample scan and applicable validation commands before release decision.",
            "Attach release checklist, accepted warnings, and approver role before approving a release.",
        ],
    }


def generate_release_evidence(governance_report: dict, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence = build_release_evidence(governance_report=governance_report, output_dir=output_dir)
    write_json(output_dir / "release-evidence.json", evidence)
    return evidence


def _release_gate_status(go_no_go_status: str) -> str:
    if go_no_go_status == "Go":
        return "Passed"
    if go_no_go_status == "Conditional Go":
        return "Warning"
    if go_no_go_status == "No-Go":
        return "Failed"
    return "Not Evaluated"


def _validation_status(summary: dict[str, Any]) -> str:
    validation_values = [
        str(summary.get("adversarial_validation_status", "unknown")).lower(),
        str(summary.get("goldset_status", "unknown")).lower(),
        str(summary.get("portfolio_status", "unknown")).lower(),
        str(summary.get("trend_gate_status", "Unknown")).lower(),
    ]
    if "failed" in validation_values:
        return "failed"
    if "warning" in validation_values:
        return "warning"
    if validation_values and all(value == "passed" for value in validation_values):
        return "passed"
    return "unknown"


def _governance_status_for_release_evidence(status: str) -> str:
    if status in {"Passed", "Warning", "Failed"}:
        return status
    return "Failed"


def build_release_evidence_from_go_no_go(report: dict[str, Any], manifest: dict[str, Any] | None = None) -> dict[str, Any]:
    summary = report.get("summary", {})
    manifest = manifest or {}
    return {
        "schema": "enterprise-whitebox-release-evidence",
        "schema_version": "0.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scanner_version": manifest.get("scanner_version", "unknown"),
        "ruleset_version": manifest.get("ruleset_version") or manifest.get("ruleset_sha256") or "unknown",
        "governance_check_status": _governance_status_for_release_evidence(summary.get("governance_check_status", "Unknown")),
        "test_status": summary.get("test_status", "unknown"),
        "validation_status": _validation_status(summary),
        "release_gate_status": _release_gate_status(report.get("status", "Not Evaluated")),
        "release_decision": summary.get("approval_decision", "Not Requested"),
        "evidence_files": sorted(set([*report.get("evidence_files", []), "release-go-no-go-report.json", "release-evidence.json"])),
        "known_limitations": report.get("known_limitations", []),
        "recommendations": report.get("recommendations", []),
    }
