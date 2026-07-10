from pathlib import Path


GOVERNANCE_DOCS = [
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
    "docs/governance/RISK_ACCEPTANCE_EXCEPTION_POLICY.md",
]

ADR_DOCS = [
    "docs/adr/ADR-0001-local-deterministic-non-ai.md",
    "docs/adr/ADR-0002-evidence-first-design.md",
    "docs/adr/ADR-0003-baseline-rulebook-governance.md",
    "docs/adr/ADR-0004-validation-gates-and-regression-control.md",
    "docs/adr/ADR-0005-no-ui-before-engine-stability.md",
]


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_governance_docs_exist():
    for doc in GOVERNANCE_DOCS:
        assert Path(doc).exists(), doc


def test_adr_docs_exist():
    for doc in ADR_DOCS:
        assert Path(doc).exists(), doc


def test_required_governance_document_headings_exist():
    expected_headings = {
        "docs/governance/SDLC_GOVERNANCE_MODEL.md": ["## Governed Lifecycle", "## Change Types and Required Artifacts"],
        "docs/governance/CHANGE_CONTROL_POLICY.md": ["## Change Request Record", "## High-Impact Changes"],
        "docs/governance/RELEASE_GATES.md": ["## Required Gates", "## Release Statuses"],
        "docs/governance/ENGINEERING_DEFINITION_OF_READY.md": ["## Ready Criteria", "## Product Boundary Check"],
        "docs/governance/ENGINEERING_DEFINITION_OF_DONE.md": ["## Done Criteria", "## Evidence Criteria"],
        "docs/governance/RACI.md": ["## Roles", "## RACI Matrix"],
        "docs/governance/ADR_POLICY.md": ["## ADR Required For", "## ADR Format"],
        "docs/governance/RULE_CHANGE_POLICY.md": ["## Baseline Rules", "## Custom Rules"],
        "docs/governance/QUALITY_METRICS.md": ["## Engineering Metrics", "## Validation Metrics"],
        "docs/governance/VALIDATION_GATE_POLICY.md": ["## Gate Types", "## Blocking Conditions"],
        "docs/governance/SECURE_DEVELOPMENT_POLICY.md": ["## Product Security Boundary", "## Safe Handling of Scanned Source Code"],
        "docs/governance/RISK_ACCEPTANCE_EXCEPTION_POLICY.md": ["## Purpose", "## Approval Role Logic", "## Acceptance Criteria"],
    }
    for doc, headings in expected_headings.items():
        text = _read(doc)
        for heading in headings:
            assert heading in text, f"{heading} missing from {doc}"


def test_adrs_use_required_structure():
    required_sections = [
        "## Status",
        "## Date",
        "## Context",
        "## Decision",
        "## Consequences",
        "## Alternatives Considered",
        "## Validation Impact",
        "## Related Files",
    ]
    for doc in ADR_DOCS:
        text = _read(doc)
        for section in required_sections:
            assert section in text, f"{section} missing from {doc}"


def test_master_spec_references_governance_pack():
    text = _read("MASTER_SPEC.md")
    assert "docs/governance/" in text
    assert "docs/adr/" in text
    assert "SDLC Governance" in text


def test_readme_references_governance_pack():
    text = _read("README.md")
    assert "docs/governance/" in text
    assert "docs/adr/" in text
    assert "SDLC Governance" in text
