# ManifestIQ GUI Information Architecture

**Status:** Screen inventory & information architecture. Design specification only — no implementation.
**Governed by:** the Phase 15D design package and the internal trust doctrine. Companion: [GUI_PRODUCT_WORKFLOW](GUI_PRODUCT_WORKFLOW.md), [GUI_NAVIGATION_MODEL](GUI_NAVIGATION_MODEL.md).

Every screen is a **room with one job** ([MANIFESTIQ_DESIGN_SKILL_PACK](MANIFESTIQ_DESIGN_SKILL_PACK.md) §1). This document inventories all rooms and stations, reconciling the ten rooms of [SCREEN_PURPOSE_MATRIX](SCREEN_PURPOSE_MATRIX.md) with the operational stations the full workflow requires.

---

## 1. Room / Station Classes

- **Home** — where the user starts (Portfolio / Home).
- **Operational stations** — pre-result, guided, linear: Assessment Launch, Preflight Gate, Scan Run Progress, Evidence Package Sealed.
- **Result rooms** — post-result, freely navigable over one sealed run: Board Verdict Room, Decision Rationale, Domain Heat Map, Finding Detail, Evidence Vault, Remediation Path, Human Review Checklist.
- **Output station** — Report / Export Center.
- **Return station** — Re-run Assessment.

Reconciliation with the ten committed rooms: **Assessment Launch, Board Verdict Room, Decision Rationale, Domain Heat Map, Finding Detail, Evidence Vault, Remediation Path, System Dossier Snapshot, Reviewer Briefing (→ Human Review Checklist), Portfolio Command (→ Home)** are the ten. **Preflight Gate, Scan Run Progress, Evidence Package Sealed, Report / Export Center, Re-run Assessment** are new operational/output/return stations that the ten rooms hang off. No room's single job is diluted.

## 2. Screen Inventory

Each screen defines: **why it exists · what the user does · what the user learns · primary action · secondary actions · drilldown routes · export routes · artifact dependencies · empty/missing-evidence behavior · forbidden behavior.**

---

### Home (Portfolio Command)
- **Why it exists.** A quiet entry point: pick a system / prior run, or start a new assessment.
- **User does.** Selects a prior sealed run or starts a new assessment.
- **User learns.** The visible decision and integrity state of prior runs — nothing aggregated.
- **Primary action.** Start a new assessment.
- **Secondary actions.** Open a prior sealed run.
- **Drilldown routes.** → Board Verdict Room (of a selected run).
- **Export routes.** None (export is per-run, in the Export Center).
- **Artifact dependencies.** Prior `manifest.json` + `decision-packet.json` summaries.
- **Empty/missing behavior.** No prior runs → an inviting "Start a new assessment" empty state, never a fake sample.
- **Forbidden behavior.** No blended health score; no green aggregate; no approval; no table-first wall.

### Assessment Launch
- **Why it exists.** Configure what will be assessed, locally and deterministically.
- **User does.** Chooses source (Folder/Git/ZIP), profile, scope.
- **User learns.** Exactly what will be scanned and the local/deterministic/no-transmission guarantees.
- **Primary action.** Proceed to Preflight.
- **Secondary actions.** Change source type; change profile; adjust scope.
- **Drilldown routes.** → Preflight Gate.
- **Export routes.** None.
- **Artifact dependencies.** None (pre-scan).
- **Empty/missing behavior.** No valid source → cannot proceed; the reason is stated plainly.
- **Forbidden behavior.** No cloud/account/upload; no AI toggle; no external enrichment; no rule builder; no telemetry.

### Preflight Gate
- **Why it exists.** Confirm the assessment can run deterministically and safely before committing.
- **User does.** Reviews preflight checks; resolves holds; starts the run.
- **User learns.** Which prechecks pass and which hold, and why.
- **Primary action.** Start scan run.
- **Secondary actions.** Return to Launch to fix a hold.
- **Drilldown routes.** → Scan Run Progress.
- **Export routes.** None.
- **Artifact dependencies.** `analyzer-capabilities.json`.
- **Empty/missing behavior.** A failed precheck **holds** the run and is shown as a limitation; never silently bypassed.
- **Forbidden behavior.** No "run anyway" that hides a failed precheck; no skipping holds silently.

### Scan Run Progress
- **Why it exists.** Show the scan executing, stage by stage, failing closed on any stage error.
- **User does.** Watches stages; drills into produced evidence; may abort.
- **User learns.** Where the scan is, what each stage produced, and any warning/failed-closed stage.
- **Primary action.** (Passive) proceed on completion to Evidence Package Sealed.
- **Secondary actions.** Drill into a completed stage's evidence; abort (fails closed).
- **Drilldown routes.** → per-stage evidence; → Evidence Package Sealed on completion.
- **Export routes.** None (until sealed).
- **Artifact dependencies.** Intermediate `*-results.json`, `scan-summary.json`, `scoring-results.json`.
- **Empty/missing behavior.** A stage that produces no evidence is shown as warning/failed-closed, not skipped.
- **Forbidden behavior.** No fake all-green progress; no success animation; no verdict before sealing.

