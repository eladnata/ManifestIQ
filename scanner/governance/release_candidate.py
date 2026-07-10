from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scanner import __version__
from scanner.core.evidence import write_json


NON_CLAIMS = [
    "This release candidate summary does not approve a release.",
    "This release candidate summary does not certify compliance.",
    "This release candidate summary does not replace release manager, CISO, CTO, AppSec, ITGC, SOX, Legal, Privacy, or architecture review.",
    "This release candidate summary is based only on local deterministic evidence artifacts available at generation time.",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _status(path: Path) -> str:
    return "present" if path.is_file() else "missing"


def _git_value(args: list[str]) -> str:
    try:
        result = subprocess.run(["git", *args], capture_output=True, text=True, check=False)
    except OSError:
        return "unknown"
    value = result.stdout.strip()
    return value or "unknown"


def _git_info() -> dict[str, Any]:
    status = _git_value(["status", "--porcelain"])
    return {
        "branch": _git_value(["branch", "--show-current"]),
        "commit": _git_value(["rev-parse", "HEAD"]),
        "dirty_working_tree": bool(status and status != "unknown"),
    }


def _test_status(data: dict[str, Any] | None, exists: bool) -> str:
    if not exists:
        return "missing"
    if not data:
        return "unknown"
    status = str(data.get("status", "unknown")).lower()
    return status if status in {"passed", "failed", "unknown"} else "unknown"


def _self_status(data: dict[str, Any] | None, exists: bool) -> str:
    if not exists:
        return "missing"
    if not data:
        return "unknown"
    status = str(data.get("self_assurance_status", "unknown")).lower()
    return status if status in {"passed", "failed", "warning", "unknown"} else "unknown"


def _release_manifest_status(path: Path | None) -> str:
    if path is None:
        return "missing"
    return "present" if path.is_file() else "missing"


def _path_string(path: Path | None) -> str | None:
    return str(path) if path else None


def _checklist_item(item_id: str, category: str, description: str, status: str, evidence_reference: str | None, required: bool) -> dict[str, Any]:
    return {
        "item_id": item_id,
        "category": category,
        "description": description,
        "status": status,
        "evidence_reference": evidence_reference,
        "required": required,
    }


def _build_checklist(
    *,
    governance_path: Path,
    test_path: Path,
    sample_path: Path,
    self_path: Path,
    release_manifest: Path | None,
    evidence_status: dict[str, str],
    manifest_data: dict[str, Any] | None,
) -> dict[str, Any]:
    items = [
        _checklist_item("GOV-001", "Governance", "Governance check report exists", "passed" if evidence_status["governance"] == "present" else "unknown", _path_string(governance_path), True),
        _checklist_item("TEST-001", "Testing", "Test result summary exists", "passed" if evidence_status["tests"] in {"passed", "failed", "unknown"} else "unknown", _path_string(test_path), True),
        _checklist_item("TEST-002", "Testing", "Tests passed", "passed" if evidence_status["tests"] == "passed" else "failed" if evidence_status["tests"] == "failed" else "unknown", _path_string(test_path), True),
        _checklist_item("SCAN-001", "Evidence", "Sample scan summary exists", "passed" if evidence_status["sample_scan"] == "present" else "unknown", _path_string(sample_path), True),
        _checklist_item("SCAN-002", "Evidence", "Sample scan evidence was generated", "passed" if evidence_status["sample_scan"] == "present" else "unknown", _path_string(sample_path), True),
        _checklist_item("SCAN-003", "Evidence", "Decision packet exists in sample evidence", "warning", _path_string(sample_path), False),
        _checklist_item("POLICY-001", "Governance", "Risk acceptance policy exists", "passed" if Path("docs/governance/RISK_ACCEPTANCE_EXCEPTION_POLICY.md").is_file() else "failed", "docs/governance/RISK_ACCEPTANCE_EXCEPTION_POLICY.md", True),
        _checklist_item("REL-001", "Release", "Release manifest exists", "passed" if evidence_status["release_manifest"] == "present" else "unknown", _path_string(release_manifest), True),
        _checklist_item("LIMIT-001", "Limitations", "Known limitations documented", "passed" if manifest_data and manifest_data.get("known_limitations") else "warning", _path_string(release_manifest), False),
        _checklist_item("REL-002", "Release", "No generated runtime outputs committed", "unknown", None, False),
        _checklist_item("SEC-001", "Security", "No .env or secrets expected in release evidence", "unknown", None, False),
        _checklist_item("VAL-001", "Validation", "Validation evidence status is explicit", "passed", None, False),
        _checklist_item("REL-003", "Release", "Release decision is not auto-approved", "passed", None, True),
        _checklist_item("SELF-001", "Evidence", "Self-assurance summary exists", "passed" if evidence_status["self_assurance"] in {"passed", "warning", "failed", "unknown"} else "unknown", _path_string(self_path), True),
    ]
    required = [item for item in items if item["required"]]
    required_failed = sum(1 for item in required if item["status"] == "failed")
    required_passed = sum(1 for item in required if item["status"] == "passed")
    warnings = sum(1 for item in items if item["status"] in {"warning", "unknown"})
    if required_failed:
        status = "Not Ready"
    elif required_passed == len(required):
        status = "Ready for Review"
    elif required:
        status = "Conditional Review"
    else:
        status = "Not Evaluated"
    return {
        "schema": "manifestiq-release-readiness-checklist",
        "schema_version": "0.1",
        "generated_at": _now_iso(),
        "items": items,
        "summary": {
            "required_total": len(required),
            "required_passed": required_passed,
            "required_failed": required_failed,
            "warnings": warnings,
            "status": status,
        },
    }


def _release_readiness(evidence_status: dict[str, str], checklist: dict[str, Any], self_summary: dict[str, Any] | None) -> dict[str, Any]:
    blocking: list[str] = []
    warnings: list[str] = []
    actions: list[str] = []
    if evidence_status["tests"] == "failed":
        blocking.append("Test result summary failed.")
        actions.append("Fix failing tests and regenerate test evidence.")
    if evidence_status["self_assurance"] == "failed":
        blocking.append("Self-assurance summary failed.")
        actions.append("Resolve self-assurance blocking reasons.")
    if checklist["summary"]["required_failed"] > 0:
        blocking.append("One or more required release checklist items failed.")

    if evidence_status["governance"] == "missing":
        warnings.append("Governance check report is missing.")
    if evidence_status["tests"] == "missing":
        warnings.append("Test result summary is missing.")
    if evidence_status["sample_scan"] == "missing":
        warnings.append("Sample scan summary is missing.")
    if evidence_status["self_assurance"] == "missing":
        warnings.append("Self-assurance summary is missing.")
    if evidence_status["release_manifest"] == "missing":
        warnings.append("Release manifest is missing.")
    if evidence_status["self_assurance"] == "warning" and self_summary:
        warnings.extend(str(item) for item in self_summary.get("warnings", []))

    if blocking:
        status = "Not Ready"
    elif warnings or checklist["summary"]["status"] == "Conditional Review":
        status = "Conditional Review"
    elif checklist["summary"]["status"] == "Ready for Review":
        status = "Ready for Review"
    else:
        status = "Not Evaluated"

    if warnings:
        actions.append("Provide or review missing and warning evidence before release review.")
    return {
        "status": status,
        "blocking_reasons": sorted(set(blocking)),
        "warnings": sorted(set(warnings)),
        "required_actions": sorted(set(actions)),
    }


def render_release_candidate_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# ManifestIQ Release Candidate Summary",
        "",
        "## Release Readiness",
        f"- Status: {summary['release_readiness']['status']}",
        f"- Release candidate: {summary['release_candidate_id']}",
        "",
        "## Evidence Status",
    ]
    lines.extend(f"- {key}: {value}" for key, value in summary.get("evidence_status", {}).items())
    lines.extend(["", "## Required Actions"])
    lines.extend(f"- {item}" for item in summary["release_readiness"].get("required_actions", []) or ["No required actions were generated."])
    lines.extend(["", "## Non-Claims"])
    lines.extend(f"- {item}" for item in summary.get("non_claims", []))
    lines.append("")
    return "\n".join(lines)


