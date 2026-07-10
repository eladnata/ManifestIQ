# Release Hardening and Self-Assurance

## Purpose

This phase prepares local release candidate evidence for ManifestIQ. It summarizes governance readiness, test evidence, sample scan evidence, self-assurance evidence, release manifest inputs, known limitations, and release readiness status.

The output is for expert release review. It does not approve a release.

## Scope

The release hardening pack uses local deterministic artifacts already produced by ManifestIQ commands. It reads governance output directories, optional release manifests, and an existing self-scan evidence package summary.

## Non-Goals

This workflow does not add cloud services, CI workflows, AI, telemetry, release approval automation, or compliance certification. It does not change scanner scoring or scanner decisions.

## Local Workflow

Recommended local workflow:

```bash
python -m scanner governance-check --output governance-output
python -m pytest --junitxml governance-output/pytest-results.xml
python -m scanner collect-test-evidence --junit governance-output/pytest-results.xml --command "python -m pytest --junitxml governance-output/pytest-results.xml" --output governance-output
python -m scanner scan-folder --path tests/sample_projects/insecure-python --output output --profile finance-sox --exception-register governance/examples/sample-exception-register.json
python -m scanner collect-scan-evidence --evidence-package output/evidence-package --command "python -m scanner scan-folder --path tests/sample_projects/insecure-python --output output --profile finance-sox --exception-register governance/examples/sample-exception-register.json" --output governance-output
python -m scanner scan-folder --path . --output self-assurance-output --profile enterprise
python -m scanner collect-self-assurance --evidence-package self-assurance-output/evidence-package --output release-candidate-output
python -m scanner prepare-release-candidate --release-manifest governance/examples/sample-release-manifest.json --governance-output governance-output --self-scan-output release-candidate-output --output release-candidate-output
```

When self-scanning with `--path .`, keep generated output directories ignored and do not commit runtime evidence folders.

## CLI Commands

`collect-self-assurance` summarizes an existing self-scan evidence package:

```bash
python -m scanner collect-self-assurance --evidence-package self-assurance-output/evidence-package --output release-candidate-output
```

`prepare-release-candidate` prepares the local release candidate pack:

```bash
python -m scanner prepare-release-candidate --release-manifest governance/examples/sample-release-manifest.json --governance-output governance-output --self-scan-output release-candidate-output --output release-candidate-output
```

## Required Input Artifacts

- `governance-output/governance-check-report.json`
- `governance-output/test_result_summary.json`
- `governance-output/sample_scan_summary.json`
- `release-candidate-output/self-assurance-summary.json`
- Optional release manifest JSON

Missing evidence is reported as missing. It is not inferred.

## Generated Output Artifacts

- `release-candidate-summary.json`
- `release-readiness-checklist.json`
- `self-assurance-summary.json`
- `release-candidate-summary.md`

## Release Readiness Status Semantics

- `Ready for Review`: required local evidence is present and passed or warning-only.
- `Conditional Review`: required evidence is missing, unknown, or requires reviewer attention.
- `Not Ready`: tests failed, self-assurance failed, or a required checklist item failed.
- `Not Evaluated`: insufficient data exists to evaluate readiness.

No status means release approval.

## Self-Assurance Limitations

Self-assurance summarizes a deterministic local scan of ManifestIQ itself. It does not certify ManifestIQ, approve a release, or replace expert review. Recursive generated output folders can affect self-scan results if they are not ignored or excluded.

## Non-Claims

The release candidate summary always states:

- This release candidate summary does not approve a release.
- This release candidate summary does not certify compliance.
- This release candidate summary does not replace release manager, CISO, CTO, AppSec, ITGC, SOX, Legal, Privacy, or architecture review.
- This release candidate summary is based only on local deterministic evidence artifacts available at generation time.

## Acceptance Criteria

- Release candidate summary is generated.
- Release readiness checklist is generated.
- Self-assurance summary is generated from an evidence package.
- Missing governance, test, sample scan, self-assurance, and manifest evidence is explicit.
- Failed tests or failed self-assurance produce `Not Ready`.
- Complete required local evidence produces `Ready for Review`.
- Non-claims are present.
- Generated runtime output folders are not committed.
