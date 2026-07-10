# ManifestIQ Internal Doctrine — Index

**Status:** Internal orientation and index. Not a substitute for the documents it references.
**Audience:** CISO, CTO, AppSec, Security Engineering, Enterprise Architecture, DevSecOps, ITGC / SOX reviewers, Legal / Privacy reviewers, Release decision reviewers.

---

## Purpose

This directory defines the internal trust foundation for ManifestIQ. This file is an index and orientation guide only. It does not restate the doctrine and is not authoritative on its own — the referenced documents govern.

## Core Principle

**ManifestIQ must be trusted to preserve truth, not to manufacture confidence.**

The following statements orient the reader and are governed in full by the documents below:

- Ready for Review is not approval.
- Risk acceptance is bounded evidence, not remediation or approval.
- Missing evidence must be explicit.
- Raw evidence and derived conclusions must remain separated.

## Top-Level Doctrine

[TRUST_SAFETY_DOCTRINE](TRUST_SAFETY_DOCTRINE.md) is the top-level doctrine. It sets the central principle and the fail-closed mandate, and the other documents operate under it.

## Authoritative Documents

The doctrine set has two tiers. The **core** documents define the trust semantics. The **hardening** documents bind those semantics to observable, falsifiable obligations (threat framing, integrity mechanism, data protection, engineering discipline, governance framing).

| Concern | Authoritative document | Tier |
|---|---|---|
| Top-level doctrine | [TRUST_SAFETY_DOCTRINE](TRUST_SAFETY_DOCTRINE.md) | Core |
| Evidence integrity, integrity manifest, provenance | [EVIDENCE_INTEGRITY_STANDARD](EVIDENCE_INTEGRITY_STANDARD.md) | Core |
| Failure safety | [FAILURE_SAFETY_STANDARD](FAILURE_SAFETY_STANDARD.md) | Core |
| Decision semantics | [DECISION_SEMANTICS_STANDARD](DECISION_SEMANTICS_STANDARD.md) | Core |
| Trust boundaries, non-claims, network isolation | [TRUST_BOUNDARY_AND_NON_CLAIMS](TRUST_BOUNDARY_AND_NON_CLAIMS.md) | Core |
| Threats, adversaries, misuse and abuse scenarios | [THREAT_AND_MISUSE_MODEL](THREAT_AND_MISUSE_MODEL.md) | Hardening |
| Data-at-rest confidentiality, secrets, redaction, artifact hygiene | [DATA_PROTECTION_AND_ARTIFACT_HYGIENE](DATA_PROTECTION_AND_ARTIFACT_HYGIENE.md) | Hardening |
| Dependency discipline, secure defaults, self-test discipline | [SECURE_ENGINEERING_STANDARD](SECURE_ENGINEERING_STANDARD.md) | Hardening |
| Governance framing, auditability, non-claiming alignment | [REGULATORY_AND_GOVERNANCE_ALIGNMENT](REGULATORY_AND_GOVERNANCE_ALIGNMENT.md) | Hardening |

For any question in one of these areas, the listed document is authoritative. Where documents cross-reference, each concern has a single owning document to avoid divergence.

## Reading Order

1. [TRUST_SAFETY_DOCTRINE](TRUST_SAFETY_DOCTRINE.md) — start here.
2. [EVIDENCE_INTEGRITY_STANDARD](EVIDENCE_INTEGRITY_STANDARD.md)
3. [FAILURE_SAFETY_STANDARD](FAILURE_SAFETY_STANDARD.md)
4. [DECISION_SEMANTICS_STANDARD](DECISION_SEMANTICS_STANDARD.md)
5. [TRUST_BOUNDARY_AND_NON_CLAIMS](TRUST_BOUNDARY_AND_NON_CLAIMS.md)
6. [THREAT_AND_MISUSE_MODEL](THREAT_AND_MISUSE_MODEL.md)
7. [DATA_PROTECTION_AND_ARTIFACT_HYGIENE](DATA_PROTECTION_AND_ARTIFACT_HYGIENE.md)
8. [SECURE_ENGINEERING_STANDARD](SECURE_ENGINEERING_STANDARD.md)
9. [REGULATORY_AND_GOVERNANCE_ALIGNMENT](REGULATORY_AND_GOVERNANCE_ALIGNMENT.md)
