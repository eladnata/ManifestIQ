import json
from pathlib import Path

from scanner.analyzers.base import AnalyzerContext, run_analyzer
from scanner.analyzers import delivery_readiness, hidden_ai_model_detector, licenses, operational, project_structure
from scanner.core.findings import REQUIRED_FINDING_FIELDS
from scanner.core.inventory import build_inventory
from scanner.core.orchestrator import run_scan
from scanner.core.rules_engine import load_rulebook, rulebook_governance_findings
from scanner.core.scoring import score_findings
from scanner.core.workspace import prepare_folder_workspace

PHASE_FIVE_EVIDENCE_FILES = {
    "signals.json",
    "analyzer-capabilities.json",
    "control-context.json",
    "rule-contract-validation.json",
    "claims.json",
    "confidence-summary.json",
    "gaps.json",
    "evidence-graph.json",
    "enterprise-acceptance-matrix.json",
    "system-dossier.json",
}


def _run_sample_scan(output_dir: Path) -> tuple[dict, Path]:
    source = Path("tests/sample_projects/insecure-python")
    workspace = prepare_folder_workspace(source, output_dir)
    result = run_scan(workspace, profile="finance-sox", scanner_version="test")
    return result, output_dir / "evidence-package"


def test_sample_scan_creates_evidence(tmp_path):
    result, evidence = _run_sample_scan(tmp_path / "out")
    assert result["decision"] in {"Not Approved", "Mandatory Review", "Conditional Approval", "Remediation Required", "Rejected"}
    assert (evidence / "scan-summary.json").exists()
    assert (evidence / "findings.json").exists()
    assert (evidence / "final-report.html").exists()
    assert (evidence / "manifest.json").exists()
    assert (evidence / "sha256.txt").exists()


def test_phase_five_assurance_outputs_are_generated_and_manifested(tmp_path):
    _, evidence = _run_sample_scan(tmp_path / "out")
    manifest = json.loads((evidence / "manifest.json").read_text(encoding="utf-8"))
    manifest_paths = {item["path"] for item in manifest["files"]}
    for file_name in PHASE_FIVE_EVIDENCE_FILES:
        assert (evidence / file_name).exists()
        assert file_name in manifest_paths

    signals = json.loads((evidence / "signals.json").read_text(encoding="utf-8"))
    capabilities = json.loads((evidence / "analyzer-capabilities.json").read_text(encoding="utf-8"))
    control_context = json.loads((evidence / "control-context.json").read_text(encoding="utf-8"))
    assert signals
    assert capabilities["capabilities"]
    assert control_context["profile"] == "finance-sox"


def test_sample_findings_are_normalized(tmp_path):
    _, evidence = _run_sample_scan(tmp_path / "out")
    findings = json.loads((evidence / "findings.json").read_text(encoding="utf-8"))
    assert findings
    for finding in findings:
        assert REQUIRED_FINDING_FIELDS <= finding.keys()
        assert finding["finding_id"]
        assert finding["severity"]
        assert finding["category"]
        assert finding["profile"] == "finance-sox"
        assert isinstance(finding["remediation"], list)
        assert finding["remediation"]
    for result_path in sorted(evidence.glob("*-results.json")):
        result = json.loads(result_path.read_text(encoding="utf-8"))
        if "analyzer_id" not in result:
            continue
        assert result["status"] in {"completed", "completed_with_warnings", "failed", "skipped"}
        assert "input_scope" in result
        assert "raw_output_path" in result
        for finding in result["findings"]:
            assert REQUIRED_FINDING_FIELDS <= finding.keys()
            assert finding["finding_id"]
            assert finding["remediation"]


def test_sample_findings_are_deterministic(tmp_path):
    result_one, evidence_one = _run_sample_scan(tmp_path / "out1")
    result_two, evidence_two = _run_sample_scan(tmp_path / "out2")
    findings_one = json.loads((evidence_one / "findings.json").read_text(encoding="utf-8"))
    findings_two = json.loads((evidence_two / "findings.json").read_text(encoding="utf-8"))
    assert result_one["decision"] == result_two["decision"]
    assert result_one["score"] == result_two["score"]
    assert findings_one == findings_two


