# ManifestIQ GUI Product Workflow

**Status:** Product & GUI information architecture. Design specification only — no implementation.
**Audience:** Product design, engineering (later phases), reviewers.
**Governed by:** the Phase 15D design package ([VISUAL_TASTE_DOCTRINE](VISUAL_TASTE_DOCTRINE.md), [UI_FOUNDATIONS](UI_FOUNDATIONS.md), [DESIGN_TOKENS](DESIGN_TOKENS.md), [COMPONENT_RULES](COMPONENT_RULES.md), [MANIFESTIQ_DESIGN_SKILL_PACK](MANIFESTIQ_DESIGN_SKILL_PACK.md), [SCREEN_PURPOSE_MATRIX](SCREEN_PURPOSE_MATRIX.md)) and the internal trust doctrine in [`docs/internal/`](../internal/README.md). Where anything here conflicts with the doctrine, the doctrine wins.

**Companion documents:** [GUI_INFORMATION_ARCHITECTURE](GUI_INFORMATION_ARCHITECTURE.md), [GUI_ARTIFACT_TO_SCREEN_MAP](GUI_ARTIFACT_TO_SCREEN_MAP.md), [SCAN_RUN_EXPERIENCE](SCAN_RUN_EXPERIENCE.md), [HUMAN_REVIEW_CHECKLIST_SPEC](HUMAN_REVIEW_CHECKLIST_SPEC.md), [REPORT_EXPORT_CENTER_SPEC](REPORT_EXPORT_CENTER_SPEC.md), [GUI_NAVIGATION_MODEL](GUI_NAVIGATION_MODEL.md).

---

## 1. Purpose

The GUI must expose the **whole assurance journey** — from loading a project to re-running after remediation — while remaining a guided instrument, not a dashboard. Each step is a room with one job; the journey between rooms is a preflight-style checklist, not a menu. Every step preserves the trust rules: fail closed on missing evidence, never infer approval, green only for integrity, export local-only.

The workflow is deliberately **linear before a result exists** (you are guided through launch → scan → sealed evidence) and **freely navigable after** (all result rooms hang off one sealed run).

## 2. Journey Overview

```
  PRE-RESULT (guided, linear)                 POST-RESULT (free navigation over one sealed run)
  ─────────────────────────────               ────────────────────────────────────────────────
  Portfolio / Home
     └▶ Assessment Launch
          └▶ Preflight Gate
               └▶ Scan Run Progress
                    └▶ Evidence Package Sealed ──▶ Board Verdict Room  ◀── entry to result rooms
                                                     ├─ Decision Rationale
                                                     ├─ Domain Heat Map ─▶ Finding Detail ─▶ Evidence Vault
                                                     ├─ Remediation Path
                                                     ├─ Human Review Checklist (Reviewer Briefing)
                                                     └─ Report / Export Center
                                                          └▶ Re-run Assessment ──▶ (back to Assessment Launch)
```

The **Integrity Line** (top) and **Non-Claims footer** (bottom) are present on every room (per [COMPONENT_RULES](COMPONENT_RULES.md) §1–2, [MANIFESTIQ_DESIGN_SKILL_PACK](MANIFESTIQ_DESIGN_SKILL_PACK.md) §5).

## 3. Step Specifications

Each step below defines: **primary question · primary user · 5-second insight · inputs · outputs · actions · artifacts used · artifacts generated · what must not appear · trust constraints.**

Artifact names refer to real evidence-package files produced by the existing scanner (`scan-summary.json`, `decision-packet.json`, `system-dossier.json`, `findings.json`, `manifest.json`, `risk-acceptance-review.json`, `release-candidate-summary.json`, `trust-safety-review.json`, `*-results.json`, `local-sbom.json`, `gaps.json`, `evidence-graph.json`, `sha256.txt`). No new scanner behavior is proposed.

---

### Step 0 — Portfolio / Home *(where the user starts)*

- **Primary question.** Which system am I assessing, and what has been assessed before?
- **Primary user.** CISO, CIO, GRC Manager.
- **5-second insight.** A quiet roster of prior sealed runs and a single "Start a new assessment" path — never a health dashboard.
- **Inputs.** Locally stored prior run manifests (read-only).
- **Outputs.** Selection of an existing run to review, or entry into Assessment Launch.
- **Actions.** Open a prior sealed run; start a new assessment.
- **Artifacts used.** Prior `manifest.json` + `decision-packet.json` summaries (visible decision + integrity state only).
- **Artifacts generated.** None.
- **What must not appear.** No blended "portfolio health" score; no green aggregate; no approval implication; no table-first wall.
- **Trust constraints.** Each system shows its own conservative visible decision; a failing system is never averaged into an aggregate ([SCREEN_PURPOSE_MATRIX](SCREEN_PURPOSE_MATRIX.md), Portfolio Command "must not show").

