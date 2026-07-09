# Enterprise White-Box Code Assurance Scanner - Master Specification

**Version:** v0.3  
**Date:** 2026-07-08  
**Status:** Working product contract  
**Purpose:** Define the deterministic local assurance scanner used to amplify CISO, CTO, AppSec, Security Engineering, DevSecOps, Architecture, ITGC, SOX, Legal, Privacy, and code-review capability with evidence-backed system assurance.

## Product Identity

Enterprise White-Box Code Assurance Scanner is a deterministic expert-amplification platform for enterprise system assurance.

It performs static review of source code, project structure, dependencies, configuration, hidden AI/model usage, security posture, delivery readiness, governance evidence, and enterprise SDLC posture. It produces strict technical findings, approval gates, risk scoring, concise decision packets, and tamper-evident evidence packages.

The product is not an AI reviewer, cloud platform, telemetry agent, marketing dashboard, or compliance certification service.

The product does not replace CISO, CTO, AppSec, Architecture, DevSecOps, ITGC, SOX, Legal, Privacy, or Security reviewers. The system prepares the evidence and amplifies the reviewer. The professional owns the judgment.

The goal is not automated approval. The goal is to let experts make faster, deeper, more consistent, better-evidenced decisions.

## Expert Capability Amplification

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

Capability amplification dimensions:

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

Target KPIs:

- 85%+ evidence coverage for static repository review.
- 85%+ system mapping coverage where evidence exists.
- 100% traceability for material findings.
- 100% deterministic repeatability.
- 80%+ reviewer agreement on top blockers during pilot.
- 70-80% initial review preparation acceleration.
- Near-zero critical miss target for covered categories.
- 0% replacement of final expert judgment.

## Non-Negotiable Boundaries

- Run locally and remain offline-capable.
- Never send source code or evidence to an external service.
- Never call AI, LLM, embedding, vector-search, or model-inference services.
- Use deterministic, rule-based, explainable analysis only.
- Preserve final expert judgment; scanner output is decision preparation, not autonomous approval.
- Preserve machine-readable JSON, HTML report, manifest, and SHA256 evidence outputs.
- Never hide analyzer failures.
- Never print full secrets in reports or logs.
- Keep all user-facing language in English.

## Core Questions

1. Is this codebase safe enough for enterprise use?
2. Are hidden AI libraries, model artifacts, inference endpoints, embeddings, vector databases, or external AI APIs present?
3. Is the project structure maintainable and professionally organized?
4. Are secrets, risky configuration, unsafe code patterns, data risks, SOX indicators, or dependency hygiene issues present?
5. Is the delivery package auditable and complete?
6. Should the system be approved, conditionally approved, mandatorily reviewed, rejected, or blocked?

## Supported Inputs

- Local folder
- ZIP archive
- Git repository

## Required Outputs

Each scan produces an evidence package containing at least:

- `scan-summary.json`
- `source-metadata.json`
- `file-inventory.json`
- analyzer result JSON files
- `local-sbom.json`
- `rule-evaluation-results.json`
- `scoring-results.json`
- `findings.json`
- `final-report.html`
- `signals.json`
- `claims.json`
- `gaps.json`
- `confidence-summary.json`
- `enterprise-acceptance-matrix.json`
- `system-dossier.json`
- `manifest.json`
- `sha256.txt`

## Analyzer Contract

Every analyzer returns:

```json
{
  "analyzer_id": "string",
  "analyzer_version": "string",
  "status": "completed|completed_with_warnings|failed|skipped",
  "duration_ms": 0,
  "input_scope": {
    "files_scanned": 0,
    "files_skipped": 0
  },
  "metrics": {},
  "findings": [],
  "raw_output_path": "string|null",
  "errors": []
}
```

Analyzer failure must produce a `Scan Integrity` finding.

## Finding Schema

Normalized findings include:

```json
{
  "finding_id": "string",
  "rule_id": "string",
  "baseline_rule": true,
  "category": "Security|Supply Chain|Governance|Documentation|Data Protection|SOX|Operations|Maintainability|Architecture|AI Model Risk|Configuration|Scan Integrity",
  "severity": "Critical|High|Medium|Low|Info",
  "confidence": "High|Medium|Low",
  "title": "string",
  "description": "string",
  "file_path": "string|null",
  "line_start": 0,
  "line_end": 0,
  "evidence_type": "pattern_match|file_presence|missing_file|metadata|dependency|configuration|model_artifact|rule_evaluation",
  "evidence_snippet": "string|null",
  "decision_impact": "Block|Mandatory Review|Conditional|Advisory",
  "owner_role": "Security|AppSec|Engineering|DevOps|SOX|ITGC|Architecture|Technical Owner|Business Owner",
  "requires_approval_from": [],
  "remediation": [],
  "status": "open",
  "created_at": "ISO-8601"
}
```

Finding IDs are deterministic and derived from rule ID, file path, line number, and evidence value.

## Decision Philosophy

The scanner is conservative by default. It must not optimize for passing scans.

Decision output is a recommendation and preparation artifact for expert review. It compresses evidence and risk into a concise technical decision packet, but it does not transfer accountability from the professional reviewer to the scanner.

Decision priority:

```text
Critical Blocking Finding
> Undeclared AI/Model Usage
> Missing Owner / Missing Accountability
> Security Architecture Risk
> Sensitive Data Risk
> SOX/Finance Impact
> Supply Chain Risk
> Operations Gaps
> Documentation Gaps
> Score Threshold
```

Any critical blocking finding results in `Not Approved` regardless of score.

## Profiles

Supported profiles:

- `sandbox`
- `team-use`
- `department-use`
- `enterprise`
- `finance-sox`
- `ai-enabled`
- `production-critical`

`enterprise`, `finance-sox`, `ai-enabled`, and `production-critical` are strict review profiles.

## Core Analyzer Roadmap

Implemented or prepared analyzers:

- inventory
- secrets
- dependencies
- sast
- config_scan
- documentation
- data_risk
- sox_detector
- maintainability
- hidden_ai_model_detector
- operational
- licenses
- project_structure
- delivery_readiness
- architecture_signals

Prepared analyzers may return `skipped` with explicit TODO metadata until implemented. They must not fake results.

## Rulebook Governance

Baseline rules are built-in, versioned, non-editable, and included in the ruleset hash. Custom rules live under `rules/custom/` and cannot override baseline rule IDs. Baseline rule disablement requests must generate governance findings and appear in the evidence package.

Detailed rule change controls are defined in `docs/governance/RULE_CHANGE_POLICY.md`. The broader scanner SDLC is governed by the documentation pack under `docs/governance/` and the ADRs under `docs/adr/`.

## SDLC Governance

Future changes to analyzers, rules, profiles, scoring, decision logic, evidence schemas, validation methods, CLI behavior, reports, and governance documents must follow the governed development lifecycle:

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

The governance pack defines change control, release gates, engineering definition of ready, engineering definition of done, RACI, ADR policy, rule change policy, quality metrics, validation gate policy, and secure development policy. These controls preserve the product constraints: local-first, deterministic, offline-capable, non-AI, no cloud dependency, no telemetry, evidence-first, conservative by default, and English-only.

## Report Requirements

Reports are technical, concise, evidence-linked, and audit-ready. Reports should support expert capability amplification by preparing the decision packet, not by automating final judgment. Required sections:

- Final decision and score
- Blocking gates
- Critical findings
- Undeclared AI/model risk
- Project structure and delivery readiness
- Security, supply chain, data/SOX, documentation, operations findings
- Disabled baseline rules
- Analyzer status and failed/skipped analyzer warnings
- Evidence package hash
- Scanner version and ruleset hash
- Required remediation before approval