def test_analyzer_failure_creates_scan_integrity_finding():
    def failing_analyzer(_context):
        raise RuntimeError("boom")

    context = AnalyzerContext(root=Path("."), inventory={"file_count": 0, "files": []}, profile="enterprise")
    result = run_analyzer("broken", "test", failing_analyzer, context)
    assert result["status"] == "failed"
    assert result["input_scope"] == {"files_scanned": 0, "files_skipped": 0}
    assert result["raw_output_path"] == "evidence/broken-results.json"
    assert result["findings"]
    assert result["findings"][0]["rule_id"] == "SCAN-001"
    assert result["findings"][0]["category"] == "Scan Integrity"


def test_hidden_ai_dependency_detection(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "requirements.txt").write_text("openai==1.0.0\nrequests==2.32.0\n", encoding="utf-8")
    context = AnalyzerContext(root=project, inventory=build_inventory(project), profile="enterprise")
    result = hidden_ai_model_detector.analyze(context)
    assert "openai" in result["metrics"]["ai_library_indicators"]
    assert any(f["rule_id"] == "AI-001" for f in result["findings"])


def test_hidden_ai_model_artifact_detection(tmp_path):
    project = tmp_path / "project"
    model_dir = project / "models"
    model_dir.mkdir(parents=True)
    (model_dir / "model.onnx").write_bytes(b"placeholder")
    context = AnalyzerContext(root=project, inventory=build_inventory(project), profile="enterprise")
    result = hidden_ai_model_detector.analyze(context)
    assert result["metrics"]["model_artifact_count"] == 1
    assert any(f["rule_id"] == "AI-003" and f["severity"] == "Critical" for f in result["findings"])


def test_external_ai_api_indicator_detection(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "app.py").write_text("url = 'https://api.openai.com/v1/chat/completions'\nmodel='gpt-4.1'\n", encoding="utf-8")
    context = AnalyzerContext(root=project, inventory=build_inventory(project), profile="enterprise")
    result = hidden_ai_model_detector.analyze(context)
    assert "api.openai.com" in result["metrics"]["ai_api_indicators"]
    assert any(f["rule_id"] == "AI-002" and f["decision_impact"] == "Block" for f in result["findings"])


def test_custom_rule_cannot_override_baseline_rule(tmp_path, monkeypatch):
    rules_dir = tmp_path / "rules"
    custom_dir = rules_dir / "custom"
    custom_dir.mkdir(parents=True)
    (rules_dir / "security.yml").write_text(
        "rules:\n"
        "  - rule_id: SEC-001\n"
        "    name: Baseline Secret Rule\n"
        "    category: Security\n"
        "    severity: Critical\n"
        "    applies_to_profiles: [all]\n"
        "    decision: Block\n",
        encoding="utf-8",
    )
    (custom_dir / "override.yml").write_text(
        "rules:\n"
        "  - rule_id: SEC-001\n"
        "    name: Weakened Custom Rule\n"
        "    category: Security\n"
        "    severity: Low\n"
        "    applies_to_profiles: [all]\n"
        "    decision: Advisory\n",
        encoding="utf-8",
    )
    import scanner.core.rules_engine as rules_engine

    monkeypatch.setattr(rules_engine, "RULES_DIR", rules_dir)
    monkeypatch.setattr(rules_engine, "CUSTOM_RULES_DIR", custom_dir)
    monkeypatch.setattr(rules_engine, "DISABLED_BASELINE_RULES_FILE", rules_dir / "disabled-baseline-rules.yml")
    rulebook = load_rulebook()
    assert rulebook["rules"]["SEC-001"]["name"] == "Baseline Secret Rule"
    assert rulebook["rules"]["SEC-001"]["baseline"] is True
    assert rulebook["governance_findings"][0]["rule_id"] == "GOV-RULEBOOK-001"