### Step 1 — Assessment Launch *(load Git / Folder / ZIP; choose profile & scope)*

- **Primary question.** What will be assessed, locally and deterministically?
- **Primary user.** DevOps lead, engineering owner, GRC Manager.
- **5-second insight.** The chosen source, profile, and scope — plus the standing guarantees (local-only · deterministic · no transmission).
- **Inputs.** A local source: **Folder**, **Git** working copy, or **ZIP**; a **profile** (e.g. `finance-sox`); a **scope** selection.
- **Outputs.** A validated assessment configuration ready for preflight.
- **Actions.** Select source type (Folder/Git/ZIP); choose profile; confirm scope; proceed to Preflight.
- **Artifacts used.** None (pre-scan).
- **Artifacts generated.** An in-memory run configuration (not evidence).
- **What must not appear.** No cloud/account/upload; no external enrichment toggle; no AI option; no telemetry opt-in; no rule builder.
- **Trust constraints.** Source stays local; the guarantees are stated on-screen; nothing is transmitted (maps to CLI `scan-folder` / `scan-zip` / `scan-git`).

### Step 2 — Preflight Gate

- **Primary question.** Is this assessment safe and complete enough to run deterministically?
- **Primary user.** DevOps lead, engineering owner.
- **5-second insight.** A short checklist of preflight conditions (source readable, scope resolved, profile valid, analyzer capabilities present) — pass/hold per item.
- **Inputs.** The run configuration from Launch.
- **Outputs.** A go/hold decision to start the scan; any preflight limitation surfaced.
- **Actions.** Review preflight items; resolve holds; start the scan run.
- **Artifacts used.** `analyzer-capabilities.json` (read to confirm the engine can honor the profile).
- **Artifacts generated.** A preflight record (transient, surfaced as limitations if any item holds).
- **What must not appear.** No skipping unresolved holds silently; no "run anyway" that hides a failed precheck as clean.
- **Trust constraints.** **Fail closed**: an unresolved preflight hold blocks the run or is carried forward as an explicit limitation; never suppressed ([FAILURE_SAFETY_STANDARD](../internal/FAILURE_SAFETY_STANDARD.md)).

### Step 3 — Scan Run Progress

- **Primary question.** What is the scan doing right now, and is any stage failing closed?
- **Primary user.** DevOps lead, engineering owner (may be watched by reviewers).
- **5-second insight.** The current stage and overall progress, with any warning/failed-closed stage visibly flagged — a preflight-instrument progression, not a spinner.
- **Inputs.** The validated run configuration.
- **Outputs.** Per-stage state and the evidence each stage produces. Full detail in [SCAN_RUN_EXPERIENCE](SCAN_RUN_EXPERIENCE.md).
- **Actions.** Watch stages; drill into a stage's produced evidence as it completes; abort (which fails closed, produces no favorable result).
- **Artifacts used.** Intermediate `*-results.json` as they are produced.
- **Artifacts generated.** All analyzer results, `scan-summary.json`, `scoring-results.json`, `evidence-graph.json`, `gaps.json`.
- **What must not appear.** No fake "all green" progress; no success animation; no premature verdict before the manifest is sealed.
- **Trust constraints.** A failed or aborted stage caps the run conservatively and is surfaced; partial runs are labelled partial and never presented as complete.

### Step 4 — Evidence Package Sealed *(evidence package created)*

- **Primary question.** Is the evidence intact, reproducible, and ready to review?
- **Primary user.** Auditor, GRC Manager, DevOps lead.
- **5-second insight.** The run manifest is sealed — content hashes computed, integrity state stated — with a single route into the Board Verdict Room.
- **Inputs.** All produced analyzer results and derived artifacts.
- **Outputs.** A sealed, integrity-manifested evidence package.
- **Actions.** Proceed to Board Verdict Room; or open the Evidence Vault directly.
- **Artifacts used.** All produced artifacts.
- **Artifacts generated.** `manifest.json`, `sha256.txt`, `decision-packet.json`, `system-dossier.json`, `risk-acceptance-review.json` (if exceptions applied), `final-report.html`.
- **What must not appear.** No "verified" seal if any artifact failed; no overall green unless integrity genuinely holds.
- **Trust constraints.** Integrity is a **fact** (green permitted here only), never a judgment; missing/stale/corrupted artifacts fail closed ([EVIDENCE_INTEGRITY_STANDARD](../internal/EVIDENCE_INTEGRITY_STANDARD.md) §9).

### Step 5 — Board Verdict Room *(the decision)*

