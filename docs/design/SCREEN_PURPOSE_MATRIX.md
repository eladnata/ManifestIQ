# ManifestIQ Screen Purpose Matrix

**Status:** Design standard — one-page screen index. Documentation only.
**Companion:** [MANIFESTIQ_DESIGN_SKILL_PACK](MANIFESTIQ_DESIGN_SKILL_PACK.md) (full standard) · governed by [`docs/internal/`](../internal/README.md).

One row per room. Each room has one job and one dominant question. If a proposed screen does not fit one row cleanly, it is a dashboard and must be split.

---

| Screen | Primary question | Primary user | 5-second insight | Dominant visual | Next action | Must not show |
|---|---|---|---|---|---|---|
| **Board Verdict Room** | Can this system proceed — if not, why not and what next? | CISO, CTO, CIO, CFO | The visible decision, top blockers, one next action; human approval visibly absent | Decision Card + five separated decision-layer slots (5th empty) | Open Remediation Path or descend to a blocker | "Approved" output · green pass hero · merged status pill · success animation |
| **Remediation Path** | What must happen, in what order, to become ready? | DevOps lead, engineering owner, GRC Manager | Ordered required actions and which blockers gate which | Blocker/action sequence in severity lanes with dependency order | Assign to reviewer / start remediation of top item | Exception shown as a fix · "resolved" on unremediated item · editing · approval capture |
| **Decision Rationale** | Why was this decision reached, and does it hold up? | CISO, CTO, auditor, senior reviewer | The ordered decisive factors, each evidence-linked | Rationale panel of ordered factors with evidence badges | Descend to a decisive finding | Prose without evidence links · inference-style language · burying the decisive blocker |
| **Evidence Vault** | Can I trust the evidence is intact and reproducible? | Auditor, CISO, GRC Manager | Integrity state: verified vs missing/stale/corrupted | Integrity Ledger (per-artifact hashes + provenance) | Investigate a failed/stale artifact | Overall green if any artifact failed · hidden failed artifacts · "looks the same" reproduction |
| **System Dossier Snapshot** | What was scanned, and what was in/out of scope? | Enterprise Architecture, CTO, auditor | System composition and coverage vs declared scope | Composition panel: in-scope vs out-of-scope + coverage ratio | Open Domain Heat Map | "100%"/complete unless truly complete · hidden out-of-scope · unscanned treated as clean |
| **Domain Heat Map** | Where is risk concentrated, and what is unknown? | CISO, CTO, Enterprise Architecture, auditor | Per-domain posture across all domains at a glance | Domain tile map with state + evidence-coverage meters | Enter a domain → Finding Detail | Green tile for "no findings" · numeric-only heatmap hiding unknowns · hidden uncovered domain |
| **Finding Detail** | What is this finding, and what evidence supports it? | AppSec, engineering owner, auditor | The finding, its rule ID and severity, and its evidence chain | Descent chain: finding → rule → evidence → file → hash | Descend to source artifact / return to blocker | Editing the finding · mutating/downgrading/suppressing raw finding · unanchored claim |
| **Reviewer Briefing** | Who must review, on what, before this can move? | GRC Manager, CISO, CTO | Required review roles mapped to items each must examine | Role × outstanding-item matrix with reviewer chips | Route items to the required roles | Approval buttons / sign-off capture · assignment implying approval · recording a human decision |
| **Portfolio Command** | Across systems, which need attention first? | CISO, CIO, CTO, GRC Manager | Relative posture of systems and where risk clusters | Portfolio grid/lanes ranked by verdict severity + open blockers | Open a system's Board Verdict Room | Blended "portfolio health" green · roll-up hiding a failing system · implied approval · averaged-away blockers |
| **Assessment Launch** | What will be assessed, locally and deterministically? | DevOps lead, engineering owner, GRC Manager | Scope, locality, and determinism of the run to be prepared | Scope-and-guarantees panel (local-only · deterministic · no transmission) | Prepare the local run | Cloud/account/upload · external enrichment · telemetry / "share results" · AI/inference toggle |

---

## Reading the matrix

- **Primary question** is the room's one job. Two questions = two rooms.
- **5-second insight** must be answerable unscrolled (the 5-Second Screen Test).
- **Next action** is the deliberate route out of the room; rooms connect by action, not by cramming content together.
- **Must not show** is enforced, not advisory — every entry derives from the trust doctrine: no unsupported green, no approval implication, decision layers never merged, missing evidence always visible, and no cloud/AI/telemetry/external transmission.

## Cross-cutting rules (apply to every row)

- Green may represent **only evidence-integrity facts** (Evidence Vault / Integrity Line) — never a decision, readiness, or approval.
- **Human approval is never inferred**; the human-approval slot is permanently empty and labelled.
- **`Ready for Review` ≠ approval · risk acceptance ≠ remediation · release readiness ≠ release approval.**
- Every room carries the global shell: **Integrity Line** (top) and **Non-Claims footer** (bottom, non-collapsible).

See [MANIFESTIQ_DESIGN_SKILL_PACK](MANIFESTIQ_DESIGN_SKILL_PACK.md) for the full header contract, visual language, status semantics, and QA checklist.
