# ManifestIQ GUI Artifact-to-Screen Map

**Status:** Information architecture — artifact/screen mapping. Design specification only.
**Governed by:** the Phase 15D design package and internal trust doctrine. Companion: [GUI_INFORMATION_ARCHITECTURE](GUI_INFORMATION_ARCHITECTURE.md), [GUI_PRODUCT_WORKFLOW](GUI_PRODUCT_WORKFLOW.md).

This document maps each **real evidence-package artifact** (produced by the existing scanner — no new artifacts proposed) to the screens that consume it, and states each screen's fail-closed behavior when an artifact is missing. It is the read-model contract for later implementation phases. The GUI is **read-only** over a sealed package; it never writes into the evidence package.

---

## 1. Artifact → Consuming Screens

| Artifact | Produced by (stage) | Primary consumer screen(s) | Also read by |
|---|---|---|---|
| `manifest.json` | Manifest sealing | Evidence Vault, Evidence Package Sealed | Board Verdict Room (fingerprint/integrity), all result rooms (integrity line) |
| `sha256.txt` | Manifest sealing | Evidence Vault | Evidence Package Sealed |
| `scan-summary.json` | Decision packet generation | Scan Run Progress, Board Verdict Room | Re-run comparison |
| `decision-packet.json` | Decision packet generation | Board Verdict Room, Decision Rationale | Remediation Path, Human Review Checklist, Export Center |
| `decision-packet.md` | Decision packet generation | — (source for Executive Decision Report export) | Export Center |
| `system-dossier.json` | Evidence collection | System Dossier Snapshot | Domain Heat Map, Human Review Checklist, Export Center |
| `enterprise-acceptance-matrix.json` | Control mapping | Domain Heat Map | Board Verdict Room (layer context) |
| `risk-acceptance-review.json` | Exception application | Remediation Path, Board Verdict Room (risk-acceptance layer) | Human Review Checklist |
| `release-candidate-summary.json` | Release candidate prep (optional) | Board Verdict Room (release-readiness layer) | Export Center |
| `trust-safety-review.json` | Trust safety checks (optional) | Board Verdict Room (limitations), Evidence Vault | Human Review Checklist |
| `findings.json` | Rule evaluation | Finding Detail, Domain Heat Map | Human Review Checklist, Findings Appendix export |
| `gaps.json` | Rule evaluation | Remediation Path, Decision Rationale | Domain Heat Map |
| `evidence-graph.json` | Evidence collection | Decision Rationale, Evidence Vault | Finding Detail (chain) |
| `scoring-results.json` | Scoring | Scan Run Progress, Board Verdict Room (bounded score) | — |
| `confidence-summary.json` | Scoring | Board Verdict Room (confidence), Decision Rationale | — |
| `sast-results.json` | Security analysis | Finding Detail | Domain Heat Map (Security) |
| `secrets-results.json` | Security analysis | Finding Detail | Domain Heat Map (Security / Data Protection) |
| `sox_detector-results.json` | SOX/control mapping | Domain Heat Map (SOX / Finance) | Human Review Checklist (ITGC/SOX) |
| `data_risk-results.json` | Security analysis | Domain Heat Map (Data Protection) | Finding Detail |
| `licenses-results.json` | License/SBOM analysis | Domain Heat Map (License) | Export Center (SBOM) |
| `local-sbom.json` | License/SBOM analysis | System Dossier Snapshot | Evidence Manifest / Audit Evidence Packet export |
| `dependencies-results.json` | Supply-chain analysis | Domain Heat Map (Supply Chain) | Finding Detail |
| `architecture_signals-results.json` | Repository structure analysis | Domain Heat Map (Architecture) | Finding Detail |
| `operational-results.json` | Operational readiness | Domain Heat Map (Operations) | Finding Detail |
| `delivery_readiness-results.json` | Operational readiness | Domain Heat Map (Delivery) | — |
| `maintainability-results.json` | Repository structure analysis | Domain Heat Map (Maintainability) | — |
| `hidden_ai_model_detector-results.json` | Repository structure analysis | Domain Heat Map (AI / Model Risk) | Finding Detail |
| `project_structure-results.json` | Repository structure analysis | System Dossier Snapshot | Domain Heat Map (Architecture) |
| `config-results.json` | Repository structure analysis | Domain Heat Map (Operations) | Finding Detail |
| `documentation-results.json` | Repository structure analysis | Domain Heat Map (Governance) | Remediation Path |
| `rule-evaluation-results.json` | Rule evaluation | Finding Detail | Decision Rationale |
| `rule-contract-validation.json` | Rule evaluation | Evidence Vault (rule integrity) | — |
| `file-inventory.json` | Source intake | System Dossier Snapshot, Finding Detail | Evidence Vault |
| `source-metadata.json` | Source intake | System Dossier Snapshot | Finding Detail |
| `analyzer-capabilities.json` | Preflight | Preflight Gate | Evidence Vault (provenance) |
| `claims.json` | Evidence collection | Decision Rationale | Human Review Checklist |
| `control-context.json` | Control mapping | Domain Heat Map (SOX / Finance) | Human Review Checklist |
| `final-report.html` | Evidence collection | — (legacy report; not a GUI room) | Export Center (reference) |
| `board-verdict-data.json` | GUI data export (`render-gui-data`) | Board Verdict Room (render contract) | — |

