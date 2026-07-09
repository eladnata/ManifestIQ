# Validation Gate Policy

## Purpose

Validation gates protect the scanner against silent reliability regression as analyzers, rules, scoring, confidence logic, report compression, evidence schemas, and validation methods evolve.

## Gate Types

- Adversarial validation gate.
- Gold set validation gate.
- Portfolio validation gate.
- Trend regression gate.

## Configurable Thresholds

Thresholds may include:

- Critical miss rate maximum.
- Evidence traceability minimum.
- Detectable recall minimum.
- Detectable recall maximum drop.
- Top blocker agreement minimum.
- Top blocker agreement maximum drop.
- Material precision after triage minimum.
- Material precision after triage maximum drop.
- Scanner-only triage burden warning threshold.
- Domain regression threshold.
- Rule-family regression threshold.

Threshold changes are high-impact changes and require approval by accountable AppSec, CISO, CTO, or Architecture stakeholders.

## Blocking Conditions

Blocking conditions include:

- Critical miss rate above approved threshold.
- Evidence traceability below approved threshold.
- Detectable recall below approved threshold.
- Detectable recall drop beyond approved threshold.
- Missing required validation evidence for a high-impact release.

## Warning Conditions

Warning conditions include:

- Top blocker agreement drop.
- Material precision drop.
- Scanner-only triage burden growth.
- Domain-level regression.
- Rule-family regression.
- Incomplete validation coverage.

## Accepted Warnings

Accepted warnings must be recorded with:

- Warning reason.
- Accountable approver.
- Expiry or follow-up date.
- Affected domain.
- Compensating control where applicable.

## Calibration Decision Logs

Calibration decision logs should capture reviewer decisions about scanner-only findings, false positives, materiality, severity, confidence, and blocker agreement.

## Limitations

A passing trend gate does not prove overall product quality. It only proves no measured regression against the compared validation set.

Real L4 validation requires multiple human-reviewed repositories. Real L5 validation requires production pilot validation.
