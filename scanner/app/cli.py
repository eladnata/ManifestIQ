from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from scanner import __version__
from scanner.core.orchestrator import run_scan
from scanner.core.workspace import prepare_folder_workspace, prepare_git_workspace, prepare_zip_workspace
from scanner.governance import collect_test_evidence, generate_release_evidence, prepare_release_evidence, run_governance_checks
from scanner.validation.goldset import compare_goldset
from scanner.validation.portfolio import aggregate_portfolio
from scanner.validation.runner import run_validation_suite
from scanner.validation.trends import compare_trend

app = typer.Typer(help="Enterprise White-Box Code Assurance Scanner")
console = Console()


def _print_result(result: dict) -> None:
    table = Table(title="Enterprise Code Assurance Scan Result")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Scan ID", result["scan_id"])
    table.add_row("Profile", result["profile"])
    table.add_row("Decision", result["decision"])
    table.add_row("Score", str(result["score"]))
    table.add_row("Critical", str(result["finding_counts"].get("Critical", 0)))
    table.add_row("High", str(result["finding_counts"].get("High", 0)))
    table.add_row("Evidence SHA256", result["evidence_sha256"])
    table.add_row("Report", result["report_path"])
    console.print(table)


@app.command("scan-folder")
def scan_folder(
    path: Path = typer.Option(..., "--path", exists=True, file_okay=False, dir_okay=True, help="Folder to scan"),
    output: Path = typer.Option(..., "--output", help="Output directory"),
    profile: str = typer.Option("enterprise", "--profile", help="Scan profile"),
) -> None:
    """Scan a local folder."""
    workspace = prepare_folder_workspace(source_path=path, output_dir=output)
    result = run_scan(workspace=workspace, profile=profile, scanner_version=__version__)
    _print_result(result)


@app.command("scan-zip")
def scan_zip(
    file: Path = typer.Option(..., "--file", exists=True, file_okay=True, dir_okay=False, help="ZIP file to scan"),
    output: Path = typer.Option(..., "--output", help="Output directory"),
    profile: str = typer.Option("enterprise", "--profile", help="Scan profile"),
) -> None:
    """Scan a ZIP file."""
    workspace = prepare_zip_workspace(zip_path=file, output_dir=output)
    result = run_scan(workspace=workspace, profile=profile, scanner_version=__version__)
    _print_result(result)


@app.command("scan-git")
def scan_git(
    url: str = typer.Option(..., "--url", help="Git repository URL"),
    output: Path = typer.Option(..., "--output", help="Output directory"),
    profile: str = typer.Option("enterprise", "--profile", help="Scan profile"),
    branch: Optional[str] = typer.Option(None, "--branch", help="Branch to clone"),
    commit: Optional[str] = typer.Option(None, "--commit", help="Commit to checkout"),
) -> None:
    """Clone and scan a Git repository."""
    workspace = prepare_git_workspace(repo_url=url, output_dir=output, branch=branch, commit=commit)
    result = run_scan(workspace=workspace, profile=profile, scanner_version=__version__)
    _print_result(result)


@app.command("validate")
def validate(
    suite: str = typer.Option("adversarial", "--suite", help="Validation suite to run"),
    output: Path = typer.Option(Path("validation-output"), "--output", help="Validation output directory"),
) -> None:
    """Run a local validation suite."""
    report = run_validation_suite(suite=suite, output_dir=output)
    table = Table(title="Enterprise Code Assurance Validation Result")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Suite", report["suite"])
    table.add_row("Status", report["status"])
    table.add_row("Expected", str(report["total_expected_findings"]))
    table.add_row("Detected", str(report["detected_expected_findings"]))
    table.add_row("Recall", str(report["recall"]))
    table.add_row("Precision", str(report["precision"]))
    table.add_row("Critical Miss Rate", str(report["critical_miss_rate"]))
    table.add_row("Evidence Traceability", str(report["evidence_traceability"]))
    table.add_row("Determinism", str(report["determinism_passed"]))
    table.add_row("Report", str(output / "validation-report.json"))
    console.print(table)


