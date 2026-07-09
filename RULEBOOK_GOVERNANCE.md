# Rulebook Governance

## Baseline Rules

Baseline rules are built into the scanner. They represent enterprise security, assurance, governance, documentation, AI/model risk, data, SOX, operations, and maintainability expectations.

Baseline rules are:

- Versioned
- Included in the ruleset hash
- Loaded before custom rules
- Treated as read-only
- Marked as `baseline: true`
- Treated as `editable: false`
- Protected with `disable_requires_approval: true`

## Custom Rules

Custom rules may be added under:

```text
rules/custom/
```

Custom rules must use unique rule IDs. They must not override built-in baseline rule IDs. If a custom rule uses a baseline rule ID, the scanner ignores the custom rule and emits a governance finding.

Recommended custom rule fields:

- `rule_id`
- `name`
- `author`
- `version`
- `category`
- `severity`
- `applies_to_profiles`
- `decision`
- `condition`
- `requires_approval_from`
- `remediation`

## Baseline Rule Disablement

Baseline rule disablement requests may be represented in:

```text
rules/disabled-baseline-rules.yml
```

Expected schema:

```yaml
disabled_rules:
  - rule_id: SEC-001
    reason: temporary exception description
    approver: ciso@example.com
    timestamp: 2026-07-08T00:00:00Z
    expiration_date: 2026-08-08
    risk_acceptance: EXC-2026-001
```

Disablement requests must generate governance evidence. If the disabled rule is critical or blocking, the governance finding is critical and blocking.

## Rule Evaluation Evidence

Each scan writes `rule-evaluation-results.json` with:

- Ruleset hash
- Baseline rule count
- Custom rule count
- Disabled baseline rule requests
- Blocking gates
- Rule metadata

The ruleset hash is part of the scan summary and final report.

## Controlled Rule Changes

Detailed rule change controls are defined in `docs/governance/RULE_CHANGE_POLICY.md`.

Baseline rule changes require governance review, validation impact analysis, and a rulebook version bump. Baseline rules must not be edited directly in a way that bypasses review. Custom rules must not reuse baseline rule IDs and must include severity, category, decision impact, remediation, and evidence expectations.

Severity changes, baseline disablement behavior, and rule deletion are material changes. They must follow the change control process in `docs/governance/CHANGE_CONTROL_POLICY.md` and applicable release gates in `docs/governance/RELEASE_GATES.md`.