### Evidence Package Sealed
- **Why it exists.** Confirm integrity and hand off to the decision.
- **User does.** Confirms the sealed manifest; proceeds to the verdict.
- **User learns.** That evidence is intact and reproducible (or which artifacts failed).
- **Primary action.** Open Board Verdict Room.
- **Secondary actions.** Open Evidence Vault.
- **Drilldown routes.** → Board Verdict Room; → Evidence Vault.
- **Export routes.** → Export Center (now available).
- **Artifact dependencies.** `manifest.json`, `sha256.txt`.
- **Empty/missing behavior.** Any failed/stale/missing artifact is surfaced; no overall "verified" seal in that case.
- **Forbidden behavior.** No green seal if integrity does not hold.

### Board Verdict Room *(implemented — Phase 16B)*
- **Why it exists.** Deliver the board-facing decision in five seconds.
- **User does.** Reads the decision; descends into detail; routes to remediation/review/export.
- **User learns.** Can it proceed, why not, what next, what is not claimed.
- **Primary action.** Open Remediation Path (the one next action).
- **Secondary actions.** Open Rationale / Domains / Evidence Vault / Review Checklist / Export.
- **Drilldown routes.** → Decision Rationale, Domain Heat Map, Evidence Vault, Finding Detail.
- **Export routes.** → Export Center.
- **Artifact dependencies.** `decision-packet.json`, `manifest.json`, `risk-acceptance-review.json`, `release-candidate-summary.json`, `trust-safety-review.json`.
- **Empty/missing behavior.** Missing evidence renders conservative (`Not Ready` / `Missing Evidence`); limitations visible.
- **Forbidden behavior.** No "Approved"; no green pass hero; no merged status pill; no success animation.

### Decision Rationale
- **Why it exists.** Explain, traceably, why the decision was reached.
- **User does.** Reads ordered decisive factors; descends to findings.
- **User learns.** What forced the decision and what would change it.
- **Primary action.** Descend to a decisive finding.
- **Secondary actions.** Return to Verdict.
- **Drilldown routes.** → Finding Detail → Evidence Vault.
- **Export routes.** Contributes to the Executive Decision Report.
- **Artifact dependencies.** `decision-packet.json`, `evidence-graph.json`, `gaps.json`.
- **Empty/missing behavior.** A factor without a traceable badge → `Insufficient Evidence`.
- **Forbidden behavior.** No prose without evidence links; no inference beyond deterministic rules.

### Domain Heat Map
- **Why it exists.** Show where risk concentrates and what is unknown.
- **User does.** Scans domains; enters one.
- **User learns.** Per-domain posture and coverage; unknown states distinct.
- **Primary action.** Enter a domain → Finding Detail.
- **Secondary actions.** Return to Verdict; open System Dossier Snapshot.
- **Drilldown routes.** → Finding Detail.
- **Export routes.** Contributes to Findings Appendix / Audit Evidence Packet.
- **Artifact dependencies.** `enterprise-acceptance-matrix.json`, per-domain `*-results.json`.
- **Empty/missing behavior.** `Insufficient Evidence` tiles rendered distinctly; no green "no findings" tile.
- **Forbidden behavior.** No numeric-only heat hiding state; no hidden uncovered domain.

### System Dossier Snapshot
- **Why it exists.** Establish what was scanned and what was in/out of scope.
- **User does.** Reviews composition and coverage.
- **User learns.** System identity, coverage ratio, unscanned/out-of-scope regions.
- **Primary action.** Open Domain Heat Map.
- **Secondary actions.** Return to Verdict; open Evidence Vault.
- **Drilldown routes.** → Domain Heat Map.
- **Export routes.** → System Dossier export.
- **Artifact dependencies.** `system-dossier.json`, `file-inventory.json`, `source-metadata.json`, `local-sbom.json`.
- **Empty/missing behavior.** Partial coverage labelled `Partial`; unscanned regions named.
- **Forbidden behavior.** No "100%/complete" unless truly complete; no hidden out-of-scope.

### Finding Detail
- **Why it exists.** Present one finding and its full evidence chain.
- **User does.** Inspects the finding; descends to source and hash.
- **User learns.** The finding, rule ID, severity, and its evidence chain.
- **Primary action.** Descend to source artifact / hash (Evidence Vault).
- **Secondary actions.** Return to Domain Heat Map / Rationale.
- **Drilldown routes.** → Evidence Vault.
- **Export routes.** Contributes to Findings Appendix.
- **Artifact dependencies.** `findings.json`, `sast-results.json`, `secrets-results.json`, `rule-evaluation-results.json`, `file-inventory.json`.
- **Empty/missing behavior.** Unanchored claim → `Insufficient Evidence`; raw finding shown verbatim.
- **Forbidden behavior.** No editing; no mutation/downgrade/suppression.

