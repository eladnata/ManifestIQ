# ManifestIQ Decision Semantics Standard

**Status:** Internal standard. Binding on all status, readiness, and decision-support semantics.
**Audience:** CISO, CTO, AppSec, Security Engineering, Enterprise Architecture, DevSecOps, ITGC / SOX reviewers, Legal / Privacy reviewers, Release decision reviewers.
**Parent doctrine:** [TRUST_SAFETY_DOCTRINE](TRUST_SAFETY_DOCTRINE.md).

---

## 1. Purpose

This standard defines what ManifestIQ's decision-facing statuses mean and, equally important, what they do **not** mean. Its purpose is to prevent the collapse of distinct concepts — scanner output, review readiness, risk acceptance coverage, release candidate readiness, and human approval — into a single misleading signal.

## 2. Distinct Decision Layers

ManifestIQ **MUST** keep the following layers distinct in both computation and presentation. Each layer **MUST NOT** be represented as, or automatically promoted to, a higher layer.

1. **Raw scanner decision** — what a scanner reported, preserved verbatim as evidence.
2. **Review readiness** — whether the evidence is assembled and coherent enough to be reviewed by a human expert.
3. **Risk acceptance coverage** — whether, and to what bounded extent, documented risk acceptances apply to specific findings.
4. **Release candidate readiness** — whether the assembled evidence is sufficient to be considered as a candidate for a release decision.
5. **Human approval** — an explicit, attributable, scoped, and auditable decision made by an authorized person.

- A raw scanner decision **MUST NOT** be presented as review readiness.
- Review readiness **MUST NOT** be presented as risk acceptance coverage.
- Risk acceptance coverage **MUST NOT** be presented as release candidate readiness.
- Release candidate readiness **MUST NOT** be presented as human approval.
- No layer **MUST** be inferred from a lower layer.

## 3. `Ready for Review` Is Not Approval

- `Ready for Review` means only that evidence has been assembled and is coherent enough to be examined by a human expert.
- `Ready for Review` **MUST NEVER** be treated as, displayed as, or implied to be approval.
- ManifestIQ **MUST NOT** derive approval from `Ready for Review`, from an absence of findings, or from any status combination.

## 4. Risk Acceptance Semantics

- Risk acceptance **MUST** be treated as **bounded evidence** describing a documented, scoped decision to accept a specific risk.
- Risk acceptance **MUST NOT** be treated as remediation. **Exceptions are not remediation.**
- Risk acceptance **MUST NOT** be treated as approval of the release, the system, or the finding.
- A risk acceptance **MUST NOT** hide, suppress, downgrade, or mutate the underlying raw finding. The finding remains visible; the acceptance is recorded alongside it as bounded evidence.
- An expired, out-of-scope, or unsupported risk acceptance **MUST NOT** provide coverage and **MUST** be surfaced as a limitation.

## 5. Readiness Is Not Release

- **Review readiness is not approval.**
- **Release readiness is not release approval.**
- A release readiness summary **MUST** describe the state of evidence for a release decision. It **MUST NOT** state or imply that release is approved, authorized, or safe.
- Only an explicit human decision, outside ManifestIQ's authority, can approve a release.

## 6. Human Approval Semantics

- ManifestIQ **MUST NOT** infer, synthesize, or record human approval on a person's behalf.
- If human approval is ever implemented in the future, it **MUST** be explicit, attributable to a named authorized person, scoped to a defined subject, and auditable.
- The absence of an explicit human approval **MUST** be represented as `Not Approved` or `Unknown`, never as an implied pass.

## 7. Status Vocabulary

### 7.1 Allowed conservative statuses

Decision-facing artifacts **MAY** use conservative statuses including:

- `Missing Evidence`
- `Insufficient Evidence`
- `Mandatory Review`
- `Conditional Review`
- `Not Ready`
- `Not Approved`
- `Unknown`
- `Limitation`
- `Ready for Review` (never approval — see §3)

### 7.2 Forbidden unsupported claims

Decision-facing artifacts **MUST NOT** use the following as positive claims. They are permitted only when explicitly framed as non-claims, denied claims, quoted forbidden terms, or labels carried verbatim from raw legacy input:

