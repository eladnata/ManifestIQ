# ManifestIQ Design Skill Pack

**Status:** Design standard. Documentation only — not implementation.
**Audience:** Product design, engineering (later implementation), reviewers.
**Governed by:** the internal trust doctrine in [`docs/internal/`](../internal/README.md) and the screen specification in [EXECUTIVE_ASSURANCE_COCKPIT](EXECUTIVE_ASSURANCE_COCKPIT.md). Where this pack and the doctrine appear to conflict, the doctrine wins.
**Companion:** [SCREEN_PURPOSE_MATRIX](SCREEN_PURPOSE_MATRIX.md) — the one-page index of every screen.

---

## 1. North Star

ManifestIQ is **not a dashboard**. It is a **premium enterprise decision instrument**.

- Every screen is a **room**.
- Every room has **one job**.
- Every job has **one dominant question**.

A person entering a room must know, within seconds, what this room is for, what insight it gives, and what it deliberately will not show them. The product's credibility comes from restraint: each room answers its one question with authority and refuses to become a catch-all.

## 2. Core UX Rule

**Reduce cognitive load without hiding risk.**

One dominant question per screen. One dominant visual per screen. Everything else is either supporting evidence for that question or a route to another room. If content does not serve the room's one job, it does not belong in the room — it belongs in a different room, reachable by a deliberate action.

Risk is never reduced to lower cognitive load. Missing evidence, blockers, and limitations are always visible; simplification happens by **routing** detail elsewhere, never by **hiding** it.

## 3. 5-Second Screen Test

Every screen must pass this test before it is considered designed:

> In five seconds, with no scrolling and no interaction, can the primary user answer the room's dominant question — and can they see what the screen is *not* claiming?

If a user needs to read a table, decode a legend, or scroll to answer the dominant question, the screen fails. If the screen could be mistaken for an approval when none exists, the screen fails. A failed 5-second test is a design defect, not a preference.

## 4. Screen Header Contract

Every screen is documented — and must be built — against a fixed eight-part contract. No screen ships without all eight defined.

```text
Screen name          — the room's name
Primary question     — the single dominant question the room answers
Primary user         — who this room is built for first
5-second insight     — what the user knows within 5 seconds, unscrolled
Dominant visual      — the one visual element that carries the answer
Above-the-fold       — what is guaranteed visible on first paint
What must not appear  — content, states, or affordances forbidden here
Product value        — why this room exists; the decision it enables
```

The header contract is the acceptance criteria for the room. A room that cannot state a single primary question is not a room; it is a dashboard, and must be split.

## 5. Global Product Shell

Elements that persist across every room, so the instrument reads as one system:

- **Integrity Line** (top): monospace chain-of-custody strip — run manifest hash, provenance (engine version, config), scan scope, integrity state. Ties every room to its evidence. Present on every screen.
- **Room label** (top): the current room's name and its dominant question, always visible so the user never loses orientation.
- **Non-Claims footer** (bottom): fixed, non-collapsible strip naming what the product does not assert (not certified; no SOX/privacy/legal approval; not a release approval; no safety claim; human approval not inferred). Limitations are never below the fold.
- **Descent affordance**: any claim is one interaction from its evidence (finding → rule → file → hash). The route is identical in every room, so it is learned once.

The shell is constant; only the room's dominant content changes. Navigation is two movements only: **descend** (into evidence) and **cross to another room**.

## 6. Full Screen System

Ten rooms. Each is specified against the header contract (§4). Order reflects the executive path from verdict to evidence, plus the two rooms that frame a scan (portfolio, launch).

---

### Room 1 — Board Verdict Room

```text
Screen name          Board Verdict Room
Primary question     Can this system proceed — and if not, why not and what next?
Primary user         CISO, CTO, CIO, CFO (boardroom, shared screen)
5-second insight     The visible decision, its top blockers, and the single next action —
                     with human approval visibly absent.
Dominant visual      One Decision Card + the five separated decision-layer slots
                     (raw scanner · review readiness · risk acceptance · release readiness
                     · human approval), the fifth permanently empty.
Above-the-fold       Visible decision; bounded score + confidence; one-line rationale;
                     top three blockers; one next action; required reviewer chips;
                     five-layer strip; integrity line; non-claims footer.
What must not appear  No "Approved" output. No green pass hero. No merged status pill.
                     No success animation. No blockers hidden behind a tab.
Product value        Lets a board reach a defensible go/return/reject position in minutes,
                     without being misled into false confidence.
```

