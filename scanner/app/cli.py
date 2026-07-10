from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from scanner import __version__
from scanner.core.orchestrator import run_scan
from scanner.core.risk_acceptance import apply_exception_register_to_evidence_package
from scanner.core.workspace import prepare_folder_workspace, prepare_git_workspace, prepare_zip_workspace
from scanner.governance import (
    collect_self_assurance,
    collect_sample_scan_evidence,
    collect_test_evidence,
    collect_trust_safety_review,
    generate_release_evidence,
    prepare_release_candidate,
    prepare_release_evidence,
    run_governance_checks,
)
from scanner.ui import build_board_verdict_view, render_executive_cockpit_html
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
    exception_register: Optional[Path] = typer.Option(None, "--exception-register", exists=True, file_okay=True, dir_okay=False, help="Optional local exception register JSON file"),
) -> None:
    """Scan a local folder."""
    workspace = prepare_folder_workspace(source_path=path, output_dir=output)
    result = run_scan(workspace=workspace, profile=profile, scanner_version=__version__, exception_register=exception_register)
    _print_result(result)


@app.command("apply-exceptions")
def apply_exceptions(
    evidence_package: Path = typer.Option(..., "--evidence-package", exists=True, file_okay=False, dir_okay=True, help="Existing evidence package directory"),
    exception_register: Path = typer.Option(..., "--exception-register", exists=True, file_okay=True, dir_okay=False, help="Local exception register JSON file"),
    output: Path = typer.Option(..., "--output", help="Output evidence package directory"),
) -> None:
    """Apply a local risk acceptance register to an existing evidence package."""
    result = apply_exception_register_to_evidence_package(evidence_package=evidence_package, exception_register=exception_register, output_dir=output)
    review = result["review"]
    summary = review["coverage_summary"]
    table = Table(title="ManifestIQ Risk Acceptance Review")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Review Status", str(review["review_status"]))
    table.add_row("Raw Decision", str(review["raw_decision"]))
    table.add_row("Raw Score", str(review["raw_score"]))
    table.add_row("Covered Findings", str(summary["material_findings_covered"]))
    table.add_row("Uncovered Findings", str(summary["material_findings_uncovered"]))
    table.add_row("Covered Gaps", str(summary["material_gaps_covered"]))
    table.add_row("Uncovered Gaps", str(summary["material_gaps_uncovered"]))
    table.add_row("Review", str(Path(output) / "risk-acceptance-review.json"))
    console.print(table)


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


@app.command("collect-scan-evidence")
def collect_scan_evidence_command(
    evidence_package: Path = typer.Option(..., "--evidence-package", file_okay=False, dir_okay=True, help="Scanner evidence package directory to parse"),
    command: str = typer.Option(..., "--command", help="Exact scanner command that produced the evidence package"),
    output: Path = typer.Option(Path("governance-output"), "--output", help="Output directory for sample scan evidence summary"),
) -> None:
    """Generate sample_scan_summary.json from a real scanner evidence package."""
    summary = collect_sample_scan_evidence(evidence_package=evidence_package, command=command, output_dir=output)
    table = Table(title="Enterprise Code Assurance Sample Scan Evidence")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Status", str(summary["status"]))
    table.add_row("Decision", str(summary["decision"]))
    table.add_row("Score", str(summary["score"]))
    table.add_row("Critical", str(summary["critical"]))
    table.add_row("High", str(summary["high"]))
    table.add_row("Medium", str(summary["medium"]))
    table.add_row("Low", str(summary["low"]))
    table.add_row("Summary", str(output / "sample_scan_summary.json"))
    table.add_row("Notes", str(len(summary["notes"])))
    console.print(table)


