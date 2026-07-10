import json
from pathlib import Path

from typer.testing import CliRunner

from scanner.app.cli import app
from scanner.core.evidence import write_json
from scanner.core.orchestrator import run_scan
from scanner.core.workspace import prepare_folder_workspace


def _finding(
    *,
    finding_id: str = "finding-sec",
    rule_id: str = "SEC-001",
    category: str = "Security",
    severity: str = "Critical",
    decision_impact: str = "Block",
) -> dict:
    return {
        "finding_id": finding_id,
        "rule_id": rule_id,
        "category": category,
        "severity": severity,
        "title": "Material finding",
        "decision_impact": decision_impact,
    }


def _gap(
    *,
    gap_id: str = "gap-ops",
    domain: str = "Operations",
    severity: str = "High",
    decision_impact: str = "Mandatory Review",
    related_rules: list[str] | None = None,
) -> dict:
    return {
        "gap_id": gap_id,
        "domain": domain,
        "severity": severity,
        "title": "Material gap",
        "decision_impact": decision_impact,
        "related_rules": related_rules or ["OPS-001"],
        "related_findings": [],
    }


def _summary(decision: str = "Not Approved", score: int = 41) -> dict:
    return {
        "scan_id": "scan_unit",
        "profile": "finance-sox",
        "source_metadata": {"source_path": "tests/sample_projects/insecure-python"},
        "decision": decision,
        "score": score,
    }


def _record(**overrides) -> dict:
    record = {
        "exception_id": "EXC-001",
        "title": "Accepted test risk",
        "status": "approved",
        "scope": {
            "profiles": ["finance-sox"],
            "source_paths": ["tests/sample_projects/insecure-python"],
            "rule_ids": ["SEC-001"],
            "finding_ids": [],
            "gap_ids": [],
            "domains": ["Security"],
        },
        "reason": "Temporary acceptance for unit test.",
        "risk_statement": "The risk is accepted for a bounded test period.",
        "compensating_controls": ["Manual review"],
        "owner": "security@example.com",
        "approved_by": "ciso@example.com",
        "approved_role": "CISO",
        "approved_at": "2026-07-01T00:00:00Z",
        "expires_at": "2026-12-31T00:00:00Z",
        "review_required_by": "2026-11-30T00:00:00Z",
        "evidence_references": ["approval-record"],
        "limitations": [],
    }
    record.update(overrides)
    return record


def _register(records: list[dict]) -> dict:
    return {
        "schema": "manifestiq-exception-register",
        "schema_version": "0.1",
        "register_id": "unit-register",
        "generated_at": "2026-07-01T00:00:00Z",
        "owner": "security-governance",
        "records": records,
    }


def _write_evidence_package(path: Path, *, decision: str = "Not Approved", score: int = 41) -> Path:
    path.mkdir(parents=True)
    write_json(path / "scan-summary.json", _summary(decision, score))
    write_json(path / "findings.json", [_finding()])
    write_json(path / "gaps.json", [_gap()])
    write_json(path / "decision-packet.json", {
        "schema": "manifestiq-decision-packet",
        "schema_version": "0.1",
        "decision": {"value": decision, "score": score},
    })
    (path / "final-report.html").write_text("<html><body><h2>Decision Packet</h2></body></html>", encoding="utf-8")
    return path


def test_missing_exception_register_returns_no_exceptions_provided():
    from scanner.core.risk_acceptance import build_risk_acceptance_review

    normalized, review = build_risk_acceptance_review(
        exception_register=None,
        summary=_summary(),
        findings=[_finding()],
        gaps=[_gap()],
    )

    assert normalized["records"] == []
    assert review["review_status"] == "No Exceptions Provided"
    assert review["raw_decision"] == "Not Approved"
    assert review["raw_score"] == 41


