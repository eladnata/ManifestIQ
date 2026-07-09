# ADR-0004: Validation Gates and Regression Control

## Status

Accepted

## Date

2026-07-09

## Context

Changes to analyzers, rules, scoring, confidence, schemas, validation methods, and report compression can silently reduce reliability unless measured across validation assets.

## Decision

Validation gates and trend comparisons are required to prevent silent reliability regression. Gate thresholds must be configurable and approved by accountable stakeholders.

## Consequences

- Release candidates should run applicable validation gates.
- Trend reports should compare baseline and candidate portfolio validation reports where available.
- Warnings may be accepted only with accountable review.

## Alternatives Considered

- Test-only release decisions.
- Manual validation without trend comparison.

These alternatives were rejected because they do not adequately protect against reliability regression.

## Validation Impact

Regression gates must track critical miss rate, detectable recall, evidence traceability, material precision, top blocker agreement, scanner-only triage burden, domain regression, and rule-family regression where data exists.

## Related Files

- `docs/governance/VALIDATION_GATE_POLICY.md`
- `validation/trends/README.md`
- `scanner/validation/trends.py`
- `scanner/validation/gates.py`
