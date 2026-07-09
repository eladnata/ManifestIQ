from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from scanner import __version__
from scanner.core.evidence import write_json
from scanner.core.orchestrator import run_scan
from scanner.core.workspace import prepare_folder_workspace
from scanner.validation.expected_findings import discover_fixtures, load_expected_findings
from scanner.validation.metrics import calculate_validation_metrics


def _read_findings(evidence_dir: Path) -> list[dict[str, Any]]:
    import json

    return json.loads((evidence_dir / "findings.json").read_text(encoding="utf-8"))


def _scan_fixture(fixture: Path, output_dir: Path, profile: str) -> tuple[dict, list[dict[str, Any]]]:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    workspace = prepare_folder_workspace(fixture, output_dir)
    summary = run_scan(workspace, profile=profile, scanner_version=__version__)
    findings = _read_findings(output_dir / "evidence-package")
    return summary, findings


def run_validation_suite(
    suite: str = "adversarial",
    output_dir: Path | str = Path("validation-output"),
    fixtures_root: Path | None = None,
) -> dict[str, Any]:
    output_dir = Path(output_dir)
    fixtures = discover_fixtures(suite, fixtures_root)
    expected = []
    all_findings = []
    fixture_reports = []
    determinism_passed = True

    for fixture in fixtures:
        metadata = load_expected_findings(fixture)
        profile = metadata.get("profile", "enterprise")
        expected.extend({**item, "fixture": fixture.name} for item in metadata.get("expected_findings", []))

        first_summary, first_findings = _scan_fixture(fixture, output_dir / fixture.name / "run-1", profile)
        _second_summary, second_findings = _scan_fixture(fixture, output_dir / fixture.name / "run-2", profile)
        fixture_deterministic = first_findings == second_findings
        determinism_passed = determinism_passed and fixture_deterministic

        for finding in first_findings:
            all_findings.append({**finding, "fixture": fixture.name})

        fixture_reports.append({
            "fixture": fixture.name,
            "profile": profile,
            "decision": first_summary.get("decision"),
            "score": first_summary.get("score"),
            "expected_findings": len(metadata.get("expected_findings", [])),
            "determinism_passed": fixture_deterministic,
        })

    report = {
        "suite": f"{suite}-v0.1" if not suite.endswith("v0.1") else suite,
        "fixtures": fixture_reports,
        **calculate_validation_metrics(expected, all_findings, determinism_passed),
    }
    write_json(output_dir / "validation-report.json", report)
    return report
