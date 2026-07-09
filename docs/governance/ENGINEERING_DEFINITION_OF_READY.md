# Engineering Definition of Ready

## Purpose

A work item is ready for implementation only when it is clear enough to build, test, validate, document, and release without guessing at product boundaries or decision semantics.

## Ready Criteria

A work item is ready only when it defines:

- Problem statement.
- Scope.
- Out of scope.
- Affected modules.
- Expected evidence outputs.
- Required tests.
- Required fixtures.
- Required documentation.
- Validation impact.
- Acceptance criteria.
- Rollback considerations.
- No UI unless explicitly authorized.

## Product Boundary Check

Every ready work item must confirm:

- No AI or LLM calls.
- No cloud dependency.
- No telemetry.
- No source code upload.
- Deterministic behavior.
- Local/offline operation.
- Evidence-first output.
- English-only product artifacts.

## ADR Check

An ADR is required before implementation when the work item changes:

- Core architecture.
- Pipeline stages.
- Evidence schemas.
- Rule contracts.
- Validation methodology.
- Decision logic.
- Security posture.
- Local/offline/non-AI boundaries.

## Validation Planning

The ready work item must identify whether it requires:

- Unit tests.
- Integration tests.
- Sample scan.
- Adversarial validation.
- Gold set validation.
- Portfolio validation.
- Trend gate comparison.
- Manual review by AppSec, CISO, CTO, SOX, ITGC, Legal, or Privacy.
