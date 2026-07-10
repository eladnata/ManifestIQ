# ManifestIQ Evidence Integrity Standard

**Status:** Internal standard. Binding on all evidence handling.
**Audience:** CISO, CTO, AppSec, Security Engineering, Enterprise Architecture, DevSecOps, ITGC / SOX reviewers, Legal / Privacy reviewers, Release decision reviewers.
**Parent doctrine:** [TRUST_SAFETY_DOCTRINE](TRUST_SAFETY_DOCTRINE.md).

---

## 1. Purpose

This standard defines how ManifestIQ handles evidence so that conclusions never drift away from what the evidence actually supports. Evidence integrity is the mechanism by which ManifestIQ preserves truth rather than manufacturing confidence.

## 2. Definitions

- **Raw evidence** — the unmodified facts collected during a scan: raw findings, scanner output, file contents referenced as evidence, and repository metadata as observed.
- **Derived summary** — any conclusion, rollup, status, score, or narrative computed from raw evidence.
- **Decision-facing artifact** — any output intended to inform a human decision: findings reports, evidence packages, system dossiers, decision packets, risk acceptance reviews, governance evidence, and release readiness summaries.

## 3. Separation of Raw and Derived

- ManifestIQ **MUST** preserve raw evidence separately from derived summaries.
- Raw evidence **MUST NOT** be overwritten by derived content.
- A derived summary **MUST NOT** be presented in a way that could be mistaken for raw evidence.
- Where both are shown together, the artifact **MUST** label which is raw and which is derived.

## 4. Preservation of Raw Findings

- ManifestIQ **MUST NOT** hide, suppress, delete, downgrade, or mutate raw findings.
- Raw findings **MUST** be retained verbatim, including severity, source, and location as originally reported.
- Filtering, grouping, deduplication, or prioritization **MAY** be applied only in derived views, and **MUST NOT** alter or discard the underlying raw findings.
- If a derived view omits a raw finding for presentation, the omission **MUST** be recoverable and the raw finding **MUST** remain available.

## 5. Traceability

- Every derived summary **MUST** be traceable back to the specific raw evidence it was derived from.
- A conclusion with no traceable supporting evidence **MUST NOT** be presented as supported. It **MUST** be marked `Insufficient Evidence` or `Unknown`.
- Traceability **MUST** survive across the artifact chain: findings → evidence packages → dossiers → decision packets → release readiness summaries.

## 6. Missing Evidence

- Missing evidence **MUST** be an explicit, first-class finding or limitation.
- ManifestIQ **MUST NOT** present missing evidence as acceptable, resolved, or favorable.
- Absence of a finding **MUST NOT** be reported as absence of risk. "No evidence of a problem" is not "evidence of no problem," and artifacts **MUST NOT** conflate the two.
- Conservative statuses for these conditions include `Missing Evidence`, `Insufficient Evidence`, and `Unknown`.

## 7. Evidence Quality Conditions

ManifestIQ **MUST** detect and disclose evidence that is:

- incomplete;
- inconsistent;
- stale;
- ambiguous;
- corrupted;
- low-confidence.

When any of these conditions applies, the affected derived status **MUST** be lowered to a conservative value and the condition **MUST** be surfaced in the decision-facing artifact. Such conditions **MUST NOT** be silently smoothed over, averaged away, or excluded from rollups.

## 8. Confidence Discipline

- ManifestIQ **MUST NOT** inflate confidence.
- Derived confidence **MUST NOT** exceed the confidence justified by the weakest necessary piece of supporting evidence.
- Aggregation **MUST NOT** turn several low-confidence inputs into a single high-confidence conclusion.
- Weak internal quality **MUST NOT** be presented as acceptable through summarization.

## 9. Integrity Manifest and Provenance

Integrity, traceability, and determinism **MUST** be bound to an observable mechanism, not asserted.

### 9.1 Content Integrity Values
- Each raw and derived artifact **MUST** carry a content integrity value (for example, a cryptographic content hash).
- ManifestIQ **MUST** detect and disclose any artifact whose content does not match its recorded integrity value, and **MUST** treat such an artifact as corrupted per [FAILURE_SAFETY_STANDARD](FAILURE_SAFETY_STANDARD.md).

### 9.2 Run Manifest and Provenance
- Every run **MUST** produce a manifest recording: ManifestIQ version, configuration, scan scope, timestamps, and the integrity value of every raw and derived artifact.
- The manifest **MUST** be sufficient to reconstruct what was scanned, with what version and configuration, producing which artifacts. This is the basis of auditability in [REGULATORY_AND_GOVERNANCE_ALIGNMENT](REGULATORY_AND_GOVERNANCE_ALIGNMENT.md).

### 9.3 Verifiable Raw-to-Derived Traceability
- A derived summary **MUST** reference the integrity values of the raw evidence it was derived from, so that traceability is verifiable rather than asserted.
- A derived conclusion whose referenced raw evidence cannot be located or verified **MUST** be represented as `Insufficient Evidence` or `Unknown`.

### 9.4 Missing, Stale, and Corrupted Artifacts
- **Missing:** any artifact expected by the manifest but absent **MUST** be surfaced as `Missing Evidence`; a run **MUST NOT** resolve favorably around it.
- **Stale:** an artifact whose inputs have changed since generation **MUST** be flagged stale and **MUST NOT** contribute to a favorable status.
- **Corrupted:** an integrity-value mismatch **MUST** be treated as corrupted, fail closed, and surfaced as a limitation.

### 9.5 Deterministic Regeneration
- Reproduction **MUST** be confirmed by matching integrity values, not by visual similarity or approximate equality.
- "Deterministic" **MUST** mean identical integrity values for evidence under identical inputs and configuration. Provenance fields that legitimately vary (such as timestamps) **MUST NOT** be part of the evidence integrity value they describe.

## 10. Integrity Under Change

- Re-scans **MUST** be reproducible: the same inputs under the same configuration **MUST** produce the same raw evidence and the same derived conclusions, confirmed by matching integrity values per §9.5.
- Evidence **MUST NOT** be corrupted or lost across storage, packaging, or export.
- If integrity cannot be verified, the affected evidence **MUST** be treated as corrupted and surfaced as a limitation per [FAILURE_SAFETY_STANDARD](FAILURE_SAFETY_STANDARD.md).

## 11. Locality of Evidence

- All evidence **MUST** be collected and retained locally.
- ManifestIQ **MUST NOT** transmit raw evidence, derived summaries, source code, repository metadata, findings, or generated artifacts to any external service.
- Confidentiality of evidence at rest is governed by [DATA_PROTECTION_AND_ARTIFACT_HYGIENE](DATA_PROTECTION_AND_ARTIFACT_HYGIENE.md).
- **Local deterministic evidence is the only basis for claims.**

## 12. Related Standards

- [TRUST_SAFETY_DOCTRINE](TRUST_SAFETY_DOCTRINE.md)
- [FAILURE_SAFETY_STANDARD](FAILURE_SAFETY_STANDARD.md)
- [DECISION_SEMANTICS_STANDARD](DECISION_SEMANTICS_STANDARD.md)
- [TRUST_BOUNDARY_AND_NON_CLAIMS](TRUST_BOUNDARY_AND_NON_CLAIMS.md)
- [DATA_PROTECTION_AND_ARTIFACT_HYGIENE](DATA_PROTECTION_AND_ARTIFACT_HYGIENE.md)
- [THREAT_AND_MISUSE_MODEL](THREAT_AND_MISUSE_MODEL.md)
- [REGULATORY_AND_GOVERNANCE_ALIGNMENT](REGULATORY_AND_GOVERNANCE_ALIGNMENT.md)
