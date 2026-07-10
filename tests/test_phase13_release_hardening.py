import json
from pathlib import Path

from typer.testing import CliRunner

from scanner.app.cli import app
from scanner.core.evidence import write_json
from scanner.core.workspace import prepare_folder_workspace


def _write_self_scan_package(path: Path, *, decision: str = "Mandatory Review", score: int = 72) -> Path:
    path.mkdir(parents=True)
    write_json(path / "scan-summary.json", {
        "scan_id": "self-scan-unit",
        "profile": "enterprise",
        "source_metadata": {"source_path": "."},
        "decision": decision,
        "score": score,
        "finding_counts": {"Critical": 0, "High": 2, "Medium": 3, "Low": 4},
    })
    write_json(path / "manifest.json", {"files": [{"path": "scan-summary.json", "sha256": "abc"}], "package_sha256": "pkg"})
    write_json(path / "decision-packet.json", {"schema": "manifestiq-decision-packet"})
    write_json(path / "system-dossier.json", {"schema": "enterprise-whitebox-system-dossier"})
    write_json(path / "evidence-graph.json", {"schema": "enterprise-whitebox-evidence-graph"})
    write_json(path / "enterprise-acceptance-matrix.json", {"schema": "enterprise-whitebox-acceptance-matrix"})
    return path


def _write_governance_output(path: Path, *, test_status: str = "passed", sample_status: str = "passed") -> Path:
    path.mkdir(parents=True)
    write_json(path / "governance-check-report.json", {"schema": "enterprise-whitebox-governance-check-report", "status": "Passed"})
    write_json(path / "test_result_summary.json", {
        "schema": "enterprise-whitebox-test-result-summary",
        "status": test_status,
        "tests_total": 10,
        "tests_failed": 0 if test_status == "passed" else 1,
    })
    write_json(path / "sample_scan_summary.json", {
        "schema": "enterprise-whitebox-sample-scan-summary",
        "status": sample_status,
        "decision": "Not Approved",
        "score": 41,
        "manifest_status": "present",
        "report_status": "present",
    })
    return path


def _write_manifest(path: Path) -> Path:
    write_json(path, {
        "schema": "enterprise-whitebox-release-manifest",
        "schema_version": "0.1",
        "release_id": "unit-release",
        "scanner_version": "test",
        "ruleset_version": "rules",
        "ruleset_sha256": "hash",
        "created_at": "2026-07-10",
        "evidence_inputs": {},
        "known_limitations": ["Unit release candidate limitation is documented."],
        "release_notes": [],
    })
    return path


def test_self_assurance_summary_generated_from_evidence_package(tmp_path):
    from scanner.governance.self_assurance import collect_self_assurance

    evidence = _write_self_scan_package(tmp_path / "self" / "evidence-package")
    summary = collect_self_assurance(evidence_package=evidence, output_dir=tmp_path / "out")

    assert (tmp_path / "out" / "self-assurance-summary.json").exists()
    assert summary["schema"] == "manifestiq-self-assurance-summary"
    assert summary["self_scan"]["decision"] == "Mandatory Review"
    assert summary["expected_artifacts"]["decision_packet"] == "present"
    assert summary["self_assurance_status"] == "warning"
    assert any("does not certify" in item for item in summary["non_claims"])


def test_self_assurance_failed_when_required_artifacts_missing(tmp_path):
    from scanner.governance.self_assurance import build_self_assurance_summary

    evidence = tmp_path / "self" / "evidence-package"
    evidence.mkdir(parents=True)
    write_json(evidence / "scan-summary.json", {
        "profile": "enterprise",
        "source_metadata": {"source_path": "."},
        "decision": "Not Approved",
        "score": 10,
        "finding_counts": {"Critical": 1, "High": 0, "Medium": 0, "Low": 0},
    })

    summary = build_self_assurance_summary(evidence)

    assert summary["self_assurance_status"] == "failed"
    assert summary["expected_artifacts"]["manifest"] == "missing"
    assert summary["blocking_reasons"]


def test_release_candidate_summary_and_checklist_generated(tmp_path):
    from scanner.governance.release_candidate import prepare_release_candidate

    governance_output = _write_governance_output(tmp_path / "governance-output")
    self_output = tmp_path / "self-output"
    evidence = _write_self_scan_package(tmp_path / "self" / "evidence-package")
    from scanner.governance.self_assurance import collect_self_assurance

    collect_self_assurance(evidence, self_output)
    manifest = _write_manifest(tmp_path / "manifest.json")

    result = prepare_release_candidate(
        release_manifest=manifest,
        governance_output=governance_output,
        self_scan_output=self_output,
        output_dir=tmp_path / "release-candidate-output",
    )

    assert (tmp_path / "release-candidate-output" / "release-candidate-summary.json").exists()
    assert (tmp_path / "release-candidate-output" / "release-readiness-checklist.json").exists()
    assert result["summary"]["schema"] == "manifestiq-release-candidate-summary"
    assert result["summary"]["evidence_status"]["tests"] == "passed"
    assert result["checklist"]["schema"] == "manifestiq-release-readiness-checklist"
    assert any("does not approve a release" in item for item in result["summary"]["non_claims"])


