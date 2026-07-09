# ADR-0003: Baseline Rulebook Governance

## Status

Accepted

## Date

2026-07-09

## Context

Baseline rules define core enterprise security, assurance, governance, documentation, supply chain, operations, AI/model risk, SOX, and maintainability expectations. Silent edits or overrides could weaken scanner behavior.

## Decision

Baseline rules are read-only, versioned, and cannot be overridden by custom rules. Disablement requires approval, reason, expiry, and evidence. Baseline rule changes require rulebook version review.

## Consequences

- Custom rules must use unique IDs and a separate namespace or directory.
- Attempts to override baseline rule IDs must generate governance evidence.
- Baseline disablement remains visible in evidence and reports.

## Alternatives Considered

- User-editable baseline rules.
- Custom rule overrides of baseline IDs.
- Silent baseline disablement.

These alternatives were rejected because they reduce assurance integrity.

## Validation Impact

Rulebook validation must check baseline immutability, custom rule ID uniqueness, and baseline disablement evidence.

## Related Files

- `RULEBOOK_GOVERNANCE.md`
- `docs/governance/RULE_CHANGE_POLICY.md`
