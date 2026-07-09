from __future__ import annotations

from typing import Any


def _threshold(policy: dict[str, Any], name: str, default: float) -> float:
    return float(policy.get("thresholds", {}).get(name, default))


def _regression(kind: str, metric: str, baseline: float, candidate: float, threshold: float, message: str) -> dict[str, Any]:
    return {
        "type": kind,
        "metric": metric,
        "baseline": baseline,
        "candidate": candidate,
        "delta": round(candidate - baseline, 4),
        "threshold": threshold,
        "message": message,
    }


def evaluate_gate(metric_deltas: dict[str, dict[str, float]], policy: dict[str, Any]) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
    blocking = []
    warnings = []

    critical_miss = metric_deltas["critical_miss_rate"]
    if critical_miss["candidate"] > _threshold(policy, "critical_miss_rate_max", 0.0):
        blocking.append(_regression(
            "critical_miss_rate_above_threshold",
            "critical_miss_rate",
            critical_miss["baseline"],
            critical_miss["candidate"],
            _threshold(policy, "critical_miss_rate_max", 0.0),
            "Candidate critical miss rate exceeds the allowed maximum.",
        ))

    traceability = metric_deltas["evidence_traceability"]
    if traceability["candidate"] < _threshold(policy, "evidence_traceability_min", 1.0):
        blocking.append(_regression(
            "evidence_traceability_below_threshold",
            "evidence_traceability",
            traceability["baseline"],
            traceability["candidate"],
            _threshold(policy, "evidence_traceability_min", 1.0),
            "Candidate evidence traceability is below the required minimum.",
        ))

    recall = metric_deltas["detectable_recall"]
    if recall["candidate"] < _threshold(policy, "detectable_recall_min", 0.8):
        blocking.append(_regression(
            "detectable_recall_below_threshold",
            "detectable_recall",
            recall["baseline"],
            recall["candidate"],
            _threshold(policy, "detectable_recall_min", 0.8),
            "Candidate detectable recall is below the required minimum.",
        ))
    if recall["delta"] < -_threshold(policy, "detectable_recall_max_drop", 0.05):
        blocking.append(_regression(
            "detectable_recall_drop",
            "detectable_recall",
            recall["baseline"],
            recall["candidate"],
            _threshold(policy, "detectable_recall_max_drop", 0.05),
            "Candidate detectable recall dropped beyond the allowed threshold.",
        ))

    top_blocker = metric_deltas["top_blocker_agreement"]
    if top_blocker["delta"] < -_threshold(policy, "top_blocker_agreement_max_drop", 0.05):
        warnings.append(_regression(
            "top_blocker_agreement_drop",
            "top_blocker_agreement",
            top_blocker["baseline"],
            top_blocker["candidate"],
            _threshold(policy, "top_blocker_agreement_max_drop", 0.05),
            "Candidate top blocker agreement dropped materially.",
        ))
    if top_blocker["candidate"] < _threshold(policy, "top_blocker_agreement_min", 0.75):
        warnings.append(_regression(
            "top_blocker_agreement_below_threshold",
            "top_blocker_agreement",
            top_blocker["baseline"],
            top_blocker["candidate"],
            _threshold(policy, "top_blocker_agreement_min", 0.75),
            "Candidate top blocker agreement is below the warning threshold.",
        ))

    precision = metric_deltas["material_precision_after_triage"]
    if precision["delta"] < -_threshold(policy, "material_precision_after_triage_max_drop", 0.1):
        warnings.append(_regression(
            "material_precision_drop",
            "material_precision_after_triage",
            precision["baseline"],
            precision["candidate"],
            _threshold(policy, "material_precision_after_triage_max_drop", 0.1),
            "Candidate material precision after triage dropped materially.",
        ))
    if precision["candidate"] < _threshold(policy, "material_precision_after_triage_min", 0.75):
        warnings.append(_regression(
            "material_precision_below_threshold",
            "material_precision_after_triage",
            precision["baseline"],
            precision["candidate"],
            _threshold(policy, "material_precision_after_triage_min", 0.75),
            "Candidate material precision after triage is below the warning threshold.",
        ))

    triage_growth = metric_deltas["scanner_only_findings_count"]
    baseline = triage_growth["baseline"]
    candidate = triage_growth["candidate"]
    if baseline > 0 and (candidate - baseline) / baseline > _threshold(policy, "scanner_only_triage_growth_warning", 0.25):
        warnings.append(_regression(
            "scanner_only_triage_growth",
            "scanner_only_findings_count",
            baseline,
            candidate,
            _threshold(policy, "scanner_only_triage_growth_warning", 0.25),
            "Candidate scanner-only triage burden grew materially.",
        ))

    if blocking:
        return "Failed", blocking, warnings
    if warnings:
        return "Warning", blocking, warnings
    return "Passed", blocking, warnings
