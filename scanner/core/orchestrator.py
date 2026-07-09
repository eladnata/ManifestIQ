from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from scanner.analyzers.base import AnalyzerContext, run_analyzer
from scanner.analyzers import (
    architecture_signals,
    config_scan,
    data_risk,
    delivery_readiness,
    dependencies,
    documentation,
    hidden_ai_model_detector,
    licenses,
    maintainability,
    operational,
    project_structure,
    sast,
    secrets,
    sox_detector,
)
from scanner.core.evidence import build_manifest, write_json
from scanner.core.inventory import build_inventory
from scanner.core.report_generator import generate_html_report
from scanner.core.assurance_pipeline import run_assurance_pipeline
from scanner.core.control_context import build_control_context
from scanner.core.rules_engine import enrich_findings, load_rulebook, rulebook_governance_findings, rulebook_summary
from scanner.core.rule_contract import evaluate_v2_rules
from scanner.core.scoring import score_findings
from scanner.core.signals import build_signals
from scanner.core.workspace import Workspace

ANALYZERS = [
    ("secrets", "0.1.0", secrets.analyze),
    ("dependencies", "0.1.0", dependencies.analyze),
    ("sast", "0.1.0", sast.analyze),
    ("config", "0.1.0", config_scan.analyze),
    ("hidden_ai_model_detector", "0.1.0", hidden_ai_model_detector.analyze),
    ("documentation", "0.1.0", documentation.analyze),
    ("data_risk", "0.1.0", data_risk.analyze),
    ("sox_detector", "0.1.0", sox_detector.analyze),
    ("maintainability", "0.1.0", maintainability.analyze),
    ("operational", "0.1.0", operational.analyze),
    ("licenses", "0.1.0", licenses.analyze),
    ("project_structure", "0.1.0", project_structure.analyze),
    ("delivery_readiness", "0.1.0", delivery_readiness.analyze),
    ("architecture_signals", "0.1.0", architecture_signals.analyze),
]


def _scan_id() -> str:
    return "scan_" + datetime.now(timezone.utc).astimezone().strftime("%Y%m%d_%H%M%S")


