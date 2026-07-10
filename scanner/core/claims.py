from __future__ import annotations

import hashlib


TYPE_BY_DOMAIN = {
    "platform": "platform",
    "architecture": "architecture",
    "data": "database",
    "egress": "egress",
    "operations": "operations",
    "delivery": "delivery",
    "license": "license",
    "ai_model": "ai_model",
    "security": "security",
    "governance": "governance",
    "maintainability": "maintainability",
}


def _claim_id(statement: str) -> str:
    return "claim-" + hashlib.sha256(statement.encode("utf-8")).hexdigest()[:12]


def _claim(statement: str, claim_type: str, confidence: str, evidence: list[dict], related_signals: list[str], generated_by: str, limitations: list[str] | None = None) -> dict:
    return {
        "claim_id": _claim_id(statement),
        "claim_type": claim_type,
        "statement": statement,
        "confidence": confidence,
        "evidence": evidence,
        "related_findings": [],
        "related_signals": related_signals,
        "limitations": limitations or [],
        "generated_by": generated_by,
    }


def build_claims(signals: list[dict], findings: list[dict], rule_evaluations: dict, control_context: dict) -> list[dict]:
    claims = []
    for signal in signals:
        signal_id = signal["signal_id"]
        claim_type = TYPE_BY_DOMAIN.get(signal.get("domain"), "unknown")
        if signal_id.startswith("language."):
            language = signal_id.split(".")[1].replace("_", " ").title()
            statement = f"The system appears to use {language}."
        elif signal_id == "license.local_sbom.generated":
            statement = "Local SBOM-style evidence was generated."
        elif signal_id == "ai.model_usage.detected":
            statement = "Hidden AI or model usage indicators were detected."
        elif signal_id == "ai.external_provider.detected":
            statement = "External AI provider or prompt indicators were detected."
        elif signal_id == "ops.backup_restore.detected":
            statement = "Backup or restore readiness evidence was detected."
        elif signal_id.endswith(".missing"):
            statement = f"Required evidence appears to be missing for {signal_id.rsplit('.', 1)[0].replace('.', ' ')}."
        elif signal_id.endswith(".detected") or signal_id.endswith(".generated"):
            statement = f"{signal_id.rsplit('.', 1)[0].replace('.', ' ').title()} evidence was detected."
        else:
            statement = f"Signal {signal_id} was extracted."
        claims.append(_claim(
            statement,
            claim_type,
            signal.get("confidence", "Medium"),
            signal.get("evidence", []),
            [signal_id],
            signal.get("source_analyzer", "assurance_pipeline"),
        ))

    finding_by_rule = {}
    for finding in findings:
        finding_by_rule.setdefault(finding.get("rule_id"), []).append(finding.get("finding_id"))
    for evaluation in rule_evaluations.get("evaluations", []):
        if not evaluation.get("applies") or not evaluation.get("claim_template") or evaluation.get("missing_signals"):
            continue
        statement = evaluation["claim_template"]
        claim = _claim(statement, "governance", "Medium", [], evaluation.get("required_signals", []), "rule_contract")
        claim["related_findings"] = finding_by_rule.get(evaluation["rule_id"], [])
        claims.append(claim)

    deduped = {claim["claim_id"]: claim for claim in claims}
    return [deduped[key] for key in sorted(deduped)]