def prepare_release_candidate(
    *,
    release_manifest: Path | str | None,
    governance_output: Path | str,
    self_scan_output: Path | str,
    output_dir: Path | str,
) -> dict[str, Any]:
    governance_dir = Path(governance_output)
    self_dir = Path(self_scan_output)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    governance_path = governance_dir / "governance-check-report.json"
    test_path = governance_dir / "test_result_summary.json"
    sample_path = governance_dir / "sample_scan_summary.json"
    self_path = self_dir / "self-assurance-summary.json"
    manifest_path = Path(release_manifest) if release_manifest else None

    governance = _read_json(governance_path)
    test_summary = _read_json(test_path)
    sample_scan = _read_json(sample_path)
    self_summary = _read_json(self_path)
    manifest_data = _read_json(manifest_path) if manifest_path else None

    evidence_status = {
        "governance": _status(governance_path),
        "tests": _test_status(test_summary, test_path.is_file()),
        "sample_scan": "present" if sample_path.is_file() else "missing",
        "self_assurance": _self_status(self_summary, self_path.is_file()),
        "release_manifest": _release_manifest_status(manifest_path),
    }
    checklist = _build_checklist(
        governance_path=governance_path,
        test_path=test_path,
        sample_path=sample_path,
        self_path=self_path,
        release_manifest=manifest_path,
        evidence_status=evidence_status,
        manifest_data=manifest_data,
    )
    readiness = _release_readiness(evidence_status, checklist, self_summary)
    release_id = (manifest_data or {}).get("release_id") or "local-release-candidate"
    summary = {
        "schema": "manifestiq-release-candidate-summary",
        "schema_version": "0.1",
        "generated_at": _now_iso(),
        "release_candidate_id": str(release_id),
        "scanner_version": str((manifest_data or {}).get("scanner_version") or __version__ or "unknown"),
        "git": _git_info(),
        "inputs": {
            "governance_check_report": str(governance_path) if governance_path.is_file() else None,
            "test_result_summary": str(test_path) if test_path.is_file() else None,
            "sample_scan_summary": str(sample_path) if sample_path.is_file() else None,
            "self_assurance_summary": str(self_path) if self_path.is_file() else None,
            "release_manifest": str(manifest_path) if manifest_path and manifest_path.is_file() else None,
        },
        "evidence_status": evidence_status,
        "release_readiness": readiness,
        "limitations": [
            *([str(item) for item in (manifest_data or {}).get("known_limitations", [])] if manifest_data else []),
            "Release candidate evidence is local and deterministic; missing evidence is not inferred.",
        ],
        "non_claims": NON_CLAIMS,
    }
    write_json(output / "release-candidate-summary.json", summary)
    write_json(output / "release-readiness-checklist.json", checklist)
    (output / "release-candidate-summary.md").write_text(render_release_candidate_markdown(summary), encoding="utf-8")
    return {"summary": summary, "checklist": checklist}
