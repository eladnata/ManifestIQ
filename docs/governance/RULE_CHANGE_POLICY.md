# Rule Change Policy

## Purpose

Rules influence findings, severity, decision impact, remediation, and enterprise acceptance. Rule changes must be controlled, evidence-backed, versioned, and validated.

## Baseline Rules

Baseline rules are:

- Read-only.
- Versioned.
- Included in the ruleset hash.
- Not editable directly by users.
- Not overrideable by custom rules.
- Protected from silent disablement.

Baseline rule disablement requires:

- Approval.
- Reason.
- Expiry.
- Evidence.
- Risk acceptance reference.

Baseline rule changes require a rulebook version bump and validation impact review.

## Custom Rules

Custom rules are allowed only under a custom namespace or custom rules directory. They must not reuse baseline rule IDs.

Custom rules must include:

- Rule ID.
- Severity.
- Category.
- Decision impact.
- Remediation.
- Evidence expectations.
- Applicable profiles.

Custom rules must pass rule validation before use.

## Severity Changes

Severity changes require:

- Justification.
- Validation impact analysis.
- Calibration note.
- Approval based on severity and affected domain.

Critical or blocking severity changes require AppSec or CISO review.

## Rule Deletion

Baseline rule deletion is forbidden.

Custom rule deletion must be logged with:

- Rule ID.
- Reason.
- Approver.
- Effective date.
- Expected impact.

## Rule Disablement

Rule disablement must not hide risk. Disablement should create governance evidence and appear in reports where material.

## Rule Validation

Rule validation should check:

- Unique rule IDs.
- Required metadata.
- Valid severity.
- Valid category.
- Valid decision impact.
- Evidence expectations.
- Profile applicability.
- Baseline/custom namespace separation.
