# ManifestIQ Report / Export Center Specification

**Status:** Specification for the local export center. Design specification only — no implementation.
**Governed by:** the Phase 15D design package and internal trust doctrine, especially [TRUST_BOUNDARY_AND_NON_CLAIMS](../internal/TRUST_BOUNDARY_AND_NON_CLAIMS.md) (§7 no external transmission), [DATA_PROTECTION_AND_ARTIFACT_HYGIENE](../internal/DATA_PROTECTION_AND_ARTIFACT_HYGIENE.md). Companion: [GUI_PRODUCT_WORKFLOW](GUI_PRODUCT_WORKFLOW.md), [GUI_ARTIFACT_TO_SCREEN_MAP](GUI_ARTIFACT_TO_SCREEN_MAP.md).

The Export Center produces **local, audience-targeted documents** from a sealed run. Every export is generated to a local path, carries its non-claims and limitations, and is classified for sensitivity. **No export is ever transmitted, uploaded, or shared to any external service.**

---

## 1. Governing Rules

- **Local-only.** Every export writes a local file. No cloud, no upload, no "share" that transmits, no telemetry.
- **Non-claims travel with the document.** Every export embeds the standing non-claims (not certified; no SOX/privacy/legal approval; not a release approval; no safety claim; human approval not inferred).
- **Limitations travel with the document.** Every export embeds the run's unresolved limitations.
- **No approval-bearing document.** No export states or implies approval, certification, compliance, safety, or production readiness.
- **Sensitivity classified.** Each export declares its sensitivity ([DATA_PROTECTION_AND_ARTIFACT_HYGIENE](../internal/DATA_PROTECTION_AND_ARTIFACT_HYGIENE.md)); none is represented as "safe to share".
- **Traceable.** Every claim in an export is traceable to a hash-verified artifact; the manifest fingerprint is included.

## 2. Export Catalog

Each export defines: **source artifacts · intended audience · format · included sections · non-claims · limitations · local-only behavior.**

---

### 2.1 Executive Decision Report
- **Source artifacts.** `decision-packet.json`, `decision-packet.md`, `scan-summary.json`, `manifest.json`.
- **Intended audience.** CISO, CTO, CIO, CFO, board.
- **Format.** Local human-readable (Markdown/PDF-style).
- **Included sections.** Visible decision + executive label; one-line reason; bounded score; top blockers; one next action; the five decision layers (human approval empty); required reviewers; limitations; non-claims; manifest fingerprint.
- **Non-claims.** Full standing non-claims block.
- **Limitations.** Run limitations, prominent.
- **Local-only.** Writes a local file; never transmitted.

### 2.2 System Dossier
- **Source artifacts.** `system-dossier.json`, `file-inventory.json`, `source-metadata.json`, `local-sbom.json`.
- **Intended audience.** Enterprise Architecture, CTO, auditor.
- **Format.** Local human-readable.
- **Included sections.** System identity; composition; in-scope vs out-of-scope; coverage ratio; scope digest; non-claims; limitations.
- **Non-claims.** Full block.
- **Limitations.** Out-of-scope/unscanned regions named; partial coverage labelled.
- **Local-only.** Local file only.

### 2.3 Evidence Manifest
- **Source artifacts.** `manifest.json`, `sha256.txt`, `evidence-graph.json`.
- **Intended audience.** Auditor, GRC Manager, ITGC/SOX.
- **Format.** Local human-readable + machine-readable JSON.
- **Included sections.** Per-artifact content hashes; provenance (engine version, config, scope, timestamps); integrity state; reproduction note (match by hash only); non-claims.
- **Non-claims.** Integrity is a fact, not approval; no reproduction-by-resemblance claim.
- **Limitations.** Any stale/missing/corrupted artifact listed.
- **Local-only.** Local file only.

### 2.4 Remediation Plan
- **Source artifacts.** `decision-packet.json` (`required_actions`, reasons), `gaps.json`, `risk-acceptance-review.json`.
- **Intended audience.** DevOps lead, engineering owner, GRC Manager.
- **Format.** Local human-readable.
- **Included sections.** Ordered required actions; per-item disposition (Remediable / Review-Gated / Exception-Eligible (bounded)); linked evidence; bounded exceptions shown beside their unmodified findings; non-claims; limitations.
- **Non-claims.** Exceptions are bounded evidence, not remediation or approval.
- **Limitations.** Material gaps (missing evidence) as first-class items.
- **Local-only.** Local file only.

