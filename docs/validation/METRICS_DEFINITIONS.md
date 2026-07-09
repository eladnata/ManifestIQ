# Metrics Definitions

This document defines validation metrics for scanner reliability. Metrics measure review preparation and capability amplification. They do not automate final expert judgment.

## Terms

- True Positive (TP): an expected finding detected by the scanner.
- False Positive (FP): a scanner finding that does not match expected or gold-set findings.
- False Negative (FN): an expected or gold-set finding missed by the scanner.
- Critical Expected Finding: an expected finding marked critical in validation metadata or ground truth.
- Material Finding: Critical, High, Block, or Mandatory Review finding.
- Detectable Human Finding: a human gold set finding marked `expected_scanner_detectable: true`.
- Non-Detectable Human Finding: a human finding requiring context outside static repository evidence.

## Precision

Formula:

```text
precision = TP / (TP + FP)
```

Meaning:

- Of findings reported by the scanner, how many matched expected or gold-set findings.

Interpretation:

- High precision reduces reviewer noise.
- Low precision indicates over-reporting or weak matching logic.

Gold set note:

- Scanner-only findings are not automatically false positives.
- Gold set material precision should use reviewer-labeled false positives:

```text
material_precision = matched_material_findings / (matched_material_findings + reviewer_labeled_false_positives)
```

Portfolio note:

- Untriaged scanner-only findings are counted as `triage_required`, not false positives.
- Material precision after triage is calculated only from matched material findings and reviewer-triaged false positives.

## Recall

Formula:

```text
recall = TP / (TP + FN)
```

Meaning:

- Of expected findings, how many the scanner detected.

Interpretation:

- High recall is critical for assurance.
- Critical expected findings should have near-zero miss rate.

Gold set detectable recall:

```text
recall_detectable = matched_detectable_human_findings / detectable_human_findings
```

Non-detectable human findings are excluded from the recall denominator.

## Critical Miss Rate

Formula:

```text
critical_miss_rate = missed_critical_expected_findings / total_critical_expected_findings
```

Meaning:

- The share of critical expected findings missed by the scanner.

Interpretation:

- Target is near zero for covered categories.

Gold set critical miss rate should consider only critical findings marked `expected_scanner_detectable: true`.

## False Positive Rate

Formula:

```text
false_positive_rate = FP / (TP + FP)
```

Meaning:

- Share of reported findings that do not match expected or gold-set findings.

Gold set note:

- Use reviewer worksheets to label false positives.
- Until triaged, scanner-only findings should be reported as `triage_required`.

After triage:

```text
false_positive_rate_after_triage = triaged_false_positive_scanner_only_findings / triaged_scanner_only_findings
```

## Scanner-Only Triage Rate

Formula:

```text
scanner_only_triage_rate = triaged_scanner_only_findings / scanner_only_findings
```

Meaning:

- Share of scanner-only findings that received reviewer labels.

## Valid Scanner-Only Material Finding Rate

Formula:

```text
valid_scanner_only_material_finding_rate = triaged_valid_material_scanner_only_findings / triaged_scanner_only_findings
```

Meaning:

- Share of triaged scanner-only findings reviewers confirmed as material.

## Evidence Traceability

Formula:

```text
evidence_traceability = material_findings_with_rule_and_evidence / total_material_findings
```

Material findings count if they include:

- Rule ID.
- Finding ID.
- Severity.
- Decision impact.
- Evidence type.
- File path or evidence snippet/value for evidence-bearing finding classes.

## Determinism

Formula:

```text
determinism = repeated_scan_findings_equal ? 1 : 0
```

Meaning:

- The same input, profile, rules, and scanner version produce the same normalized findings.

Target:

- 100%.

## Reviewer Agreement

Formula:

```text
reviewer_agreement = matching_reviewer_decisions / total_reviewed_decisions
```

Meaning:

- Share of cases where reviewers agree with the scanner-prepared top decision category after review.

## Review Preparation Acceleration

Formula:

```text
acceleration = (manual_preparation_minutes - scanner_prepared_minutes) / manual_preparation_minutes
```

Meaning:

- Reduction in initial evidence preparation time.

Target:

- 70-80% for target pilot workflows.

This does not mean final judgment automation.

## Report Actionability

Formula:

```text
report_actionability = actionable_material_findings / total_material_findings
```

A material finding is actionable when it includes:

- Clear title.
- Evidence reference.
- Decision impact.
- Required remediation.
- Owner role or review role.

## Confidence Calibration

Formula:

```text
confidence_calibration = findings_with_appropriate_confidence / sampled_findings_reviewed
```

Meaning:

- Human reviewers agree that confidence labels are consistent with evidence strength.

Current implementation:

- If a reviewer worksheet is provided, evidence quality score is captured as a calibration input.
- Without a worksheet, confidence calibration is reported as not evaluated.

## Domain Coverage

Formula:

```text
domain_coverage = domains_with_applicable_controls_evaluated / domains_with_applicable_expected_controls
```

Meaning:

- Share of expected enterprise domains covered for a suite or gold set.

Portfolio domain metrics:

```text
domain_detectable_recall = matched_detectable_findings_in_domain / detectable_human_findings_in_domain
domain_critical_miss_rate = missed_detectable_critical_findings_in_domain / detectable_critical_findings_in_domain
```

## Rule Family Metrics

Formula:

```text
rule_family_detectable_recall = matched_detectable_findings_in_rule_family / detectable_human_findings_in_rule_family
```

Meaning:

- Reliability summarized by rule ID prefix such as `SEC`, `OPS`, `LIC`, or `AI`.

## Profile Metrics

Formula:

```text
profile_detectable_recall = matched_detectable_findings_for_profile / detectable_human_findings_for_profile
```

Meaning:

- Reliability summarized by configured assurance profile.

## Top Blocker Agreement

Formula:

```text
top_blocker_agreement = scanner_top_blockers_confirmed_by_reviewers / scanner_top_blockers_reviewed
```

Meaning:

- Share of scanner-highlighted top blockers that reviewers agree are material.

Target:

- 80%+ during pilot validation.

Gold set implementation:

```text
top_blocker_agreement = matched_human_top_blockers / human_top_blockers
```

If a reviewer worksheet provides `top_blocker_agreement`, the worksheet value may be used for pilot reporting.

## Versioned Trend Tracking

Portfolio validation reports must record:

- Scanner version.
- Ruleset version.
- Portfolio ID.
- Repository count.

This enables deterministic trend comparison across ruleset and scanner releases.

## Validation Gate Status

Gate status values:

- `Passed`: no blocking regression or warning was detected.
- `Warning`: warning-level regression was detected and requires review.
- `Failed`: blocking regression was detected.

Blocking examples:

- Critical miss rate above threshold.
- Evidence traceability below threshold.
- Detectable recall below threshold.
- Detectable recall drop beyond allowed threshold.

Warning examples:

- Top blocker agreement drop.
- Material precision drop.
- Scanner-only triage burden growth.
- Domain-level regression.
- Rule-family regression.

Gate thresholds are configurable policy inputs and should be approved by AppSec, CISO, CTO, or delegated assurance owners.
