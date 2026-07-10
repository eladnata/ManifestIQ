# ManifestIQ Regulatory and Governance Alignment

**Status:** Internal standard. Framing document; binding on how ManifestIQ describes its governance relevance.
**Audience:** CISO, CTO, AppSec, Security Engineering, Enterprise Architecture, DevSecOps, ITGC / SOX reviewers, Legal / Privacy reviewers, Release decision reviewers.
**Parent doctrine:** [TRUST_SAFETY_DOCTRINE](TRUST_SAFETY_DOCTRINE.md).

---

## 1. Purpose

This standard frames how ManifestIQ's properties relate to established governance concerns — positively and precisely — **without claiming compliance, certification, or approval of any kind**. It exists so that reviewers can see the governance relevance of the product without the product overstating its role.

## 2. Governing Constraint

- ManifestIQ **MUST NOT** claim certification, compliance signoff, SOX approval, legal approval, privacy approval, penetration testing completion, production approval, release approval, or safety.
- ManifestIQ **MAY** describe the **state of evidence** relevant to a governance process. It **MUST NOT** describe that state as the **outcome** of the process.
- ManifestIQ is not a control owner, an approver, or an attestation authority. It **prepares evidence for expert review** and **does not replace** it.

## 3. Alignment Framing

Each area below states how ManifestIQ's properties are relevant and the explicit non-claim that bounds them.

### 3.1 ASDLC / Secure SDLC
ManifestIQ produces local, deterministic evidence inputs that can inform secure-SDLC review activities. It **MUST NOT** be represented as an SDLC gate, a passing control, or an approval within the SDLC. It supports early evidence collection without transmitting source or evidence.

### 3.2 SOX / ITGC
ManifestIQ's immutable raw evidence, run provenance, deterministic regeneration, and enforced separation between tool output and human approval are relevant to ITGC concerns of completeness, accuracy, and segregation of duties. ManifestIQ **MUST NOT** claim to be a SOX control, to provide SOX signoff, or to establish control effectiveness. Those are determinations of control owners and auditors.

### 3.3 Privacy / Legal
Local-only handling, data minimization in derived summaries, artifact sensitivity classification, and redaction (see [DATA_PROTECTION_AND_ARTIFACT_HYGIENE](DATA_PROTECTION_AND_ARTIFACT_HYGIENE.md)) are relevant to privacy and legal review. ManifestIQ **MUST NOT** make any privacy or legal determination and **MUST NOT** claim privacy approval or legal approval.

### 3.4 Release Governance
ManifestIQ supplies release **readiness evidence**. The release decision and its approval remain human and external. **Release readiness is not release approval** ([DECISION_SEMANTICS_STANDARD](DECISION_SEMANTICS_STANDARD.md)).

### 3.5 Risk Acceptance Governance
Risk acceptances are treated as bounded, scoped, attributable evidence recorded alongside the underlying finding. **Exceptions are not remediation and not approval.** ManifestIQ **MUST NOT** present an exception as closing, resolving, or approving a finding.

## 4. Auditability

- Every run **MUST** be reconstructable from its provenance record and integrity manifest ([EVIDENCE_INTEGRITY_STANDARD](EVIDENCE_INTEGRITY_STANDARD.md)): what was scanned, with what tool version and configuration, producing which artifacts with which integrity values.
- Auditability **MUST** rest on recorded provenance and matching integrity values, not on assertion.
- A conclusion that cannot be traced to supporting evidence **MUST** be represented as `Insufficient Evidence` or `Unknown`.

## 5. Repeatability and Operational Efficiency

Stated as operational properties, without marketing framing:

- **Repeatability** — deterministic runs produce comparable evidence across time and across reviewers.
- **Evidence reuse** — identical inputs yield identical, integrity-verifiable evidence, reducing repeated manual re-derivation.
- **Consistency** — the same conditions produce the same conservative statuses, reducing reviewer-to-reviewer variance.

These properties reduce review friction. They **MUST NOT** be described as reducing the need for human expert review, which remains required for material conclusions ([TRUST_SAFETY_DOCTRINE §9](TRUST_SAFETY_DOCTRINE.md)).

## 6. Related Standards

- [TRUST_SAFETY_DOCTRINE](TRUST_SAFETY_DOCTRINE.md)
- [EVIDENCE_INTEGRITY_STANDARD](EVIDENCE_INTEGRITY_STANDARD.md)
- [DECISION_SEMANTICS_STANDARD](DECISION_SEMANTICS_STANDARD.md)
- [TRUST_BOUNDARY_AND_NON_CLAIMS](TRUST_BOUNDARY_AND_NON_CLAIMS.md)
- [DATA_PROTECTION_AND_ARTIFACT_HYGIENE](DATA_PROTECTION_AND_ARTIFACT_HYGIENE.md)
