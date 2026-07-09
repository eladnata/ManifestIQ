from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from scanner.core.evidence import write_json
from scanner.validation.calibration import load_calibration_log, summarize_calibration_logs
from scanner.validation.triage import load_triage, material_precision_after_triage, summarize_triage


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve(base: Path, value: str | None) -> Path | None:
    if value is None:
        return None
    path = Path(value)
    if path.is_absolute():
        return path
    base_path = base / path
    return base_path if base_path.exists() else path


def _safe_ratio(numerator: int | float, denominator: int | float) -> float:
    if denominator == 0:
        return 1.0
    return round(float(numerator) / float(denominator), 4)


def _rule_family(rule_id: str | None) -> str:
    if not rule_id:
        return "unknown"
    return str(rule_id).split("-", 1)[0]


def _domain_from_human(item: dict[str, Any]) -> str:
    return str(item.get("domain") or "unknown")


def _domain_from_scanner(item: dict[str, Any]) -> str:
    return str(item.get("category") or item.get("domain") or "unknown")


def _empty_bucket() -> dict[str, Any]:
    return {
        "detectable": 0,
        "matched": 0,
        "missed": 0,
        "critical_detectable": 0,
        "critical_missed": 0,
        "scanner_only": 0,
        "matched_material": 0,
        "false_positive": 0,
    }


def _bucket_metrics(name: str, bucket: dict[str, Any], key_name: str) -> dict[str, Any]:
    return {
        key_name: name,
        "detectable_human_findings_count": bucket["detectable"],
        "matched_findings_count": bucket["matched"],
        "missed_detectable_findings_count": bucket["missed"],
        "scanner_only_findings_count": bucket["scanner_only"],
        "detectable_recall": _safe_ratio(bucket["matched"], bucket["detectable"]),
        "critical_miss_rate": _safe_ratio(bucket["critical_missed"], bucket["critical_detectable"]),
        "material_precision_after_triage": _safe_ratio(bucket["matched_material"], bucket["matched_material"] + bucket["false_positive"]),
    }


def _load_manifest(manifest_path: Path) -> dict[str, Any]:
    return _read_json(manifest_path)