def run_scan(workspace: Workspace, profile: str, scanner_version: str) -> dict:
    scan_id = _scan_id()
    evidence_dir = workspace.evidence_dir

    inventory = build_inventory(workspace.working_path)
    write_json(evidence_dir / "source-metadata.json", workspace.source_metadata)
    write_json(evidence_dir / "file-inventory.json", inventory)

    context = AnalyzerContext(root=workspace.working_path, inventory=inventory, profile=profile, evidence_dir=evidence_dir)
    analyzer_results = []
    all_findings = []
    for analyzer_id, version, fn in ANALYZERS:
        result = run_analyzer(analyzer_id, version, fn, context)
        tagged_findings = []
        for finding in result["findings"]:
            tagged = {**finding, "_analyzer_id": analyzer_id}
            tagged_findings.append(tagged)
            all_findings.append(tagged)
        result["findings"] = tagged_findings
        analyzer_results.append(result)

    for finding in rulebook_governance_findings(profile=profile):
        all_findings.append({**finding, "_analyzer_id": "rulebook_governance"})

    rulebook = load_rulebook()
    preliminary_signals = build_signals(inventory, analyzer_results, all_findings)
    preliminary_control_context = build_control_context(profile, inventory, preliminary_signals, all_findings)
    rule_evaluations = evaluate_v2_rules(rulebook, preliminary_signals, preliminary_control_context, profile)
    for finding in rule_evaluations["findings"]:
        all_findings.append({**finding, "_analyzer_id": "rule_contract"})

    normalized_findings = enrich_findings(all_findings, profile=profile)
    findings_by_analyzer: dict[str, list[dict]] = {analyzer_id: [] for analyzer_id, _, _ in ANALYZERS}
    findings_by_analyzer["rulebook_governance"] = []
    findings_by_analyzer["rule_contract"] = []
    findings = []
    for finding in normalized_findings:
        analyzer_id = finding.get("_analyzer_id")
        public_finding = {key: value for key, value in finding.items() if not key.startswith("_")}
        findings.append(public_finding)
        if analyzer_id in findings_by_analyzer:
            findings_by_analyzer[analyzer_id].append(public_finding)

    for result in analyzer_results:
        result["findings"] = findings_by_analyzer.get(result["analyzer_id"], [])
        write_json(evidence_dir / f"{result['analyzer_id']}-results.json", result)

    scoring = score_findings(findings)
    rule_summary = rulebook_summary()
    blocking_gates = [
        {
            "finding_id": finding["finding_id"],
            "rule_id": finding["rule_id"],
            "severity": finding["severity"],
            "category": finding["category"],
            "title": finding["title"],
            "decision_impact": finding["decision_impact"],
        }
        for finding in findings
        if finding.get("decision_impact") in {"Block", "Mandatory Review"} or finding.get("severity") == "Critical"
    ]
    write_json(evidence_dir / "findings.json", findings)
    write_json(evidence_dir / "scoring-results.json", scoring)
    write_json(evidence_dir / "rule-evaluation-results.json", {
        "ruleset_hash": rule_summary["ruleset_hash"],
        "baseline_rule_count": rule_summary["baseline_rule_count"],
        "custom_rule_count": rule_summary["custom_rule_count"],
        "disabled_baseline_rules": rule_summary["disabled_baseline_rules"],
        "blocking_gates": blocking_gates,
        "v2_rule_evaluations": rule_evaluations["evaluations"],
        "v2_generated_finding_count": len(rule_evaluations["findings"]),
        "rules": rule_summary["rules"],
    })

    summary = {
        "scan_id": scan_id,
        "scanner_version": scanner_version,
        "ruleset_version": rule_summary["ruleset_hash"],
        "profile": profile,
        "source_metadata": workspace.source_metadata,
        "inventory_summary": {
            "file_count": inventory["file_count"],
            "total_bytes": inventory["total_bytes"],
            "languages": inventory["languages"],
            "package_managers": inventory["package_managers"],
        },
        "decision": scoring["decision"],
        "score": scoring["score"],
        "finding_counts": scoring["finding_counts"],
        "category_scores": scoring["category_scores"],
        "blocking_gates": blocking_gates,
        "disabled_baseline_rules": rule_summary["disabled_baseline_rules"],
        "ruleset": {
            "baseline_rule_count": rule_summary["baseline_rule_count"],
            "custom_rule_count": rule_summary["custom_rule_count"],
            "governance_finding_count": rule_summary["governance_finding_count"],
        },
    }
    write_json(evidence_dir / "scan-summary.json", summary)

    assurance = run_assurance_pipeline(
        profile=profile,
        inventory=inventory,
        analyzer_results=analyzer_results,
        findings=findings,
        scoring=scoring,
        rulebook=rulebook,
        summary=summary,
        precomputed_rule_evaluations=rule_evaluations,
    )
    write_json(evidence_dir / "signals.json", assurance["signals"])
    write_json(evidence_dir / "analyzer-capabilities.json", assurance["analyzer_capabilities"])
    write_json(evidence_dir / "control-context.json", assurance["control_context"])
    write_json(evidence_dir / "rule-contract-validation.json", assurance["rule_contract_validation"])
    write_json(evidence_dir / "claims.json", assurance["claims"])
    write_json(evidence_dir / "confidence-summary.json", assurance["confidence_summary"])
    write_json(evidence_dir / "gaps.json", assurance["gaps"])
    write_json(evidence_dir / "evidence-graph.json", assurance["evidence_graph"])
    write_json(evidence_dir / "enterprise-acceptance-matrix.json", assurance["enterprise_acceptance_matrix"])
    write_json(evidence_dir / "system-dossier.json", assurance["system_dossier"])

    report_path = generate_html_report(evidence_dir, {
        "summary": summary,
        "findings": findings,
        "analyzer_results": analyzer_results,
        "assurance": assurance,
    })
    manifest = build_manifest(evidence_dir)

    summary["evidence_sha256"] = manifest["package_sha256"]
    summary["report_path"] = str(report_path)
    write_json(evidence_dir / "scan-summary.json", summary)
    build_manifest(evidence_dir)
    return summary
