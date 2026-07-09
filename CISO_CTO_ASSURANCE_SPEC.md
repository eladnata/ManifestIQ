# CISO/CTO Assurance Specification

## Audience

This scanner is for technical assurance users: CISO, CTO, AppSec, Security Engineering, Enterprise Architecture, DevSecOps, ITGC, SOX, Legal, Privacy, and senior code reviewers.

The platform is a deterministic expert-amplification platform for enterprise system assurance.

It does not replace CISO, CTO, AppSec, Architecture, DevSecOps, ITGC, SOX, Legal, Privacy, or Security reviewers. The system prepares the evidence and amplifies the reviewer. The professional owns the judgment.

## Assurance Standard

The scanner evaluates whether a codebase is suitable for enterprise use under a selected profile. It is strict, deterministic, local-first, offline-capable, non-AI, conservative by default, and evidence-first. It does not attempt to explain findings with AI and does not send source code outside the local environment.

The goal is not automated approval. The goal is to let experts make faster, deeper, more consistent, better-evidenced decisions.

The platform amplifies expert capability by:

- Extracting deep system intelligence.
- Organizing evidence.
- Evaluating deterministic controls.
- Linking findings to proof.
- Explaining gaps.
- Assigning confidence.
- Compressing risk into a concise decision packet.
- Preserving audit-ready evidence.
- Enforcing a repeatable review workflow.

## Capability Amplification Dimensions

- Evidence coverage.
- System understanding.
- Control coverage.
- Traceability.
- Repeatability.
- Risk compression.
- Decision readiness.
- Audit readiness.
- Remediation clarity.
- Review consistency.

## Target KPIs

- 85%+ evidence coverage for static repository review.
- 85%+ system mapping coverage where evidence exists.
- 100% traceability for material findings.
- 100% deterministic repeatability.
- 80%+ reviewer agreement on top blockers during pilot.
- 70-80% initial review preparation acceleration.
- Near-zero critical miss target for covered categories.
- 0% replacement of final expert judgment.

These targets measure review preparation, evidence coverage, consistency, and capability amplification. They do not measure final judgment automation.

## Approval Gates

The following conditions block or force review before enterprise approval:

- Critical security findings
- Hardcoded secrets
- Critical SAST findings
- Hidden or undeclared AI/model usage
- External AI API calls without explicit declaration and approval
- Model artifacts without inventory or architecture notes
- Missing owner or accountability evidence
- Sensitive data indicators without classification
- SOX/Finance indicators without assessment
- Missing enterprise delivery evidence
- Analyzer failures
- Disabled baseline rules without risk acceptance evidence

## Evidence Expectations

Every scan must preserve:

- Source metadata
- File inventory
- Analyzer outputs
- Normalized findings
- Rule evaluation summary
- Signals, claims, gaps, confidence summary, acceptance matrix, and system dossier
- Scoring and decision output
- HTML report
- Manifest and package SHA256

## Decision Semantics

Decision semantics describe scanner recommendations and review-preparation status. They do not replace accountable expert approval.

- `Approved`: No blocking or mandatory-review findings and score threshold met.
- `Conditional Approval`: Non-blocking remediation required.
- `Pilot Only`: Limited controlled use only.
- `Remediation Required`: Material gaps must be resolved.
- `Mandatory Review`: Human technical review required before approval.
- `Not Approved`: Critical blocker or blocked gate.
- `Rejected`: Not suitable in current state.

## Non-Claims

The scanner does not certify compliance, replace penetration testing, replace secure code review, replace architecture review, replace CISO/CTO/AppSec/DevSecOps/ITGC/SOX/Legal/Privacy/Security judgment, or replace formal SOX/privacy/legal review.

The scanner may accelerate initial review preparation by 70-80% in target use cases, but this ambition applies to evidence gathering, repository mapping, deterministic control pre-evaluation, risk compression, and decision packet preparation. It does not mean automated final approval or replacement of professional accountability.

## SDLC Governance

The scanner itself is developed under the governance pack in `docs/governance/` and the ADRs in `docs/adr/`. Material changes to analyzers, rules, profiles, scoring, decision logic, validation thresholds, evidence schemas, and report compression require change control, validation impact review, documentation updates, and release gate review.

This governance protects the CISO/CTO assurance boundary: the product remains local-first, deterministic, offline-capable, non-AI, evidence-first, conservative by default, and accountable to expert review.