def aggregate_portfolio(
    manifest_path: Path | str,
    output_dir: Path | str,
    calibration_log_paths: list[Path | str] | None = None,
) -> dict[str, Any]:
    manifest_path = Path(manifest_path)
    output_dir = Path(output_dir)
    base = manifest_path.parent
    manifest = _load_manifest(manifest_path)
    reports = []
    triages = []
    acceleration_values = []
    top_blocker_values = []
    evidence_traceability_values = []
    confidence_status_counts = defaultdict(int)
    by_domain = defaultdict(_empty_bucket)
    by_rule_family = defaultdict(_empty_bucket)
    by_profile = defaultdict(_empty_bucket)
    total_detectable = total_matched = total_missed = 0
    total_critical_detectable = total_critical_missed = 0
    total_scanner_only = total_triaged_scanner_only = 0
    total_matched_material = 0

    for entry in manifest.get("comparison_reports", []):
        report_path = _resolve(base, entry["comparison_report_path"])
        report = _read_json(report_path)
        reports.append(report)
        raw_triage = load_triage(_resolve(base, entry.get("triage_path")))
        scanner_only_ids = {item.get("finding_id") for item in report.get("scanner_only_findings", [])}
        triage = None
        if raw_triage:
            triage = {
                **raw_triage,
                "triage_items": [
                    item
                    for item in raw_triage.get("triage_items", [])
                    if item.get("scanner_finding_id") in scanner_only_ids
                ],
            }
        triages.append(triage)
        triage_items = {item.get("scanner_finding_id"): item for item in (triage or {}).get("triage_items", [])}

        summary = report["summary"]
        profile = entry.get("profile") or report.get("profile", "unknown")
        total_detectable += summary.get("detectable_human_findings_count", 0)
        total_matched += summary.get("matched_findings_count", 0)
        total_missed += summary.get("missed_detectable_findings_count", 0)
        total_scanner_only += summary.get("scanner_only_findings_count", 0)
        total_triaged_scanner_only += len((triage or {}).get("triage_items", []))
        top_blocker_values.append(summary.get("top_blocker_agreement", 1.0))
        evidence_traceability_values.append(summary.get("evidence_traceability", 1.0))
        acceleration = summary.get("review_preparation_acceleration", {}).get("acceleration")
        if isinstance(acceleration, (int, float)):
            acceleration_values.append(float(acceleration))
        confidence_status = summary.get("confidence_calibration", {}).get("status", "Unknown")
        confidence_status_counts[confidence_status] += 1

        for item in report.get("matched_findings", []):
            domain = str(item.get("human_domain") or "unknown")
            family = _rule_family(item.get("human_rule_id") or item.get("scanner_rule_id"))
            material = item.get("human_materiality", "material") == "material"
            critical = item.get("human_severity") == "Critical"
            if material:
                total_matched_material += 1
            by_domain[domain]["matched"] += 1
            by_domain[domain]["detectable"] += 1
            by_rule_family[family]["matched"] += 1
            by_rule_family[family]["detectable"] += 1
            by_profile[profile]["matched"] += 1
            by_profile[profile]["detectable"] += 1
            if material:
                by_domain[domain]["matched_material"] += 1
                by_rule_family[family]["matched_material"] += 1
                by_profile[profile]["matched_material"] += 1
            if critical:
                total_critical_detectable += 1
                by_domain[domain]["critical_detectable"] += 1
                by_rule_family[family]["critical_detectable"] += 1
                by_profile[profile]["critical_detectable"] += 1

        for item in report.get("missed_detectable_findings", []):
            domain = _domain_from_human(item)
            family = _rule_family(item.get("rule_id"))
            by_domain[domain]["detectable"] += 1
            by_domain[domain]["missed"] += 1
            by_rule_family[family]["detectable"] += 1
            by_rule_family[family]["missed"] += 1
            by_profile[profile]["detectable"] += 1
            by_profile[profile]["missed"] += 1
            if item.get("severity") == "Critical":
                total_critical_detectable += 1
                total_critical_missed += 1
                by_domain[domain]["critical_detectable"] += 1
                by_domain[domain]["critical_missed"] += 1
                by_rule_family[family]["critical_detectable"] += 1
                by_rule_family[family]["critical_missed"] += 1
                by_profile[profile]["critical_detectable"] += 1
                by_profile[profile]["critical_missed"] += 1

        for item in report.get("scanner_only_findings", []):
            domain = _domain_from_scanner(item)
            family = _rule_family(item.get("rule_id"))
            by_domain[domain]["scanner_only"] += 1
            by_rule_family[family]["scanner_only"] += 1
            by_profile[profile]["scanner_only"] += 1
            label = triage_items.get(item.get("finding_id"), {}).get("label")
            if label == "false_positive":
                by_domain[domain]["false_positive"] += 1
                by_rule_family[family]["false_positive"] += 1
                by_profile[profile]["false_positive"] += 1

    calibration_logs = [load_calibration_log(Path(path)) for path in calibration_log_paths or []]
    triage_summary = summarize_triage(triages, total_scanner_only)
    material_precision = material_precision_after_triage(total_matched_material, triages)
    avg_top_blocker = round(sum(top_blocker_values) / len(top_blocker_values), 4) if top_blocker_values else 1.0
    avg_traceability = round(sum(evidence_traceability_values) / len(evidence_traceability_values), 4) if evidence_traceability_values else 1.0
    avg_acceleration = round(sum(acceleration_values) / len(acceleration_values), 4) if acceleration_values else 0.0

    recommendations = []
    if total_missed:
        recommendations.append("Review missed detectable findings and calibrate analyzers or rules.")
    if triage_summary["untriaged_scanner_only_findings_count"]:
        recommendations.append("Complete scanner-only finding triage before treating precision as final.")
    if calibration_logs:
        recommendations.append("Review calibration logs before changing ruleset behavior.")
    if not recommendations:
        recommendations.append("Continue portfolio validation after major scanner or ruleset changes.")

    report = {
        "schema": "enterprise-whitebox-portfolio-validation-report",
        "schema_version": "0.1",
        "portfolio_id": manifest.get("portfolio_id"),
        "scanner_version": manifest.get("scanner_version"),
        "ruleset_version": manifest.get("ruleset_version"),
        "summary": {
            "repositories_count": len(reports),
            "profiles": sorted({entry.get("profile") for entry in manifest.get("comparison_reports", []) if entry.get("profile")}),
            "detectable_human_findings_count": total_detectable,
            "matched_findings_count": total_matched,
            "missed_detectable_findings_count": total_missed,
            "scanner_only_findings_count": total_scanner_only,
            "triaged_scanner_only_findings_count": total_triaged_scanner_only,
            "detectable_recall": _safe_ratio(total_matched, total_detectable),
            "material_precision_after_triage": material_precision,
            "critical_miss_rate": _safe_ratio(total_critical_missed, total_critical_detectable),
            "top_blocker_agreement": avg_top_blocker,
            "evidence_traceability": avg_traceability,
            "average_review_preparation_acceleration": avg_acceleration,
        },
        "by_domain": [_bucket_metrics(name, bucket, "domain") for name, bucket in sorted(by_domain.items())],
        "by_rule_family": [_bucket_metrics(name, bucket, "rule_family") for name, bucket in sorted(by_rule_family.items())],
        "by_profile": [_bucket_metrics(name, bucket, "profile") for name, bucket in sorted(by_profile.items())],
        "confidence_calibration": {
            "status_counts": dict(sorted(confidence_status_counts.items())),
            **summarize_calibration_logs(calibration_logs),
        },
        "scanner_only_triage_summary": triage_summary,
        "reviewer_agreement_summary": {
            "top_blocker_agreement_average": avg_top_blocker,
            "reports_with_top_blocker_data": len(top_blocker_values),
        },
        "recommendations": recommendations,
        "limitations": [
            "Portfolio aggregation depends on the quality of gold set and worksheet inputs.",
            "Untriaged scanner-only findings are not counted as false positives.",
            "Non-detectable human findings remain outside scanner recall metrics.",
        ],
    }
    write_json(Path(output_dir) / "portfolio-validation-report.json", report)
    return report
