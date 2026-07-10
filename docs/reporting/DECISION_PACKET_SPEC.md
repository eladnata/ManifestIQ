# ManifestIQ Decision Packet Specification

## Purpose

The Decision Packet is a concise, evidence-backed review artifact generated from deterministic scan outputs. It compresses the existing scanner decision, score, top risks, material gaps, acceptance matrix, confidence summary, system dossier, and evidence references into a review-ready package.

The packet supports review preparation. It does not approve a release or certify compliance.

## Audience

The packet is intended for CISO, CTO, AppSec, Security Engineering, Enterprise Architecture, DevSecOps, ITGC / SOX reviewers, and release decision reviewers.

## Schema

The JSON artifact is written as `decision-packet.json` with:

```json
{
  "schema": "manifestiq-decision-packet",
  "schema_version": "0.1",
  "packet_id": "string",
  "generated_at": "string",
  "source": {},
  "decision": {},
  "executive_technical_summary": {},
  "top_risks": [],
  "material_gaps": [],
  "acceptance_summary": {},
  "confidence_summary": {},
  "required_actions": [],
  "required_reviewers": [],
  "evidence_references": [],
  "excluded_claims": [],
  "limitations": [],
  "non_claims": []
}
```

`decision.value` and `decision.score` preserve the existing scanner decision and score. The packet must not independently recalculate either value.

## Input Artifacts

The builder derives its content only from deterministic local scanner artifacts:

- `scan-summary.json`
- `findings.json`
- `gaps.json`
- `confidence-summary.json`
- `enterprise-acceptance-matrix.json`
- `system-dossier.json`
- `control-context.json`
- evidence manifest data and local artifact hashes

## Deterministic Selection Rules

Top risks are selected from material findings: Critical, High, Block, or Mandatory Review. They are sorted by severity, then decision impact, then `rule_id`, then `finding_id`.

Material gaps are selected from Critical, High, Block, or Mandatory Review gaps. They are sorted by severity, then decision impact, then `gap_id`.

Acceptance summaries are derived from acceptance matrix domain statuses without reclassifying domains.

Evidence references point only to local artifacts, hashes, finding IDs, rule IDs, and gap IDs.

## Required Reviewers

Reviewer roles are derived conservatively. The packet lists required reviewer roles only; it does not assign approvals.

Examples:

- Critical security finding: AppSec, CISO
- Hidden AI/model risk: CISO, Data Governance, Security Architecture
- SOX/finance indicator: ITGC / SOX Reviewer
- External egress: Security Architecture, Data Governance
- License risk: Legal / Open Source Review
- Operational readiness gap: DevOps / SRE
- Architecture gap: CTO / Enterprise Architecture
- Governance gap: Release Manager / Control Owner

## Non-Claims

Every packet includes:

- This packet does not certify compliance.
- This packet does not replace CISO, CTO, AppSec, Architecture, ITGC, SOX, Legal, Privacy, or Security review.
- This packet does not represent penetration testing completion.
- This packet does not grant production approval by itself.
- This packet is based only on deterministic local static analysis and available repository evidence.

## Limitations

The packet is limited to available repository evidence and deterministic local static analysis. Unknown means the scanner did not find sufficient evidence. The packet does not represent legal, privacy, SOX, ITGC, penetration testing, architecture, or production approval.

## Markdown Artifact

`decision-packet.md` is generated deterministically from `decision-packet.json` and includes:

- Decision
- Why This Decision
- Top Risks
- Material Gaps
- Acceptance Summary
- Confidence and Limitations
- Required Actions
- Required Reviewers
- Evidence References
- Non-Claims

## Report Integration

`final-report.html` includes a concise Decision Packet section near the top with decision, score, rationale, top risks, required reviewers, confidence, and a reference to `decision-packet.json`.

## Acceptance Criteria

- `decision-packet.json` is generated for scans.
- `decision-packet.md` is generated when Markdown output is enabled.
- Both packet artifacts are included in `manifest.json`.
- Scanner decision and score are preserved.
- Top risks and material gaps sort deterministically.
- Required reviewers are derived conservatively.
- Non-claims are always present.
- Acceptance summaries come from the acceptance matrix.
- Confidence limitations are included.
- The HTML report includes a Decision Packet section.
- Generated runtime output folders are not committed.
