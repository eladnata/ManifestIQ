from __future__ import annotations

from pathlib import Path
from typing import Any

from scanner.core.evidence import write_json
from scanner.governance.release_evidence import build_release_evidence_from_go_no_go
from scanner.governance.release_manifest import load_optional_json, load_release_manifest


VALIDATION_STATUS_MAP = {
    "passed": "passed",
    "pass": "passed",
    "warning": "warning",
    "warnings": "warning",
    "failed": "failed",
    "fail": "failed",
}


def _normalize_validation_status(value: Any) -> str:
    if value is None:
        return "unknown"
    text = str(value).strip().lower()
    return VALIDATION_STATUS_MAP.get(text, "unknown")


def _normalize_gate_status(value: Any) -> str:
    if value is None:
        return "Unknown"
    text = str(value).strip().lower()
    if text == "passed":
        return "Passed"
    if text == "warning":
        return "Warning"
    if text == "failed":
        return "Failed"
    return "Unknown"


def _input_record(manifest_path: Path, value: str | None, label: str) -> tuple[dict[str, Any] | None, str, str | None]:
    data, path, state = load_optional_json(manifest_path, value)
    if state == "not_provided":
        return None, "missing", None
    if state == "missing":
        return None, "missing", path
    return data, "provided", path


def _status_from_test(data: dict[str, Any] | None, state: str) -> str:
    if state == "missing":
        return "missing"
    if not data:
        return "unknown"
    status = str(data.get("status", "unknown")).lower()
    return status if status in {"passed", "failed", "unknown"} else "unknown"


def _status_from_sample_scan(data: dict[str, Any] | None, state: str) -> str:
    return _status_from_test(data, state)


def _status_from_governance(data: dict[str, Any] | None, state: str) -> str:
    if state == "missing":
        return "Missing"
    if not data:
        return "Unknown"
    status = str(data.get("status", "Unknown"))
    return status if status in {"Passed", "Warning", "Failed"} else "Unknown"


def _status_from_validation(data: dict[str, Any] | None, state: str) -> str:
    if state == "missing":
        return "missing"
    if not data:
        return "unknown"
    if "status" in data:
        return _normalize_validation_status(data.get("status"))
    summary = data.get("summary", {})
    if "status" in summary:
        return _normalize_validation_status(summary.get("status"))
    if "gate_status" in summary:
        gate_status = _normalize_gate_status(summary.get("gate_status"))
        return {"Passed": "passed", "Warning": "warning", "Failed": "failed"}.get(gate_status, "unknown")
    if data.get("critical_miss_rate") == 0 or summary.get("critical_miss_rate") == 0:
        return "passed"
    return "unknown"


def _status_from_trend(data: dict[str, Any] | None, state: str) -> str:
    if state == "missing":
        return "Missing"
    if not data:
        return "Unknown"
    return _normalize_gate_status(data.get("summary", {}).get("gate_status", data.get("gate_status")))


def _approval_decision(data: dict[str, Any] | None) -> str:
    if not data:
        return "Not Requested"
    decision = str(data.get("decision", "Not Requested"))
    allowed = {
        "Blocked",
        "Conditional",
        "Approved for internal validation",
        "Approved for pilot",
        "Approved for production use",
    }
    return decision if decision in allowed else "Not Requested"


def _warning_has_acceptance(source: str, accepted_warnings: list[dict[str, Any]]) -> bool:
    return any(warning.get("source") == source for warning in accepted_warnings)


def _portable_path(path: str | None) -> str | None:
    if not path:
        return None
    resolved = Path(path).resolve()
    try:
        return resolved.relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return str(resolved)


def _release_target_is_internal_validation(decision: str) -> bool:
    return decision == "Approved for internal validation"


