# Governance Evidence Packet Specification

## Purpose

The governance evidence packet is a lightweight local evidence artifact for scanner releases and material changes. It converts SDLC governance policy into repeatable files that reviewers can inspect.

This is not a compliance certification. It is internal SDLC governance evidence. It supports traceable release decisions by showing which governance checks were evaluated and which release evidence is known, unknown, or not evaluated.

## Packet Contents

A governance evidence packet contains:

- `release-evidence.json`
- `governance-check-report.json`
- `release-go-no-go-report.json` when prepared from a release manifest
- Test result summary, when supplied by a release process
- Sample scan summary, when supplied by a release process
- Validation report references
- Trend gate result
- Rulebook version
- Scanner version
- Ruleset version
- Known limitations
- Release decision
- Approver role

## Governance Check Report

`governance-check-report.json` records deterministic repository checks:

- Required governance documents exist.
- Required ADRs exist.
- Required templates exist.
- Required schemas exist.
- `README.md` references governance.
- `MASTER_SPEC.md` references governance.
- `RULEBOOK_GOVERNANCE.md` exists.
- Validation documentation exists.
- Release gates documentation exists.
- Known limitations are documented somewhere in project docs.

The report status is:

- `Passed` when all required checks pass.
- `Warning` when required checks pass but cautionary conditions exist.
- `Failed` when one or more required checks fail.

## Release Evidence

`release-evidence.json` records release-preparation state:

```json
{
  "schema": "enterprise-whitebox-release-evidence",
  "schema_version": "0.1",
  "generated_at": "string",
  "scanner_version": "string|unknown",
  "ruleset_version": "string|unknown",
  "governance_check_status": "Passed|Warning|Failed",
  "test_status": "unknown|passed|failed",
  "validation_status": "unknown|passed|warning|failed",
  "release_gate_status": "Not Evaluated|Passed|Warning|Failed",
  "release_decision": "Not Requested|Blocked|Conditional|Approved for internal validation|Approved for pilot|Approved for production use",
  "evidence_files": [],
  "known_limitations": [],
  "recommendations": []
}
```

The governance check command does not run tests, sample scans, gold set validation, portfolio validation, or trend validation. If those results are not supplied by a future release workflow, they must remain `unknown` or `Not Evaluated`.

## Release Evidence Intake

Prepare release evidence from a manifest with:

```bash
python -m scanner prepare-release-evidence --manifest governance/examples/sample-release-manifest.json --output release-output
```

The command reads evidence paths from the release manifest and generates:

- `release-output/release-evidence.json`
- `release-output/release-go-no-go-report.json`

The command does not run tests, scans, validation suites, trend gates, or governance checks. It summarizes provided evidence. Missing evidence is explicitly marked as `missing`, `Missing`, `unknown`, or `Unknown` depending on the report field.

Approval is never inferred. A `Go` or `Conditional Go` status requires an approval record. Without an approval record, the Go/No-Go status remains `Not Evaluated` unless a blocking condition produces `No-Go`.

## Test Evidence Collection

Generate test evidence from pytest JUnit XML with:

```bash
python -m pytest --junitxml governance-output/pytest-results.xml
python -m scanner collect-test-evidence --junit governance-output/pytest-results.xml --command "python -m pytest --junitxml governance-output/pytest-results.xml" --output governance-output
```

The collector parses real JUnit XML evidence and writes:

- `governance-output/test_result_summary.json`

It does not run tests, approve a release, or replace validation suites. Missing, invalid, or zero-test XML produces `status: unknown` with notes.

## Sample Scan Evidence Collection

Generate sample scan evidence from an existing scanner evidence package with:

```bash
python -m scanner scan-folder --path tests/sample_projects/insecure-python --output output --profile finance-sox
python -m scanner collect-scan-evidence --evidence-package output/evidence-package --command "python -m scanner scan-folder --path tests/sample_projects/insecure-python --output output --profile finance-sox" --output governance-output
```

The collector parses the real evidence package and writes:

- `governance-output/sample_scan_summary.json`

It does not run the scan, approve a release, or change scanner decisions. A scanner decision such as `Not Approved` can still produce `status: passed` when the evidence package, manifest, and scan summary were generated and parsed correctly.

## Recommended Local Sequence

```bash
python -m scanner governance-check --output governance-output
python -m pytest --junitxml governance-output/pytest-results.xml
python -m scanner collect-test-evidence --junit governance-output/pytest-results.xml --command "python -m pytest --junitxml governance-output/pytest-results.xml" --output governance-output
python -m scanner scan-folder --path tests/sample_projects/insecure-python --output output --profile finance-sox
python -m scanner collect-scan-evidence --evidence-package output/evidence-package --command "python -m scanner scan-folder --path tests/sample_projects/insecure-python --output output --profile finance-sox" --output governance-output
python -m scanner prepare-release-evidence --manifest governance/examples/sample-release-manifest.json --output release-output
```

## Release Manifest Inputs

The release manifest may reference:

- Governance check report.
- Test result summary.
- Sample scan summary.
- Adversarial validation report.
- Gold set comparison report.
- Portfolio validation report.
- Validation trend report.
- Accepted warning records.
- Approval record.
- Known limitations.
- Release notes.

If an input path is null, missing, or unreadable, the generated Go/No-Go report records that state instead of assuming success.

## Traceability

The packet should link release decisions to:

- Governance check result.
- Test result summary.
- Sample scan summary.
- Validation report references.
- Trend gate status.
- Known limitations.
- Approver role.

## Go/No-Go Semantics

- `No-Go`: A blocking input failed, such as failed governance, failed tests, failed sample scan, failed trend gate, failed adversarial validation, or blocked approval.
- `Conditional Go`: Approval exists but warnings, accepted warnings, internal-validation limitations, or conditions remain.
- `Go`: Required evidence supports release, no blocking reasons exist, and an approval record approves the target.
- `Not Evaluated`: Approval context is missing or evidence is insufficient for a release decision.

## Limitations

The packet does not prove product quality, certify compliance, or replace CISO, CTO, AppSec, ITGC, SOX, Legal, Privacy, Architecture, or release-manager judgment. It prepares evidence for accountable review.
