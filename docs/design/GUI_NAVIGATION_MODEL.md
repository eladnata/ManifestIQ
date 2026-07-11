# ManifestIQ GUI Navigation Model

**Status:** Navigation & wayfinding model, plus implementation phasing. Design specification only — no implementation.
**Governed by:** the Phase 15D design package and internal trust doctrine. Companion: [GUI_PRODUCT_WORKFLOW](GUI_PRODUCT_WORKFLOW.md), [GUI_INFORMATION_ARCHITECTURE](GUI_INFORMATION_ARCHITECTURE.md).

Navigation must feel like a **guided assurance journey** — a private-bank onboarding flow crossed with an aerospace preflight checklist — not a generic SaaS sidebar full of menu items. The user is guided while a result is being produced, and navigates freely among result rooms once one sealed run exists.

---

## 1. Navigation Principles

- **A journey spine, not a menu.** The primary navigation is a **workflow rail** that represents the assurance journey, not an app menu. It shows where you are, what is done, and what is next.
- **Two modes.** *Guided* (pre-result: Launch → Preflight → Scan → Sealed) is linear and cannot be skipped. *Free* (post-result) lets the user move among result rooms, all anchored to one sealed run.
- **One run in context at a time.** The interface always makes clear which sealed run you are looking at (its fingerprint and integrity state), so no room is ever ambiguous about its evidence.
- **Descent is universal.** Every decisive claim descends the same chain to evidence (finding → rule → file → hash); learned once, used everywhere.
- **Return is always obvious.** Every result room has a clear return to the Board Verdict Room (the result home).
- **Calm, few affordances.** No dense menu, no filter bar, no settings sprawl. Wayfinding is quiet.

## 2. Persistent Frame (every screen)

Per [MANIFESTIQ_DESIGN_SKILL_PACK](MANIFESTIQ_DESIGN_SKILL_PACK.md) §5 and [COMPONENT_RULES](COMPONENT_RULES.md) §1–2:

- **Top: Integrity Line** — brand, current room name + its dominant question, the run's **manifest fingerprint** (monospace) and **integrity state**. This is the run-context anchor.
- **Left: Workflow Rail** — the journey spine (see §3).
- **Bottom: Non-Claims footer** — fixed, non-collapsible standing denials.
- **Descent affordance** — any claim is one interaction from its evidence.

## 3. The Workflow Rail

A vertical rail expressing the journey as ordered stations, grouped into three phases. It is a **progress spine**, not a nav list: stations show state (done / current / pending / held / failed-closed) and are only reachable when their evidence exists.

```
  ┌─ RUN CONTEXT ────────────────┐
  │  ⌗ 8e2840…91f5   Verified    │   ← current run fingerprint + integrity (top of rail)
  ├─ 1 · CONFIGURE ──────────────┤
  │   ○ Assessment Launch        │
  │   ○ Preflight Gate           │
  ├─ 2 · ASSESS ─────────────────┤
  │   ◐ Scan Run Progress        │
  │   ○ Evidence Package Sealed  │
  ├─ 3 · REVIEW ─────────────────┤   ← unlocked only once a run is sealed
  │   ● Board Verdict Room       │   (result home)
  │   · Decision Rationale       │
  │   · Domain Heat Map          │
  │   · Evidence Vault           │
  │   · Remediation Path         │
  │   · Human Review Checklist   │
  │   · Report / Export Center   │
  ├──────────────────────────────┤
  │   ↻ Re-run Assessment        │   ← return path (back to Configure)
  └──────────────────────────────┘
```

- **Phase 1 · Configure** and **Phase 2 · Assess** are the *guided* stations — linear, non-skippable.
- **Phase 3 · Review** stations are the *free* result rooms — reachable in any order once evidence is sealed, all anchored to the run in the rail's context header.
- **Finding Detail** and **System Dossier Snapshot** are reached by descent from within Phase 3 rooms rather than as top-level rail stations (they are drilldowns, not journey stops), keeping the rail short and calm.
- **Report / Export Center** is a Phase 3 station and is also reachable via an "export" affordance in every result room.
- **Re-run Assessment** is a distinct return control at the rail's foot, routing back to Configure with the prior run retained for comparison.