def test_missing_governance_and_test_evidence_are_explicit_conditional_review(tmp_path):
    from scanner.governance.release_candidate import prepare_release_candidate

    result = prepare_release_candidate(
        release_manifest=None,
        governance_output=tmp_path / "missing-governance",
        self_scan_output=tmp_path / "missing-self",
        output_dir=tmp_path / "release-candidate-output",
    )

    summary = result["summary"]
    assert summary["evidence_status"]["governance"] == "missing"
    assert summary["evidence_status"]["tests"] == "missing"
    assert summary["release_readiness"]["status"] == "Conditional Review"
    assert "Test result summary is missing." in summary["release_readiness"]["warnings"]


def test_failed_tests_result_in_not_ready(tmp_path):
    from scanner.governance.release_candidate import prepare_release_candidate

    governance_output = _write_governance_output(tmp_path / "governance-output", test_status="failed")
    result = prepare_release_candidate(
        release_manifest=None,
        governance_output=governance_output,
        self_scan_output=tmp_path / "missing-self",
        output_dir=tmp_path / "release-candidate-output",
    )

    assert result["summary"]["evidence_status"]["tests"] == "failed"
    assert result["summary"]["release_readiness"]["status"] == "Not Ready"
    assert "Test result summary failed." in result["summary"]["release_readiness"]["blocking_reasons"]


def test_missing_self_assurance_is_conditional_and_failed_self_assurance_is_not_ready(tmp_path):
    from scanner.governance.release_candidate import prepare_release_candidate

    governance_output = _write_governance_output(tmp_path / "governance-output")
    missing = prepare_release_candidate(
        release_manifest=None,
        governance_output=governance_output,
        self_scan_output=tmp_path / "missing-self",
        output_dir=tmp_path / "out-missing",
    )
    assert missing["summary"]["evidence_status"]["self_assurance"] == "missing"
    assert missing["summary"]["release_readiness"]["status"] == "Conditional Review"

    failed_self = tmp_path / "failed-self"
    failed_self.mkdir()
    write_json(failed_self / "self-assurance-summary.json", {
        "schema": "manifestiq-self-assurance-summary",
        "self_assurance_status": "failed",
        "blocking_reasons": ["Self-scan missing required artifacts."],
    })
    failed = prepare_release_candidate(
        release_manifest=None,
        governance_output=governance_output,
        self_scan_output=failed_self,
        output_dir=tmp_path / "out-failed",
    )
    assert failed["summary"]["evidence_status"]["self_assurance"] == "failed"
    assert failed["summary"]["release_readiness"]["status"] == "Not Ready"


def test_all_required_evidence_present_results_in_ready_for_review(tmp_path):
    from scanner.governance.release_candidate import prepare_release_candidate

    governance_output = _write_governance_output(tmp_path / "governance-output")
    self_output = tmp_path / "self-output"
    write_json(self_output / "self-assurance-summary.json", {
        "schema": "manifestiq-self-assurance-summary",
        "self_assurance_status": "passed",
        "blocking_reasons": [],
        "warnings": [],
    })
    manifest = _write_manifest(tmp_path / "manifest.json")

    result = prepare_release_candidate(
        release_manifest=manifest,
        governance_output=governance_output,
        self_scan_output=self_output,
        output_dir=tmp_path / "release-candidate-output",
    )

    assert result["summary"]["release_readiness"]["status"] == "Ready for Review"
    assert result["checklist"]["summary"]["status"] == "Ready for Review"


def test_cli_writes_expected_release_candidate_files(tmp_path):
    governance_output = _write_governance_output(tmp_path / "governance-output")
    self_output = tmp_path / "self-output"
    write_json(self_output / "self-assurance-summary.json", {
        "schema": "manifestiq-self-assurance-summary",
        "self_assurance_status": "passed",
        "blocking_reasons": [],
        "warnings": [],
    })
    manifest = _write_manifest(tmp_path / "manifest.json")

    runner = CliRunner()
    result = runner.invoke(app, [
        "prepare-release-candidate",
        "--release-manifest",
        str(manifest),
        "--governance-output",
        str(governance_output),
        "--self-scan-output",
        str(self_output),
        "--output",
        str(tmp_path / "release-candidate-output"),
    ])

    assert result.exit_code == 0
    out = tmp_path / "release-candidate-output"
    assert (out / "release-candidate-summary.json").exists()
    assert (out / "release-readiness-checklist.json").exists()
    assert (out / "release-candidate-summary.md").exists()


def test_collect_self_assurance_cli_writes_summary(tmp_path):
    evidence = _write_self_scan_package(tmp_path / "self" / "evidence-package")
    runner = CliRunner()

    result = runner.invoke(app, [
        "collect-self-assurance",
        "--evidence-package",
        str(evidence),
        "--output",
        str(tmp_path / "release-candidate-output"),
    ])

    assert result.exit_code == 0
    summary = json.loads((tmp_path / "release-candidate-output" / "self-assurance-summary.json").read_text(encoding="utf-8"))
    assert summary["schema"] == "manifestiq-self-assurance-summary"


def test_self_scan_workspace_copy_ignores_runtime_output_folders(tmp_path):
    source = tmp_path / "repo"
    source.mkdir()
    (source / "app.py").write_text("print('hello')\n", encoding="utf-8")
    for folder in ["output", "governance-output", "self-assurance-output", "release-candidate-output"]:
        nested = source / folder
        nested.mkdir()
        (nested / "generated.json").write_text("{}", encoding="utf-8")

    workspace = prepare_folder_workspace(source, source / "self-assurance-output")
    copied = workspace.working_path

    assert (copied / "app.py").exists()
    assert not (copied / "output").exists()
    assert not (copied / "governance-output").exists()
    assert not (copied / "self-assurance-output").exists()
    assert not (copied / "release-candidate-output").exists()
