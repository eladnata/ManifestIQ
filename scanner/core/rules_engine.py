from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

from scanner.core.findings import normalize_findings

RULES_DIR = Path(__file__).resolve().parents[2] / "rules"
CUSTOM_RULES_DIR = RULES_DIR / "custom"
DISABLED_BASELINE_RULES_FILE = RULES_DIR / "disabled-baseline-rules.yml"


def _read_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _baseline_rule_files() -> list[Path]:
    return sorted(path for path in RULES_DIR.glob("*.yml") if path.name != DISABLED_BASELINE_RULES_FILE.name)


def _custom_rule_files() -> list[Path]:
    if not CUSTOM_RULES_DIR.exists():
        return []
    return sorted(CUSTOM_RULES_DIR.glob("*.yml"))


def _rulebook_material(rules: dict[str, dict], governance_findings: list[dict], disabled_rules: list[dict]) -> str:
    return json.dumps({
        "rules": rules,
        "governance_findings": governance_findings,
        "disabled_rules": disabled_rules,
    }, sort_keys=True, ensure_ascii=False, default=str)


def load_rules() -> dict:
    return load_rulebook()["rules"]


def load_rulebook() -> dict:
    rules: dict[str, dict] = {}
    governance_findings: list[dict] = []
    disabled_rules: list[dict] = []

    for path in _baseline_rule_files():
        data = _read_yaml(path)
        for rule in data.get("rules", []):
            normalized = {
                "baseline": True,
                "editable": False,
                "disable_requires_approval": True,
                **rule,
            }
            rules[normalized["rule_id"]] = normalized

    for path in _custom_rule_files():
        data = _read_yaml(path)
        for rule in data.get("rules", []):
            rule_id = rule["rule_id"]
            if rule_id in rules:
                governance_findings.append({
                    "rule_id": "GOV-RULEBOOK-001",
                    "category": "Governance",
                    "severity": "High",
                    "title": f"Custom rule attempted to override baseline rule: {rule_id}",
                    "description": f"Custom rule file {path.relative_to(RULES_DIR).as_posix()} used a baseline rule ID. The custom rule was ignored.",
                    "file_path": path.relative_to(RULES_DIR.parent).as_posix(),
                    "evidence_type": "rule_evaluation",
                    "evidence_value": rule_id,
                    "confidence": "High",
                    "decision_impact": "Mandatory Review",
                    "owner_role": "Security",
                    "requires_approval_from": ["Security Architecture"],
                    "remediation": ["Assign a unique custom rule ID", "Re-run the scanner", "Review rulebook governance evidence"],
                })
                continue
            rules[rule_id] = {
                "baseline": False,
                "editable": True,
                "disable_requires_approval": False,
                **rule,
            }

    if DISABLED_BASELINE_RULES_FILE.exists():
        data = _read_yaml(DISABLED_BASELINE_RULES_FILE)
        disabled_rules = data.get("disabled_rules", [])
        for item in disabled_rules:
            rule_id = item.get("rule_id") if isinstance(item, dict) else str(item)
            rule = rules.get(rule_id)
            if not rule:
                continue
            required_fields = ["reason", "approver", "timestamp", "expiration_date", "risk_acceptance"]
            missing = [field for field in required_fields if not item.get(field)]
            severity = "Critical" if rule.get("severity") == "Critical" or rule.get("decision") == "Block" else "High"
            governance_findings.append({
                "rule_id": "GOV-BASELINE-001",
                "category": "Governance",
                "severity": severity,
                "title": f"Baseline rule disabled: {rule_id} {rule.get('name', '')}".strip(),
                "description": "A baseline rule disablement was requested. Baseline disablement requires explicit risk acceptance evidence and must remain visible in the scan package."
                + (f" Missing fields: {', '.join(missing)}." if missing else ""),
                "file_path": DISABLED_BASELINE_RULES_FILE.relative_to(RULES_DIR.parent).as_posix(),
                "evidence_type": "rule_evaluation",
                "evidence_value": rule_id,
                "confidence": "High",
                "decision_impact": "Block" if severity == "Critical" else "Mandatory Review",
                "owner_role": "Security",
                "requires_approval_from": ["CISO", "Security Architecture"],
                "remediation": ["Remove the baseline rule disablement or attach complete approval evidence", "Re-run the scanner"],
            })

    ruleset_hash = hashlib.sha256(_rulebook_material(rules, governance_findings, disabled_rules).encode("utf-8")).hexdigest()
    return {
        "rules": rules,
        "governance_findings": governance_findings,
        "disabled_baseline_rules": disabled_rules,
        "ruleset_hash": ruleset_hash,
    }


def enrich_findings(findings: list[dict], profile: str) -> list[dict]:
    rulebook = load_rulebook()
    rules = rulebook["rules"]
    return normalize_findings(findings=findings, rules=rules, profile=profile)


def rulebook_governance_findings(profile: str) -> list[dict]:
    rulebook = load_rulebook()
    return normalize_findings(findings=rulebook["governance_findings"], rules=rulebook["rules"], profile=profile)


def rulebook_summary() -> dict:
    rulebook = load_rulebook()
    rules = rulebook["rules"]
    disabled_baseline_rules = json.loads(json.dumps(rulebook["disabled_baseline_rules"], sort_keys=True, default=str))
    return {
        "ruleset_hash": rulebook["ruleset_hash"],
        "baseline_rule_count": sum(1 for rule in rules.values() if rule.get("baseline")),
        "custom_rule_count": sum(1 for rule in rules.values() if not rule.get("baseline")),
        "disabled_baseline_rules": disabled_baseline_rules,
        "governance_finding_count": len(rulebook["governance_findings"]),
        "rules": [
            {
                "rule_id": rule["rule_id"],
                "name": rule.get("name"),
                "category": rule.get("category"),
                "severity": rule.get("severity"),
                "baseline": bool(rule.get("baseline")),
                "editable": bool(rule.get("editable")),
                "disable_requires_approval": bool(rule.get("disable_requires_approval")),
            }
            for rule in sorted(rules.values(), key=lambda item: item["rule_id"])
        ],
    }


def has_blocking_finding(findings: list[dict]) -> bool:
    for finding in findings:
        if finding.get("severity") == "Critical" and finding.get("decision_impact") in {"Block", "Not Approved"}:
            return True
        if finding.get("decision_impact") == "Block":
            return True
    return False


def has_mandatory_review(findings: list[dict]) -> bool:
    return any(f.get("decision_impact") == "Mandatory Review" for f in findings)


def has_undeclared_ai_model_usage(findings: list[dict]) -> bool:
    return any(
        f.get("category") == "AI Model Risk" and f.get("decision_impact") in {"Block", "Mandatory Review"}
        for f in findings
    )
