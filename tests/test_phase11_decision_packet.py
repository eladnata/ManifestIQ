import json
from pathlib import Path

from scanner.core.orchestrator import run_scan
from scanner.core.workspace import prepare_folder_workspace


def _summary(decision: str = "Conditional Approval", score: int = 82) -> dict:
    return {
        "scan_id": "scan_unit",
        "scanner_version": "test",
        "ruleset_version": "rules-hash",
        "profile": "finance-sox",
        "source_metadata": {
            "source_type": "folder",
            "source_path": "tests/sample_projects/insecure-python",
        },
        "decision": decision,
        "score": score,
        "blocking_gates": [
            {
                "finding_id": "finding-critical",
                "rule_id": "SEC-001",
                "severity": "Critical",
                "category": "Security",
                "title": "Hardcoded secret",
                "decision_impact": "Block",
            }
        ],
    }


def _findings() -> list[dict]:
    return [
        {
            "finding_id": "finding-high-review",
            "rule_id": "LIC-004",
            "category": "License Risk",
            "severity": "High",
            "confidence": "High",
            "title": "Unknown license",
            "description": "License review is required.",
            "file_path": "package.json",
            "line_start": 1,
            "decision_impact": "Mandatory Review",
            "requires_approval_from": ["Legal"],
            "remediation": ["Review dependency license before approval"],
        },
        {
            "finding_id": "finding-critical",
            "rule_id": "SEC-001",
            "category": "Security",
            "severity": "Critical",
            "confidence": "High",
            "title": "Hardcoded secret",
            "description": "A hardcoded secret was detected.",
            "file_path": "app.py",
            "line_start": 12,
            "decision_impact": "Block",
            "requires_approval_from": ["AppSec", "CISO"],
            "remediation": ["Remove the secret and rotate credentials"],
        },
        {
            "finding_id": "finding-high-block",
            "rule_id": "DATA-001",
            "category": "Data Protection",
            "severity": "High",
            "confidence": "Medium",
            "title": "Sensitive data indicator",
            "description": "Sensitive data was detected.",
            "file_path": "sample_customers.csv",
            "line_start": 1,
            "decision_impact": "Block",
            "requires_approval_from": ["Security"],
            "remediation": ["Classify and protect sensitive data"],
        },
    ]


def _gaps() -> list[dict]:
    return [
        {
            "gap_id": "gap-ops",
            "title": "Missing runbook",
            "domain": "Operations",
            "severity": "High",
            "decision_impact": "Mandatory Review",
            "required_remediation": ["Add a runbook"],
            "related_findings": ["finding-ops"],
            "related_rules": ["OPS-001"],
        },
        {
            "gap_id": "gap-arch",
            "title": "Missing architecture evidence",
            "domain": "Architecture",
            "severity": "Critical",
            "decision_impact": "Block",
            "required_remediation": ["Add architecture evidence"],
            "related_findings": ["finding-arch"],
            "related_rules": ["ARCH-001"],
        },
    ]


def _acceptance_matrix() -> dict:
    return {
        "domains": [
            {"domain": "Security", "status": "Blocked"},
            {"domain": "License", "status": "Mandatory Review"},
            {"domain": "Operations", "status": "Conditional"},
            {"domain": "Delivery", "status": "Accepted"},
            {"domain": "External Egress", "status": "Insufficient Evidence"},
        ]
    }


def _system_dossier() -> dict:
    return {
        "technical_summary": {
            "languages": {"Python": 2},
            "package_managers": ["pip"],
        },
        "control_context": {
            "profile": "finance-sox",
            "external_egress_detected": True,
            "ai_model_usage_detected": False,
            "sensitive_data_indicators_detected": True,
            "financial_indicators_detected": True,
        },
        "limitations": ["The dossier is derived only from deterministic local static analysis."],
    }


