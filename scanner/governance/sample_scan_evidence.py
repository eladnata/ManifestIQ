from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scanner.core.evidence import write_json


ALLOWED_DECISIONS = {"Approved", "Conditional", "Mandatory Review", "Not Approved", "Rejected", "Unknown"}
DECISION_ALIASES = {
    "Conditional Approval": "Conditional",
    "Remediation Required": "Conditional",
    "Pilot Only": "Conditional",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _find_file(evidence_package: Path, name: str) -> Path | None:
    direct = evidence_package / name
    if direct.is_file():
        return direct
    matches = sorted(path for path in evidence_package.rglob(name) if path.is_file())
    return matches[0] if matches else None


def _read_json(path: Path, label: str, notes: list[str]) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        notes.append(f"{label} could not be parsed: {exc}")
        return None
    if not isinstance(data, dict):
        notes.append(f"{label} is not a JSON object: {path}")
        return None
    return data


def _empty_summary(command: str, notes: list[str]) -> dict[str, Any]:
    return {
        "schema": "enterprise-whitebox-sample-scan-summary",
        "schema_version": "0.1",
        "command": command,
        "profile": "unknown",
        "scan_target": "unknown",
        "decision": "Unknown",
        "score": 0,
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "findings_total": 0,
        "evidence_package_path": None,
        "manifest_path": None,
        "report_path": None,
        "manifest_status": "unknown",
        "report_status": "unknown",
        "status": "unknown",
        "generated_at": _now_iso(),
        "notes": notes,
    }


def _decision(value: Any) -> str:
    decision = str(value or "Unknown")
    decision = DECISION_ALIASES.get(decision, decision)
    return decision if decision in ALLOWED_DECISIONS else "Unknown"


def _int_value(value: Any) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def _severity_counts(scan_summary: dict[str, Any]) -> dict[str, int]:
    counts = scan_summary.get("finding_counts", {})
    if not isinstance(counts, dict):
        counts = {}
    return {
        "critical": _int_value(counts.get("Critical", counts.get("critical", 0))),
        "high": _int_value(counts.get("High", counts.get("high", 0))),
        "medium": _int_value(counts.get("Medium", counts.get("medium", 0))),
        "low": _int_value(counts.get("Low", counts.get("low", 0))),
    }


def _scan_target(scan_summary: dict[str, Any]) -> str:
    source_metadata = scan_summary.get("source_metadata", {})
    if isinstance(source_metadata, dict):
        for key in ("source_path", "repo_url"):
            value = source_metadata.get(key)
            if value:
                return str(value)
    return "unknown"


def _report_path_from_summary(evidence_package: Path, scan_summary: dict[str, Any]) -> Path | None:
    report_path = scan_summary.get("report_path")
    if not report_path:
        return None
    path = Path(str(report_path))
    if path.is_absolute():
        return path if path.is_file() else None
    candidates = [Path.cwd() / path, evidence_package / path]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def _report_path(evidence_package: Path, manifest: dict[str, Any] | None, scan_summary: dict[str, Any] | None) -> Path | None:
    direct = evidence_package / "final-report.html"
    if direct.is_file():
        return direct

    if scan_summary:
        from_summary = _report_path_from_summary(evidence_package, scan_summary)
        if from_summary:
            return from_summary

    if manifest:
        files = manifest.get("files", [])
        if isinstance(files, list):
            for item in files:
                if not isinstance(item, dict):
                    continue
                relative = item.get("path")
                if relative and str(relative).endswith(".html"):
                    candidate = evidence_package / str(relative)
                    if candidate.is_file():
                        return candidate
    matches = sorted(path for path in evidence_package.rglob("*.html") if path.is_file())
    return matches[0] if matches else None


def build_sample_scan_summary(evidence_package: Path | str, command: str) -> dict[str, Any]:
    package = Path(evidence_package)
    notes: list[str] = []
    if not package.exists() or not package.is_dir():
        notes.append(f"Evidence package is missing or not a directory: {package}")
        return _empty_summary(command, notes)

    manifest_path = _find_file(package, "manifest.json")
    scan_summary_path = _find_file(package, "scan-summary.json")

    manifest_status = "present" if manifest_path else "missing"
    if not manifest_path:
        notes.append("Manifest file is missing from the evidence package.")
    if not scan_summary_path:
        notes.append("Scan summary file is missing from the evidence package.")

    manifest = _read_json(manifest_path, "Manifest file", notes) if manifest_path else None
    scan_summary = _read_json(scan_summary_path, "Scan summary file", notes) if scan_summary_path else None

    counts = _severity_counts(scan_summary or {})
    report_path = _report_path(package, manifest, scan_summary)
    report_status = "present" if report_path else "missing"
    if not report_path:
        notes.append("Final HTML report is missing from the evidence package.")

    status = "passed" if manifest and scan_summary else "failed"

    return {
        "schema": "enterprise-whitebox-sample-scan-summary",
        "schema_version": "0.1",
        "command": command,
        "profile": str((scan_summary or {}).get("profile") or "unknown"),
        "scan_target": _scan_target(scan_summary or {}),
        "decision": _decision((scan_summary or {}).get("decision")),
        "score": _int_value((scan_summary or {}).get("score")),
        **counts,
        "findings_total": sum(counts.values()),
        "evidence_package_path": str(package),
        "manifest_path": str(manifest_path) if manifest_path else None,
        "report_path": str(report_path) if report_path else None,
        "manifest_status": manifest_status,
        "report_status": report_status,
        "status": status,
        "generated_at": _now_iso(),
        "notes": notes,
    }


def collect_sample_scan_evidence(evidence_package: Path | str, command: str, output_dir: Path | str) -> dict[str, Any]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    summary = build_sample_scan_summary(evidence_package=evidence_package, command=command)
    write_json(output / "sample_scan_summary.json", summary)
    return summary
