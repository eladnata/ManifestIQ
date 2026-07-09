# Quality Metrics

## Purpose

Quality metrics help evaluate scanner engineering quality and validation reliability. They are decision-support signals, not standalone proof of product quality.

## Engineering Metrics

- Test pass rate.
- Analyzer coverage.
- Rule coverage.
- Documentation completeness.
- Report actionability.
- Known limitation closure rate.
- Deterministic repeatability.

## Evidence Metrics

- Evidence traceability.
- Manifest completeness.
- Evidence package generation success.
- Material finding evidence coverage.
- Analyzer status completeness.

## Validation Metrics

- Critical miss rate.
- Detectable recall.
- Material precision after triage.
- Top blocker agreement.
- Validation gate status.
- Scanner-only triage burden.

## Interpretation Rules

Validation metrics are meaningful only when based on comparable datasets. A metric trend can indicate regression or improvement only when baseline and candidate validation sets are comparable in scope, review method, reviewer expectations, and profile.

## Target Direction

- Test pass rate should remain high.
- Deterministic repeatability should be 100%.
- Evidence traceability for material findings should be 100%.
- Critical miss rate should trend toward zero for covered categories.
- Detectable recall should improve without masking false positives.
- Scanner-only triage burden should remain manageable.
- Known limitations should be closed or explicitly carried forward.

## Limitations

Quality metrics do not certify compliance, prove security, replace expert review, or prove production readiness by themselves.
