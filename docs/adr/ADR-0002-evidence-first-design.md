# ADR-0002: Evidence-First Design

## Status

Accepted

## Date

2026-07-09

## Context

Enterprise reviewers need findings that are traceable to source files, metadata, rules, signals, claims, gaps, and confidence. Unsupported conclusions create review risk and reduce audit readiness.

## Decision

Every material conclusion must be linked to evidence. Reports may compress risk for decision readiness, but drill-down evidence must remain available in machine-readable outputs.

## Consequences

- Material findings require evidence references.
- Evidence packages must preserve analyzer outputs, normalized findings, rule evaluations, confidence summaries, and manifests.
- Report compression must not remove auditability.

## Alternatives Considered

- Summary-only report generation.
- Confidence-only decision output without evidence.

These alternatives were rejected because they weaken reviewer accountability and audit readiness.

## Validation Impact

Validation must include evidence traceability metrics and must fail or warn when material findings are not evidence-linked.

## Related Files

- `docs/architecture/ASSURANCE_ENGINE_MODEL.md`
- `docs/reporting/DECISION_PACKET_SPEC.md`
- `docs/governance/QUALITY_METRICS.md`