- Approved
- Certified
- Compliant
- Safe
- Production Ready
- SOX Approved
- Privacy Approved
- Legally Approved
- Fully Secure

The authoritative control for this language is defined in [TRUST_BOUNDARY_AND_NON_CLAIMS](TRUST_BOUNDARY_AND_NON_CLAIMS.md).

## 8. Confidence and Aggregation

- A rollup status **MUST NOT** be more favorable than its least favorable required input.
- Missing or low-confidence inputs **MUST** pull an aggregate toward the conservative side, never away from it.
- ManifestIQ **MUST NOT** inflate confidence through aggregation, and **MUST NOT** manufacture a favorable status from incomplete facts.

## 9. Traceability of Decisions

- Every decision-facing status **MUST** be traceable to the raw evidence that produced it, per [EVIDENCE_INTEGRITY_STANDARD](EVIDENCE_INTEGRITY_STANDARD.md).
- A status that cannot be traced to supporting evidence **MUST** be represented as `Insufficient Evidence` or `Unknown`.

## 10. Misuse Controls

The decision layers above are only trustworthy if they cannot be bypassed. The following controls are normative and apply to every decision-facing artifact.

### 10.1 Status Laundering
- ManifestIQ **MUST NOT** provide any mechanism, configuration, exception, display mode, report mode, or summary mode that converts an unfavorable raw decision into a favorable one without new supporting evidence.
- Review readiness, risk acceptance coverage, and release readiness **MUST NOT** promote, overwrite, or replace the raw scanner decision. The raw decision is preserved and remains visible per [EVIDENCE_INTEGRITY_STANDARD](EVIDENCE_INTEGRITY_STANDARD.md).

### 10.2 Exception Misuse
- Risk acceptance **MUST NOT** reduce the count, severity, visibility, or traceability of the underlying raw finding or material gap.
- Exceptions **MUST** be recorded alongside raw evidence, never in place of it.
- Expired, invalid, draft, revoked, rejected, or scope-mismatched exceptions **MUST NOT** provide coverage, and **MUST** be surfaced as a limitation.

### 10.3 Readiness / Approval Confusion
- `Ready for Review` **MUST NOT** be treated as approval.
- Release readiness **MUST NOT** be treated as release approval.
- Human approval, if ever implemented, **MUST** be explicit, attributable, scoped, and auditable, and **MUST NOT** be inferred or synthesized by ManifestIQ.

### 10.4 Partial Scan Misuse
- Partial, failed, interrupted, degraded, or missing-evidence runs **MUST NOT** be represented as complete.
- Missing evidence **MUST** be surfaced using an allowed conservative status only: `Missing Evidence`, `Insufficient Evidence`, `Mandatory Review`, `Conditional Review`, `Not Ready`, `Unknown`, or `Limitation`. See [FAILURE_SAFETY_STANDARD](FAILURE_SAFETY_STANDARD.md).

### 10.5 Cross-Reference
- These controls correspond to the misuse and abuse scenarios M1–M7 in [THREAT_AND_MISUSE_MODEL](THREAT_AND_MISUSE_MODEL.md).
- Forbidden-language controls for decision-facing artifacts are authoritative in [TRUST_BOUNDARY_AND_NON_CLAIMS](TRUST_BOUNDARY_AND_NON_CLAIMS.md).

## 11. Related Standards

- [TRUST_SAFETY_DOCTRINE](TRUST_SAFETY_DOCTRINE.md)
- [EVIDENCE_INTEGRITY_STANDARD](EVIDENCE_INTEGRITY_STANDARD.md)
- [FAILURE_SAFETY_STANDARD](FAILURE_SAFETY_STANDARD.md)
- [TRUST_BOUNDARY_AND_NON_CLAIMS](TRUST_BOUNDARY_AND_NON_CLAIMS.md)
- [THREAT_AND_MISUSE_MODEL](THREAT_AND_MISUSE_MODEL.md)
- [REGULATORY_AND_GOVERNANCE_ALIGNMENT](REGULATORY_AND_GOVERNANCE_ALIGNMENT.md)