def test_disabled_baseline_rule_generates_warning(tmp_path, monkeypatch):
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    (rules_dir / "security.yml").write_text(
        "rules:\n"
        "  - rule_id: SEC-001\n"
        "    name: Hardcoded Secret Detected\n"
        "    category: Security\n"
        "    severity: Critical\n"
        "    applies_to_profiles: [all]\n"
        "    decision: Block\n",
        encoding="utf-8",
    )
    (rules_dir / "disabled-baseline-rules.yml").write_text(
        "disabled_rules:\n"
        "  - rule_id: SEC-001\n"
        "    reason: temporary exception\n"
        "    approver: ciso@example.com\n"
        "    timestamp: 2026-07-08T00:00:00Z\n"
        "    expiration_date: 2026-08-08\n"
        "    risk_acceptance: EXC-1\n",
        encoding="utf-8",
    )
    import scanner.core.rules_engine as rules_engine

    monkeypatch.setattr(rules_engine, "RULES_DIR", rules_dir)
    monkeypatch.setattr(rules_engine, "CUSTOM_RULES_DIR", rules_dir / "custom")
    monkeypatch.setattr(rules_engine, "DISABLED_BASELINE_RULES_FILE", rules_dir / "disabled-baseline-rules.yml")
    findings = rulebook_governance_findings(profile="enterprise")
    assert findings
    assert findings[0]["rule_id"] == "GOV-BASELINE-001"
    assert findings[0]["severity"] == "Critical"
    assert findings[0]["decision_impact"] == "Block"


def test_custom_v2_rule_generates_finding_and_gap_when_required_signal_missing(tmp_path, monkeypatch):
    rules_dir = tmp_path / "rules"
    custom_dir = rules_dir / "custom"
    custom_dir.mkdir(parents=True)
    (custom_dir / "runbook-required.yml").write_text(
        "rules:\n"
        "  - rule_id: CUSTOM-V2-001\n"
        "    name: Custom Runbook Signal Required\n"
        "    category: Governance\n"
        "    severity: High\n"
        "    decision_impact: Mandatory Review\n"
        "    applies_to_profiles: [enterprise]\n"
        "    required_signals: [delivery.runbook.detected]\n"
        "    if_required_signal_missing:\n"
        "      create_gap: true\n"
        "      gap_severity: High\n"
        "      decision_impact: Mandatory Review\n"
        "      gap_title: Custom v2 missing runbook signal\n"
        "    claim_template: Runbook evidence is present.\n"
        "    gap_template: Custom rule requires runbook evidence before enterprise approval.\n"
        "    why_this_matters: Runbooks support operational handoff and incident response.\n"
        "    required_remediation:\n"
        "      - Add runbook evidence\n"
        "      - Re-run the scanner\n",
        encoding="utf-8",
    )
    project = tmp_path / "project"
    project.mkdir()
    (project / "app.py").write_text("print('hello')\n", encoding="utf-8")

    import scanner.core.rules_engine as rules_engine

    monkeypatch.setattr(rules_engine, "RULES_DIR", rules_dir)
    monkeypatch.setattr(rules_engine, "CUSTOM_RULES_DIR", custom_dir)
    monkeypatch.setattr(rules_engine, "DISABLED_BASELINE_RULES_FILE", rules_dir / "disabled-baseline-rules.yml")

    workspace = prepare_folder_workspace(project, tmp_path / "out")
    run_scan(workspace, profile="enterprise", scanner_version="test")
    evidence = tmp_path / "out" / "evidence-package"
    findings = json.loads((evidence / "findings.json").read_text(encoding="utf-8"))
    gaps = json.loads((evidence / "gaps.json").read_text(encoding="utf-8"))
    rule_evaluations = json.loads((evidence / "rule-evaluation-results.json").read_text(encoding="utf-8"))
    validation = json.loads((evidence / "rule-contract-validation.json").read_text(encoding="utf-8"))

    assert any(finding["rule_id"] == "CUSTOM-V2-001" for finding in findings)
    assert any("CUSTOM-V2-001" in gap["related_rules"] for gap in gaps)
    assert any(evaluation["rule_id"] == "CUSTOM-V2-001" and evaluation["missing_signals"] == ["delivery.runbook.detected"] for evaluation in rule_evaluations["v2_rule_evaluations"])
    assert validation["valid"] is True


