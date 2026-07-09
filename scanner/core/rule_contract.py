from __future__ import annotations

from scanner.core.capabilities import known_signal_ids


VALID_SEVERITIES = {"Critical", "High", "Medium", "Low", "Info"}
VALID_DECISION_IMPACTS = {"Block", "Mandatory Review", "Conditional", "Advisory"}


def _decision(rule: dict) -> str:
    return str(rule.get("decision_impact") or rule.get("decision") or "Advisory")


def _rule_applies(rule: dict, control_context: dict, profile: str) -> bool:
    profiles = rule.get("applies_to_profiles", ["all"])
    if "all" not in profiles and profile not in profiles:
        return False
    applies_when = rule.get("applies_when") or {}
    checks = {
        "system_type": control_context.get("system_type"),
        "data_detected": control_context.get("sensitive_data_indicators_detected"),
        "external_egress_detected": control_context.get("external_egress_detected"),
        "ai_model_usage_detected": control_context.get("ai_model_usage_detected"),
        "finance_sox_indicators_detected": control_context.get("financial_indicators_detected"),
    }
    for key, actual in checks.items():
        expected = applies_when.get(key)
        if expected is None:
            continue
        if isinstance(expected, list):
            if actual not in expected:
                return False
        elif bool(actual) is not bool(expected):
            return False
    return True


def validate_rule_contracts(rulebook: dict, capabilities: list[dict], known_signals: set[str] | None = None) -> dict:
    known_signals = known_signals or known_signal_ids()
    known_analyzers = {item["analyzer_id"] for item in capabilities}
    rules = rulebook["rules"]
    validations = []
    errors = []
    warnings = []

    for rule_id in sorted(rules):
        rule = rules[rule_id]
        rule_errors = []
        rule_warnings = []
        if not rule.get("rule_id"):
            rule_errors.append("rule_id is required")
        if rule.get("severity") not in VALID_SEVERITIES:
            rule_errors.append("severity must be one of Critical, High, Medium, Low, Info")
        if _decision(rule) not in VALID_DECISION_IMPACTS:
            rule_errors.append("decision impact must be one of Block, Mandatory Review, Conditional, Advisory")
        if rule.get("baseline") and rule.get("editable"):
            rule_errors.append("baseline rules must be read-only")
        if rule.get("baseline") and not rule.get("disable_requires_approval", True):
            rule_warnings.append("baseline rule should require approval before disablement")
        for analyzer_id in rule.get("requires_analyzers", []) or []:
            if analyzer_id not in known_analyzers:
                rule_errors.append(f"required analyzer is not registered: {analyzer_id}")
        for signal_id in rule.get("required_signals", []) or []:
            future_allowed = bool(rule.get("allow_future_signals")) or str(signal_id).startswith("future.")
            if signal_id not in known_signals and not future_allowed:
                rule_errors.append(f"required signal is not registered: {signal_id}")

        validations.append({
            "rule_id": rule_id,
            "baseline": bool(rule.get("baseline")),
            "editable": bool(rule.get("editable")),
            "valid": not rule_errors,
            "errors": rule_errors,
            "warnings": rule_warnings,
        })
        errors.extend({"rule_id": rule_id, "error": error} for error in rule_errors)
        warnings.extend({"rule_id": rule_id, "warning": warning} for warning in rule_warnings)

    return {
        "schema": "enterprise-whitebox-rule-contract-validation",
        "schema_version": "0.2",
        "valid": not errors,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "rules": validations,
    }


def evaluate_v2_rules(rulebook: dict, signals: list[dict], control_context: dict, profile: str) -> dict:
    signal_ids = {signal["signal_id"] for signal in signals}
    evaluations = []
    findings = []

    for rule_id in sorted(rulebook["rules"]):
        rule = rulebook["rules"][rule_id]
        v2_fields_present = any(
            key in rule
            for key in ["required_signals", "requires_analyzers", "if_required_signal_missing", "claim_template", "gap_template", "applies_when"]
        )
        if not v2_fields_present:
            continue
        applies = _rule_applies(rule, control_context, profile)
        required_signals = sorted(rule.get("required_signals", []) or [])
        missing_signals = [signal_id for signal_id in required_signals if signal_id not in signal_ids]
        evaluation = {
            "rule_id": rule_id,
            "applies": applies,
            "required_signals": required_signals,
            "missing_signals": missing_signals,
            "satisfied": applies and not missing_signals,
            "claim_template": rule.get("claim_template"),
            "gap_template": rule.get("gap_template"),
            "control_mapping": rule.get("control_mapping", []),
        }
        evaluations.append(evaluation)

        missing_policy = rule.get("if_required_signal_missing") or {}
        if applies and missing_signals and missing_policy.get("create_gap"):
            findings.append({
                "rule_id": rule_id,
                "category": rule.get("category", "Governance"),
                "severity": missing_policy.get("gap_severity") or rule.get("severity", "High"),
                "title": missing_policy.get("gap_title") or f"Required evidence signal missing for {rule_id}",
                "description": rule.get("gap_template") or f"Required signal evidence was missing: {', '.join(missing_signals)}.",
                "file_path": None,
                "evidence_type": "rule_evaluation",
                "evidence_value": f"missing_signals={missing_signals}",
                "evidence_snippet": f"missing_signals={missing_signals}",
                "confidence": "High",
                "decision_impact": missing_policy.get("decision_impact") or _decision(rule),
                "owner_role": rule.get("owner_role", "Technical Owner"),
                "requires_approval_from": rule.get("requires_approval_from", []),
                "remediation": rule.get("required_remediation") or rule.get("remediation") or ["Provide the required evidence and re-run the scanner."],
            })

    return {
        "schema": "enterprise-whitebox-rule-evaluations-v2",
        "schema_version": "0.2",
        "evaluations": evaluations,
        "findings": findings,
    }