### Evidence Vault
- **Why it exists.** Prove the run's evidence is intact and reproducible.
- **User does.** Inspects per-artifact integrity; traces evidence chains.
- **User learns.** Verified vs missing/stale/corrupted; provenance/fingerprint.
- **Primary action.** Investigate a failed/stale artifact.
- **Secondary actions.** Trace a finding's chain; return to Verdict.
- **Drilldown routes.** ← from any claim; → artifact detail.
- **Export routes.** → Evidence Manifest / Audit Evidence Packet.
- **Artifact dependencies.** `manifest.json`, `sha256.txt`, `evidence-graph.json`, all referenced artifacts.
- **Empty/missing behavior.** Failed/stale/missing shown prominently; no overall green if any failed.
- **Forbidden behavior.** No "looks the same" reproduction; no green migrating to a decision surface.

### Remediation Path
- **Why it exists.** Convert the verdict into an ordered path to readiness.
- **User does.** Reviews required actions; routes items to reviewers; prepares a re-run.
- **User learns.** What must change, in what order, and each item's disposition.
- **Primary action.** Route an item to its reviewer (into Human Review Checklist).
- **Secondary actions.** Open an item's evidence; start Re-run.
- **Drilldown routes.** → Finding Detail / Evidence Vault; → Re-run Assessment.
- **Export routes.** → Remediation Plan.
- **Artifact dependencies.** `decision-packet.json`, `gaps.json`, `risk-acceptance-review.json`.
- **Empty/missing behavior.** A material gap (missing evidence) is a first-class blocker lane.
- **Forbidden behavior.** No exception as a fix; no "resolved" on unremediated items; no editing/approval.

### Human Review Checklist (Reviewer Briefing)
- **Why it exists.** Prepare humans to review — never to sign off.
- **User does.** Prepares the checklist; opens evidence per item; exports.
- **User learns.** Who must review, on what, and what remains unresolved.
- **Primary action.** Prepare / export the review checklist.
- **Secondary actions.** Open evidence per item; open the review packet summary.
- **Drilldown routes.** → Finding Detail / Evidence Vault per item.
- **Export routes.** → Human Review Checklist export / Audit Evidence Packet.
- **Artifact dependencies.** `decision-packet.json`, `system-dossier.json`, `findings.json`, `manifest.json`.
- **Empty/missing behavior.** Unresolved limitations listed explicitly; no item marked reviewed.
- **Forbidden behavior.** No Approve/Sign-off/Certify; no captured decision; no green approval.

### Report / Export Center
- **Why it exists.** Produce local, audience-targeted exports of the sealed run.
- **User does.** Selects an export; generates it locally.
- **User learns.** Which outputs exist and for whom.
- **Primary action.** Generate a selected export to a local path.
- **Secondary actions.** Preview an export's included sections and non-claims.
- **Drilldown routes.** ← from any result room's "export" affordance.
- **Export routes.** All exports (see [REPORT_EXPORT_CENTER_SPEC](REPORT_EXPORT_CENTER_SPEC.md)).
- **Artifact dependencies.** Per export (see [GUI_ARTIFACT_TO_SCREEN_MAP](GUI_ARTIFACT_TO_SCREEN_MAP.md)).
- **Empty/missing behavior.** An export whose sources are incomplete carries an explicit limitations section.
- **Forbidden behavior.** No cloud upload; no transmitting "share"; no approval-bearing document; no forbidden claim.

### Re-run Assessment
- **Why it exists.** Re-assess after remediation and compare deterministically.
- **User does.** Starts a new run; compares to the prior sealed run.
- **User learns.** Whether the decision changed and how the runs compare.
- **Primary action.** Start a new assessment (→ Assessment Launch).
- **Secondary actions.** Open the prior run for comparison.
- **Drilldown routes.** → Assessment Launch; → comparison (maps to `validate-trend`).
- **Export routes.** New run exports via its own Export Center.
- **Artifact dependencies.** Prior `manifest.json`, `scan-summary.json`, `decision-packet.json`.
- **Empty/missing behavior.** No prior run → comparison unavailable, stated plainly.
- **Forbidden behavior.** No "looks improved" claim; no mutation of the prior run.

## 3. One-Job Guarantee

No screen above answers two dominant questions; where a concern spans rooms (e.g. a blocker appears in Verdict, Remediation, and Rationale), each room presents it for a **different job** (decide / sequence / justify), never duplicated verbatim without purpose ([MANIFESTIQ_DESIGN_SKILL_PACK](MANIFESTIQ_DESIGN_SKILL_PACK.md) §7).

## 4. Related

- [GUI_PRODUCT_WORKFLOW](GUI_PRODUCT_WORKFLOW.md) · [GUI_ARTIFACT_TO_SCREEN_MAP](GUI_ARTIFACT_TO_SCREEN_MAP.md) · [GUI_NAVIGATION_MODEL](GUI_NAVIGATION_MODEL.md)
