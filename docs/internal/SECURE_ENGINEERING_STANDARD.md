# ManifestIQ Secure Engineering Standard

**Status:** Internal standard. Binding on ManifestIQ's own build, dependencies, defaults, and tests.
**Audience:** CISO, CTO, AppSec, Security Engineering, Enterprise Architecture, DevSecOps, ITGC / SOX reviewers, Legal / Privacy reviewers, Release decision reviewers.
**Parent doctrine:** [TRUST_SAFETY_DOCTRINE](TRUST_SAFETY_DOCTRINE.md).

---

## 1. Purpose

The doctrine states that **ManifestIQ itself must exceed the standards it evaluates** ([TRUST_SAFETY_DOCTRINE §10](TRUST_SAFETY_DOCTRINE.md)). This standard makes that obligation concrete and falsifiable: it governs ManifestIQ's own dependencies, defaults, and test discipline, because the product's trust guarantees hold only if its own construction upholds them.

## 2. Dependency Discipline

- ManifestIQ's dependencies **MUST** be minimal. A dependency **MUST NOT** be introduced where the same result can be achieved without it.
- Dependencies **MUST** be pinned to specific, locally verifiable versions.
- The no-transmission, no-telemetry, and determinism guarantees **MUST** hold transitively through every dependency. A dependency that opens a network path, emits telemetry, or introduces non-determinism into the analysis flow **MUST** be treated as a doctrine violation, not an acceptable trade-off.
- ManifestIQ **MUST NOT** depend on any component that introduces AI inference, LLM calls, embeddings, cloud services, external enrichment, or external source transmission.
- Dependency resolution **MUST NOT** occur over a network as part of a scan or analysis run.

## 3. Secure Defaults

- The default configuration **MUST** be the most cautious configuration.
- No default **MAY** favor a more permissive outcome or a more favorable status.
- Enabling a less cautious option **MUST** require an explicit operator action and **MUST NOT** be implied, silent, or reachable through scanned input.
- Where a setting is absent or unreadable, ManifestIQ **MUST** apply the more cautious value, consistent with [FAILURE_SAFETY_STANDARD](FAILURE_SAFETY_STANDARD.md).

## 4. Determinism in Construction

- ManifestIQ's analysis path **MUST** be deterministic: identical inputs and configuration **MUST** produce identical raw evidence and identical derived conclusions, verifiable by matching integrity values per [EVIDENCE_INTEGRITY_STANDARD](EVIDENCE_INTEGRITY_STANDARD.md).
- Sources of non-determinism (unordered iteration, wall-clock-dependent logic, locale- or environment-dependent formatting) **MUST NOT** affect evidence content or status.
- Timestamps and environment data **MAY** appear in provenance records but **MUST NOT** change integrity values of the evidence they describe.

## 5. Test and Verification Discipline

- ManifestIQ **MUST** maintain test coverage commensurate with a critical assurance product.
- The following behaviors **MUST** be covered by tests, as they are the behaviors on which trust depends:
  - fail-closed behavior on missing, incomplete, stale, corrupted, ambiguous, and low-confidence evidence;
  - preservation of raw findings without hide, suppress, delete, downgrade, or mutation;
  - non-inflation of confidence through aggregation;
  - separation and non-promotion of decision layers;
  - the forbidden-language control in decision-facing artifacts;
  - integrity-value matching for deterministic regeneration.
- A change that weakens any doctrine guarantee **MUST** be detectable by the test suite. Absence of such a test for a guarantee **SHOULD** itself be treated as a defect.

## 6. Change Control and Provenance of the Tool

- ManifestIQ's version **MUST** be recorded in every run provenance record so that any result can be attributed to a specific build. See [EVIDENCE_INTEGRITY_STANDARD](EVIDENCE_INTEGRITY_STANDARD.md).
- Changes to doctrine-governed behavior **MUST** be reviewable and attributable.

## 7. Self-Standard

This standard exists so that the claim in [TRUST_SAFETY_DOCTRINE §10](TRUST_SAFETY_DOCTRINE.md) is backed by observable obligations rather than assertion. ManifestIQ **MUST NOT** hold evidence it evaluates to a standard it does not meet in its own dependencies, defaults, determinism, and tests. This document makes no claim of penetration testing completion, security certification, or production approval.

## 8. Related Standards

- [TRUST_SAFETY_DOCTRINE](TRUST_SAFETY_DOCTRINE.md)
- [EVIDENCE_INTEGRITY_STANDARD](EVIDENCE_INTEGRITY_STANDARD.md)
- [FAILURE_SAFETY_STANDARD](FAILURE_SAFETY_STANDARD.md)
- [TRUST_BOUNDARY_AND_NON_CLAIMS](TRUST_BOUNDARY_AND_NON_CLAIMS.md)
- [THREAT_AND_MISUSE_MODEL](THREAT_AND_MISUSE_MODEL.md)
