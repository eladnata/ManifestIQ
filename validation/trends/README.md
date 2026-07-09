# Validation Trends

Trend validation compares portfolio validation reports across scanner and ruleset versions.

Trend comparison does not prove overall product quality by itself. It detects regression across versions and helps prevent silent degradation in validation reliability.

The workflow remains local, deterministic, offline-capable, non-AI, evidence-first, conservative by default, and English-only.

## Purpose

Trend comparison answers:

- Did detectable recall decrease?
- Did critical miss rate increase?
- Did evidence traceability decrease?
- Did material precision after triage decrease?
- Did top blocker agreement decrease?
- Did review preparation acceleration decrease?
- Did scanner-only triage burden increase materially?
- Did any domain or rule family regress?
- Is the candidate scanner/ruleset validation status acceptable for release?

## Gate Policy

Gate thresholds are configurable and should be approved by AppSec, CISO, CTO, or delegated assurance owners.

Blocking conditions fail the gate. Warning conditions require review but do not automatically fail release.

## Inputs

- Baseline `portfolio-validation-report.json`
- Candidate `portfolio-validation-report.json`
- Validation gate policy JSON
- Trend manifest JSON

## Output

- `validation-trend-report.json`

## Limitation

Trend gates only compare measured validation evidence. They do not replace expert judgment, production pilot validation, penetration testing, secure code review, legal review, privacy review, or SOX/control review.
