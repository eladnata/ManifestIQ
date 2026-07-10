# ManifestIQ Trust & Safety Doctrine

**Status:** Internal doctrine. Binding on design, implementation, and review.
**Audience:** CISO, CTO, AppSec, Security Engineering, Enterprise Architecture, DevSecOps, ITGC / SOX reviewers, Legal / Privacy reviewers, Release decision reviewers.
**Scope:** Governs all ManifestIQ behavior that produces or influences findings, evidence, dossiers, decision packets, risk acceptance reviews, governance evidence, and release readiness summaries.

---

## 1. Purpose

This doctrine defines the trust foundation of ManifestIQ. It exists to prevent one specific, unacceptable failure: **false confidence** — a state in which ManifestIQ presents something as approved, compliant, safe, or ready when the underlying evidence does not support that conclusion.

A wrong warning is tolerable. An unsupported green status is dangerous.

This is doctrine, not aspiration. Where a requirement below uses **MUST** or **MUST NOT**, it is a constraint on the product, not a preference.

## 2. Central Principle

**ManifestIQ must be trusted to preserve truth, not to manufacture confidence.**

ManifestIQ is a local-first, deterministic, non-AI, non-cloud, evidence-backed enterprise assurance platform. It prepares evidence for expert review. It does not replace expert review.

Trust in ManifestIQ is **controlled trust, not blind trust**. Every conclusion it presents MUST be traceable to local, deterministic, reproducible evidence.

## 3. Fail-Closed Mandate

ManifestIQ **MUST fail closed, never fail open.**

- When evidence is missing, incomplete, inconsistent, stale, ambiguous, corrupted, or low-confidence, ManifestIQ **MUST** disclose that limitation explicitly.
- ManifestIQ **MUST NOT** convert uncertainty into approval, compliance, readiness, safety, or trust.
- When ManifestIQ cannot establish a fact from evidence, its output **MUST** default to the more cautious status (for example `Unknown`, `Insufficient Evidence`, `Missing Evidence`, `Mandatory Review`, or `Not Ready`), never to a favorable one.

The system is more dangerous when silent than when noisy. It **MUST** therefore choose explicit caution. ManifestIQ **MUST prefer false caution over false confidence.**

## 4. Prohibited Outcomes

ManifestIQ **MUST NOT** silently:

- produce false confidence;
- produce an unsupported green status;
- corrupt, mutate, or lose evidence;
- transmit source code, evidence, repository metadata, findings, or generated artifacts to external services;
- imply approval where only review readiness exists;
- hide, suppress, delete, downgrade, or mutate raw findings;
- present missing evidence as acceptable;
- make weak internal quality look acceptable;
- manufacture confidence from incomplete facts.

## 5. Non-Inference of Approval

- ManifestIQ **MUST NOT** infer human approval from any combination of evidence, status, or absence of findings.
- ManifestIQ **MUST** distinguish clearly between (a) a raw scanner decision, (b) review readiness, (c) risk acceptance coverage, (d) release candidate readiness, and (e) human approval. See [DECISION_SEMANTICS_STANDARD](DECISION_SEMANTICS_STANDARD.md).
- `Ready for Review` **MUST NEVER** be treated as approval.
- Risk acceptance **MUST** be treated as bounded evidence, not as remediation or approval. Exceptions are not remediation.
- Human approval, if ever implemented in the future, **MUST** be explicit, attributable, scoped, and auditable. It **MUST NOT** be synthesized by the system.

## 6. Non-Claims

ManifestIQ **MUST NOT** claim, imply, or state as a positive fact any of the following:

- certification;
- compliance signoff;
- SOX approval;
- legal approval;
- privacy approval;
- penetration testing completion;
- production approval;
- release approval.

The authoritative treatment of these boundaries and the forbidden-language controls are defined in [TRUST_BOUNDARY_AND_NON_CLAIMS](TRUST_BOUNDARY_AND_NON_CLAIMS.md).

## 7. Evidence Integrity

- Raw evidence and derived conclusions **MUST** remain separated.
- Raw findings **MUST** be preserved verbatim, separate from derived summaries.
- Any derived summary **MUST** be traceable back to the evidence it was derived from.
- Missing evidence **MUST** be a first-class finding or limitation, never an omission.

Detailed requirements are defined in [EVIDENCE_INTEGRITY_STANDARD](EVIDENCE_INTEGRITY_STANDARD.md).

## 8. Determinism and Locality

- All analysis **MUST** be deterministic, local, reproducible, and evidence-backed.
- ManifestIQ **MUST NOT** use AI inference, LLM calls, embeddings, cloud services, telemetry, or any external source transmission.
- **Local deterministic evidence is the only basis for claims.** No conclusion may rest on non-local, non-reproducible, or inferred data.

## 9. Human Review Requirement

ManifestIQ **MUST** require human expert review for any material security, architecture, SOX, privacy, legal, operational, or release-impacting conclusion.

- ManifestIQ **prepares** evidence for expert review.
- ManifestIQ **does not replace** expert review.
- Decision-facing artifacts **MUST** expose their limitations prominently, so that reviewers see what ManifestIQ could not establish alongside what it could.

## 10. Self-Standard

**ManifestIQ itself MUST exceed the standards it evaluates.**

The product that judges evidence integrity, fail-closed behavior, and truthful status **MUST NOT** violate those same standards in its own design, defaults, or output.

## 11. Related Standards

- [EVIDENCE_INTEGRITY_STANDARD](EVIDENCE_INTEGRITY_STANDARD.md)
- [FAILURE_SAFETY_STANDARD](FAILURE_SAFETY_STANDARD.md)
- [DECISION_SEMANTICS_STANDARD](DECISION_SEMANTICS_STANDARD.md)
- [TRUST_BOUNDARY_AND_NON_CLAIMS](TRUST_BOUNDARY_AND_NON_CLAIMS.md)
- [THREAT_AND_MISUSE_MODEL](THREAT_AND_MISUSE_MODEL.md)
- [DATA_PROTECTION_AND_ARTIFACT_HYGIENE](DATA_PROTECTION_AND_ARTIFACT_HYGIENE.md)
- [SECURE_ENGINEERING_STANDARD](SECURE_ENGINEERING_STANDARD.md)
- [REGULATORY_AND_GOVERNANCE_ALIGNMENT](REGULATORY_AND_GOVERNANCE_ALIGNMENT.md)