### Room 2 — Remediation Path

```text
Screen name          Remediation Path
Primary question     What must happen, in what order, for this to become ready?
Primary user         DevOps lead, engineering owner, GRC Manager
5-second insight     The ordered set of required actions and which blockers gate which.
Dominant visual      Blocker/action sequence (severity lanes + dependency ordering),
                     each item tagged Remediable / Review-Gated / Exception-Eligible.
Above-the-fold       The critical and material items first, with disposition and impact.
What must not appear  No implication that an exception is a fix. No "resolved" state applied
                     to an unremediated item. No approval capture. No editing workflow.
Product value        Converts a verdict into an actionable, prioritized path to readiness.
```

### Room 3 — Decision Rationale

```text
Screen name          Decision Rationale
Primary question     Why was this decision reached, and does it hold up?
Primary user         CISO, CTO, auditor, senior reviewer
5-second insight     The ordered factors that forced the decision, each evidence-linked.
Dominant visual      Rationale panel — ordered decisive factors, each with a severity
                     marker and an evidence badge that descends to the finding.
Above-the-fold       The decisive factors, and what would have to change to move the decision.
What must not appear  No prose rationale without evidence links. No inference-style language
                     implying reasoning beyond the deterministic rules. No reordering that
                     buries the decisive blocker.
Product value        Makes the decision auditable and defensible, not a black box.
```

### Room 4 — Evidence Vault

```text
Screen name          Evidence Vault
Primary question     Can I trust that this evidence is intact and reproducible?
Primary user         Auditor, CISO, GRC Manager
5-second insight     Integrity state of the run — verified vs. missing/stale/corrupted.
Dominant visual      Integrity Ledger — per-artifact content hashes, provenance, and
                     integrity state; a ledger, not a dashboard.
Above-the-fold       Run manifest hash, provenance, and any failed/stale/missing artifact.
What must not appear  No overall green "integrity OK" if any artifact failed. No hiding failed
                     artifacts. No "looks the same" reproduction claim — match by hash only.
Product value        Proves the evidence base is intact and the run is reproducible;
                     the foundation all other rooms rest on.
```

### Room 5 — System Dossier Snapshot

```text
Screen name          System Dossier Snapshot
Primary question     What was scanned, and what was in and out of scope?
Primary user         Enterprise Architecture, CTO, auditor
5-second insight     The system's composition and its coverage vs. declared scope.
Dominant visual      Composition panel — components, in-scope vs out-of-scope, coverage ratio.
Above-the-fold       System identity, coverage ratio, and named unscanned/out-of-scope regions.
What must not appear  No "100%"/complete visual unless coverage is genuinely complete and
                     integrity-verified. No hiding out-of-scope items. No treating
                     unscanned as clean.
Product value        Establishes exactly what the verdict does and does not cover.
```

### Room 6 — Domain Heat Map

```text
Screen name          Domain Heat Map
Primary question     Where is risk concentrated, and what is unknown?
Primary user         CISO, CTO, Enterprise Architecture, auditor
5-second insight     Per-domain posture across all assurance domains at a glance.
Dominant visual      Domain map of tiles (Architecture, Security, Data Protection,
                     SOX/Finance, AI/Model Risk, Supply Chain, License, Operations,
                     Delivery, Governance) with state + evidence-coverage meter.
Above-the-fold       All domains, with unknown/insufficient states visually distinct.
What must not appear  No green tile for "no findings". No numeric-only heatmap that hides
                     the unknown state. No hiding an uncovered domain. Absence of findings
                     is never rendered as a pass.
Product value        Directs attention to concentrated risk and to what was not established.
```

### Room 7 — Finding Detail

```text
Screen name          Finding Detail
Primary question     What is this finding, and what evidence supports it?
Primary user         AppSec, engineering owner, auditor
5-second insight     The finding, its rule ID and severity, and its evidence chain.
Dominant visual      Descent chain — finding → rule ID → evidence reference → affected
                     file(s) → source artifact → content hash.
Above-the-fold       The finding statement, rule ID, severity, and the top evidence reference.
What must not appear  No editing of the finding. No mutation, downgrade, or suppression of the
                     raw finding. No claim not anchored to a hash-verified evidence reference.
Product value        Makes every finding traceable to raw, integrity-verified evidence.
```

