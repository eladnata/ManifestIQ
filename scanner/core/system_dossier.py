from __future__ import annotations


def build_system_dossier(
    *,
    summary: dict,
    inventory: dict,
    control_context: dict,
    claims: list[dict],
    gaps: list[dict],
    acceptance_matrix: dict,
    findings: list[dict],
    confidence_summary: dict,
) -> dict:
    return {
        "schema": "enterprise-whitebox-system-dossier",
        "schema_version": "0.2",
        "system_identity": {
            "source_type": summary.get("source_metadata", {}).get("source_type", "unknown"),
            "source_path": summary.get("source_metadata", {}).get("source_path", "unknown"),
            "profile": summary.get("profile", "unknown"),
            "scanner_version": summary.get("scanner_version", "unknown"),
        },
        "control_context": control_context,
        "technical_summary": {
            "file_count": inventory.get("file_count", 0),
            "total_bytes": inventory.get("total_bytes", 0),
            "languages": inventory.get("languages", {}),
            "package_managers": inventory.get("package_managers", []),
        },
        "claims": claims,
        "gaps": gaps,
        "findings_summary": {
            "decision": summary.get("decision"),
            "score": summary.get("score"),
            "finding_counts": summary.get("finding_counts", {}),
            "blocking_gate_count": len(summary.get("blocking_gates", [])),
        },
        "acceptance_matrix": acceptance_matrix,
        "maintenance_continuation_notes": [
            "Review custom rule contracts when analyzer capabilities or signal names change.",
            "Keep evidence artifacts with the scan package for audit replay.",
        ],
        "limitations": confidence_summary.get("limitations", []) + [
            "The dossier is derived only from deterministic local static analysis.",
            "Unknown means the scanner did not find sufficient local evidence.",
            "The dossier supports expert review and does not certify compliance or grant final approval.",
        ],
    }
