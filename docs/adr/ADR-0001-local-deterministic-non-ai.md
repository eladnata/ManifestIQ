# ADR-0001: Local Deterministic Non-AI Operation

## Status

Accepted

## Date

2026-07-09

## Context

The scanner reviews sensitive source code and produces assurance evidence for enterprise reviewers. Trust depends on local execution, repeatability, explainability, and the absence of external runtime services.

## Decision

The product remains local-first, deterministic, offline-capable, and non-AI. It must not call AI, LLM, embedding, vector-search, model-inference, telemetry, or cloud services during scanner execution.

## Consequences

- Results must be produced by deterministic rules, analyzers, and evidence processing.
- The scanner can be used in restricted environments.
- The product does not claim autonomous expert judgment.
- Some tasks that could be handled by AI must instead be handled through explicit rules, evidence models, and reviewer workflow.

## Alternatives Considered

- Cloud-assisted analysis.
- LLM-based explanation.
- Telemetry-assisted product learning.

These alternatives were rejected because they conflict with local-first, offline-capable, non-AI assurance requirements.

## Validation Impact

Validation must measure deterministic scanner behavior and cannot rely on AI-generated judgments.

## Related Files

- `MASTER_SPEC.md`
- `CISO_CTO_ASSURANCE_SPEC.md`
- `docs/governance/SECURE_DEVELOPMENT_POLICY.md`