## 2. Screen → Required Artifacts (fail-closed summary)

| Screen | Requires | Behavior if a required artifact is missing |
|---|---|---|
| Preflight Gate | `analyzer-capabilities.json` | Precheck holds; surfaced as a limitation; run not started clean. |
| Scan Run Progress | intermediate `*-results.json` | Missing stage output → warning/failed-closed stage, never skipped. |
| Evidence Package Sealed | `manifest.json`, `sha256.txt` | No overall "verified" seal; integrity state = Missing/Partial. |
| Board Verdict Room | `decision-packet.json`, `manifest.json` | Conservative decision (`Not Ready`/`Missing Evidence`); limitation shown. |
| Decision Rationale | `decision-packet.json`, `evidence-graph.json` | Factors without a traceable chain → `Insufficient Evidence`. |
| Domain Heat Map | `enterprise-acceptance-matrix.json`, per-domain `*-results.json` | Uncovered domain → `Insufficient Evidence` tile, never green. |
| Finding Detail | `findings.json`, analyzer `*-results.json` | Unanchored claim → `Insufficient Evidence`; raw finding verbatim. |
| Evidence Vault | `manifest.json`, `sha256.txt` | Failed/stale/missing artifacts surfaced; no overall green. |
| Remediation Path | `decision-packet.json`, `gaps.json` | Missing evidence → material-gap blocker lane. |
| Human Review Checklist | `decision-packet.json` (`required_reviewers`) | Missing reviewer data → `Mandatory Review` with explicit limitation. |
| Report / Export Center | per export (§1) | Export carries an explicit limitations section; never fabricates. |

## 3. Layer-to-Artifact Mapping (Board Verdict five-layer strip)

| Decision layer | Source artifact / field | Fail-closed rule |
|---|---|---|
| Raw Scanner Decision | `decision-packet.json` `raw_decision`/`raw_score` | If absent → `Not Approved`/`Missing Evidence`, limitation "Raw decision provenance incomplete"; never promoted from derived value. |
| Review Readiness | `decision-packet.json` `decision.value` | `Mandatory Review` label; never rendered as approval. |
| Risk Acceptance Coverage | `risk-acceptance-review.json` `review_status` | Missing → `Missing Evidence`; bounded evidence, never remediation. |
| Release Readiness | `release-candidate-summary.json` `status` | Missing → `Missing Evidence`; never inferred from raw decision; never release approval. |
| Human Approval | — (no artifact) | Permanently empty, labelled "Human approval is not inferred". |

## 4. Constraints

- The GUI **reads** these artifacts; it never mutates, deletes, downgrades, or writes into the evidence package.
- Every value shown is traceable to a hash-verified artifact ([EVIDENCE_INTEGRITY_STANDARD](../internal/EVIDENCE_INTEGRITY_STANDARD.md) §9).
- No artifact is transmitted externally; all consumption and export is local.

## 5. Related

- [GUI_PRODUCT_WORKFLOW](GUI_PRODUCT_WORKFLOW.md) · [GUI_INFORMATION_ARCHITECTURE](GUI_INFORMATION_ARCHITECTURE.md) · [SCAN_RUN_EXPERIENCE](SCAN_RUN_EXPERIENCE.md) · [REPORT_EXPORT_CENTER_SPEC](REPORT_EXPORT_CENTER_SPEC.md)
