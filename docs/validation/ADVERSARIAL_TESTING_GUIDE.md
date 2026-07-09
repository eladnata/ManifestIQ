# Adversarial Testing Guide

Adversarial testing verifies that the scanner remains conservative when repositories are difficult, misleading, or intentionally evasive.

The scanner must remain local-first, deterministic, offline-capable, non-AI, evidence-first, conservative by default, and English-only.

## Scenario Catalog

### Split Secrets

Goal:

- Verify whether secrets split across variables or strings are detected or explicitly recorded as a limitation.

Expected behavior:

- Direct secrets should be detected.
- Split secrets not supported by current rules should become validation gaps for future analyzer work.

### Hidden AI / Model Usage

Goal:

- Detect AI dependencies, provider endpoints, prompts, embeddings, vector database use, and local model artifacts.

Expected behavior:

- Hidden AI/model indicators produce AI Model Risk findings and signals.
- Strict profiles block or require mandatory review when declaration evidence is missing.

### Renamed Model Artifacts

Goal:

- Verify whether model-like artifacts renamed with common extensions are detected.

Expected behavior:

- Known model extensions and filenames are detected.
- Unsupported renamed artifacts are tracked as adversarial limitations.

### External Egress Through Wrappers

Goal:

- Detect outbound calls wrapped by helper functions or indirect client code.

Expected behavior:

- Direct network calls without timeout evidence produce operations findings.
- Explicit AI provider URLs produce AI/model egress findings.

### Empty Or Misleading Documentation

Goal:

- Ensure placeholder documentation does not suppress missing evidence gaps.

Expected behavior:

- Empty or misleading docs should not count as strong evidence when analyzers support content validation.
- Until content validation exists, adversarial fixtures should capture this limitation.

### Fake Health Checks

Goal:

- Detect superficial health-check claims that are not implemented or connected to runtime.

Expected behavior:

- Code/config health indicators are stronger than claims in README-only text.
- Weak documentation-only evidence should have lower confidence or remain a validation limitation.

### Print-Only Logging

Goal:

- Ensure console/print statements do not satisfy enterprise logging expectations.

Expected behavior:

- Print-only logging produces operational findings.

### Committed Binaries

Goal:

- Detect committed binary artifacts requiring provenance and license review.

Expected behavior:

- Binary artifacts produce Architecture, Supply Chain, or License findings.

### Local Databases

Goal:

- Detect committed local database files and storage without recovery evidence.

Expected behavior:

- Local database artifacts produce critical or mandatory-review findings in strict profiles.

### Mixed Applications

Goal:

- Detect repositories containing multiple unrelated applications or multiple dependency ecosystems without clear boundaries.

Expected behavior:

- Mixed applications produce architecture review findings.

### Undocumented APIs

Goal:

- Identify likely interface exposure without architecture or data-flow documentation.

Expected behavior:

- Current analyzer support should be measured; missing support should be recorded as a validation gap.

### Sensitive Data Near Outbound Calls

Goal:

- Detect privacy and data governance risk when sensitive fields appear near network calls.

Expected behavior:

- Sensitive data indicators and network calls should both be visible; cross-signal correlation should be validated as future capability if not implemented.

### License Ambiguity

Goal:

- Detect ambiguous, missing, custom, restrictive, or unknown license posture.

Expected behavior:

- License ambiguity produces Legal or Supply Chain review findings.

### Disabled Baseline Rules

Goal:

- Ensure baseline disablement remains visible and requires approval evidence.

Expected behavior:

- Disablement requests produce governance findings and appear in evidence.

### Missing Evidence That Must Become Gaps

Goal:

- Ensure required evidence absence is not treated as a pass.

Expected behavior:

- Missing runbook, deployment guide, rollback, data-flow, monitoring, backup/restore, or owner evidence becomes a finding or gap under strict profiles.

## Fixture Requirements

Each adversarial fixture should include:

- Minimal source files.
- Expected findings metadata.
- Clear seeded conditions.
- No dependency on network access.
- No real secrets.
- English-only comments and documentation.

## Reporting Requirements

Validation runs should produce `validation-report.json` with:

- Expected findings.
- Detected expected findings.
- Missed expected findings.
- Unexpected findings.
- Precision.
- Recall.
- Critical miss rate.
- Evidence traceability.
- Determinism result.
- Pass/fail status.
