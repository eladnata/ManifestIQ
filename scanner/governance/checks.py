from __future__ import annotations

from pathlib import Path

from scanner.core.evidence import write_json

REQUIRED_GOVERNANCE_DOCS = [
    "docs/governance/SDLC_GOVERNANCE_MODEL.md",
    "docs/governance/CHANGE_CONTROL_POLICY.md",
    "docs/governance/RELEASE_GATES.md",
    "docs/governance/ENGINEERING_DEFINITION_OF_READY.md",
    "docs/governance/ENGINEERING_DEFINITION_OF_DONE.md",
    "docs/governance/RACI.md",
    "docs/governance/ADR_POLICY.md",
    "docs/governance/RULE_CHANGE_POLICY.md",
    "docs/governance/QUALITY_METRICS.md",
    "docs/governance/VALIDATION_GATE_POLICY.md",
    "docs/governance/SECURE_DEVELOPMENT_POLICY.md",
    "docs/governance/GOVERNANCE_EVIDENCE_PACKET_SPEC.md",
]

REQUIRED_ADRS = [
    "docs/adr/ADR-0001-local-deterministic-non-ai.md",
    "docs/adr/ADR-0002-evidence-first-design.md",
    "docs/adr/ADR-0003-baseline-rulebook-governance.md",
    "docs/adr/ADR-0004-validation-gates-and-regression-control.md",
    "docs/adr/ADR-0005-no-ui-before-engine-stability.md",
]

REQUIRED_TEMPLATES = [
    "governance/templates/CHANGE_REQUEST_TEMPLATE.md",
    "governance/templates/RELEASE_CHECKLIST_TEMPLATE.md",
    "governance/templates/CALIBRATION_DECISION_TEMPLATE.md",
    "governance/templates/ADR_TEMPLATE.md",
]

REQUIRED_SCHEMAS = [
    "governance/schemas/change_request.schema.json",
    "governance/schemas/release_checklist.schema.json",
    "governance/schemas/release_evidence.schema.json",
    "governance/schemas/release_manifest.schema.json",
    "governance/schemas/test_result_summary.schema.json",
    "governance/schemas/sample_scan_summary.schema.json",
    "governance/schemas/accepted_warning.schema.json",
    "governance/schemas/approval_record.schema.json",
    "governance/schemas/release_go_no_go_report.schema.json",
]

VALIDATION_DOCS = [
    "docs/validation/VALIDATION_PROGRAM.md",
    "docs/validation/RELIABILITY_LEVELS.md",
    "docs/validation/METRICS_DEFINITIONS.md",
]


def _check_file(root: Path, relative_path: str, description: str) -> dict:
    path = root / relative_path
    passed = path.exists() and path.is_file()
    return {
        "check_id": relative_path.replace("/", "."),
        "description": description,
        "status": "Passed" if passed else "Failed",
        "path": relative_path,
    }


def _check_text_reference(root: Path, relative_path: str, terms: list[str], description: str) -> dict:
    path = root / relative_path
    passed = False
    if path.exists() and path.is_file():
        text = path.read_text(encoding="utf-8").lower()
        passed = all(term.lower() in text for term in terms)
    return {
        "check_id": f"{relative_path.replace('/', '.')}.references",
        "description": description,
        "status": "Passed" if passed else "Failed",
        "path": relative_path,
    }


def _known_limitations_documented(root: Path) -> bool:
    candidate_roots = [root / "docs", root]
    for candidate_root in candidate_roots:
        if not candidate_root.exists():
            continue
        for path in sorted(candidate_root.glob("*.md") if candidate_root == root else candidate_root.rglob("*.md")):
            text = path.read_text(encoding="utf-8").lower()
            if "known limitations" in text or "limitations" in text:
                return True
    return False


def run_governance_checks(repo_root: Path | None = None, output_dir: Path | None = None) -> dict:
    root = (repo_root or Path.cwd()).resolve()
    checks: list[dict] = []

    for path in REQUIRED_GOVERNANCE_DOCS:
        checks.append(_check_file(root, path, "Required governance document exists."))
    for path in REQUIRED_ADRS:
        checks.append(_check_file(root, path, "Required ADR exists."))
    for path in REQUIRED_TEMPLATES:
        checks.append(_check_file(root, path, "Required governance template exists."))
    for path in REQUIRED_SCHEMAS:
        checks.append(_check_file(root, path, "Required governance schema exists."))

    checks.append(_check_text_reference(root, "README.md", ["governance"], "README references governance."))
    checks.append(_check_text_reference(root, "MASTER_SPEC.md", ["governance"], "MASTER_SPEC references governance."))
    checks.append(_check_file(root, "RULEBOOK_GOVERNANCE.md", "Rulebook governance document exists."))
    checks.append(_check_file(root, "docs/governance/RELEASE_GATES.md", "Release gates documentation exists."))

    for path in VALIDATION_DOCS:
        checks.append(_check_file(root, path, "Validation documentation exists."))

    limitations_passed = _known_limitations_documented(root)
    checks.append({
        "check_id": "docs.known_limitations.documented",
        "description": "Known limitations are documented somewhere in project docs.",
        "status": "Passed" if limitations_passed else "Failed",
        "path": "docs/",
    })

    failures = [check for check in checks if check["status"] == "Failed"]
    warnings: list[dict] = []
    status = "Failed" if failures else "Warning" if warnings else "Passed"
    report = {
        "schema": "enterprise-whitebox-governance-check-report",
        "schema_version": "0.1",
        "status": status,
        "checks": checks,
        "warnings": warnings,
        "failures": failures,
        "limitations": [
            "Governance checks verify required local artifacts and references; they do not run tests or validation suites.",
            "Passing governance checks do not certify compliance or prove product quality.",
        ],
    }
    if output_dir is not None:
        write_json(output_dir / "governance-check-report.json", report)
    return report
