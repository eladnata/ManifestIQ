# ManifestIQ Trust Boundary and Non-Claims

**Status:** Internal standard. Binding on all decision-facing output and external boundaries.
**Audience:** CISO, CTO, AppSec, Security Engineering, Enterprise Architecture, DevSecOps, ITGC / SOX reviewers, Legal / Privacy reviewers, Release decision reviewers.
**Parent doctrine:** [TRUST_SAFETY_DOCTRINE](TRUST_SAFETY_DOCTRINE.md).

---

## 1. Purpose

This standard defines the boundary of what ManifestIQ is trusted to do, the claims it **MUST NOT** make, and the data boundary it **MUST NOT** cross. It exists so that reviewers, auditors, and decision-makers understand precisely where ManifestIQ's authority ends and human judgment begins.

## 2. What ManifestIQ Is

- ManifestIQ is a local-first, deterministic, non-AI, non-cloud, evidence-backed enterprise assurance platform.
- ManifestIQ **prepares evidence for expert review.**
- ManifestIQ produces findings, evidence packages, system dossiers, decision packets, risk acceptance reviews, governance evidence, and release readiness summaries.

## 3. What ManifestIQ Is Not

- ManifestIQ **does not replace expert review.**
- ManifestIQ is not an approver, certifier, or authority.
- ManifestIQ does not grant compliance, safety, readiness, or trust.
- Trust in ManifestIQ is **controlled trust, not blind trust.** It is trusted to preserve truth, not to manufacture confidence.

## 4. Non-Claims

ManifestIQ **MUST NOT** claim, state, imply, or allow a reader to reasonably infer any of the following:

- certification;
- compliance signoff;
- SOX approval;
- legal approval;
- privacy approval;
- penetration testing completion;
- production approval;
- release approval.

These are outcomes of human and organizational processes outside ManifestIQ. ManifestIQ **MAY** describe the state of evidence relevant to such processes, but **MUST NOT** represent that state as the outcome.

## 5. Forbidden Unsupported Language

The following terms **MUST NOT** appear as positive claims in decision-facing artifacts:

- Approved
- Certified
- Compliant
- Safe
- Production Ready
- SOX Approved
- Privacy Approved
- Legally Approved
- Fully Secure

### 5.1 Narrow permitted uses

These terms **MAY** appear only when they are unambiguously **not** a claim by ManifestIQ, specifically when they are:

- **non-claims** — statements that ManifestIQ does not assert the term (e.g., "ManifestIQ does not determine whether this system is Compliant");
- **denied claims** — explicit denials (e.g., "Not Approved");
- **quoted forbidden terms** — the term shown as a controlled example of language that must not be used as a claim;
- **labels from raw legacy input** — a value carried verbatim from external raw input and clearly attributed as such, preserved as evidence under [EVIDENCE_INTEGRITY_STANDARD](EVIDENCE_INTEGRITY_STANDARD.md), not adopted as ManifestIQ's own conclusion.

In every permitted use, the framing **MUST** make clear that ManifestIQ is not asserting the term.

## 6. Allowed Conservative Language

Decision-facing artifacts **MAY** use conservative statuses, including:

- `Missing Evidence`
- `Insufficient Evidence`
- `Mandatory Review`
- `Conditional Review`
- `Not Ready`
- `Not Approved`
- `Unknown`
- `Limitation`
- `Ready for Review`

`Ready for Review` **MUST NEVER** be treated as approval. See [DECISION_SEMANTICS_STANDARD](DECISION_SEMANTICS_STANDARD.md).

## 7. Data Boundary (No External Transmission)

- ManifestIQ **MUST NOT** transmit source code, evidence, repository metadata, findings, or generated artifacts to any external service.
- ManifestIQ **MUST NOT** use AI inference, LLM calls, embeddings, cloud services, telemetry, or any external source transmission.
- All analysis **MUST** remain deterministic, local, reproducible, and evidence-backed.
- **Local deterministic evidence is the only basis for claims.**

### 7.1 Enforceable Network Isolation

The non-transmission guarantee **MUST** be a verifiable property, not an assertion.

- ManifestIQ **MUST** be fully operable in a network-isolated environment. The complete scan, analysis, and artifact-generation path **MUST NOT** depend on any network access.
- Any outbound network capability in ManifestIQ **MUST** be treated as a defect, not a feature. ManifestIQ **MUST NOT** contain code paths that open network connections during scanning, analysis, or artifact generation.
- Absence of such network paths **SHOULD** be verifiable by inspection and by running under network isolation without loss of function.

### 7.2 No External Enrichment

- ManifestIQ **MUST NOT** perform external enrichment as part of a run, including vulnerability-feed retrieval, license lookups, reputation or intelligence queries, or dependency resolution over a network.
- Every conclusion **MUST** rest only on local, deterministic evidence. ManifestIQ **MUST NOT** substitute externally retrieved data for local evidence.

### 7.3 No Telemetry, No Silent Network Calls

- ManifestIQ **MUST NOT** emit telemetry of any kind — usage, diagnostic, metrics, or crash reporting — at any time, including during error handling.
- ManifestIQ **MUST NOT** perform silent or background network calls, update checks that transmit data, or any "phone-home" behavior.

### 7.4 Transitive Dependency Responsibility

- The guarantees in this section **MUST** hold transitively through all dependencies. A dependency that opens a network path, emits telemetry, or performs external enrichment **MUST** be treated as a violation of this standard.
- Dependency discipline that upholds these guarantees is specified in [SECURE_ENGINEERING_STANDARD](SECURE_ENGINEERING_STANDARD.md).

## 8. Limitations Must Be Prominent

- Decision-facing artifacts **MUST** expose their limitations prominently, alongside the conclusions those limitations affect.
- Missing evidence **MUST** be presented as a first-class finding or limitation, never as an omission or an implied pass.
- ManifestIQ **MUST prefer false caution over false confidence**, and **MUST** choose explicit caution because it is more dangerous when silent than when noisy.

## 9. Human Authority

- Material security, architecture, SOX, privacy, legal, operational, and release-impacting conclusions **MUST** be reserved for human expert review.
- Human approval, if ever implemented in the future, **MUST** be explicit, attributable, scoped, and auditable, and **MUST NOT** be inferred or synthesized by ManifestIQ.

## 10. Self-Standard

**ManifestIQ itself MUST exceed the standards it evaluates.** It **MUST NOT** make, about itself or its own output, any claim it forbids others' evidence from implying.

## 11. Related Standards

- [TRUST_SAFETY_DOCTRINE](TRUST_SAFETY_DOCTRINE.md)
- [EVIDENCE_INTEGRITY_STANDARD](EVIDENCE_INTEGRITY_STANDARD.md)
- [FAILURE_SAFETY_STANDARD](FAILURE_SAFETY_STANDARD.md)
- [DECISION_SEMANTICS_STANDARD](DECISION_SEMANTICS_STANDARD.md)
- [THREAT_AND_MISUSE_MODEL](THREAT_AND_MISUSE_MODEL.md)
- [DATA_PROTECTION_AND_ARTIFACT_HYGIENE](DATA_PROTECTION_AND_ARTIFACT_HYGIENE.md)
- [SECURE_ENGINEERING_STANDARD](SECURE_ENGINEERING_STANDARD.md)