def test_decision_packet_preserves_scanner_decision_and_orders_top_risks():
    from scanner.core.decision_packet import build_decision_packet

    packet = build_decision_packet(
        summary=_summary(),
        findings=_findings(),
        gaps=_gaps(),
        confidence_summary={
            "confidence_counts": {"High": 3, "Medium": 1, "Low": 1},
            "low_confidence_domains": ["External Egress"],
            "limitations": ["Confidence is deterministic and based only on local static evidence."],
        },
        acceptance_matrix=_acceptance_matrix(),
        system_dossier=_system_dossier(),
        control_context=_system_dossier()["control_context"],
        manifest={"files": [{"path": "findings.json", "sha256": "abc"}], "package_sha256": "pkg"},
    )

    assert packet["schema"] == "manifestiq-decision-packet"
    assert packet["decision"]["value"] == "Conditional Approval"
    assert packet["decision"]["score"] == 82
    assert [risk["finding_id"] for risk in packet["top_risks"]] == [
        "finding-critical",
        "finding-high-block",
        "finding-high-review",
    ]


def test_decision_packet_derives_reviewers_acceptance_confidence_and_non_claims():
    from scanner.core.decision_packet import build_decision_packet

    packet = build_decision_packet(
        summary=_summary("Not Approved", 0),
        findings=_findings(),
        gaps=_gaps(),
        confidence_summary={
            "confidence_counts": {"High": 1, "Medium": 1, "Low": 2},
            "low_confidence_domains": ["External Egress"],
            "limitations": ["Confidence is deterministic and based only on local static evidence."],
        },
        acceptance_matrix=_acceptance_matrix(),
        system_dossier=_system_dossier(),
        control_context=_system_dossier()["control_context"],
        manifest={"files": [{"path": "gaps.json", "sha256": "def"}], "package_sha256": "pkg"},
    )

    assert packet["acceptance_summary"]["blocked_domains"] == ["Security"]
    assert packet["acceptance_summary"]["mandatory_review_domains"] == ["License"]
    assert packet["acceptance_summary"]["conditional_domains"] == ["Operations"]
    assert packet["acceptance_summary"]["accepted_domains"] == ["Delivery"]
    assert packet["acceptance_summary"]["insufficient_evidence_domains"] == ["External Egress"]
    assert packet["confidence_summary"]["overall_confidence"] == "Low"
    assert "External Egress" in packet["confidence_summary"]["low_confidence_areas"]
    assert "AppSec" in packet["required_reviewers"]
    assert "CISO" in packet["required_reviewers"]
    assert "ITGC / SOX Reviewer" in packet["required_reviewers"]
    assert "Security Architecture" in packet["required_reviewers"]
    assert "Legal / Open Source Review" in packet["required_reviewers"]
    assert any("does not certify compliance" in item for item in packet["non_claims"])
    assert packet["evidence_references"]


def test_decision_packet_markdown_is_generated_from_json_packet():
    from scanner.core.decision_packet import build_decision_packet, render_decision_packet_markdown

    packet = build_decision_packet(
        summary=_summary("Not Approved", 0),
        findings=_findings(),
        gaps=_gaps(),
        confidence_summary={"confidence_counts": {"High": 2}, "low_confidence_domains": [], "limitations": []},
        acceptance_matrix=_acceptance_matrix(),
        system_dossier=_system_dossier(),
        control_context=_system_dossier()["control_context"],
        manifest=None,
    )
    markdown = render_decision_packet_markdown(packet)

    assert markdown.startswith("# ManifestIQ Decision Packet")
    assert "## Decision" in markdown
    assert "## Required Reviewers" in markdown
    assert "This packet does not certify compliance." in markdown


def test_sample_scan_generates_decision_packet_manifest_and_report_section(tmp_path):
    source = Path("tests/sample_projects/insecure-python")
    workspace = prepare_folder_workspace(source, tmp_path / "out")
    run_scan(workspace, profile="finance-sox", scanner_version="test")
    evidence = tmp_path / "out" / "evidence-package"

    packet = json.loads((evidence / "decision-packet.json").read_text(encoding="utf-8"))
    manifest = json.loads((evidence / "manifest.json").read_text(encoding="utf-8"))
    report = (evidence / "final-report.html").read_text(encoding="utf-8")

    manifest_paths = {item["path"] for item in manifest["files"]}
    assert packet["schema"] == "manifestiq-decision-packet"
    assert packet["decision"]["value"] == json.loads((evidence / "scan-summary.json").read_text(encoding="utf-8"))["decision"]
    assert "decision-packet.json" in manifest_paths
    assert (evidence / "decision-packet.md").exists()
    assert "decision-packet.md" in manifest_paths
    assert "Decision Packet" in report
    assert "decision-packet.json" in report