@app.command("validate-goldset")
def validate_goldset(
    scan_output: Path = typer.Option(..., "--scan-output", exists=True, file_okay=False, dir_okay=True, help="Existing evidence package directory"),
    goldset: Path = typer.Option(..., "--goldset", exists=True, file_okay=True, dir_okay=False, help="Gold set JSON file"),
    output: Path = typer.Option(..., "--output", help="Output directory for comparison report"),
    worksheet: Optional[Path] = typer.Option(None, "--worksheet", exists=True, file_okay=True, dir_okay=False, help="Optional reviewer worksheet JSON file"),
) -> None:
    """Compare scanner output against a human-reviewed gold set."""
    report = compare_goldset(scan_output=scan_output, goldset_path=goldset, output_dir=output, worksheet_path=worksheet)
    table = Table(title="Enterprise Code Assurance Gold Set Comparison")
    table.add_column("Field")
    table.add_column("Value")
    summary = report["summary"]
    table.add_row("Repository", str(report["repo_id"]))
    table.add_row("Profile", str(report["profile"]))
    table.add_row("Scanner Run", str(report["scanner_run_id"]))
    table.add_row("Human Findings", str(summary["human_findings_count"]))
    table.add_row("Detectable Human Findings", str(summary["detectable_human_findings_count"]))
    table.add_row("Matched", str(summary["matched_findings_count"]))
    table.add_row("Missed Detectable", str(summary["missed_detectable_findings_count"]))
    table.add_row("Recall Detectable", str(summary["recall_detectable"]))
    table.add_row("Material Precision", str(summary["material_precision"]))
    table.add_row("Critical Miss Rate", str(summary["critical_miss_rate"]))
    table.add_row("Top Blocker Agreement", str(summary["top_blocker_agreement"]))
    table.add_row("Triage Required", str(len(report["triage_required"])))
    table.add_row("Report", str(output / "goldset-comparison-report.json"))
    console.print(table)


@app.command("validate-portfolio")
def validate_portfolio(
    manifest: Path = typer.Option(..., "--manifest", exists=True, file_okay=True, dir_okay=False, help="Portfolio manifest JSON file"),
    output: Path = typer.Option(..., "--output", help="Output directory for portfolio validation report"),
    calibration_log: list[Path] = typer.Option(None, "--calibration-log", exists=True, file_okay=True, dir_okay=False, help="Optional calibration log JSON file"),
) -> None:
    """Aggregate multiple gold set comparison reports into portfolio validation evidence."""
    report = aggregate_portfolio(manifest_path=manifest, output_dir=output, calibration_log_paths=calibration_log or [])
    table = Table(title="Enterprise Code Assurance Portfolio Validation")
    table.add_column("Field")
    table.add_column("Value")
    summary = report["summary"]
    table.add_row("Portfolio", str(report["portfolio_id"]))
    table.add_row("Scanner Version", str(report["scanner_version"]))
    table.add_row("Ruleset Version", str(report["ruleset_version"]))
    table.add_row("Repositories", str(summary["repositories_count"]))
    table.add_row("Detectable Recall", str(summary["detectable_recall"]))
    table.add_row("Material Precision After Triage", str(summary["material_precision_after_triage"]))
    table.add_row("Critical Miss Rate", str(summary["critical_miss_rate"]))
    table.add_row("Top Blocker Agreement", str(summary["top_blocker_agreement"]))
    table.add_row("Evidence Traceability", str(summary["evidence_traceability"]))
    table.add_row("Average Review Acceleration", str(summary["average_review_preparation_acceleration"]))
    table.add_row("Triage Rate", str(report["scanner_only_triage_summary"]["triage_rate"]))
    table.add_row("Report", str(output / "portfolio-validation-report.json"))
    console.print(table)


@app.command("validate-trend")
def validate_trend(
    manifest: Path = typer.Option(..., "--manifest", exists=True, file_okay=True, dir_okay=False, help="Validation trend manifest JSON file"),
    gate_policy: Path = typer.Option(..., "--gate-policy", exists=True, file_okay=True, dir_okay=False, help="Validation gate policy JSON file"),
    output: Path = typer.Option(..., "--output", help="Output directory for trend report"),
) -> None:
    """Compare portfolio validation reports and evaluate deterministic regression gates."""
    report = compare_trend(manifest_path=manifest, gate_policy_path=gate_policy, output_dir=output)
    table = Table(title="Enterprise Code Assurance Validation Trend")
    table.add_column("Field")
    table.add_column("Value")
    summary = report["summary"]
    table.add_row("Trend", str(report["trend_id"]))
    table.add_row("Baseline Portfolio", str(report["baseline"]["portfolio_id"]))
    table.add_row("Candidate Portfolio", str(report["candidate"]["portfolio_id"]))
    table.add_row("Gate Status", str(summary["gate_status"]))
    table.add_row("Blocking Regressions", str(summary["blocking_regressions_count"]))
    table.add_row("Warnings", str(summary["warnings_count"]))
    table.add_row("Detectable Recall Delta", str(summary["metric_deltas"]["detectable_recall"]["delta"]))
    table.add_row("Critical Miss Rate Delta", str(summary["metric_deltas"]["critical_miss_rate"]["delta"]))
    table.add_row("Evidence Traceability Delta", str(summary["metric_deltas"]["evidence_traceability"]["delta"]))
    table.add_row("Report", str(output / "validation-trend-report.json"))
    console.print(table)


