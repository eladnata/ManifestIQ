# ManifestIQ Human Review Checklist Specification

**Status:** Specification for the human-review preparation instrument. Design specification only — no implementation.
**Governed by:** the Phase 15D design package and internal trust doctrine, especially [DECISION_SEMANTICS_STANDARD](../internal/DECISION_SEMANTICS_STANDARD.md) (§6 Human Approval Semantics, §10 Misuse Controls) and [TRUST_BOUNDARY_AND_NON_CLAIMS](../internal/TRUST_BOUNDARY_AND_NON_CLAIMS.md). Companion: [GUI_PRODUCT_WORKFLOW](GUI_PRODUCT_WORKFLOW.md), [REPORT_EXPORT_CENTER_SPEC](REPORT_EXPORT_CENTER_SPEC.md).

The Human Review Checklist **prepares humans to review**. It never captures, records, implies, or infers approval. Its entire purpose is to make a reviewer ready — to put the right evidence, questions, and limitations in front of the right role — and then get out of the way. The human decision happens outside ManifestIQ.

---

## 1. Governing Rule

- ManifestIQ **prepares** review; it **does not** perform, capture, or infer it.
- There is **no Approve, Sign-off, Certify, or Release control** anywhere in this instrument.
- The human-approval decision layer remains **empty and labelled "Human approval is not inferred"** throughout.

## 2. Allowed vs Forbidden Language

**Allowed** (the only sanctioned vocabulary for this instrument):
- Prepare checklist
- Ready for human review
- Review required
- Export checklist

**Forbidden** (must never appear as a product claim or control):
- Approve · Sign off · Certified · Compliant · Release approved · SOX approved · Privacy approved

`Ready for human review` means the evidence is assembled and coherent enough to be examined by a human — it is **not** approval, and must never be styled or worded as such ([DECISION_SEMANTICS_STANDARD](../internal/DECISION_SEMANTICS_STANDARD.md) §3).

## 3. Checklist Structure

A prepared checklist is organized by **reviewer role**. Each role's section contains one or more review items. Each item is a preparation unit, never a decision unit.

### 3.1 Per reviewer role
- **Reviewer role** — the required role (e.g. CISO, AppSec, ITGC / SOX Reviewer, Security Architecture, Data Governance, Legal / Open Source Review), sourced from `decision-packet.json` `required_reviewers`.
- **Why review is required** — the specific blockers/domains/limitations that make this role's review necessary (deterministic, evidence-linked).
- **Scope of review** — which artifacts and domains fall to this role.

### 3.2 Per review item
- **Item title** — the finding, gap, domain posture, or limitation to inspect.
- **Items to inspect** — the concrete evidence to open (rule ID, affected files, domain results).
- **Evidence links** — a descent route to the hash-verified evidence (Finding Detail → Evidence Vault). An item without a traceable link is marked `Insufficient Evidence`, never presented as reviewable-and-clear.
- **Questions to answer** — the deterministic questions a reviewer must resolve (e.g. "Is the bounded risk acceptance for X within its stated scope and validity?", "Does the SOX control gap have compensating evidence outside this scan's scope?"). These are prompts for the human, not judgments by ManifestIQ.
- **Unresolved limitations** — the run limitations relevant to this item (e.g. "Raw decision provenance incomplete", missing `release-candidate-summary.json`), carried verbatim.
- **Item state** — `Review required` / `Mandatory Review` / `Conditional Review` only. Never "reviewed", never "approved".

## 4. Review Packet Summary

A one-page summary that accompanies the checklist:

- **Run identity & integrity** — the manifest fingerprint and integrity state (fact, not judgment).
- **Visible decision** — the conservative visible decision and its one-line reason (never an approval).
- **Roles required** — the set of reviewer roles and why each is required.
- **Outstanding blockers** — the top blockers still gating the decision.
- **Unresolved limitations** — the full limitations list, prominent.
- **Non-claims** — the standing non-claims (not certified; no SOX/privacy/legal approval; not a release approval; no safety claim; human approval not inferred).

The summary states plainly: *This packet prepares a human review. It records no approval and infers none.*

## 5. Artifact Dependencies

| Content | Source artifact |
|---|---|
| Reviewer roles | `decision-packet.json` `required_reviewers` |
| Why review required | `decision-packet.json` (blocking/conditional reasons), `gaps.json` |
| Items to inspect / evidence links | `findings.json`, `evidence-graph.json`, `manifest.json` |
| Domain scope | `enterprise-acceptance-matrix.json`, `control-context.json` |
| Unresolved limitations | `decision-packet.json` `limitations`, `trust-safety-review.json` |
| Integrity / fingerprint | `manifest.json`, `sha256.txt` |

## 6. Exportable Checklist

- **Action label.** "Export checklist" (never "Export approval").
- **Formats.** Local human-readable (Markdown/PDF-style) and machine-readable JSON.
- **Contents.** The full role-organized checklist + the review packet summary + non-claims + limitations.
- **Local-only.** Writes a local file; never transmitted, never uploaded. See [REPORT_EXPORT_CENTER_SPEC](REPORT_EXPORT_CENTER_SPEC.md).
- **Non-claims embedded.** Every exported checklist carries the standing non-claims and a header stating it is a preparation instrument, not an approval.

## 7. Empty / Missing Evidence Behavior

- Missing `required_reviewers` → the checklist still renders with a `Mandatory Review` catch-all and an explicit limitation that reviewer routing could not be derived.
- An item whose evidence cannot be traced → `Insufficient Evidence`, listed for the reviewer's attention, never hidden.
- Unresolved limitations are **first-class content**, never below the fold.

## 8. Forbidden Behavior

- No Approve/Sign-off/Certify/Release control or state.
- No capture of a human decision, name-as-approver, or timestamp-as-approval.
- No green approval styling; the only green permitted is the integrity fingerprint (a fact).
- No implication that completing the checklist approves anything.
- No transmission of the checklist or its evidence.

## 9. Related

- [GUI_PRODUCT_WORKFLOW](GUI_PRODUCT_WORKFLOW.md) · [REPORT_EXPORT_CENTER_SPEC](REPORT_EXPORT_CENTER_SPEC.md) · [DECISION_SEMANTICS_STANDARD](../internal/DECISION_SEMANTICS_STANDARD.md) · [TRUST_BOUNDARY_AND_NON_CLAIMS](../internal/TRUST_BOUNDARY_AND_NON_CLAIMS.md)
