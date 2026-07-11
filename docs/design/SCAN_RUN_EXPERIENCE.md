# ManifestIQ Scan Run Experience

**Status:** Scan-progress experience specification. Design specification only — no implementation.
**Governed by:** the Phase 15D design package and internal trust doctrine. Companion: [GUI_PRODUCT_WORKFLOW](GUI_PRODUCT_WORKFLOW.md), [GUI_ARTIFACT_TO_SCREEN_MAP](GUI_ARTIFACT_TO_SCREEN_MAP.md).

The Scan Run Progress station shows the assessment executing as a **preflight-instrument progression** — a disciplined, calm sequence of gates, not a spinner or a log tail. It answers one question: *what is the scan doing right now, and is any stage failing closed?* It must not feel like a build log or a SIEM console.

---

## 1. Experience Principles

- **A checklist that advances, not a spinner.** Stages read like a preflight sequence: each is a gate that is pending, running, complete, warning, or failed-closed.
- **Calm criticality.** A failed stage is stated plainly (restrained red), never with alarm density (taste doctrine §7).
- **Evidence as it lands.** Each completed stage exposes the evidence it produced, drillable immediately — provenance is visible as it forms.
- **Fail closed, visibly.** A warning or failure never advances silently to a favorable state; it caps the run conservatively and is carried into the sealed package as a limitation.
- **No verdict before sealing.** The Board Verdict Room is unreachable until the manifest is sealed.

## 2. Stage State Model

Every stage renders in exactly one state. Color follows [DESIGN_TOKENS](DESIGN_TOKENS.md); green is **never** used for stage success (green is reserved for evidence-integrity facts only — see stage 10).

| State | Meaning | Visual (token) | Advances? |
|---|---|---|---|
| **Pending** | Not yet started | `--color-unknown-gray`, quiet | — |
| **Running** | Executing now | `--color-review-slate`, subtle motion (reveal only) | — |
| **Complete** | Produced its evidence | neutral graphite + a small integrity tick (slate, **not green**) | Yes |
| **Warning** | Produced partial/low-confidence evidence | `--color-caution-amber` + label | Yes, but caps result conservatively |
| **Failed-closed** | Could not produce required evidence | `--color-critical-red` + label | Halts or carries an explicit limitation; never a clean pass |

**Stage completion is not a judgment.** A "Complete" stage means "this stage produced its evidence," never "this is good." The integrity/verified green appears only at manifest sealing (stage 10) and only as a fact.

## 3. Stages

Each stage defines its **running / complete / warning / failed-closed** meaning, the **evidence produced**, and the **drilldown** available.

---

### Stage 1 — Source Intake
- **Running.** Reading the local Folder/Git/ZIP source into a deterministic workspace.
- **Complete.** Source inventoried; file list and metadata captured.
- **Warning.** Some files unreadable/skipped — listed, not hidden.
- **Failed-closed.** Source unreadable or empty → run halts; reason stated.
- **Evidence produced.** `file-inventory.json`, `source-metadata.json`.
- **Drilldown.** Into the file inventory and scope coverage.

### Stage 2 — Repository Structure Analysis
- **Running.** Analyzing project structure, architecture signals, maintainability, config, documentation.
- **Complete.** Structural signals captured.
- **Warning.** Ambiguous/partial structure — flagged.
- **Failed-closed.** Structure analysis cannot complete → limitation recorded.
- **Evidence produced.** `project_structure-results.json`, `architecture_signals-results.json`, `maintainability-results.json`, `config-results.json`, `documentation-results.json`, `hidden_ai_model_detector-results.json`.
- **Drilldown.** Into architecture/maintainability/config signals (later feeds Domain Heat Map).

### Stage 3 — Security Analysis
- **Running.** Static analysis, secrets detection, data-risk analysis.
- **Complete.** Security findings captured.
- **Warning.** Reduced coverage (e.g. unsupported files) — stated.
- **Failed-closed.** Security stage cannot run → conservative cap + limitation.
- **Evidence produced.** `sast-results.json`, `secrets-results.json`, `data_risk-results.json`.
- **Drilldown.** Into individual security findings (later Finding Detail).

### Stage 4 — SOX / Control Mapping
- **Running.** Mapping findings/gaps to SOX/ITGC control context.
- **Complete.** Control context and acceptance matrix populated.
- **Warning.** Insufficient evidence for some controls → `Insufficient Evidence`, not a pass.
- **Failed-closed.** Control mapping unavailable → limitation.
- **Evidence produced.** `sox_detector-results.json`, `control-context.json`, `enterprise-acceptance-matrix.json`.
- **Drilldown.** Into SOX/Finance domain posture.

