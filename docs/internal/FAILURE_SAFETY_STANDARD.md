# ManifestIQ Failure Safety Standard

**Status:** Internal standard. Binding on all failure and degraded-mode behavior.
**Audience:** CISO, CTO, AppSec, Security Engineering, Enterprise Architecture, DevSecOps, ITGC / SOX reviewers, Legal / Privacy reviewers, Release decision reviewers.
**Parent doctrine:** [TRUST_SAFETY_DOCTRINE](TRUST_SAFETY_DOCTRINE.md).

---

## 1. Purpose

This standard defines how ManifestIQ behaves when something goes wrong: missing inputs, partial scans, corrupted evidence, internal errors, or ambiguous state. The governing rule is simple and non-negotiable: **fail closed, never fail open.**

## 2. Fail-Closed Rule

- On any error, uncertainty, or incomplete condition, ManifestIQ **MUST** resolve to the more cautious outcome.
- ManifestIQ **MUST NOT** emit a favorable status (approval, compliance, readiness, safety, or trust) as a fallback, default, or error-recovery path.
- A failure **MUST NOT** be silently swallowed. It **MUST** surface as an explicit limitation in the affected decision-facing artifact.

The system is more dangerous when silent than when noisy. It **MUST** therefore choose explicit caution over a clean-looking but unsupported result.

## 3. Failure and Degradation Conditions

ManifestIQ **MUST** detect and explicitly disclose at least the following conditions:

- missing inputs or missing evidence;
- incomplete or partial scans;
- inconsistent evidence;
- stale evidence;
- ambiguous state;
- corrupted evidence;
- low-confidence results;
- internal errors or aborted processing.

## 4. Required Behavior Per Condition

For each condition above, ManifestIQ **MUST**:

1. Refuse to upgrade any status on the basis of unavailable or unreliable evidence.
2. Set the affected status to a conservative value — for example `Missing Evidence`, `Insufficient Evidence`, `Unknown`, `Not Ready`, `Mandatory Review`, or `Not Approved`.
3. Record the condition as a first-class limitation, traceable to the affected scope.
4. Preserve all raw evidence collected before the failure, per [EVIDENCE_INTEGRITY_STANDARD](EVIDENCE_INTEGRITY_STANDARD.md).

ManifestIQ **MUST NOT**:

- treat a partial scan as a complete scan;
- treat absence of findings caused by failure as a clean result;
- average, round, or roll up a failure into a passing aggregate;
- suppress a failure to preserve a favorable appearance.

## 5. Partial Results

- Partial results **MAY** be presented **only** when clearly labeled as partial and accompanied by the scope that was not covered.
- A partial result **MUST NOT** be promoted to a complete or favorable status.
- Coverage gaps **MUST** be stated explicitly, not implied by omission.

## 6. Error Visibility

- Errors that affect any decision-facing artifact **MUST** be visible in that artifact, not only in logs.
- Limitations arising from failure **MUST** be exposed prominently, alongside the affected conclusions, not buried.
- ManifestIQ **MUST NOT** present a decision-facing artifact that looks complete while concealing that it is degraded.

## 7. Determinism Under Failure

- Failure handling **MUST** be deterministic: the same failing condition **MUST** produce the same conservative outcome.
- ManifestIQ **MUST NOT** introduce randomness, guessing, inference, or external calls to recover from a failure.
- Recovery **MUST NOT** fabricate evidence or substitute assumed values for missing ones.

## 8. No External Escalation

- Failure handling **MUST** remain local.
- ManifestIQ **MUST NOT** transmit failure data, source code, evidence, repository metadata, findings, or artifacts to any external service as part of error handling, diagnostics, or telemetry.

## 9. Self-Standard

ManifestIQ's own failure behavior **MUST** meet or exceed the fail-closed standard it expects of the systems it evaluates. A defect in ManifestIQ **MUST NOT** be allowed to express itself as a falsely favorable result.

## 10. Related Standards

- [TRUST_SAFETY_DOCTRINE](TRUST_SAFETY_DOCTRINE.md)
- [EVIDENCE_INTEGRITY_STANDARD](EVIDENCE_INTEGRITY_STANDARD.md)
- [DECISION_SEMANTICS_STANDARD](DECISION_SEMANTICS_STANDARD.md)
- [TRUST_BOUNDARY_AND_NON_CLAIMS](TRUST_BOUNDARY_AND_NON_CLAIMS.md)
- [THREAT_AND_MISUSE_MODEL](THREAT_AND_MISUSE_MODEL.md)
- [SECURE_ENGINEERING_STANDARD](SECURE_ENGINEERING_STANDARD.md)
