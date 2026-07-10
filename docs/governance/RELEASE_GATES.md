# Release Gates

## Purpose

Release gates define the minimum evidence required before a scanner version, ruleset version, or validation methodology is released for internal validation, pilot, or production use.

## Required Gates

A release candidate must pass or explicitly disposition:

1. Unit tests.
2. Integration tests.
3. Sample scans.
4. Evidence package generation.
5. Manifest completeness check.
6. Adversarial validation.
7. Gold set validation where available.
8. Portfolio validation where available.
9. Trend validation gate where baseline exists.
10. Rule contract validation when available.
11. Documentation completeness.
12. Known limitations update.
13. Changelog update.
14. No hidden skipped analyzers.
15. Determinism check.

## Release Statuses

| Status | Meaning |
| --- | --- |
| Blocked | A blocking gate failed or required evidence is missing. |
| Conditional | Non-blocking warnings exist and require accepted-risk approval. |
| Approved for internal validation | Suitable for controlled internal validation only. |
| Approved for pilot | Suitable for limited pilot use with accountable reviewers. |
| Approved for production use | Suitable for governed production use under documented constraints. |

## Blocking Conditions

The release is blocked when:

- Tests fail.
- Evidence package generation fails.
- Manifest is incomplete.
- Analyzer failures are hidden.
- Determinism check fails.
- Critical miss rate exceeds the approved threshold in applicable validation.
- Evidence traceability falls below the approved threshold.
- Detectable recall falls below the approved threshold.
- A high-impact change lacks required approval.
- Documentation claims exceed implemented behavior.

## Conditional Conditions

The release is conditional when:

- Warning thresholds are breached but accepted by accountable reviewers.
- Validation coverage is incomplete but limitations are explicit.
- Gold set or portfolio validation is unavailable for the affected area.
- Documentation is complete but pending final business approval.

## Determinism Check

For representative sample inputs, repeated runs should produce equivalent findings, scores, decisions, evidence graph outputs, and report decisions, excluding timestamps, output paths, and expected package hashes.

## Release Evidence

Release evidence should include:

- Test command and result.
- Sample scan command and result.
- Validation command and result where applicable.
- Trend gate result where applicable.
- Known limitations.
- Approval status.
- Release status.

## Governance Evidence Command

Generate a local governance evidence packet with:

```bash
python -m scanner governance-check --output governance-output
```

The command writes:

- `governance-output/governance-check-report.json`
- `governance-output/release-evidence.json`

The command does not run tests, sample scans, gold set validation, portfolio validation, or trend validation. It marks those statuses as `unknown` or `Not Evaluated` unless a future release workflow supplies real evidence.

## Release Evidence Intake Command

Summarize provided release evidence and generate a Go/No-Go report with:

```bash
python -m scanner prepare-release-evidence --manifest governance/examples/sample-release-manifest.json --output release-output
```

The command writes:

- `release-output/release-evidence.json`
- `release-output/release-go-no-go-report.json`

This command does not run tests and does not approve releases. It ingests existing evidence files from the manifest, marks missing evidence explicitly, and requires an approval record before a Go decision can be made.

## Test Evidence Collector

Generate a test summary from real pytest JUnit XML:

```bash
python -m pytest --junitxml governance-output/pytest-results.xml
python -m scanner collect-test-evidence --junit governance-output/pytest-results.xml --command "python -m pytest --junitxml governance-output/pytest-results.xml" --output governance-output
```

This writes:

- `governance-output/test_result_summary.json`

The collector does not approve releases and does not replace adversarial, gold set, portfolio, or trend validation. It only creates a deterministic test summary artifact for governance evidence.

## Sample Scan Evidence Collector

Generate a sample scan summary from a real scanner evidence package:

```bash
python -m scanner scan-folder --path tests/sample_projects/insecure-python --output output --profile finance-sox
python -m scanner collect-scan-evidence --evidence-package output/evidence-package --command "python -m scanner scan-folder --path tests/sample_projects/insecure-python --output output --profile finance-sox" --output governance-output
```

This writes:

- `governance-output/sample_scan_summary.json`

The collector summarizes evidence-collection status only. It does not turn a failed scanner decision into failed evidence collection, and it does not infer release approval.

## Recommended Release Evidence Sequence

```bash
python -m scanner governance-check --output governance-output
python -m pytest --junitxml governance-output/pytest-results.xml
python -m scanner collect-test-evidence --junit governance-output/pytest-results.xml --command "python -m pytest --junitxml governance-output/pytest-results.xml" --output governance-output
python -m scanner scan-folder --path tests/sample_projects/insecure-python --output output --profile finance-sox
python -m scanner collect-scan-evidence --evidence-package output/evidence-package --command "python -m scanner scan-folder --path tests/sample_projects/insecure-python --output output --profile finance-sox" --output governance-output
python -m scanner prepare-release-evidence --manifest governance/examples/sample-release-manifest.json --output release-output
```