- **Primary question.** Can this system proceed — if not, why not and what next?
- **Primary user.** CISO, CTO, CIO, CFO.
- **5-second insight.** Visible decision, one-line reason, top blockers, one next action, five separated decision layers (human approval empty). *(Implemented in Phase 16B.)*
- **Inputs.** The sealed evidence package.
- **Outputs.** The board-facing decision surface and routes into every result room.
- **Actions.** Descend to rationale/domains/findings/evidence; open remediation; prepare review; export.
- **Artifacts used.** `decision-packet.json`, `manifest.json`, `risk-acceptance-review.json`, `release-candidate-summary.json` (if present), `trust-safety-review.json` (if present).
- **Artifacts generated.** None (read-only view; `board-verdict-data.json` is the render contract).
- **What must not appear.** No "Approved" output; no green pass hero; no merged status pill; no success animation.
- **Trust constraints.** Human approval never inferred; readiness ≠ approval; risk acceptance ≠ remediation; conservative when raw provenance is incomplete.

### Step 6 — Decision Rationale

- **Primary question.** Why was this decision reached, and does it hold up?
- **Primary user.** CISO, CTO, auditor, senior reviewer.
- **5-second insight.** The ordered decisive factors, each evidence-linked.
- **Inputs.** `decision-packet.json` (blocking/conditional reasons, rationale), `evidence-graph.json`.
- **Outputs.** A traceable rationale; routes to each contributing finding.
- **Actions.** Descend from a factor to its finding and evidence.
- **Artifacts used.** `decision-packet.json`, `evidence-graph.json`, `gaps.json`.
- **Artifacts generated.** None.
- **What must not appear.** No prose without evidence links; no inference-style language beyond the deterministic rules.
- **Trust constraints.** A factor without a traceable badge renders `Insufficient Evidence`, never confirmed.

### Step 7 — Domain Heat Map

- **Primary question.** Where is risk concentrated, and what is unknown?
- **Primary user.** CISO, CTO, Enterprise Architecture, auditor.
- **5-second insight.** Per-domain posture across all domains; unknown/insufficient visibly distinct.
- **Inputs.** `enterprise-acceptance-matrix.json`, `system-dossier.json`, per-domain `*-results.json`.
- **Outputs.** Domain tiles with coverage; routes into findings per domain.
- **Actions.** Enter a domain → Finding Detail.
- **Artifacts used.** `enterprise-acceptance-matrix.json`, `sox_detector-results.json`, `data_risk-results.json`, `architecture_signals-results.json`, `operational-results.json`, `dependencies-results.json`, `licenses-results.json`, etc.
- **Artifacts generated.** None.
- **What must not appear.** No green tile for "no findings"; absence of findings never a pass; no hidden uncovered domain.
- **Trust constraints.** `Insufficient Evidence` is a first-class tile state.

### Step 8 — Finding Detail

- **Primary question.** What is this finding, and what evidence supports it?
- **Primary user.** AppSec, engineering owner, auditor.
- **5-second insight.** The finding, its rule ID and severity, and its evidence chain.
- **Inputs.** `findings.json`, `sast-results.json`, `secrets-results.json`, `rule-evaluation-results.json`.
- **Outputs.** The full descent chain finding → rule → evidence → file → hash.
- **Actions.** Descend to source artifact and content hash (into Evidence Vault).
- **Artifacts used.** `findings.json`, analyzer `*-results.json`, `file-inventory.json`, `source-metadata.json`.
- **Artifacts generated.** None.
- **What must not appear.** No editing; no mutation/downgrade/suppression of the raw finding; no unanchored claim.
- **Trust constraints.** Raw finding shown verbatim; every claim anchored to a hash-verified reference.

### Step 9 — Evidence Vault

- **Primary question.** Can I trust the evidence is intact and reproducible?
- **Primary user.** Auditor, CISO, GRC Manager.
- **5-second insight.** Integrity state of the run — verified vs missing/stale/corrupted.
- **Inputs.** `manifest.json`, `sha256.txt`, `evidence-graph.json`.
- **Outputs.** Per-artifact integrity states; provenance/fingerprint.
- **Actions.** Investigate a failed/stale artifact; trace a finding's evidence chain.
- **Artifacts used.** `manifest.json`, `sha256.txt`, all referenced artifacts.
- **Artifacts generated.** None.
- **What must not appear.** No overall green if any artifact failed; no "looks the same" reproduction claim.
- **Trust constraints.** Green only here and only for verified integrity; failures fail closed.

### Step 10 — Remediation Path

- **Primary question.** What must change, in what order, to move the decision?
- **Primary user.** DevOps lead, engineering owner, GRC Manager.
- **5-second insight.** The ordered required actions and which blockers gate which.
- **Inputs.** `decision-packet.json` (`required_actions`, blocking/conditional reasons), `gaps.json`, `risk-acceptance-review.json`.
- **Outputs.** A prioritized remediation sequence; disposition per item (Remediable / Review-Gated / Exception-Eligible (bounded)).
- **Actions.** Route an item to its reviewer; open its evidence; prepare a re-run once remediated.
- **Artifacts used.** `decision-packet.json`, `gaps.json`, `risk-acceptance-review.json`.
- **Artifacts generated.** None (a Remediation Plan may be exported — see Export Center).
- **What must not appear.** No exception styled as a fix; no "resolved" on an unremediated item; no editing/approval capture.
- **Trust constraints.** Exceptions are bounded evidence, not remediation; expired/invalid exceptions give no coverage.

