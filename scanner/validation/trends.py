from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scanner.core.evidence import write_json
from scanner.validation.gates import evaluate_gate


SUMMARY_METRICS = [
    "detectable_recall",
    "material_precision_after_triage",
    "critical_miss_rate",
    "top_blocker_agreement",
    "evidence_traceability",
    "average_review_preparation_acceleration",
    "scanner_only_findings_count",
]
TRIAGE_METRICS = [
    "triage_rate",
    "valid_scanner_only_material_finding_rate",
    "false_positive_rate_after_triage",
]


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve(base: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    base_path = base / path
    return base_path if base_path.exists() else path


def _metric(report: dict[str, Any], name: str) -> float:
    if name in SUMMARY_METRICS:
        return float(report.get("summary", {}).get(name, 0))
    return float(report.get("scanner_only_triage_summary", {}).get(name, 0))


def _delta(name: str, baseline: float, candidate: float) -> dict[str, float]:
    return {"baseline": baseline, "candidate": candidate, "delta": round(candidate - baseline, 4)}


def compute_metric_deltas(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, dict[str, float]]:
    deltas = {}
    for metric in [*SUMMARY_METRICS, *TRIAGE_METRICS]:
        deltas[metric] = _delta(metric, _metric(baseline, metric), _metric(candidate, metric))
    return deltas


def _items_by_key(report: dict[str, Any], section: str, key: str) -> dict[str, dict[str, Any]]:
    return {str(item.get(key)): item for item in report.get(section, []) if item.get(key) is not None}


def _section_deltas(baseline: dict[str, Any], candidate: dict[str, Any], section: str, key: str, metric: str) -> list[dict[str, Any]]:
    base_items = _items_by_key(baseline, section, key)
    cand_items = _items_by_key(candidate, section, key)
    out = []
    for name in sorted(set(base_items) | set(cand_items)):
        base_value = float(base_items.get(name, {}).get(metric, 0))
        cand_value = float(cand_items.get(name, {}).get(metric, 0))
        out.append({
            key: name,
            "metric": metric,
            "baseline": base_value,
            "candidate": cand_value,
            "delta": round(cand_value - base_value, 4),
        })
    return out


def _regression_warnings(deltas: list[dict[str, Any]], max_drop: float, warning_type: str) -> list[dict[str, Any]]:
    warnings = []
    for item in deltas:
        if item["delta"] < -max_drop:
            warnings.append({
                "type": warning_type,
                "metric": item["metric"],
                "identifier": item.get("domain") or item.get("rule_family") or item.get("profile"),
                "baseline": item["baseline"],
                "candidate": item["candidate"],
                "delta": item["delta"],
                "threshold": max_drop,
                "message": f"{warning_type} detected for {item.get('domain') or item.get('rule_family') or item.get('profile')}.",
            })
    return warnings


def compare_trend(manifest_path: Path | str, gate_policy_path: Path | str, output_dir: Path | str) -> dict[str, Any]:
    manifest_path = Path(manifest_path)
    base_dir = manifest_path.parent
    manifest = _read_json(manifest_path)
    policy = _read_json(Path(gate_policy_path))
    baseline_report = _read_json(_resolve(base_dir, manifest["baseline_report_path"]))
    candidate_report = _read_json(_resolve(base_dir, manifest["candidate_report_path"]))

    metric_deltas = compute_metric_deltas(baseline_report, candidate_report)
    gate_status, blocking, warnings = evaluate_gate(metric_deltas, policy)

    domain_deltas = _section_deltas(baseline_report, candidate_report, "by_domain", "domain", "detectable_recall")
    rule_family_deltas = _section_deltas(baseline_report, candidate_report, "by_rule_family", "rule_family", "detectable_recall")
    profile_deltas = _section_deltas(baseline_report, candidate_report, "by_profile", "profile", "detectable_recall")
    threshold_domain = float(policy.get("thresholds", {}).get("domain_metric_max_drop", 0.1))
    threshold_family = float(policy.get("thresholds", {}).get("rule_family_metric_max_drop", 0.1))
    warnings.extend(_regression_warnings(domain_deltas, threshold_domain, "domain_regression"))
    warnings.extend(_regression_warnings(rule_family_deltas, threshold_family, "rule_family_regression"))
    if gate_status == "Passed" and warnings:
        gate_status = "Warning"

    recommendations = []
    if blocking:
        recommendations.append("Block release until validation regressions are investigated and remediated.")
    if warnings:
        recommendations.append("Review validation warnings with AppSec, CISO, CTO, or delegated assurance owners.")
    if not blocking and not warnings:
        recommendations.append("No validation trend regression detected under the selected gate policy.")

    report = {
        "schema": "enterprise-whitebox-validation-trend-report",
        "schema_version": "0.1",
        "trend_id": manifest.get("trend_id"),
        "baseline": {
            "portfolio_id": baseline_report.get("portfolio_id"),
            "scanner_version": baseline_report.get("scanner_version"),
            "ruleset_version": baseline_report.get("ruleset_version"),
        },
        "candidate": {
            "portfolio_id": candidate_report.get("portfolio_id"),
            "scanner_version": candidate_report.get("scanner_version"),
            "ruleset_version": candidate_report.get("ruleset_version"),
        },
        "summary": {
            "gate_status": gate_status,
            "blocking_regressions_count": len(blocking),
            "warnings_count": len(warnings),
            "metric_deltas": metric_deltas,
        },
        "blocking_regressions": blocking,
        "warnings": warnings,
        "by_domain_deltas": domain_deltas,
        "by_rule_family_deltas": rule_family_deltas,
        "by_profile_deltas": profile_deltas,
        "recommendations": recommendations,
        "limitations": [
            "Trend comparison detects measured validation regression; it does not prove product quality by itself.",
            "Gate thresholds are policy inputs and should be approved by accountable reviewers.",
            "Portfolio reports must be comparable in scope for trend results to be meaningful.",
        ],
    }
    write_json(Path(output_dir) / "validation-trend-report.json", report)
    return report