@app.command("collect-self-assurance")
def collect_self_assurance_command(
    evidence_package: Path = typer.Option(..., "--evidence-package", exists=True, file_okay=False, dir_okay=True, help="Self-scan evidence package directory"),
    output: Path = typer.Option(Path("release-candidate-output"), "--output", help="Output directory for self-assurance summary"),
) -> None:
    """Summarize a local ManifestIQ self-scan evidence package."""
    summary = collect_self_assurance(evidence_package=evidence_package, output_dir=output)
    table = Table(title="ManifestIQ Self-Assurance Summary")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Status", str(summary["self_assurance_status"]))
    table.add_row("Decision", str(summary["self_scan"]["decision"]))
    table.add_row("Score", str(summary["self_scan"]["score"]))
    table.add_row("Critical", str(summary["self_scan"]["critical"]))
    table.add_row("High", str(summary["self_scan"]["high"]))
    table.add_row("Summary", str(output / "self-assurance-summary.json"))
    console.print(table)


@app.command("prepare-release-candidate")
def prepare_release_candidate_command(
    release_manifest: Optional[Path] = typer.Option(None, "--release-manifest", file_okay=True, dir_okay=False, help="Optional release manifest JSON file"),
    governance_output: Path = typer.Option(Path("governance-output"), "--governance-output", help="Directory containing governance evidence outputs"),
    self_scan_output: Path = typer.Option(Path("release-candidate-output"), "--self-scan-output", help="Directory containing self-assurance-summary.json"),
    output: Path = typer.Option(Path("release-candidate-output"), "--output", help="Output directory for release candidate artifacts"),
) -> None:
    """Prepare local release candidate evidence for expert review."""
    result = prepare_release_candidate(
        release_manifest=release_manifest,
        governance_output=governance_output,
        self_scan_output=self_scan_output,
        output_dir=output,
    )
    summary = result["summary"]
    table = Table(title="ManifestIQ Release Candidate")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Release Candidate", str(summary["release_candidate_id"]))
    table.add_row("Readiness", str(summary["release_readiness"]["status"]))
    table.add_row("Governance", str(summary["evidence_status"]["governance"]))
    table.add_row("Tests", str(summary["evidence_status"]["tests"]))
    table.add_row("Sample Scan", str(summary["evidence_status"]["sample_scan"]))
    table.add_row("Self Assurance", str(summary["evidence_status"]["self_assurance"]))
    table.add_row("Summary", str(output / "release-candidate-summary.json"))
    console.print(table)


@app.command("trust-safety-check")
def trust_safety_check_command(
    repo_root: Path = typer.Option(Path("."), "--repo-root", exists=True, file_okay=False, dir_okay=True, help="Repository root containing docs/internal"),
    evidence_package: Optional[Path] = typer.Option(None, "--evidence-package", exists=True, file_okay=False, dir_okay=True, help="Optional evidence package directory for integrity checks"),
    output: Path = typer.Option(Path("trust-safety-output"), "--output", help="Output directory for trust safety review"),
) -> None:
    """Run deterministic local trust-safety checks for internal doctrine and evidence boundaries."""
    review = collect_trust_safety_review(repo_root=repo_root, evidence_package=evidence_package, output_dir=output)
    table = Table(title="ManifestIQ Trust Safety Review")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Review Status", str(review["review_status"]))
    table.add_row("Domains", str(len(review["domains"])))
    table.add_row("Blocking Gaps", str(len(review["blocking_gaps"])))
    table.add_row("Warnings", str(len(review["warnings"])))
    table.add_row("Summary", str(output / "trust-safety-review.json"))
    console.print(table)


@app.command("render-gui")
def render_gui_command(
    evidence_package: Path = typer.Option(..., "--evidence-package", exists=True, file_okay=False, dir_okay=True, help="Evidence package directory to render"),
    output: Path = typer.Option(Path("gui-output"), "--output", help="Output directory for the rendered GUI"),
) -> None:
    """Render the local, read-only Board Verdict Room from an existing evidence package."""
    view = build_board_verdict_view(evidence_package)
    document = render_executive_cockpit_html(view)
    output.mkdir(parents=True, exist_ok=True)
    out_path = output / "manifestiq-executive-cockpit.html"
    out_path.write_text(document, encoding="utf-8")

    table = Table(title="ManifestIQ Executive Cockpit — Board Verdict Room")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Visible Decision", str(view["visible_decision"]))
    table.add_row("Human Approval", str(view["layers"]["human_approval"]["display"]))
    table.add_row("Limitations", str(len(view["limitations"])))
    table.add_row("Output", str(out_path))
    console.print(table)
