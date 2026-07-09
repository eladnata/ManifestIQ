from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Callable

from scanner.core.inventory import iter_files

ALLOWED_ANALYZER_STATUSES = {"completed", "completed_with_warnings", "failed", "skipped"}
TEXT_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".cs", ".go", ".ps1", ".sql", ".html", ".css",
    ".yml", ".yaml", ".json", ".xml", ".sh", ".md", ".txt", ".toml", ".ini", ".env", ""
}


@dataclass
class AnalyzerContext:
    root: Path
    inventory: dict
    profile: str
    evidence_dir: Path | None = None


def read_text_safely(path: Path, max_bytes: int = 1_000_000) -> str | None:
    if path.stat().st_size > max_bytes:
        return None
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None


def iter_text_files(root: Path):
    for path in iter_files(root):
        if path.suffix.lower() in TEXT_EXTENSIONS or path.name.startswith(".env"):
            text = read_text_safely(path)
            if text is not None:
                yield path, text


def make_finding(
    rule_id: str,
    category: str,
    severity: str,
    title: str,
    description: str,
    file_path: str | None = None,
    line_start: int | None = None,
    line_end: int | None = None,
    evidence_type: str = "pattern_match",
    confidence: str = "medium",
    remediation: list[str] | None = None,
    owner_role: str = "Technical Owner",
) -> dict:
    return {
        "rule_id": rule_id,
        "category": category,
        "severity": severity,
        "title": title,
        "description": description,
        "file_path": file_path,
        "line_start": line_start,
        "line_end": line_end,
        "evidence_type": evidence_type,
        "confidence": confidence,
        "remediation": remediation or [],
        "owner_role": owner_role,
        "status": "open",
    }


def _failure_finding(analyzer_id: str, error: str) -> dict:
    return make_finding(
        rule_id="SCAN-001",
        category="Scan Integrity",
        severity="High",
        title=f"Analyzer failed: {analyzer_id}",
        description=error,
        evidence_type="analyzer_error",
        confidence="high",
        remediation=["Review analyzer error details", "Fix or disable the failing analyzer with documented approval", "Re-run the scanner"],
        owner_role="Scanner Maintainer",
    )


def validate_analyzer_result(result: dict) -> list[str]:
    errors = []
    if result.get("status") not in ALLOWED_ANALYZER_STATUSES:
        errors.append("Invalid analyzer status")
    if not isinstance(result.get("metrics"), dict):
        errors.append("Analyzer metrics must be an object")
    if not isinstance(result.get("findings"), list):
        errors.append("Analyzer findings must be a list")
    if not isinstance(result.get("errors"), list):
        errors.append("Analyzer errors must be a list")
    if not isinstance(result.get("input_scope"), dict):
        errors.append("Analyzer input_scope must be an object")
    if not result.get("raw_output_path"):
        errors.append("Analyzer raw_output_path is required")
    return errors


def run_analyzer(analyzer_id: str, analyzer_version: str, fn: Callable[[AnalyzerContext], dict], context: AnalyzerContext) -> dict:
    started = perf_counter()
    status = "completed"
    errors = []
    try:
        partial = fn(context)
        if not isinstance(partial, dict):
            raise TypeError("Analyzer returned a non-dict result")
    except Exception as exc:  # noqa: BLE001 - analyzer failure must become evidence
        partial = {
            "metrics": {},
            "findings": [_failure_finding(analyzer_id, str(exc))],
        }
        status = "failed"
        errors = [str(exc)]

    result = {
        "analyzer_id": analyzer_id,
        "analyzer_version": analyzer_version,
        "status": partial.get("status", status),
        "duration_ms": int((perf_counter() - started) * 1000),
        "input_scope": partial.get("input_scope", {
            "files_scanned": context.inventory.get("file_count", len(context.inventory.get("files", []))),
            "files_skipped": 0,
        }),
        "metrics": partial.get("metrics", {}),
        "findings": partial.get("findings", []),
        "raw_output_path": partial.get("raw_output_path", f"evidence/{analyzer_id}-results.json"),
        "errors": partial.get("errors", errors),
    }
    validation_errors = validate_analyzer_result(result)
    if validation_errors:
        result["status"] = "failed"
        existing_errors = result.get("errors", [])
        if not isinstance(existing_errors, list):
            existing_errors = [str(existing_errors)]
        existing_findings = result.get("findings", [])
        if not isinstance(existing_findings, list):
            existing_findings = []
        result["errors"] = [*existing_errors, *validation_errors]
        result["findings"] = [
            *existing_findings,
            _failure_finding(analyzer_id, "; ".join(validation_errors)),
        ]
    elif result["status"] == "failed" and not any(f.get("category") == "Scan Integrity" for f in result["findings"]):
        result["findings"].append(_failure_finding(analyzer_id, "; ".join(result.get("errors", [])) or "Analyzer reported failed status"))
    return result