### Step 11 — Human Review Checklist *(Reviewer Briefing)*

- **Primary question.** Who must review, on what, and are they prepared?
- **Primary user.** GRC Manager, CISO, CTO, and the assigned reviewers.
- **5-second insight.** Required review roles mapped to what each must inspect — a preparation instrument, never a sign-off.
- **Inputs.** `decision-packet.json` (`required_reviewers`), blockers, domains, limitations.
- **Outputs.** A prepared, exportable review checklist and a review packet summary. Full spec in [HUMAN_REVIEW_CHECKLIST_SPEC](HUMAN_REVIEW_CHECKLIST_SPEC.md).
- **Actions.** Prepare checklist; open evidence per item; export checklist / review packet.
- **Artifacts used.** `decision-packet.json`, `system-dossier.json`, `findings.json`, `manifest.json`.
- **Artifacts generated.** An exported checklist / review packet (local file).
- **What must not appear.** No Approve/Sign-off/Certify control; no captured decision; no green approval.
- **Trust constraints.** Prepares humans to review; never records or infers approval ([DECISION_SEMANTICS_STANDARD](../internal/DECISION_SEMANTICS_STANDARD.md) §6, §10).

### Step 12 — Report / Export Center

- **Primary question.** What can I take out of this run, for whom, and in what form?
- **Primary user.** CISO, CFO, auditor, GRC Manager.
- **5-second insight.** A small set of named, audience-targeted exports — each local-only, each carrying its non-claims. Full spec in [REPORT_EXPORT_CENTER_SPEC](REPORT_EXPORT_CENTER_SPEC.md).
- **Inputs.** The sealed evidence package.
- **Outputs.** Local files (Executive Decision Report, System Dossier, Evidence Manifest, Remediation Plan, Human Review Checklist, Findings Appendix, Audit Evidence Packet, machine-readable JSON).
- **Actions.** Select an export; generate it to a local path.
- **Artifacts used.** Depends on export (see the artifact-to-screen map).
- **Artifacts generated.** Local export files only.
- **What must not appear.** No cloud upload; no "share" that transmits; no approval-bearing document; no forbidden positive claim.
- **Trust constraints.** Export is **local-only**; every export states its non-claims and limitations.

### Step 13 — Re-run Assessment

- **Primary question.** After remediation, does the decision change — and is it comparable?
- **Primary user.** DevOps lead, engineering owner, GRC Manager.
- **5-second insight.** A one-path return to Assessment Launch with the prior run available for deterministic comparison.
- **Inputs.** A new local source state (post-remediation); the prior sealed run for reference.
- **Outputs.** A new assessment configuration; a comparison anchored to prior integrity values.
- **Actions.** Start a new run; compare against the prior sealed run (maps to CLI `validate-trend`).
- **Artifacts used.** Prior `manifest.json`, `scan-summary.json`, `decision-packet.json`.
- **Artifacts generated.** A new sealed run (its own package).
- **What must not appear.** No "looks improved" claim; no mutation of the prior run; comparison by integrity values only.
- **Trust constraints.** Deterministic and reproducible; prior evidence never altered; a new run is a new sealed package.

## 4. Cross-Cutting Trust Constraints (all steps)

- **One screen, one job.** No dashboard catch-all; no room does two jobs.
- **Fail closed everywhere.** Missing/incomplete/ambiguous evidence is surfaced, never converted to a favorable state.
- **Human approval never inferred.** No Approve/Sign-off/Certify control exists anywhere.
- **Green is only evidence integrity.** No approved-green on any decision/readiness surface.
- **Every decisive claim descends to evidence** (finding → rule → file → hash).
- **Local-only.** No cloud, no telemetry, no AI, no external transmission; export writes local files only.

## 5. Related

- [GUI_INFORMATION_ARCHITECTURE](GUI_INFORMATION_ARCHITECTURE.md) · [GUI_ARTIFACT_TO_SCREEN_MAP](GUI_ARTIFACT_TO_SCREEN_MAP.md) · [SCAN_RUN_EXPERIENCE](SCAN_RUN_EXPERIENCE.md) · [HUMAN_REVIEW_CHECKLIST_SPEC](HUMAN_REVIEW_CHECKLIST_SPEC.md) · [REPORT_EXPORT_CENTER_SPEC](REPORT_EXPORT_CENTER_SPEC.md) · [GUI_NAVIGATION_MODEL](GUI_NAVIGATION_MODEL.md)
