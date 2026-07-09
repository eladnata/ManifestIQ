# Enterprise White-Box Code Assurance Scanner

Deterministic local scanner for enterprise code assurance, CISO/CTO review, AppSec triage, Security Engineering, DevSecOps, ITGC, and technical architecture evidence.

The scanner runs locally, uses static rule-based analysis, and produces tamper-evident evidence packages. It does not use AI, LLMs, cloud services, telemetry, or external source-code transmission.

## What It Scans

- Source files and project structure
- Dependency manifests
- Secrets and credential-like values
- SAST-style risky code patterns
- Risky configuration
- Sensitive data and SOX/Finance indicators
- Documentation and ownership evidence
- Maintainability and operations indicators
- Hidden AI/model usage, AI dependencies, model artifacts, external AI APIs, prompts, embeddings, and vector database indicators

## Outputs

Each scan writes an evidence package containing:

- `scan-summary.json`
- `source-metadata.json`
- `file-inventory.json`
- analyzer result JSON files
- `local-sbom.json`
- `rule-evaluation-results.json`
- `scoring-results.json`
- `findings.json`
- `final-report.html`
- `manifest.json`
- `sha256.txt`

## Quick Start

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the included sample scan:

```bash
python -m scanner scan-folder --path tests/sample_projects/insecure-python --output output --profile finance-sox
```

Open:

```text
output/evidence-package/final-report.html
```

## Commands

```bash
python -m scanner scan-folder --path <folder> --output <output-dir> --profile enterprise
python -m scanner scan-zip --file <zip-file> --output <output-dir> --profile enterprise
python -m scanner scan-git --url <repo-url> --branch main --output <output-dir> --profile enterprise
```

## Profiles

- `sandbox`
- `team-use`
- `department-use`
- `enterprise`
- `finance-sox`
- `ai-enabled`
- `production-critical`

## Rulebook Governance

Built-in baseline rules are immutable. Custom rules may be added under `rules/custom/`, but they cannot override baseline rule IDs. Baseline rule disablement requests generate governance findings and are included in the evidence package.

## SDLC Governance

The scanner is developed under a formal governance pack in `docs/governance/`, with Architecture Decision Records in `docs/adr/`. The pack defines change control, release gates, engineering definition of ready, engineering definition of done, RACI, ADR policy, rule change policy, quality metrics, validation gate policy, and secure development policy.

Future material changes to analyzers, rules, profiles, scoring, decision logic, evidence schemas, validation thresholds, reports, or CLI behavior must preserve the product constraints: local-first, deterministic, offline-capable, non-AI, no cloud dependency, no telemetry, evidence-first, conservative by default, and English-only.

Generate local governance evidence:

```bash
python -m scanner governance-check --output governance-output
```

This writes `governance-check-report.json` and `release-evidence.json`. It does not run tests or validation suites, so those statuses remain `unknown` unless supplied by a separate release workflow.

Prepare release evidence and a Go/No-Go report from an evidence manifest:

```bash
python -m scanner prepare-release-evidence --manifest governance/examples/sample-release-manifest.json --output release-output
```

This command does not run tests, scans, validation suites, or approvals. It summarizes provided evidence, marks missing evidence explicitly, and requires an approval record before approval can be represented.

Recommended local release evidence sequence:

```bash
python -m scanner governance-check --output governance-output
python -m pytest --junitxml governance-output/pytest-results.xml
python -m scanner collect-test-evidence --junit governance-output/pytest-results.xml --command "python -m pytest --junitxml governance-output/pytest-results.xml" --output governance-output
python -m scanner prepare-release-evidence --manifest governance/examples/sample-release-manifest.json --output release-output
```

`collect-test-evidence` parses real pytest JUnit XML and writes `test_result_summary.json`. It does not run tests, approve a release, or replace validation suites.

## Tests

```bash
python -m pytest
```

## Disclaimer

This scanner is a deterministic static assurance tool. It does not replace penetration testing, secure code review, privacy review, legal review, architecture review, or formal SOX/control assessment where required.