## 4. Cross-Room Navigation (Phase 3)

Two movements only, learned once:

- **Descend** — into evidence: Verdict/Rationale/Domain factor → Finding Detail → Evidence Vault (hash). Read-only.
- **Cross** — to a sibling result room via the rail or a room's explicit route (e.g. Verdict → Remediation Path; Domain Heat Map → Finding Detail; Remediation Path → Human Review Checklist).

Every descent has an obvious **return** to where it started, and every result room has a return to the **Board Verdict Room** as the result home.

## 5. Return Paths

| From | Returns to |
|---|---|
| Any drilldown (Finding Detail, artifact detail) | The room it was opened from |
| Any Phase 3 room | Board Verdict Room (result home) |
| Export Center | The room whose export was requested (or Verdict) |
| Re-run Assessment | Assessment Launch (Configure), prior run retained |
| A held Preflight item | Assessment Launch (to fix the hold) |

## 6. Run Context & Multi-Run

- The rail's **Run Context header** always shows the fingerprint + integrity of the sealed run currently in view.
- Switching runs (from Home / Portfolio) reloads the rail's context; result rooms then reflect that run. Runs are never blended.
- A **Re-run** produces a **new** sealed run (its own package); the prior run is retained, unaltered, for deterministic comparison (maps to `validate-trend`). The GUI never mutates a prior run.

## 7. What the Navigation Must Not Be

- Not a generic sidebar of app sections (Dashboard / Reports / Settings / Admin).
- Not a filter-and-table console.
- Not a place to configure rules, capture approval, or manage users.
- Not a set of tabs that hide risk or limitations.
- No settings sprawl; no notification center; no telemetry-driven "recommended" surfaces.

## 8. Implementation Phasing (proposed, after this design phase)

Each phase is independently reviewable, ships one coherent slice of the journey, and passes a doctrine gate (no approved-green, layers never merged, missing evidence visible, read-only, local-only, no transmission). Build order front-loads the guided intake and the trust-critical output stations before the deeper result rooms.

| Phase | Scope | Depends on | Exit criterion |
|---|---|---|---|
| **17A** | Assessment Launch + Preflight Gate | 16B shell | Configure a local Folder/Git/ZIP run with profile/scope; preflight holds fail closed and are visible. |
| **17B** | Scan Run Progress | 17A | The ten-stage progression renders with running/complete/warning/failed-closed states; no fake green; no verdict before sealing. |
| **17C** | Evidence Package Sealed + Evidence Vault | 17B | Integrity manifest + per-artifact states; green only for verified integrity; failures fail closed. |
| **17D** | Report / Export Center + Human Review Checklist | 17C | Local-only exports with embedded non-claims/limitations; checklist prepares review, captures no approval. |
| **17E** | Decision Rationale + Domain Heat Map + Finding Detail | 17C | Full evidence descent (claim → finding → rule → file → hash); unknown/insufficient states distinct. |
| **17F** | Remediation Path + Re-run flow | 17C, 17E | Ordered remediation with dispositions; re-run produces a new sealed run and deterministic comparison; prior run unaltered. |

Sequencing rationale: the Board Verdict Room already exists (16B); 17A–17C establish the *guided intake and the sealed-evidence spine* the whole product hangs on; 17D lands the trust-critical human-facing outputs early (review prep + local export) so the product is defensible before the deeper analytical rooms (17E) and the remediation/re-run loop (17F).

## 9. Related

- [GUI_PRODUCT_WORKFLOW](GUI_PRODUCT_WORKFLOW.md) · [GUI_INFORMATION_ARCHITECTURE](GUI_INFORMATION_ARCHITECTURE.md) · [GUI_ARTIFACT_TO_SCREEN_MAP](GUI_ARTIFACT_TO_SCREEN_MAP.md) · [SCAN_RUN_EXPERIENCE](SCAN_RUN_EXPERIENCE.md) · [HUMAN_REVIEW_CHECKLIST_SPEC](HUMAN_REVIEW_CHECKLIST_SPEC.md) · [REPORT_EXPORT_CENTER_SPEC](REPORT_EXPORT_CENTER_SPEC.md)
