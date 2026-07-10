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
from scanner.core.system_dossier import build_system_dossier


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
