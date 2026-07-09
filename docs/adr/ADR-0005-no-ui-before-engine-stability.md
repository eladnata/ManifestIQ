# ADR-0005: No UI Before Engine Stability

## Status

Accepted

## Date

2026-07-09

## Context

The scanner's value depends on deterministic engine outputs, evidence schemas, decision packets, validation gates, rule governance, and exception workflow. A UI built before those contracts stabilize could hide unresolved product decisions.

## Decision

GUI implementation is deferred until engine outputs, evidence schemas, decision packet, and exception workflow are stable.

## Consequences

- Near-term work should prioritize engine correctness, evidence integrity, validation, governance, and documentation.
- Reports and CLI outputs remain the primary user-facing surfaces.
- UI work requires explicit authorization and a stable product contract.

## Alternatives Considered

- Build UI in parallel with unstable engine contracts.
- Use UI to define product behavior.

These alternatives were rejected because they could obscure evidence and governance issues.

## Validation Impact

Validation remains focused on deterministic engine outputs and evidence packages before UI-level validation is introduced.

## Related Files

- `MASTER_SPEC.md`
- `docs/reporting/DECISION_PACKET_SPEC.md`
- `docs/governance/ENGINEERING_DEFINITION_OF_READY.md`
