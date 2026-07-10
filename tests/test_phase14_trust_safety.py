import json
from pathlib import Path

from typer.testing import CliRunner

from scanner.app.cli import app
from scanner.core.evidence import write_json


REQUIRED_DOMAINS = [
    "Trust Boundary",
    "Evidence Integrity",
    "Decision Semantics",
    "Failure Safety",
    "Non-Claims",
    "Local-Only Execution",
    "Raw Evidence Preservation",
    "Missing Evidence Handling",
    "Risk Acceptance Boundary",
    "Release Readiness Boundary",
    "Threat and Misuse Model",
    "Data Protection and Artifact Hygiene",
    "Secure Engineering",
    "Regulatory and Governance Alignment",
]


def _write_doc(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _build_internal_docs(root: Path, *, trust_boundary_extra: str = "", doctrine_extra: str = "") -> Path:
    docs = root / "docs" / "internal"
    _write_doc(docs / "README.md", """# ManifestIQ Internal Doctrine - Index

## Purpose

Index only.

## Top-Level Doctrine

[TRUST_SAFETY_DOCTRINE](TRUST_SAFETY_DOCTRINE.md) is the top-level doctrine.
""")
    _write_doc(docs / "TRUST_SAFETY_DOCTRINE.md", f"""# ManifestIQ Trust and Safety Doctrine

## 1. Purpose

Doctrine.

## 2. Core Principle

ManifestIQ must be trusted to preserve truth, not to manufacture confidence.
ManifestIQ MUST fail closed, never fail open.
Ready for Review MUST NEVER be treated as approval.
ManifestIQ is a local-first, deterministic, non-AI, non-cloud platform.
ManifestIQ MUST NOT use AI inference, LLM calls, embeddings, cloud services, telemetry, or any external source transmission.
{doctrine_extra}
""")
    _write_doc(docs / "EVIDENCE_INTEGRITY_STANDARD.md", """# ManifestIQ Evidence Integrity Standard

## 1. Purpose

Evidence integrity.

## 9. Integrity Manifest and Provenance

Each raw and derived artifact MUST carry a content integrity value.
Every run MUST produce a manifest recording version, configuration, scan scope, timestamps, and integrity values.
A derived summary MUST reference the integrity values of the raw evidence it was derived from so every result is traceable.
ManifestIQ MUST NOT hide, suppress, delete, downgrade, or mutate raw findings.
Raw findings MUST be retained verbatim.
Missing evidence MUST be an explicit first-class finding or limitation.
ManifestIQ MUST NOT present missing evidence as acceptable.
Missing artifacts MUST be surfaced as Missing Evidence.
Stale artifacts MUST be flagged stale.
Corrupted artifacts MUST fail closed.
Deterministic regeneration MUST be confirmed by matching integrity values.
""")
    _write_doc(docs / "FAILURE_SAFETY_STANDARD.md", """# ManifestIQ Failure Safety Standard

## 1. Purpose

Failure safety.

## 3. Core Rule

ManifestIQ MUST fail closed, never fail open.
""")
    _write_doc(docs / "DECISION_SEMANTICS_STANDARD.md", """# ManifestIQ Decision Semantics Standard

## 1. Purpose

Decision semantics.

## 2. Raw Scanner Decision Separation

Raw scanner decision and score remain separate from downstream summaries.

## 3. `Ready for Review` Is Not Approval

Ready for Review is not approval.
Risk acceptance is not remediation or approval.
Release readiness is not release approval.
Misuse controls address status laundering and exception misuse across M1-M7.

## 4. Forbidden Unsupported Language

Approved
Certified
Compliant
Safe
Production Ready
SOX Approved
Privacy Approved
Legally Approved
Fully Secure
""")
    _write_doc(docs / "TRUST_BOUNDARY_AND_NON_CLAIMS.md", f"""# ManifestIQ Trust Boundary and Non-Claims

## 1. Purpose

Trust boundary.

## 4. Non-Claims

ManifestIQ does not certify ManifestIQ.
ManifestIQ does not approve a release.

## 5. Forbidden Unsupported Language

Approved
Certified
Compliant
Safe
Production Ready
SOX Approved
Privacy Approved
Legally Approved
Fully Secure

## 7. Data Boundary (No External Transmission)

ManifestIQ MUST NOT transmit source code, evidence, repository metadata, findings, or generated artifacts to any external service.
ManifestIQ MUST NOT perform external enrichment.
ManifestIQ MUST NOT emit telemetry.
ManifestIQ MUST NOT perform silent or background network calls.
Dependency responsibility is transitive through all dependencies.
{trust_boundary_extra}
""")
    _write_doc(docs / "THREAT_AND_MISUSE_MODEL.md", """# ManifestIQ Threat and Misuse Model

## 1. Purpose

Threat model.

## 3. Adversaries and Controlling Properties

A1 untrusted repository content
A2 user seeking a favorable result
A3 evidence-store tamperer
A4 compromised or malicious dependency
A5 exfiltration via the tool
A6 careless or coerced operator

## 5. Misuse and Abuse Scenarios

M1 status laundering
M2 exception abuse
M3 stale-evidence reuse
M4 selective omission
M5 partial-as-complete
M6 approval implication
M7 silent exfiltration
""")
    _write_doc(docs / "DATA_PROTECTION_AND_ARTIFACT_HYGIENE.md", """# ManifestIQ Data Protection and Artifact Hygiene

## 1. Purpose

Data protection.

## 2. Local-Only Handling

Source and evidence remain within the local environment and remain local only.

## 4. Secrets, Credentials, and Personal Data

Secrets, credentials, and PII handling must be explicit.
Redaction expectations apply to derived outputs.

## 5. Artifact Sensitivity Classification

Artifacts have sensitivity classification.
ManifestIQ must not imply that any artifact is externally safe to share.
""")
    _write_doc(docs / "SECURE_ENGINEERING_STANDARD.md", """# ManifestIQ Secure Engineering Standard

## 1. Purpose

Secure engineering.

## 3. Dependency Discipline

Dependencies must be minimal.
Secure defaults are required.
Test coverage is required.
Dependency discipline is required.
The no-transmission, no-telemetry discipline is required.
No AI, no telemetry, and no network dependency are allowed in the analysis flow.
ManifestIQ must not depend on any component that introduces AI inference.

## 6. Test Discipline

Test discipline is required.
""")
    _write_doc(docs / "REGULATORY_AND_GOVERNANCE_ALIGNMENT.md", """# ManifestIQ Regulatory and Governance Alignment

## 1. Purpose

Governance alignment.

## 2. ASDLC and Secure SDLC Framing

ASDLC / secure SDLC framing applies.

## 3. SOX and ITGC Framing

SOX / ITGC framing applies.

## 4. Privacy and Legal Framing

Privacy / legal framing applies.

## 5. Release Governance Framing

Release governance framing applies.
ManifestIQ must not claim certification or approval.
""")
    return docs


def _write_evidence_package(path: Path, *, include_manifest: bool = True, manifest_hash: str | None = "abc123") -> Path:
    path.mkdir(parents=True, exist_ok=True)
    write_json(path / "scan-summary.json", {"decision": "Not Approved", "score": 41})
    write_json(path / "decision-packet.json", {"raw_decision": "Not Approved", "raw_score": 41})
    write_json(path / "risk-acceptance-review.json", {"raw_decision": "Not Approved", "raw_score": 41})
    write_json(path / "release-candidate-summary.json", {
        "release_readiness": {"status": "Not Ready"},
        "non_claims": ["This release candidate summary does not approve a release."],
    })
    if include_manifest:
        entry = {"path": "scan-summary.json"}
        if manifest_hash is not None:
            entry["sha256"] = manifest_hash
        write_json(path / "manifest.json", {"files": [entry], "package_sha256": "pkg"})
    return path


def test_trust_safety_review_json_is_generated(tmp_path):
    from scanner.governance.trust_safety import collect_trust_safety_review

    docs_root = _build_internal_docs(tmp_path)
    review = collect_trust_safety_review(repo_root=tmp_path, output_dir=tmp_path / "out")

    assert (tmp_path / "out" / "trust-safety-review.json").exists()
    assert review["schema"] == "manifestiq-trust-safety-review"
    assert any(ref.endswith("TRUST_SAFETY_DOCTRINE.md") for domain in review["domains"] for ref in domain["evidence_references"])
    assert (docs_root / "TRUST_SAFETY_DOCTRINE.md").exists()


def test_all_required_domains_exist(tmp_path):
    from scanner.governance.trust_safety import build_trust_safety_review

    _build_internal_docs(tmp_path)
    review = build_trust_safety_review(repo_root=tmp_path)

    domains = [item["domain"] for item in review["domains"]]
    assert domains == REQUIRED_DOMAINS


def test_missing_critical_trust_doctrine_produces_failed(tmp_path):
    from scanner.governance.trust_safety import build_trust_safety_review

    docs = _build_internal_docs(tmp_path)
    (docs / "TRUST_SAFETY_DOCTRINE.md").unlink()

    review = build_trust_safety_review(repo_root=tmp_path)

    assert review["review_status"] == "Failed"
    assert any("TRUST_SAFETY_DOCTRINE.md" in item for item in review["blocking_gaps"])


def test_missing_critical_trust_phrase_produces_failed(tmp_path):
    from scanner.governance.trust_safety import build_trust_safety_review

    _build_internal_docs(tmp_path, trust_boundary_extra="Network isolation text removed.")
    path = tmp_path / "docs" / "internal" / "TRUST_BOUNDARY_AND_NON_CLAIMS.md"
    path.write_text(path.read_text(encoding="utf-8").replace("ManifestIQ MUST NOT emit telemetry.\n", ""), encoding="utf-8")

    review = build_trust_safety_review(repo_root=tmp_path)

    assert review["review_status"] == "Failed"
    assert any(domain["domain"] == "Trust Boundary" and domain["status"] == "failed" for domain in review["domains"])


def test_non_claims_are_always_present(tmp_path):
    from scanner.governance.trust_safety import NON_CLAIMS, build_trust_safety_review

    _build_internal_docs(tmp_path)
    review = build_trust_safety_review(repo_root=tmp_path)

    assert review["non_claims"] == NON_CLAIMS


def test_unsupported_approval_language_is_detected(tmp_path):
    from scanner.governance.trust_safety import build_trust_safety_review

    _build_internal_docs(tmp_path, doctrine_extra="ManifestIQ is Fully Secure.\n")
    review = build_trust_safety_review(repo_root=tmp_path)

    assert review["review_status"] == "Failed"
    assert any("Fully Secure" in item for item in review["blocking_gaps"])


def test_forbidden_terms_allowed_when_explicitly_denied_or_listed(tmp_path):
    from scanner.governance.trust_safety import build_trust_safety_review

    _build_internal_docs(tmp_path)
    review = build_trust_safety_review(repo_root=tmp_path)

    assert review["review_status"] == "Passed"


def test_ready_for_review_is_not_treated_as_approval(tmp_path):
    from scanner.governance.trust_safety import build_trust_safety_review

    evidence = _write_evidence_package(tmp_path / "evidence-package")
    _build_internal_docs(tmp_path)
    write_json(evidence / "release-candidate-summary.json", {
        "release_readiness": {"status": "Ready for Review"},
        "non_claims": ["This release candidate summary does not approve a release."],
    })

    review = build_trust_safety_review(repo_root=tmp_path, evidence_package=evidence)

    assert review["review_status"] in {"Passed", "Warning"}
    assert not any("Ready for Review" in item and "approval" in item.lower() and "unsupported" in item.lower() for item in review["blocking_gaps"])


def test_missing_evidence_is_reported_explicitly(tmp_path):
    from scanner.governance.trust_safety import build_trust_safety_review

    _build_internal_docs(tmp_path)
    review = build_trust_safety_review(repo_root=tmp_path, evidence_package=tmp_path / "missing-evidence")

    assert review["review_status"] == "Warning"
    assert any("manifest" in item.lower() or "missing" in item.lower() for item in review["warnings"])


def test_cli_writes_expected_output(tmp_path):
    _build_internal_docs(tmp_path)
    runner = CliRunner()

    result = runner.invoke(app, ["trust-safety-check", "--repo-root", str(tmp_path), "--output", str(tmp_path / "trust-safety-output")])

    assert result.exit_code == 0
    out = tmp_path / "trust-safety-output"
    assert (out / "trust-safety-review.json").exists()
    assert (out / "trust-safety-review.md").exists()


def test_evidence_package_check_reports_manifest_artifact_limitations(tmp_path):
    from scanner.governance.trust_safety import build_trust_safety_review

    _build_internal_docs(tmp_path)
    evidence = _write_evidence_package(tmp_path / "evidence-package", manifest_hash=None)

    review = build_trust_safety_review(repo_root=tmp_path, evidence_package=evidence)

    assert review["review_status"] == "Warning"
    assert any("hash" in item.lower() for item in review["warnings"] + review["limitations"])


def test_missing_manifest_entry_file_is_reported(tmp_path):
    from scanner.governance.trust_safety import build_trust_safety_review

    _build_internal_docs(tmp_path)
    evidence = _write_evidence_package(tmp_path / "evidence-package")
    write_json(evidence / "manifest.json", {"files": [{"path": "missing.json", "sha256": "abc"}], "package_sha256": "pkg"})

    review = build_trust_safety_review(repo_root=tmp_path, evidence_package=evidence)

    assert review["review_status"] == "Failed"
    assert any("missing.json" in item for item in review["blocking_gaps"] + review["warnings"])