### 2.5 Human Review Checklist
- **Source artifacts.** `decision-packet.json` (`required_reviewers`), `findings.json`, `evidence-graph.json`, `manifest.json`. See [HUMAN_REVIEW_CHECKLIST_SPEC](HUMAN_REVIEW_CHECKLIST_SPEC.md).
- **Intended audience.** Assigned reviewers (CISO, AppSec, ITGC/SOX, etc.).
- **Format.** Local human-readable + machine-readable JSON.
- **Included sections.** Role-organized checklist; items to inspect; evidence links; questions to answer; unresolved limitations; review packet summary; non-claims.
- **Non-claims.** Prepares review; records/infers no approval.
- **Limitations.** Unresolved limitations per item and overall.
- **Local-only.** Local file only.

### 2.6 Findings Appendix
- **Source artifacts.** `findings.json`, analyzer `*-results.json`, `rule-evaluation-results.json`, `file-inventory.json`.
- **Intended audience.** AppSec, engineering owner, auditor.
- **Format.** Local human-readable + machine-readable JSON.
- **Included sections.** Raw findings verbatim (rule ID, severity, affected files, evidence reference); no downgrade/suppression; non-claims; limitations.
- **Non-claims.** Full block; raw findings unmodified.
- **Limitations.** Coverage gaps stated.
- **Local-only.** Local file only.

### 2.7 Audit Evidence Packet
- **Source artifacts.** The full sealed package (`manifest.json`, `sha256.txt`, `decision-packet.json`, `system-dossier.json`, `findings.json`, `risk-acceptance-review.json`, `evidence-graph.json`, analyzer `*-results.json`, `local-sbom.json`, `trust-safety-review.json`).
- **Intended audience.** Auditor, ITGC/SOX, Legal/Privacy reviewers.
- **Format.** Local bundle (directory/archive) + machine-readable JSON index.
- **Included sections.** The sealed evidence set + manifest + integrity states + provenance + non-claims + limitations index.
- **Non-claims.** Full block; the packet supports review, it does not certify or approve.
- **Limitations.** Full limitations index; any failed/stale artifact flagged.
- **Local-only.** Written to a local path; never transmitted. Sensitivity: high — treated as at least as sensitive as source; not represented as safe to share.

### 2.8 Machine-readable JSON
- **Source artifacts.** `board-verdict-data.json` and/or the relevant packet JSONs.
- **Intended audience.** Downstream local tooling, auditors' own local pipelines.
- **Format.** JSON (schema-versioned).
- **Included sections.** The structured data contract (decision, layers, blockers, integrity, limitations, non-claims).
- **Non-claims.** Present as data fields; no approval field exists.
- **Limitations.** Present as data fields.
- **Local-only.** Local file only; consumed locally.

## 3. Export Center Behavior

- **One job.** The Export Center selects and generates exports; it is not a document editor and captures no decision.
- **Preview before generate.** A reviewer can preview an export's included sections and its non-claims before writing the file.
- **Missing-source behavior.** An export whose sources are incomplete is still generated with an explicit limitations section describing what is missing; it never fabricates content and never omits the gap.
- **Sensitivity on every file.** Each generated file states its sensitivity classification; none is labelled "safe to distribute".

## 4. Forbidden Behavior

- No cloud upload, no external share, no transmission of any export.
- No telemetry on export.
- No approval-bearing, certification-bearing, or compliance-bearing document.
- No forbidden positive claim (Approved, Certified, Compliant, Safe, Production Ready, SOX/Privacy/Legally Approved, Fully Secure) as a claim in any export.
- No export that omits its non-claims or limitations.

## 5. Related

- [GUI_PRODUCT_WORKFLOW](GUI_PRODUCT_WORKFLOW.md) · [GUI_ARTIFACT_TO_SCREEN_MAP](GUI_ARTIFACT_TO_SCREEN_MAP.md) · [HUMAN_REVIEW_CHECKLIST_SPEC](HUMAN_REVIEW_CHECKLIST_SPEC.md) · [TRUST_BOUNDARY_AND_NON_CLAIMS](../internal/TRUST_BOUNDARY_AND_NON_CLAIMS.md) · [DATA_PROTECTION_AND_ARTIFACT_HYGIENE](../internal/DATA_PROTECTION_AND_ARTIFACT_HYGIENE.md)