def test_valid_exception_register_covers_matching_material_finding_and_gap():
    from scanner.core.risk_acceptance import build_risk_acceptance_review

    record = _record(scope={
        "profiles": ["finance-sox"],
        "source_paths": ["tests/sample_projects/insecure-python"],
        "rule_ids": ["SEC-001", "OPS-001"],
        "finding_ids": ["finding-sec"],
        "gap_ids": ["gap-ops"],
        "domains": ["Security", "Operations"],
    })
    normalized, review = build_risk_acceptance_review(
        exception_register=_register([record]),
        summary=_summary(),
        findings=[_finding()],
        gaps=[_gap(gap_id="gap-sec", domain="Security", related_rules=["SEC-001"])],
    )

    assert normalized["records"][0]["status"] == "valid"
    assert normalized["records"][0]["covered_finding_ids"] == ["finding-sec"]
    assert normalized["records"][0]["covered_gap_ids"] == ["gap-sec"]
    assert review["coverage_summary"]["material_findings_covered"] == 1
    assert review["coverage_summary"]["material_gaps_covered"] == 1
    assert review["review_status"] == "Covered With Active Exceptions"


def test_expired_exception_is_expired_and_does_not_cover_risk():
    from scanner.core.risk_acceptance import build_risk_acceptance_review

    normalized, review = build_risk_acceptance_review(
        exception_register=_register([_record(expires_at="2026-01-01T00:00:00Z")]),
        summary=_summary(),
        findings=[_finding()],
        gaps=[],
    )

    assert normalized["records"][0]["status"] == "expired"
    assert normalized["records"][0]["covered_finding_ids"] == []
    assert review["coverage_summary"]["expired_exceptions"] == 1
    assert review["review_status"] == "Expired Or Invalid Exceptions Present"


def test_draft_rejected_and_revoked_exceptions_do_not_cover_risk():
    from scanner.core.risk_acceptance import build_risk_acceptance_review

    normalized, review = build_risk_acceptance_review(
        exception_register=_register([
            _record(exception_id="EXC-DRAFT", status="draft"),
            _record(exception_id="EXC-REJECTED", status="rejected"),
            _record(exception_id="EXC-REVOKED", status="revoked"),
        ]),
        summary=_summary(),
        findings=[_finding()],
        gaps=[],
    )

    assert [record["status"] for record in normalized["records"]] == ["draft", "rejected", "revoked"]
    assert review["coverage_summary"]["material_findings_covered"] == 0
    assert review["review_status"] == "Expired Or Invalid Exceptions Present"


def test_missing_required_fields_make_record_invalid():
    from scanner.core.risk_acceptance import build_risk_acceptance_review

    bad_record = _record(reason="", risk_statement="", owner="", approved_by="")
    normalized, review = build_risk_acceptance_review(
        exception_register=_register([bad_record]),
        summary=_summary(),
        findings=[_finding()],
        gaps=[],
    )

    assert normalized["records"][0]["status"] == "invalid"
    assert {"reason is required", "risk_statement is required", "owner is required", "approved_by is required"} <= set(normalized["records"][0]["validation_errors"])
    assert review["coverage_summary"]["invalid_exceptions"] == 1


def test_scope_mismatch_does_not_cover_risk():
    from scanner.core.risk_acceptance import build_risk_acceptance_review

    normalized, review = build_risk_acceptance_review(
        exception_register=_register([_record(scope={"profiles": ["enterprise"], "rule_ids": ["SEC-001"]})]),
        summary=_summary(),
        findings=[_finding()],
        gaps=[],
    )

    assert normalized["records"][0]["status"] == "scope_mismatch"
    assert review["coverage_summary"]["material_findings_uncovered"] == 1