def test_critical_blocking_finding_blocks_approval():
    scoring = score_findings([
        {
            "severity": "Critical",
            "category": "Security",
            "decision_impact": "Block",
        }
    ])
    assert scoring["decision"] == "Not Approved"


def test_project_structure_missing_tests_produces_finding():
    project = Path("tests/sample_projects/structure-risky")
    context = AnalyzerContext(root=project, inventory=build_inventory(project), profile="enterprise")
    result = project_structure.analyze(context)
    assert result["metrics"]["test_directory_detected"] is False
    assert any(f["rule_id"] == "ARCH-009" for f in result["findings"])


def test_delivery_readiness_missing_deployment_guide_produces_finding():
    project = Path("tests/sample_projects/structure-risky")
    context = AnalyzerContext(root=project, inventory=build_inventory(project), profile="enterprise")
    result = delivery_readiness.analyze(context)
    assert result["metrics"]["deployment_guide_present"] is False
    assert any(f["rule_id"] == "DEL-001" for f in result["findings"])


def test_project_structure_database_binary_and_archive_findings():
    project = Path("tests/sample_projects/structure-risky")
    context = AnalyzerContext(root=project, inventory=build_inventory(project), profile="finance-sox")
    result = project_structure.analyze(context)
    rule_ids = {f["rule_id"] for f in result["findings"]}
    assert {"ARCH-006", "ARCH-007", "ARCH-008"} <= rule_ids
    assert any(f["rule_id"] == "ARCH-008" and f["severity"] == "Critical" for f in result["findings"])


def test_missing_rollback_blocks_production_critical_profile():
    project = Path("tests/sample_projects/structure-risky")
    context = AnalyzerContext(root=project, inventory=build_inventory(project), profile="production-critical")
    result = delivery_readiness.analyze(context)
    assert any(
        f["rule_id"] == "DEL-002" and f["severity"] == "Critical" and f["decision_impact"] == "Block"
        for f in result["findings"]
    )


def test_missing_data_flow_affects_finance_sox_profile():
    project = Path("tests/sample_projects/structure-risky")
    context = AnalyzerContext(root=project, inventory=build_inventory(project), profile="finance-sox")
    result = delivery_readiness.analyze(context)
    assert result["metrics"]["data_flow_documentation_present"] is False
    assert any(f["rule_id"] == "DEL-007" for f in result["findings"])


def test_clean_structure_produces_fewer_phase_two_findings():
    risky = Path("tests/sample_projects/structure-risky")
    clean = Path("tests/sample_projects/structured-clean")
    risky_context = AnalyzerContext(root=risky, inventory=build_inventory(risky), profile="enterprise")
    clean_context = AnalyzerContext(root=clean, inventory=build_inventory(clean), profile="enterprise")
    risky_findings = [
        *project_structure.analyze(risky_context)["findings"],
        *delivery_readiness.analyze(risky_context)["findings"],
    ]
    clean_findings = [
        *project_structure.analyze(clean_context)["findings"],
        *delivery_readiness.analyze(clean_context)["findings"],
    ]
    assert len(clean_findings) < len(risky_findings)


def test_project_structure_and_delivery_readiness_are_not_skipped():
    project = Path("tests/sample_projects/structure-risky")
    context = AnalyzerContext(root=project, inventory=build_inventory(project), profile="enterprise")
    structure_result = run_analyzer("project_structure", "test", project_structure.analyze, context)
    delivery_result = run_analyzer("delivery_readiness", "test", delivery_readiness.analyze, context)
    assert structure_result["status"] == "completed"
    assert delivery_result["status"] == "completed"


def test_phase_two_findings_are_deterministic(tmp_path):
    source = Path("tests/sample_projects/structure-risky")
    workspace_one = prepare_folder_workspace(source, tmp_path / "out1")
    workspace_two = prepare_folder_workspace(source, tmp_path / "out2")
    run_scan(workspace_one, profile="finance-sox", scanner_version="test")
    run_scan(workspace_two, profile="finance-sox", scanner_version="test")
    findings_one = json.loads((tmp_path / "out1" / "evidence-package" / "findings.json").read_text(encoding="utf-8"))
    findings_two = json.loads((tmp_path / "out2" / "evidence-package" / "findings.json").read_text(encoding="utf-8"))
    phase_two_one = [f for f in findings_one if f["rule_id"].startswith(("ARCH-", "DEL-"))]
    phase_two_two = [f for f in findings_two if f["rule_id"].startswith(("ARCH-", "DEL-"))]
    assert phase_two_one == phase_two_two