@app.command("governance-check")
def governance_check(
    output: Path = typer.Option(Path("governance-output"), "--output", help="Output directory for governance evidence"),
) -> None:
    """Generate local SDLC governance evidence without running tests or validation suites."""
    output.mkdir(parents=True, exist_ok=True)
    report = run_governance_checks(output_dir=output)
    release_evidence = generate_release_evidence(governance_report=report, output_dir=output)
    table = Table(title="Enterprise Code Assurance Governance Check")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Governance Status", report["status"])
    table.add_row("Checks", str(len(report["checks"])))
    table.add_row("Failures", str(len(report["failures"])))
    table.add_row("Warnings", str(len(report["warnings"])))
    table.add_row("Test Status", release_evidence["test_status"])
    table.add_row("Validation Status", release_evidence["validation_status"])
    table.add_row("Release Gate Status", release_evidence["release_gate_status"])
    table.add_row("Governance Report", str(output / "governance-check-report.json"))
    table.add_row("Release Evidence", str(output / "release-evidence.json"))
    console.print(table)


@app.command("prepare-release-evidence")
def prepare_release_evidence_command(
    manifest: Path = typer.Option(..., "--manifest", exists=True, file_okay=True, dir_okay=False, help="Release manifest JSON file"),
    output: Path = typer.Option(Path("release-output"), "--output", help="Output directory for release evidence"),
) -> None:
    """Summarize provided release evidence and generate a deterministic Go/No-Go report."""
    release_evidence, report = prepare_release_evidence(manifest_path=manifest, output_dir=output)
    table = Table(title="Enterprise Code Assurance Release Evidence")
    table.add_column("Field")
    table.add_column("Value")
    summary = report["summary"]
    table.add_row("Release", str(report["release_id"]))
    table.add_row("Go/No-Go Status", str(report["status"]))
    table.add_row("Governance", str(summary["governance_check_status"]))
    table.add_row("Tests", str(summary["test_status"]))
    table.add_row("Sample Scan", str(summary["sample_scan_status"]))
    table.add_row("Trend Gate", str(summary["trend_gate_status"]))
    table.add_row("Approval Decision", str(summary["approval_decision"]))
    table.add_row("Blocking Reasons", str(len(report["blocking_reasons"])))
    table.add_row("Release Gate Status", str(release_evidence["release_gate_status"]))
    table.add_row("Release Evidence", str(output / "release-evidence.json"))
    table.add_row("Go/No-Go Report", str(output / "release-go-no-go-report.json"))
    console.print(table)


@app.command("collect-test-evidence")
def collect_test_evidence_command(
    junit: Path = typer.Option(..., "--junit", file_okay=True, dir_okay=False, help="Pytest JUnit XML file to parse"),
    command: str = typer.Option(..., "--command", help="Exact test command that produced the JUnit XML"),
    output: Path = typer.Option(Path("governance-output"), "--output", help="Output directory for test evidence summary"),
) -> None:
    """Generate test_result_summary.json from real pytest JUnit XML evidence."""
    summary = collect_test_evidence(junit_path=junit, command=command, output_dir=output)
    table = Table(title="Enterprise Code Assurance Test Evidence")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Status", str(summary["status"]))
    table.add_row("Total", str(summary["tests_total"]))
    table.add_row("Passed", str(summary["tests_passed"]))
    table.add_row("Failed", str(summary["tests_failed"]))
    table.add_row("Skipped", str(summary["tests_skipped"]))
    table.add_row("Duration Seconds", str(summary["duration_seconds"]))
    table.add_row("Source", str(summary["source"]))
    table.add_row("Summary", str(output / "test_result_summary.json"))
    console.print(table)
