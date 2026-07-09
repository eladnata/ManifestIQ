# Decision Packet Specification

The final human-facing report must be concise. The scanner may generate deep evidence, but the primary decision packet should compress the result into a short technical review artifact.

The scanner aligns to enterprise secure SDLC, SaaS trust, vendor review, operations, data protection, AI governance, supply chain, and license review practices. It does not certify compliance, replace audit work, or produce a formal attestation.

## Length Target

The decision packet should be approximately:

1. One page decision summary.
2. One page domain matrix.
3. One page top blockers and remediation.

Full evidence remains in JSON artifacts and HTML drill-down sections.

The goal is not a 20-page report. The goal is a decision-ready packet with traceable evidence.

## Required Sections

### 1. Final Decision

Include:

- Decision: Approved, Conditional Approval, Pilot Only, Remediation Required, Mandatory Review, Not Approved, or Rejected.
- Score.
- Profile.
- Scanner version.
- Ruleset hash.
- Evidence package hash.
- Scan timestamp or scan ID.

Compression rule:

- Show the final answer first.
- Critical blockers and explicit block decisions override score.

### 2. System Identity

Include only evidence-backed identity fields:

- Source type.
- Source path or repository metadata when available.
- File count.
- Dominant languages.
- Package managers.
- System type if inferred.
- Architecture style if inferred.

Compression rule:

- Use `unknown` when evidence is insufficient.
- Do not infer business purpose from filenames unless rules explicitly support it.

### 3. Assurance Matrix

Include the domain matrix:

- Domain.
- Status: Passed, Conditional, Mandatory Review, Blocked, or Unknown.
- Confidence: High, Medium, or Low.
- Reason.
- Blocking finding references.

Domains should follow the enterprise acceptance taxonomy:

- Architecture
- Platform
- Interfaces
- Database and Storage
- External Egress
- Application Security
- Supply Chain
- License
- Data Protection
- SOX / Finance
- AI / Model Risk
- Operations
- Delivery
- Maintainability
- Governance

Compression rule:

- Show one row per domain.
- Do not list every finding in the matrix.
- Link or reference detailed evidence IDs.

### 4. Top Blocking Reasons

Include only the highest-impact causes of the decision:

- Critical findings.
- Block decision findings.
- Mandatory review findings.
- Missing evidence that created a blocking or mandatory-review gap.
- Rule contract validation errors if they affect trust in the scan.

Compression rule:

- Deduplicate by root cause where possible.
- Prefer rule ID, finding ID, title, severity, and decision impact.
- Keep detailed evidence in `findings.json`, `gaps.json`, and analyzer outputs.

### 5. Required Remediation

Include:

- Required remediation before approval.
- Owner role.
- Approval roles when applicable.
- Related finding IDs.
- Related domain.

Compression rule:

- Group repeated remediation by rule or domain.
- Put high-volume details in deep evidence only.

### 6. Evidence & Confidence

Include:

- Evidence package hash.
- Evidence artifact list summary.
- Confidence summary.
- Low-confidence domains.
- Limitations.

Compression rule:

- Show confidence as a review aid, not as a mathematical probability.
- Use limitations to prevent overclaiming.

### 7. Limitations

Always include:

- The scanner is deterministic static analysis.
- It does not replace penetration testing.
- It does not replace secure code review.
- It does not replace privacy, legal, SOX, or architecture review where required.
- It does not certify compliance with any external framework.
- It does not send source code or evidence to external services.
- It does not use AI or LLMs.

## Evidence Drill-Down

The decision packet should point to deep evidence artifacts:

- `scan-summary.json`
- `findings.json`
- `signals.json`
- `claims.json`
- `gaps.json`
- `confidence-summary.json`
- `evidence-graph.json`
- `enterprise-acceptance-matrix.json`
- `system-dossier.json`
- `rule-contract-validation.json`
- Analyzer result JSON files
- `manifest.json`
- `sha256.txt`

## Decision Semantics

Decision compression should follow this precedence:

1. Critical blocking finding.
2. Explicit block decision impact.
3. Undeclared AI/model usage requiring block or mandatory review.
4. Missing accountability or owner evidence in strict profiles.
5. Security architecture, sensitive data, SOX/Finance, supply chain, operations, or delivery gaps requiring review.
6. Score thresholds.

## Packet Non-Goals

The decision packet must not:

- Claim certification.
- Include marketing language.
- Include unsupported maturity ratings.
- Include every analyzer metric.
- Include full source snippets.
- Expose secrets.
- Become a long audit report.

## Reference Sources

- NIST SSDF SP 800-218: https://csrc.nist.gov/pubs/sp/800/218/final
- NIST Cybersecurity Framework: https://www.nist.gov/cyberframework
- CSA CAIQ: https://cloudsecurityalliance.org/artifacts/star-level-1-security-questionnaire-caiq-v4
- AICPA Trust Services Criteria: https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022
