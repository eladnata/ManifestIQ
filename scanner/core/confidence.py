from __future__ import annotations


WEIGHTS = {
    "direct_code_evidence": 40,
    "configuration_evidence": 25,
    "dependency_manifest_evidence": 20,
    "documentation_evidence": 15,
    "multiple_source_confirmation": 10,
    "conflicting_signal_penalty": -25,
    "weak_keyword_only_penalty": -20,
    "missing_context_penalty": -10,
}


def _confidence(score: int) -> str:
    if score >= 70:
        return "High"
    if score >= 40:
        return "Medium"
    return "Low"


def _score_evidence(evidence: list[dict], limitations: list[str]) -> int:
    score = 0
    analyzers = {item.get("source_analyzer") for item in evidence if item.get("source_analyzer")}
    for item in evidence:
        metric = str(item.get("metric", "")).lower()
        if item.get("file_path") or metric in {"ai_api_indicators", "model_artifacts"}:
            score += WEIGHTS["direct_code_evidence"]
        elif "config" in metric:
            score += WEIGHTS["configuration_evidence"]
        elif "depend" in metric or "component" in metric or "license" in metric:
            score += WEIGHTS["dependency_manifest_evidence"]
        elif "doc" in metric or "runbook" in metric:
            score += WEIGHTS["documentation_evidence"]
        else:
            score += 20
    if len(analyzers) > 1:
        score += WEIGHTS["multiple_source_confirmation"]
    if not evidence:
        score += WEIGHTS["missing_context_penalty"]
    if limitations:
        score += WEIGHTS["missing_context_penalty"]
    return max(0, min(100, score))


def build_confidence_summary(claims: list[dict], signals: list[dict], findings: list[dict]) -> dict:
    claim_scores = []
    for claim in claims:
        score = _score_evidence(claim.get("evidence", []), claim.get("limitations", []))
        claim_scores.append({
            "claim_id": claim["claim_id"],
            "statement": claim["statement"],
            "score": score,
            "confidence": _confidence(score),
            "declared_confidence": claim.get("confidence", "Medium"),
        })

    confidence_counts = {"High": 0, "Medium": 0, "Low": 0}
    for item in claim_scores:
        confidence_counts[item["confidence"]] += 1
    for signal in signals:
        confidence_counts[signal.get("confidence", "Medium")] = confidence_counts.get(signal.get("confidence", "Medium"), 0) + 1

    low_confidence_domains = sorted({
        signal.get("domain", "unknown")
        for signal in signals
        if signal.get("confidence") == "Low"
    } | {
        claim.get("claim_type", "unknown")
        for claim in claims
        if claim.get("confidence") == "Low"
    })

    return {
        "schema": "enterprise-whitebox-confidence-summary",
        "schema_version": "0.1",
        "weights": WEIGHTS,
        "claim_scores": claim_scores,
        "confidence_counts": confidence_counts,
        "low_confidence_domains": low_confidence_domains,
        "finding_confidence_counts": {
            level: sum(1 for finding in findings if finding.get("confidence") == level)
            for level in ["High", "Medium", "Low"]
        },
        "limitations": ["Confidence is deterministic and based only on local static evidence."],
    }