### Room 8 — Reviewer Briefing

```text
Screen name          Reviewer Briefing
Primary question     Who must review, on what, before this can move?
Primary user         GRC Manager, CISO, CTO
5-second insight     The required review roles mapped to the items each must examine.
Dominant visual      Role × outstanding-item matrix with reviewer role chips.
Above-the-fold       Required roles and the specific blockers/domains each must review.
What must not appear  No approval buttons or sign-off capture. No implying assignment equals
                     approval. No recording or inferring a human decision.
Product value        Makes required human review explicit and scoped — the necessary
                     precondition for any human approval, which happens outside the product.
```

### Room 9 — Portfolio Command

```text
Screen name          Portfolio Command
Primary question     Across systems, which need attention first?
Primary user         CISO, CIO, CTO, GRC Manager
5-second insight     The relative posture of multiple assessed systems and where risk clusters.
Dominant visual      Portfolio grid/lanes ranking systems by verdict severity and open blockers.
Above-the-fold       The systems most in need of attention, with their visible decision state.
What must not appear  No blended "portfolio health" green score. No single roll-up that hides a
                     failing system. No implied approval of any system. No averaging away a
                     blocker or unknown state.
Product value        Prioritizes attention and resources across a portfolio without laundering
                     individual failures into an aggregate.
```

### Room 10 — Assessment Launch

```text
Screen name          Assessment Launch
Primary question     What will be assessed, locally and deterministically?
Primary user         DevOps lead, engineering owner, GRC Manager
5-second insight     The scope, locality, and determinism of the run about to be prepared.
Dominant visual      Scope-and-guarantees panel — target, declared scope, and the standing
                     guarantees (local-only, deterministic, no transmission).
Above-the-fold       Scope selection and the local/deterministic/no-transmission guarantees.
What must not appear  No cloud/account/upload affordance. No external enrichment option. No
                     telemetry or "share results" affordance. No AI/inference toggle.
Product value        Frames a run so users know exactly what is examined and that nothing
                     leaves the local environment — trust begins before the scan.
```

## 7. Screen Separation Rules

- **One question per room.** If a room answers two dominant questions, split it into two rooms.
- **No duplicated major content without purpose.** Content may be *referenced* across rooms (a blocker appears in the verdict, the remediation path, and the rationale), but each room presents it for a *different job* (decide vs. sequence vs. justify). Verbatim repetition with no new job is forbidden.
- **No room is a container of convenience.** A room never includes content merely because the content exists. Everything present serves the room's one question or routes elsewhere.
- **Descent is shared; content is not.** The evidence descent chain is identical everywhere; the dominant content is unique to each room.

## 8. Cognitive Load Rules

- **One dominant visual per room.** Secondary elements are visually subordinate.
- **Above-the-fold answers the question.** The dominant question is answerable on first paint, unscrolled.
- **Progressive disclosure by routing, not hiding.** Detail lives one deliberate interaction away; it is never crammed in and never concealed.
- **Risk is never simplified away.** Blockers, missing evidence, and limitations remain visible even as detail is routed elsewhere.
- **No table-first rooms.** A raw table is never the first thing a user sees; tables are a drill-down, not a landing.
- **Quiet by default.** No decoration, no vanity charts, no motion beyond functional reveal/focus transitions.

## 9. Visual Language

The design world is a **precision instrument crossed with a legal evidence dossier** — the materials of ManifestIQ's own domain (manifests, content hashes, provenance, chain-of-custody) are the aesthetic. This deliberately avoids generic SaaS-dashboard and cyber-cliché looks.

- **Signature elements:** the **Integrity Line** (monospace chain-of-custody strip on every room) and the **Empty Approval Slot** (the fifth decision-layer slot, always visibly empty and labelled "human approval is not inferred"). The instrument's boldest move is a refusal.
- **Typography:** three roles — a restrained display face for decision headlines (used sparingly), a legible body face for rationale and labels, and a **monospace data face** for hashes, rule IDs, manifests, and file paths (the evidence typeface; it recurs wherever raw truth appears).
- **Layout:** calm, generous spacing; one focal point per room; severity encoded by lane/position (structure), not by color alone.
- **Motion:** minimal and functional — reveal and focus only. No success or celebratory motion, ever. Respect reduced-motion.
- **Quality floor:** responsive to boardroom displays and laptops; visible keyboard focus; sufficient contrast in light and dark; meaning never conveyed by color alone.