def test_required_approval_roles_are_enforced_by_category():
    from scanner.core.risk_acceptance import build_risk_acceptance_review

    cases = [
        (_finding(rule_id="SEC-001", category="Security", severity="Critical"), "Security Architecture", "critical security findings require CISO or AppSec role"),
        (_finding(rule_id="SOX-001", category="SOX", severity="High"), "Release Manager / Control Owner", "SOX/Finance findings require ITGC / SOX Reviewer or CISO"),
        (_finding(rule_id="AI-001", category="AI Model Risk", severity="High"), "AppSec", "AI/model risk findings require CISO, Data Governance, or Security Architecture"),
        (_finding(rule_id="LIC-004", category="License Risk", severity="High"), "AppSec", "license findings require Legal / Open Source Review or CISO"),
        (_finding(rule_id="ARCH-001", category="Architecture", severity="High"), "DevOps / SRE", "architecture findings require CTO / Enterprise Architecture or Security Architecture"),
        (_finding(rule_id="OPS-001", category="Operations", severity="High"), "CISO", "operational readiness findings require DevOps / SRE or Release Manager / Control Owner"),
    ]
    for finding, role, expected_error in cases:
        record = _record(approved_role=role, scope={"rule_ids": [finding["rule_id"]], "domains": [finding["category"]]})
        normalized, _ = build_risk_acceptance_review(
            exception_register=_register([record]),
            summary=_summary(),
            findings=[finding],
            gaps=[],
        )
        assert expected_error in normalized["records"][0]["validation_errors"]
        assert normalized["records"][0]["covered_finding_ids"] == []


def test_review_status_is_partially_covered_when_some_material_risks_uncovered():
    from scanner.core.risk_acceptance import build_risk_acceptance_review

    normalized, review = build_risk_acceptance_review(
        exception_register=_register([_record(scope={"rule_ids": ["SEC-001"], "domains": ["Security"]})]),
        summary=_summary(),
        findings=[_finding(), _finding(finding_id="finding-data", rule_id="DATA-001", category="Data Protection", severity="High", decision_impact="Mandatory Review")],
        gaps=[],
    )

    assert normalized["records"][0]["status"] == "valid"
    assert review["review_status"] == "Partially Covered"
    assert review["coverage_summary"]["material_findings_covered"] == 1
    assert review["coverage_summary"]["material_findings_uncovered"] == 1


def test_apply_exceptions_updates_evidence_package_packet_manifest_and_report(tmp_path):
    from scanner.core.risk_acceptance import apply_exception_register_to_evidence_package

    evidence = _write_evidence_package(tmp_path / "evidence-package")
    register_path = tmp_path / "register.json"
    write_json(register_path, _register([_record(scope={"rule_ids": ["SEC-001"], "domains": ["Security"]})]))

    result = apply_exception_register_to_evidence_package(evidence, register_path, evidence)

    manifest = json.loads((evidence / "manifest.json").read_text(encoding="utf-8"))
    packet = json.loads((evidence / "decision-packet.json").read_text(encoding="utf-8"))
    report = (evidence / "final-report.html").read_text(encoding="utf-8")
    paths = {item["path"] for item in manifest["files"]}

    assert result["review"]["raw_decision"] == "Not Approved"
    assert result["review"]["raw_score"] == 41
    assert "risk-acceptance-review.json" in paths
    assert "exception-register-normalized.json" in paths
    assert "risk-acceptance-review.md" in paths
    assert packet["risk_acceptance"]["review_status"] == "Partially Covered"
    assert "Risk Acceptance" in report
    assert "risk-acceptance-review.json" in report


def test_scan_folder_exception_register_cli_generates_risk_acceptance_outputs(tmp_path):
    register_path = Path("governance/examples/sample-exception-register.json")
    runner = CliRunner()
    result = runner.invoke(app, [
        "scan-folder",
        "--path",
        "tests/sample_projects/insecure-python",
        "--output",
        str(tmp_path / "out"),
        "--profile",
        "finance-sox",
        "--exception-register",
        str(register_path),
    ])

    assert result.exit_code == 0
    evidence = tmp_path / "out" / "evidence-package"
    review = json.loads((evidence / "risk-acceptance-review.json").read_text(encoding="utf-8"))
    packet = json.loads((evidence / "decision-packet.json").read_text(encoding="utf-8"))
    summary = json.loads((evidence / "scan-summary.json").read_text(encoding="utf-8"))

    assert review["raw_decision"] == summary["decision"]
    assert review["raw_score"] == summary["score"]
    assert packet["decision"]["value"] == summary["decision"]
    assert "risk_acceptance" in packet
