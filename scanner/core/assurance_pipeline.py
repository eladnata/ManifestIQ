from __future__ import annotations

from scanner.core.acceptance_matrix import build_acceptance_matrix
from scanner.core.capabilities import capability_registry, known_signal_ids
from scanner.core.claims import build_claims
from scanner.core.confidence import build_confidence_summary
from scanner.core.control_context import build_control_context
from scanner.core.evidence_graph import build_evidence_graph
from scanner.core.gaps import build_gaps
from scanner.core.rule_contract import evaluate_v2_rules, validate_rule_contracts
from scanner.core.signals import build_signals


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
        ],
    }


def run_assurance_pipeline(
    *,
    profile: str,
    inventory: dict,
    analyzer_results: list[dict],
    findings: list[dict],
    scoring: dict,
    rulebook: dict,
    summary: dict,
    precomputed_signals: list[dict] | None = None,
    precomputed_control_context: dict | None = None,
    precomputed_rule_evaluations: dict | None = None,
) -> dict:
    capabilities = capability_registry()
    signals = precomputed_signals or build_signals(inventory, analyzer_results, findings)
    control_context = precomputed_control_context or build_control_context(profile, inventory, signals, findings)
    rule_contract_validation = validate_rule_contracts(rulebook, capabilities, known_signal_ids())
    rule_evaluations = precomputed_rule_evaluations or evaluate_v2_rules(rulebook, signals, control_context, profile)
    claims = build_claims(signals, findings, rule_evaluations, control_context)
    confidence_summary = build_confidence_summary(claims, signals, findings)
    gaps = build_gaps(findings, rule_evaluations)
    evidence_graph = build_evidence_graph(inventory, signals, findings, claims, gaps, rulebook, scoring)
    acceptance_matrix = build_acceptance_matrix(findings, gaps, confidence_summary, scoring)
    system_dossier = build_system_dossier(
        summary=summary,
        inventory=inventory,
        control_context=control_context,
        claims=claims,
        gaps=gaps,
        acceptance_matrix=acceptance_matrix,
        findings=findings,
        confidence_summary=confidence_summary,
    )

    return {
        "signals": signals,
        "analyzer_capabilities": {
            "schema": "enterprise-whitebox-analyzer-capabilities",
            "schema_version": "0.1",
            "capabilities": capabilities,
        },
        "control_context": control_context,
        "rule_contract_validation": rule_contract_validation,
        "rule_evaluations": rule_evaluations,
        "claims": claims,
        "confidence_summary": confidence_summary,
        "gaps": gaps,
        "evidence_graph": evidence_graph,
        "enterprise_acceptance_matrix": acceptance_matrix,
        "system_dossier": system_dossier,
    }