## 10. Status Language Rules

Color and label encode **evidence state and severity**, never sentiment or approval. **There is no "approved green," because ManifestIQ never approves.**

| Token | Meaning | May appear on | Never used for |
|---|---|---|---|
| Ink / Graphite | Calm neutral baseline | All rooms | — |
| Signal Red | Critical blocker / corrupted integrity | Blockers, integrity failures | Decoration |
| Amber | Caution / high risk / stale evidence | Domains, findings, staleness | A pass |
| Slate-Blue (neutral-positive) | Review readiness / release readiness | `Ready for Review`, release readiness | Approval, safety, "done" |
| Hatched / Attenuated | Unknown / missing / insufficient evidence | Unknown states, thin confidence | Hiding gaps |
| Verified Teal-Green | **Integrity verified — a fact about evidence** | Evidence Vault / Integrity Line only | Decisions, approval, readiness |

Hard status rules (from the doctrine):

- **`Ready for Review` must not look like approval.** Slate-blue, never green, never an approval affordance.
- **Risk acceptance must not look like remediation.** Styled as bounded evidence, always beside the unmodified raw finding.
- **Release readiness must not look like release approval.** Neutral styling; explicit "not approval" statement; no "authorized" affordance.
- **Human approval is never inferred.** The human-approval slot is permanently empty and labelled.
- **Green is only an evidence-integrity fact**, confined to the Integrity Line and Evidence Vault. It says "the evidence is intact," never "the system is good."
- **Allowed conservative statuses only** for negative/unknown states: `Missing Evidence`, `Insufficient Evidence`, `Mandatory Review`, `Conditional Review`, `Not Ready`, `Not Approved`, `Unknown`, `Limitation`, `Ready for Review`. Forbidden positive claims (Approved, Certified, Compliant, Safe, Production Ready, SOX/Privacy/Legally Approved, Fully Secure) never appear as claims.

## 11. Design QA Checklist

A room is not "designed" until every item passes:

- [ ] The room states exactly **one** primary question.
- [ ] The **5-second test** passes: the dominant question is answerable unscrolled, and non-claims are visible.
- [ ] The **eight-part header contract** is fully defined.
- [ ] There is **one dominant visual**; secondary content is subordinate.
- [ ] The **Integrity Line** and **Non-Claims footer** are present.
- [ ] The **five decision layers** (wherever status appears) are separate, never merged; the human-approval slot is empty and labelled.
- [ ] **No "approved green"**; green appears only as a verified-integrity fact.
- [ ] **`Ready for Review`, risk acceptance, and release readiness** do not read as approval/remediation/release approval respectively.
- [ ] **Missing/unknown/insufficient** states are visible and visually distinct — absence of findings is not a pass.
- [ ] **No table is the landing**; detail is reached by descent.
- [ ] **No duplicated major content** without a distinct job.
- [ ] **No approval capture, editing, rule builder, cloud, telemetry, AI, or external transmission** affordance anywhere.

## 12. Implementation Boundary

This pack is **design standard documentation only**. It does not implement UI, add HTML, or change any mockup.

- **In scope of this document:** the reusable screen standard — rooms, header contract, separation/cognitive-load/visual/status rules, and QA checklist — to guide later implementation.
- **Out of scope (and unchanged):** application architecture, backend logic, frontend framework choices, any editing/approval/rule-builder workflow, and any cloud/AI/telemetry/external-transmission capability. The reference build remains a local, read-only, deterministic viewer over an already-generated, integrity-manifested report, per [EXECUTIVE_ASSURANCE_COCKPIT §11](EXECUTIVE_ASSURANCE_COCKPIT.md).
- **Existing artifacts are authoritative and unmodified:** the spec in [EXECUTIVE_ASSURANCE_COCKPIT](EXECUTIVE_ASSURANCE_COCKPIT.md) and the mockup at [`mockups/executive-decision-room.html`](mockups/executive-decision-room.html) are not changed by this pack.

---

*This document is design standard only. It introduces no product claims beyond those permitted by the trust doctrine, asserts no certification/compliance/approval/safety, and does not weaken the local-first, deterministic, non-AI, non-cloud, evidence-backed constraints.*