def build_release_go_no_go_report(manifest_path: Path | str) -> dict[str, Any]:
    manifest_path = Path(manifest_path)
    manifest = load_release_manifest(manifest_path)
    inputs = manifest.get("evidence_inputs", {})

    governance_report, governance_state, governance_path = _input_record(manifest_path, inputs.get("governance_check_report"), "governance_check_report")
    test_summary, test_state, test_path = _input_record(manifest_path, inputs.get("test_result_summary"), "test_result_summary")
    sample_scan, sample_state, sample_path = _input_record(manifest_path, inputs.get("sample_scan_summary"), "sample_scan_summary")
    adversarial, adversarial_state, adversarial_path = _input_record(manifest_path, inputs.get("adversarial_validation_report"), "adversarial_validation_report")
    goldset, goldset_state, goldset_path = _input_record(manifest_path, inputs.get("goldset_comparison_report"), "goldset_comparison_report")
    portfolio, portfolio_state, portfolio_path = _input_record(manifest_path, inputs.get("portfolio_validation_report"), "portfolio_validation_report")
    trend, trend_state, trend_path = _input_record(manifest_path, inputs.get("validation_trend_report"), "validation_trend_report")
    approval, approval_state, approval_path = _input_record(manifest_path, inputs.get("approval_record"), "approval_record")

    accepted_warnings = []
    evidence_files = []
    warnings = []
    for label, path in [
        ("governance_check_report", governance_path),
        ("test_result_summary", test_path),
        ("sample_scan_summary", sample_path),
        ("adversarial_validation_report", adversarial_path),
        ("goldset_comparison_report", goldset_path),
        ("portfolio_validation_report", portfolio_path),
        ("validation_trend_report", trend_path),
        ("approval_record", approval_path),
    ]:
        if path:
            evidence_files.append(_portable_path(path) or path)
    for warning_path_value in inputs.get("accepted_warnings", []):
        warning_data, warning_path, warning_state = load_optional_json(manifest_path, warning_path_value)
        if warning_path:
            evidence_files.append(_portable_path(warning_path) or warning_path)
        if warning_state == "provided" and warning_data:
            accepted_warnings.append(warning_data)
        else:
            warnings.append(f"Accepted warning evidence is {warning_state}: {warning_path_value}")

    summary = {
        "governance_check_status": _status_from_governance(governance_report, governance_state),
        "test_status": _status_from_test(test_summary, test_state),
        "sample_scan_status": _status_from_sample_scan(sample_scan, sample_state),
        "adversarial_validation_status": _status_from_validation(adversarial, adversarial_state),
        "goldset_status": _status_from_validation(goldset, goldset_state),
        "portfolio_status": _status_from_validation(portfolio, portfolio_state),
        "trend_gate_status": _status_from_trend(trend, trend_state),
        "accepted_warnings_count": len(accepted_warnings),
        "known_limitations_count": len(manifest.get("known_limitations", [])),
        "approval_decision": _approval_decision(approval),
    }

    blocking_reasons: list[str] = []
    if summary["governance_check_status"] == "Failed":
        blocking_reasons.append("Governance check failed.")
    if summary["test_status"] == "failed":
        blocking_reasons.append("Test result summary failed.")
    if summary["sample_scan_status"] == "failed":
        blocking_reasons.append("Sample scan summary failed.")
    if summary["trend_gate_status"] == "Failed":
        blocking_reasons.append("Validation trend gate failed.")
    if summary["adversarial_validation_status"] == "failed":
        blocking_reasons.append("Adversarial validation failed.")
    if summary["approval_decision"] == "Blocked":
        blocking_reasons.append("Approval record blocks release.")

    if summary["governance_check_status"] in {"Missing", "Unknown"}:
        warnings.append("Governance check evidence is missing or unknown.")
    if summary["test_status"] in {"missing", "unknown"}:
        warnings.append("Test result summary is missing or unknown.")
    if summary["sample_scan_status"] in {"missing", "unknown"}:
        warnings.append("Sample scan summary is missing or unknown.")
    if summary["trend_gate_status"] == "Warning" and not _warning_has_acceptance("trend_gate", accepted_warnings):
        warnings.append("Validation trend gate warning has no accepted warning record.")
    if summary["trend_gate_status"] in {"Missing", "Unknown"}:
        warnings.append("Validation trend evidence is missing or unknown.")
    if summary["goldset_status"] == "missing":
        warnings.append("Gold set validation evidence is missing.")
    if summary["portfolio_status"] == "missing":
        warnings.append("Portfolio validation evidence is missing.")
    if summary["adversarial_validation_status"] == "missing":
        warnings.append("Adversarial validation evidence is missing.")
    if approval_state != "provided":
        warnings.append("Approval record is not provided; approval is not inferred.")

    approval_decision = summary["approval_decision"]
    conditional_reasons = []
    if approval_decision == "Conditional":
        conditional_reasons.append("Approval record is Conditional.")
    if summary["trend_gate_status"] == "Warning" and _warning_has_acceptance("trend_gate", accepted_warnings):
        conditional_reasons.append("Trend gate warning is accepted.")
    if _release_target_is_internal_validation(approval_decision) and (
        summary["portfolio_status"] == "missing" or summary["goldset_status"] == "missing"
    ):
        conditional_reasons.append("Portfolio or gold set evidence is missing for internal validation release.")
    if manifest.get("known_limitations") and approval and approval.get("conditions"):
        conditional_reasons.append("Known limitations exist and approval record includes conditions.")

    if not manifest:
        status = "Not Evaluated"
    elif blocking_reasons:
        status = "No-Go"
    elif approval_decision == "Not Requested":
        status = "Not Evaluated"
    elif conditional_reasons:
        status = "Conditional Go"
        warnings.extend(conditional_reasons)
    elif (
        summary["governance_check_status"] == "Passed"
        and summary["test_status"] == "passed"
        and summary["sample_scan_status"] == "passed"
        and summary["trend_gate_status"] in {"Passed", "Missing", "Unknown"}
        and not blocking_reasons
        and approval_decision in {"Approved for internal validation", "Approved for pilot", "Approved for production use"}
    ):
        status = "Go"
    else:
        status = "Not Evaluated"

    recommendations = []
    if blocking_reasons:
        recommendations.append("Do not release until blocking reasons are remediated.")
    if approval_decision == "Not Requested":
        recommendations.append("Provide an approval record before making a release decision.")
    if summary["test_status"] in {"missing", "unknown"}:
        recommendations.append("Provide a real test result summary; do not infer test status.")
    if status == "Conditional Go":
        recommendations.append("Track accepted warnings, limitations, and approval conditions through the release window.")
    if status == "Go":
        recommendations.append("Release evidence supports Go under the provided approval record.")

    return {
        "schema": "enterprise-whitebox-release-go-no-go-report",
        "schema_version": "0.1",
        "release_id": manifest.get("release_id", "unknown"),
        "status": status,
        "summary": summary,
        "blocking_reasons": blocking_reasons,
        "warnings": warnings,
        "accepted_warnings": accepted_warnings,
        "known_limitations": manifest.get("known_limitations", []),
        "evidence_files": sorted(set(evidence_files)),
        "recommendations": recommendations,
    }


def prepare_release_evidence(manifest_path: Path | str, output_dir: Path | str) -> tuple[dict[str, Any], dict[str, Any]]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    manifest = load_release_manifest(Path(manifest_path))
    report = build_release_go_no_go_report(manifest_path)
    write_json(output / "release-go-no-go-report.json", report)
    release_evidence = build_release_evidence_from_go_no_go(report, manifest=manifest)
    write_json(output / "release-evidence.json", release_evidence)
    return release_evidence, report
