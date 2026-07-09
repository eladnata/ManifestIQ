# Change Control Policy

## Purpose

This policy defines how material changes to the scanner are proposed, reviewed, validated, documented, approved, and released. It protects deterministic behavior, evidence traceability, conservative decision logic, and the local/offline/non-AI product boundary.

## Change Request Record

Each material change must be represented by a change request with this minimum structure:

```json
{
  "change_id": "string",
  "change_type": "analyzer|rule|profile|scoring|decision|report|schema|validation|governance|cli|refactor|bug|security|docs",
  "reason": "string",
  "affected_domains": [],
  "risk_level": "High|Medium|Low",
  "expected_outputs": [],
  "tests_required": [],
  "validation_required": true,
  "documentation_required": true,
  "approval_role": "Maintainer|AppSec|CISO|CTO|Architecture|SOX|ITGC"
}
```

## Required Review Steps

1. Define the problem and scope.
2. Classify the change type and risk level.
3. Identify affected analyzers, rules, profiles, schemas, reports, and validation assets.
4. Define expected evidence output changes.
5. Define required tests and fixtures.
6. Determine whether an ADR is required.
7. Implement the change.
8. Run applicable tests and validation commands.
9. Update documentation and limitations.
10. Record the release recommendation.

## High-Impact Changes

High-impact changes require validation gate review and approval by the accountable role.

Examples:

- Severity changes.
- Scoring changes.
- Decision logic changes.
- Rule disablement behavior changes.
- Confidence logic changes.
- Report compression logic changes.
- Evidence schema changes.
- Baseline rule changes.
- Validation threshold changes.

## Approval Guidance

| Risk level | Typical approval role |
| --- | --- |
| High | CISO, CTO, Architecture, AppSec, SOX, or ITGC, depending on domain. |
| Medium | Engineering Maintainer plus domain reviewer. |
| Low | Engineering Maintainer. |

## Change Control Constraints

- Changes must not add AI, LLM calls, telemetry, cloud dependencies, or source-code upload behavior.
- Changes must not weaken baseline rules without documented approval, reason, expiry, and evidence.
- Changes must not reduce evidence traceability for material findings.
- Changes must not hide analyzer failures or skipped analyzer status.
- Changes must preserve English-only product artifacts.

## Accepted Warnings

A release may proceed with accepted warnings only when the accountable reviewer records:

- The warning.
- The reason for acceptance.
- The expiry or follow-up date.
- The affected domains.
- The compensating control, if any.

## Templates and Evidence

Change requests should start from:

```text
governance/templates/CHANGE_REQUEST_TEMPLATE.md
```

Release checklists should start from:

```text
governance/templates/RELEASE_CHECKLIST_TEMPLATE.md
```

Calibration decisions should start from:

```text
governance/templates/CALIBRATION_DECISION_TEMPLATE.md
```

Local governance evidence can be generated with:

```bash
python -m scanner governance-check --output governance-output
```

The generated evidence supports review. It does not approve a change or certify compliance.