def test_operational_missing_logging_produces_finding():
    project = Path("tests/sample_projects/structure-risky")
    context = AnalyzerContext(root=project, inventory=build_inventory(project), profile="enterprise")
    result = operational.analyze(context)
    assert result["metrics"]["logging_indicators_count"] == 0
    assert any(f["rule_id"] == "OPS-001" for f in result["findings"])


def test_operational_missing_monitoring_for_enterprise():
    project = Path("tests/sample_projects/operational-risky")
    context = AnalyzerContext(root=project, inventory=build_inventory(project), profile="enterprise")
    result = operational.analyze(context)
    assert result["metrics"]["monitoring_indicators_count"] == 0
    assert any(f["rule_id"] == "OPS-003" for f in result["findings"])


def test_operational_missing_health_check_affects_production_critical():
    project = Path("tests/sample_projects/operational-risky")
    context = AnalyzerContext(root=project, inventory=build_inventory(project), profile="production-critical")
    result = operational.analyze(context)
    assert result["metrics"]["health_check_indicators_count"] == 0
    assert any(f["rule_id"] == "OPS-004" and f["decision_impact"] == "Block" for f in result["findings"])


def test_operational_data_storage_without_backup_restore():
    project = Path("tests/sample_projects/operational-risky")
    context = AnalyzerContext(root=project, inventory=build_inventory(project), profile="finance-sox")
    result = operational.analyze(context)
    assert result["metrics"]["data_storage_detected"] is True
    assert any(f["rule_id"] == "OPS-009" and f["severity"] == "Critical" for f in result["findings"])


def test_operational_committed_env_file_produces_finding():
    project = Path("tests/sample_projects/operational-risky")
    context = AnalyzerContext(root=project, inventory=build_inventory(project), profile="enterprise")
    result = operational.analyze(context)
    assert any(f["rule_id"] == "OPS-015" and f["file_path"] == ".env" for f in result["findings"])


def test_operational_sensitive_data_logging_is_critical():
    project = Path("tests/sample_projects/operational-risky")
    context = AnalyzerContext(root=project, inventory=build_inventory(project), profile="enterprise")
    result = operational.analyze(context)
    assert any(f["rule_id"] == "OPS-014" and f["severity"] == "Critical" for f in result["findings"])


def test_operational_container_without_health_check():
    project = Path("tests/sample_projects/operational-risky")
    context = AnalyzerContext(root=project, inventory=build_inventory(project), profile="enterprise")
    result = operational.analyze(context)
    assert result["metrics"]["containerization_detected"] is True
    assert result["metrics"]["container_health_check_detected"] is False
    assert any(f["rule_id"] == "OPS-008" for f in result["findings"])


def test_operational_clean_sample_has_fewer_findings():
    risky = Path("tests/sample_projects/operational-risky")
    clean = Path("tests/sample_projects/operational-clean")
    risky_context = AnalyzerContext(root=risky, inventory=build_inventory(risky), profile="production-critical")
    clean_context = AnalyzerContext(root=clean, inventory=build_inventory(clean), profile="production-critical")
    risky_result = operational.analyze(risky_context)
    clean_result = operational.analyze(clean_context)
    assert len(clean_result["findings"]) < len(risky_result["findings"])
    assert clean_result["metrics"]["operational_readiness_score"] > risky_result["metrics"]["operational_readiness_score"]


def test_operational_analyzer_is_not_skipped():
    project = Path("tests/sample_projects/operational-risky")
    context = AnalyzerContext(root=project, inventory=build_inventory(project), profile="enterprise")
    result = run_analyzer("operational", "test", operational.analyze, context)
    assert result["status"] == "completed"


def test_license_missing_repository_license_produces_finding():
    project = Path("tests/sample_projects/license-risky")
    context = AnalyzerContext(root=project, inventory=build_inventory(project), profile="enterprise")
    result = licenses.analyze(context)
    assert result["metrics"]["repository_license_present"] is False
    assert any(f["rule_id"] == "LIC-001" for f in result["findings"])