### Stage 5 — License / SBOM Analysis
- **Running.** Building a local SBOM and analyzing licenses.
- **Complete.** SBOM and license posture captured.
- **Warning.** Dependencies without a lock file / unresolved licenses — flagged.
- **Failed-closed.** SBOM cannot be built → limitation; no license "clear" claim.
- **Evidence produced.** `local-sbom.json`, `licenses-results.json`, `dependencies-results.json`.
- **Drilldown.** Into License and Supply Chain domains; SBOM export later.

### Stage 6 — Operational Readiness Checks
- **Running.** Assessing operational and delivery readiness signals.
- **Complete.** Operational/delivery signals captured.
- **Warning.** Missing runbook/recovery/audit-logging evidence — surfaced as gaps.
- **Failed-closed.** Operational checks cannot run → limitation.
- **Evidence produced.** `operational-results.json`, `delivery_readiness-results.json`.
- **Drilldown.** Into Operations and Delivery domains.

### Stage 7 — Evidence Collection
- **Running.** Assembling findings, gaps, claims, and the evidence graph.
- **Complete.** Evidence graph and consolidated findings/gaps assembled.
- **Warning.** Some claims unsupported → recorded as `Insufficient Evidence`.
- **Failed-closed.** Evidence graph cannot be assembled → run cannot seal cleanly.
- **Evidence produced.** `findings.json`, `gaps.json`, `claims.json`, `evidence-graph.json`, `system-dossier.json`.
- **Drilldown.** Into the evidence graph and dossier.

### Stage 8 — Decision Packet Generation
- **Running.** Deriving the decision, scoring, blocking/conditional reasons, required actions/reviewers.
- **Complete.** Decision packet and scoring produced.
- **Warning.** Low confidence / incomplete provenance → carried as limitation (e.g. "Raw decision provenance incomplete").
- **Failed-closed.** Decision packet cannot be generated → no verdict; conservative state.
- **Evidence produced.** `decision-packet.json`, `decision-packet.md`, `scan-summary.json`, `scoring-results.json`, `confidence-summary.json`.
- **Drilldown.** Into the decision rationale (later Decision Rationale room).

### Stage 9 — Trust Safety Checks
- **Running.** Running deterministic local trust-safety checks (maps to `trust-safety-check`).
- **Complete.** Trust-safety review produced (`Passed` / `Warning` / `Failed`).
- **Warning.** Non-blocking trust-safety warnings recorded.
- **Failed-closed.** Trust-safety failure (e.g. missing raw provenance in the packet) → surfaced as a blocking gap; never hidden.
- **Evidence produced.** `trust-safety-review.json`.
- **Drilldown.** Into trust-safety domains and blocking gaps (surfaced in Board Verdict limitations).

### Stage 10 — Manifest Sealing
- **Running.** Computing per-artifact content hashes and the run manifest.
- **Complete.** Manifest sealed; **integrity verified** — the one place a verified-integrity **green** appears, and only as a fact.
- **Warning.** Some artifacts stale → integrity `Partial`, amber, not green.
- **Failed-closed.** Missing/corrupted artifact → integrity `Missing`/`Corrupted`; no overall green seal.
- **Evidence produced.** `manifest.json`, `sha256.txt`.
- **Drilldown.** Into the Evidence Vault (per-artifact integrity).

## 4. Completion & Handoff

- On successful sealing → a single route to **Board Verdict Room** (and the Evidence Vault).
- On any failed-closed stage → the run still seals what it has, labelled **partial/degraded**, and the Board Verdict Room renders conservatively with the failure as a first-class limitation. There is no favorable shortcut.
- **Abort** at any time fails closed: it produces no favorable result and seals only what was legitimately collected, labelled aborted.

## 5. Forbidden in the Scan Run Experience

- No fake "all green" progress; no celebratory/success animation.
- No verdict, score-as-pass, or approval language before sealing.
- No raw build-log / SIEM-console aesthetic.
- No green for stage success (green = integrity fact only, stage 10).
- No telemetry, no network calls, no external progress reporting.

## 6. Related

- [GUI_PRODUCT_WORKFLOW](GUI_PRODUCT_WORKFLOW.md) · [GUI_ARTIFACT_TO_SCREEN_MAP](GUI_ARTIFACT_TO_SCREEN_MAP.md) · [FAILURE_SAFETY_STANDARD](../internal/FAILURE_SAFETY_STANDARD.md) · [EVIDENCE_INTEGRITY_STANDARD](../internal/EVIDENCE_INTEGRITY_STANDARD.md)
