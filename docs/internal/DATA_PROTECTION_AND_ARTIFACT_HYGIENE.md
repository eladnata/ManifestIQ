# ManifestIQ Data Protection and Artifact Hygiene Standard

**Status:** Internal standard. Binding on all data-at-rest handling and artifact generation.
**Audience:** CISO, CTO, AppSec, Security Engineering, Enterprise Architecture, DevSecOps, ITGC / SOX reviewers, Legal / Privacy reviewers, Release decision reviewers.
**Parent doctrine:** [TRUST_SAFETY_DOCTRINE](TRUST_SAFETY_DOCTRINE.md).

---

## 1. Purpose

The doctrine already governs data in motion (no external transmission). This standard governs data **at rest** and the **hygiene of generated artifacts**, so that ManifestIQ does not become the path by which source code, secrets, or personal data leak — including through an artifact an operator later shares in good faith.

## 2. Locality and Confidentiality at Rest

- All scanned source and all evidence **MUST** remain within the local environment.
- The evidence storage location **MUST** be explicit and operator-controlled. ManifestIQ **MUST NOT** default to a shared, synchronized, or externally backed location.
- Raw evidence **MUST** be treated as at least as sensitive as the source it derives from.
- ManifestIQ **MUST NOT** retain source or evidence in undisclosed locations, temporary or otherwise, beyond what the operator can see and control.
- Retention and deletion **MUST** be under explicit operator control. ManifestIQ **MUST NOT** silently persist evidence after the operator has requested its removal.

## 3. Secret and Personal-Data Handling

- Secrets, credentials, tokens, keys, and personal data encountered in source **MUST NOT** be introduced into derived summaries.
- Such values **MUST NOT** be transmitted (there is no transmission) and **MUST NOT** be written to logs or diagnostic output.
- Where such values must appear in raw evidence to preserve fidelity, the containing artifact **MUST** be marked sensitive, and that artifact **MUST NOT** be represented as safe to distribute.
- ManifestIQ **MUST NOT** expand exposure: it **MUST NOT** copy a secret into more artifacts than fidelity requires.

## 4. Redaction

- ManifestIQ **SHOULD** support redaction in derived, decision-facing artifacts.
- Redaction **MUST** be a presentation-layer operation on derived artifacts only. It **MUST NOT** alter, overwrite, or destroy the corresponding raw evidence.
- A redacted artifact **MUST NOT** be presented as though the underlying sensitive value never existed; the raw evidence and its integrity value remain intact per [EVIDENCE_INTEGRITY_STANDARD](EVIDENCE_INTEGRITY_STANDARD.md).

## 5. Artifact Sensitivity Classification

- Every generated artifact **MUST** carry an explicit sensitivity classification.
- Decision-facing artifacts **MUST** state their classification.
- ManifestIQ **MUST NOT** imply, by wording, formatting, or default, that any artifact is safe to share externally. Distribution decisions are the operator's, informed by the stated classification.
- Classification **MUST** default to the more sensitive value when the correct classification is uncertain, consistent with fail-closed behavior in [FAILURE_SAFETY_STANDARD](FAILURE_SAFETY_STANDARD.md).

## 6. Generated Output Hygiene

- Derived artifacts **MUST NOT** embed content beyond what their stated purpose requires.
- ManifestIQ **MUST NOT** embed hidden fields, undisclosed metadata, or content not visible to the reviewer within a decision-facing artifact.
- Filenames and artifact metadata **MUST NOT** leak sensitive values (for example, secrets or personal data in a filename).

## 7. Relationship to Non-Transmission

This standard **complements** the non-transmission guarantee in [TRUST_BOUNDARY_AND_NON_CLAIMS](TRUST_BOUNDARY_AND_NON_CLAIMS.md); it does not replace it. Local confidentiality and artifact hygiene reduce leakage risk **after** ManifestIQ has produced evidence and **before** an operator distributes it. This document makes no claim of privacy approval or legal approval.

## 8. Related Standards

- [TRUST_SAFETY_DOCTRINE](TRUST_SAFETY_DOCTRINE.md)
- [EVIDENCE_INTEGRITY_STANDARD](EVIDENCE_INTEGRITY_STANDARD.md)
- [FAILURE_SAFETY_STANDARD](FAILURE_SAFETY_STANDARD.md)
- [TRUST_BOUNDARY_AND_NON_CLAIMS](TRUST_BOUNDARY_AND_NON_CLAIMS.md)
- [THREAT_AND_MISUSE_MODEL](THREAT_AND_MISUSE_MODEL.md)
