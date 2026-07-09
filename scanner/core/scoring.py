from __future__ import annotations

from collections import Counter, defaultdict

from scanner.core.rules_engine import has_blocking_finding, has_mandatory_review, has_undeclared_ai_model_usage

WEIGHTS = {
    "AI Model Risk": 0.15,
    "Architecture": 0.05,
    "Security": 0.25,
    "Data Protection": 0.20,
    "Maintainability": 0.15,
    "Operations": 0.15,
    "Documentation": 0.10,
    "Supply Chain": 0.10,
    "Governance": 0.05,
    "License Risk": 0.10,
    "SOX": 0.05,
    "Configuration": 0.10,
    "Scan Integrity": 0.05,
}
SEVERITY_PENALTY = {"Critical": 40, "High": 20, "Medium": 10, "Low": 3}


def score_findings(findings: list[dict]) -> dict:
    category_scores = defaultdict(lambda: 100)
    counts = Counter()
    for finding in findings:
        severity = finding.get("severity", "Low")
        category = finding.get("category", "Governance")
        counts[severity] += 1
        category_scores[category] = max(0, category_scores[category] - SEVERITY_PENALTY.get(severity, 3))

    weighted_total = 0
    total_weight = 0
    for category, weight in WEIGHTS.items():
        weighted_total += category_scores[category] * weight
        total_weight += weight
    score = round(weighted_total / total_weight) if total_weight else 100

    if has_blocking_finding(findings):
        decision = "Not Approved"
    elif has_undeclared_ai_model_usage(findings):
        decision = "Mandatory Review"
    elif has_mandatory_review(findings):
        decision = "Mandatory Review"
    elif score >= 90:
        decision = "Approved"
    elif score >= 75:
        decision = "Conditional Approval"
    elif score >= 60:
        decision = "Pilot Only"
    elif score >= 45:
        decision = "Remediation Required"
    else:
        decision = "Rejected"

    return {
        "score": score,
        "decision": decision,
        "category_scores": dict(category_scores),
        "finding_counts": dict(counts),
    }
