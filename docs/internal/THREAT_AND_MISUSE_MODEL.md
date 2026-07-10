# ManifestIQ Threat and Misuse Model

**Status:** Internal standard. Binding on design, implementation, and review.
**Audience:** CISO, CTO, AppSec, Security Engineering, Enterprise Architecture, DevSecOps, ITGC / SOX reviewers, Legal / Privacy reviewers, Release decision reviewers.
**Parent doctrine:** [TRUST_SAFETY_DOCTRINE](TRUST_SAFETY_DOCTRINE.md).

---

## 1. Purpose

This standard names the adversaries and misuse paths ManifestIQ must defend against, and binds each to a controlling property. Its purpose is to make the doctrine falsifiable: every trust claim must trace to a defense against a specific, named threat.

This document does not describe an incident, a test result, or an assurance outcome. It defines expectations.

## 2. Trust Boundaries

- **Untrusted:** all repository content under analysis — source, configuration, metadata, and any legacy or third-party artifacts within scope.
- **Untrusted between generation and review:** the evidence store, once written, may be altered by parties other than ManifestIQ.
- **Trusted only when verified:** ManifestIQ's own binaries and dependencies. Trust in them is conditional on the controls in [SECURE_ENGINEERING_STANDARD](SECURE_ENGINEERING_STANDARD.md).
- **Outside the boundary:** any network, external service, or remote store. Nothing inside the boundary may depend on anything outside it. See [TRUST_BOUNDARY_AND_NON_CLAIMS](TRUST_BOUNDARY_AND_NON_CLAIMS.md).

## 3. Adversaries and Controlling Properties

ManifestIQ **MUST** defend against at least the following actors. Each row states the controlling property and where it is specified.

| # | Adversary | Objective | Controlling property | Specified in |
|---|---|---|---|---|
| A1 | Untrusted repository content | Execute code, influence ManifestIQ control flow or output classification | Scanned content is treated as inert data; never executed or evaluated; cannot influence status | §4, [FAILURE_SAFETY_STANDARD](FAILURE_SAFETY_STANDARD.md) |
| A2 | User seeking a favorable result | Convert an unfavorable status into a favorable one ("status laundering") | No mechanism upgrades a status without new supporting evidence | [DECISION_SEMANTICS_STANDARD](DECISION_SEMANTICS_STANDARD.md) |
| A3 | Evidence-store tamperer | Alter raw or derived evidence between generation and review | Content integrity values and run manifest make tampering detectable; fail closed on mismatch | [EVIDENCE_INTEGRITY_STANDARD](EVIDENCE_INTEGRITY_STANDARD.md) |
| A4 | Compromised or malicious dependency | Exfiltrate data, open network paths, introduce non-determinism | Minimal, pinned, locally verifiable dependencies; no network paths; no telemetry | [SECURE_ENGINEERING_STANDARD](SECURE_ENGINEERING_STANDARD.md) |
| A5 | Exfiltration via the tool | Move source or evidence out of the local environment through ManifestIQ | Fully operable network-isolated; any outbound path is a defect | [TRUST_BOUNDARY_AND_NON_CLAIMS](TRUST_BOUNDARY_AND_NON_CLAIMS.md) |
| A6 | Careless or coerced operator | Share evidence that embeds secrets or personal data | Artifact sensitivity classification; secrets excluded from derived summaries; no artifact implied safe to share | [DATA_PROTECTION_AND_ARTIFACT_HYGIENE](DATA_PROTECTION_AND_ARTIFACT_HYGIENE.md) |

## 4. Untrusted-Input Requirements

- ManifestIQ **MUST** treat all scanned content as untrusted input.
- Scanned content **MUST NOT** be executed, interpreted, or evaluated as code, expression, template, or query by ManifestIQ.
- Scanned content **MUST NOT** influence ManifestIQ's control flow, configuration, dependency resolution, output classification, or status decisions.
- Values carried from raw input (including status-like labels) **MUST** be preserved as attributed evidence, never adopted as ManifestIQ's own conclusion. See [EVIDENCE_INTEGRITY_STANDARD](EVIDENCE_INTEGRITY_STANDARD.md) and the raw-legacy-label rule in [TRUST_BOUNDARY_AND_NON_CLAIMS](TRUST_BOUNDARY_AND_NON_CLAIMS.md).
- Path, filename, and content handling **MUST** be resistant to traversal, injection, and resource-exhaustion via crafted input; on any such condition ManifestIQ **MUST** fail closed.

## 5. Misuse and Abuse Scenarios

Each scenario **MUST** be prevented by a control, not by convention.

| # | Misuse | Required control |
|---|---|---|
| M1 | **Status laundering** — re-running or reconfiguring to obtain a greener status without new evidence | No configuration or default MAY upgrade a status without new supporting evidence; status derives only from evidence |
| M2 | **Exception abuse** — using a risk acceptance to reduce the count, severity, or visibility of a finding | Risk acceptance is recorded alongside the raw finding, never in place of it; the finding remains fully visible |
| M3 | **Stale-evidence reuse** — presenting prior evidence as current | Staleness is detected and disclosed; stale evidence MUST NOT contribute to a favorable status |
| M4 | **Selective omission** — dropping raw findings from a derived view to improve appearance | Raw findings are preserved verbatim and recoverable; omissions in derived views MUST be recoverable |
| M5 | **Partial-as-complete** — presenting an incomplete scan as complete | Partial results MUST be labeled partial with uncovered scope stated; MUST NOT be promoted to complete |
| M6 | **Approval implication** — reading `Ready for Review` or absence of findings as approval | Decision layers remain separate and non-promotable; `Ready for Review` is never approval |
| M7 | **Silent exfiltration** — routing source or evidence outward through the tool | No outbound network path exists in the analysis flow; any such path is a defect |

## 6. Explicitly Out of Scope

To avoid overclaiming, ManifestIQ's threat model **does not** assert defense against:

- a fully compromised host operating system or privileged local attacker with arbitrary code execution;
- physical access to unencrypted local storage outside ManifestIQ's control;
- actions taken on evidence after it has left ManifestIQ's local environment by an operator's own choice.

These limitations **MUST** be stated in decision-facing contexts where relevant, and **MUST NOT** be presented as covered. This document makes no claim of penetration testing completion, security certification, or production approval.

## 7. Related Standards

- [TRUST_SAFETY_DOCTRINE](TRUST_SAFETY_DOCTRINE.md)
- [EVIDENCE_INTEGRITY_STANDARD](EVIDENCE_INTEGRITY_STANDARD.md)
- [FAILURE_SAFETY_STANDARD](FAILURE_SAFETY_STANDARD.md)
- [DECISION_SEMANTICS_STANDARD](DECISION_SEMANTICS_STANDARD.md)
- [TRUST_BOUNDARY_AND_NON_CLAIMS](TRUST_BOUNDARY_AND_NON_CLAIMS.md)
- [DATA_PROTECTION_AND_ARTIFACT_HYGIENE](DATA_PROTECTION_AND_ARTIFACT_HYGIENE.md)
- [SECURE_ENGINEERING_STANDARD](SECURE_ENGINEERING_STANDARD.md)