def test_license_missing_dependency_license_produces_finding():
    project = Path("tests/sample_projects/license-risky")
    context = AnalyzerContext(root=project, inventory=build_inventory(project), profile="enterprise")
    result = licenses.analyze(context)
    assert result["metrics"]["components_missing_license"] > 0
    assert any(f["rule_id"] == "LIC-003" for f in result["findings"])


def test_license_unknown_license_produces_finding():
    project = Path("tests/sample_projects/license-risky")
    context = AnalyzerContext(root=project, inventory=build_inventory(project), profile="enterprise")
    result = licenses.analyze(context)
    assert result["metrics"]["components_unknown_license"] > 0
    assert any(f["rule_id"] == "LIC-004" for f in result["findings"])


def test_license_gpl_and_agpl_produce_high_or_critical_findings():
    project = Path("tests/sample_projects/license-risky")
    context = AnalyzerContext(root=project, inventory=build_inventory(project), profile="enterprise")
    result = licenses.analyze(context)
    assert any(f["rule_id"] == "LIC-006" and f["severity"] == "High" for f in result["findings"])
    assert any(f["rule_id"] == "LIC-007" and f["severity"] == "Critical" for f in result["findings"])


def test_license_binary_artifact_without_license_evidence_produces_finding():
    project = Path("tests/sample_projects/license-risky")
    context = AnalyzerContext(root=project, inventory=build_inventory(project), profile="enterprise")
    result = licenses.analyze(context)
    assert result["metrics"]["binary_artifacts_detected"] == 1
    assert any(f["rule_id"] == "LIC-009" for f in result["findings"])


def test_license_vendored_dependency_without_attribution_produces_finding():
    project = Path("tests/sample_projects/license-risky")
    context = AnalyzerContext(root=project, inventory=build_inventory(project), profile="enterprise")
    result = licenses.analyze(context)
    assert result["metrics"]["vendored_directories_detected"] == 1
    assert any(f["rule_id"] == "LIC-010" for f in result["findings"])


def test_local_sbom_is_generated_and_manifested(tmp_path):
    source = Path("tests/sample_projects/license-risky")
    workspace = prepare_folder_workspace(source, tmp_path / "out")
    run_scan(workspace, profile="enterprise", scanner_version="test")
    evidence = tmp_path / "out" / "evidence-package"
    sbom = json.loads((evidence / "local-sbom.json").read_text(encoding="utf-8"))
    manifest = json.loads((evidence / "manifest.json").read_text(encoding="utf-8"))
    assert sbom["schema"] == "enterprise-whitebox-local-sbom"
    assert sbom["components"]
    assert any(item["path"] == "local-sbom.json" for item in manifest["files"])


def test_license_analyzer_is_not_skipped():
    project = Path("tests/sample_projects/license-risky")
    context = AnalyzerContext(root=project, inventory=build_inventory(project), profile="enterprise")
    result = run_analyzer("licenses", "test", licenses.analyze, context)
    assert result["status"] == "completed"


def test_ai_enabled_profile_flags_ai_dependency_missing_license_evidence():
    project = Path("tests/sample_projects/license-risky")
    context = AnalyzerContext(root=project, inventory=build_inventory(project), profile="ai-enabled")
    result = licenses.analyze(context)
    assert any(
        f["rule_id"] == "LIC-003" and "AI dependency" in f["title"]
        for f in result["findings"]
    )


def test_license_clean_sample_has_lower_risk():
    risky = Path("tests/sample_projects/license-risky")
    clean = Path("tests/sample_projects/license-clean")
    risky_result = licenses.analyze(AnalyzerContext(root=risky, inventory=build_inventory(risky), profile="enterprise"))
    clean_result = licenses.analyze(AnalyzerContext(root=clean, inventory=build_inventory(clean), profile="enterprise"))
    assert clean_result["metrics"]["license_risk_score"] > risky_result["metrics"]["license_risk_score"]
    assert len(clean_result["findings"]) < len(risky_result["findings"])
