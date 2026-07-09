# SDLC Governance Model

## Purpose

The Enterprise White-Box Code Assurance Scanner evaluates other systems for evidence, readiness, governance, control quality, delivery discipline, and enterprise acceptance. Its own development lifecycle must therefore be governed, repeatable, evidence-first, and conservative by default.

This governance model applies to scanner code, rules, profiles, validation assets, schemas, documentation, release decisions, and product claims. It does not create compliance certification. It defines internal development controls for a local-first, deterministic, offline-capable, non-AI assurance product.

## Product Boundaries

- Local-first operation.
- Offline-capable execution.
- Deterministic analysis and reporting.
- No AI, LLM calls, embeddings, model inference, or AI-assisted runtime decisions.
- No cloud dependency.
- No telemetry.
- No source code upload.
- Evidence-first conclusions.
- Conservative default decisions.
- English-only product artifacts.

## Governed Lifecycle

```text
Idea / Requirement
-> Change Request
-> Scope Definition
-> Design / ADR if needed
-> Implementation
-> Tests
-> Evidence Output
-> Validation Impact Review
-> Documentation
-> Regression Gate
-> Release Decision
```

## Change Types and Required Artifacts

| Change type | Required artifacts |
| --- | --- |
| analyzer | Change request, scope, analyzer contract impact, fixtures, unit tests, sample scan evidence, documentation, validation impact note, ADR if pipeline behavior changes. |
| rule | Change request, rule diff, rule metadata, evidence expectations, severity rationale, rule validation, profile impact, rulebook version impact. |
| profile | Change request, affected controls, required analyzers, expected decision impact, sample scan evidence, documentation, validation impact note. |
| scoring | Change request, scoring rationale, before/after examples, regression tests, validation gate review, ADR, documentation. |
| decision logic | Change request, decision semantics, before/after examples, regression tests, validation gate review, ADR, CISO/CTO review. |
| report | Change request, report section impact, evidence linkage review, sample report output, tests, documentation. |
| evidence schema | Change request, schema diff, compatibility note, manifest impact, tests, ADR, documentation. |
| validation | Change request, methodology note, fixtures, tests, threshold impact, calibration note, documentation. |
| governance | Change request, affected policies, approval role, documentation, release note. |
| CLI | Change request, command contract, help text, positive and negative tests, documentation. |
| refactor | Scope note, behavior-preservation tests, determinism check, validation impact note if shared logic changes. |
| bug fix | Reproduction, root cause, targeted test, fix evidence, limitation update if needed. |
| documentation | Scope note, affected product claims, source alignment check, English-only check. |
| security fix | Risk description, secure fix, test evidence, release note, reviewer approval, accelerated release decision if needed. |

## Material Change Review

Material changes are changes that can affect scanner decisions, confidence, evidence shape, validation metrics, user interpretation, or release readiness. Material changes require explicit validation impact review and may require an ADR.

High-impact material changes include:

- Severity changes.
- Scoring changes.
- Decision logic changes.
- Rule disablement behavior.
- Confidence logic.
- Report compression logic.
- Evidence schema changes.
- Baseline rule changes.
- Validation threshold changes.

## Evidence Requirements

Each governed change should leave enough evidence for a reviewer to understand:

- What changed.
- Why it changed.
- Which domains are affected.
- Which tests were run.
- Which evidence outputs changed.
- Whether validation gates were affected.
- Which limitations remain.

## Release Decision

Release decisions must be based on test evidence, validation evidence where available, documentation completeness, known limitations, and explicit approval status. A release decision must not be based on unreviewed assumptions or unsupported product claims.

## Governance Evidence Automation

The project includes lightweight local evidence automation for governance readiness:

```bash
python -m scanner governance-check --output governance-output
```

This command checks required governance documents, ADRs, templates, schemas, validation documentation, release gates documentation, main specification references, and known limitation documentation. It writes:

- `governance-check-report.json`
- `release-evidence.json`

The command is deterministic with respect to repository contents. It does not run tests or validation suites and does not make a release decision.
