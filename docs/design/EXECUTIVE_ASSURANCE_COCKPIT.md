# ManifestIQ — Executive Assurance Cockpit

**Status:** Product experience architecture and executive decision UX. Design specification only — not implementation.
**Audience:** CISO, CTO, CIO, CFO, DevOps lead, GRC Manager, auditor, senior reviewer; and the engineering team who will later implement it.
**Governed by:** the internal trust doctrine in [`docs/internal/`](../internal/README.md). Every UX rule here inherits from that doctrine; where they appear to conflict, the doctrine wins.

**Product name:** ManifestIQ **Executive Assurance Cockpit**. The landing surface is the **Executive Decision Room**. "Cockpit" is retained deliberately: an instrument panel presents state and limits; it does not fly the aircraft. The reviewer decides.

---

## 1. Product Experience Thesis

ManifestIQ's GUI is a **decision instrument, not a report viewer**. Its job is to let a senior decision-maker reach a defensible position on a software system in about ten minutes, and to make the *basis* of that position visible at every step.

Three theses govern the whole experience:

1. **The surface presents a decision; it never issues one.** ManifestIQ computes a raw scanner decision and assembles evidence. Approval is a human act performed outside the product. The GUI must make that boundary structural, not a disclaimer.
2. **Confidence is earned pixel by pixel.** No visual element may look more resolved than its evidence. A conclusion with missing evidence must *look* incomplete. This is the interface expression of "preserve truth, not manufacture confidence."
3. **Drill-down is a promise, not a feature.** Every headline is a claim, and every claim is one interaction away from the raw evidence, rule ID, affected file, and integrity hash that support it. A headline that cannot be traced does not appear as a headline; it appears as a limitation.

The experience is calm because it is certain about what it does and does not know — not because it hides risk.

## 2. Executive Meeting Use Case

**Setting.** A release/steering meeting. The candidate system's ManifestIQ report has already been generated locally. The GRC Manager opens the Cockpit on a shared screen. Attendees: CISO, CTO, CFO, DevOps lead, an auditor.

**The ten-minute path.**

- **0:00 — Executive Decision Room.** One decision card. The visible decision reads `Not Ready — Return for Remediation`. A single-line rationale, the top three blockers, and the next action are on screen. Nobody has scrolled.
- **1:30 — Critical Blockers.** The DevOps lead opens the blockers screen. Two blockers: a SOX-relevant control gap and a supply-chain integrity gap. Each shows business/release impact and whether it is remediable or review-gated.
- **4:00 — Domain Assurance Map.** The CISO scans domains. Security and Data Protection are amber; SOX/Finance is a hard blocker; everything else is either clear-with-evidence or explicitly `Insufficient Evidence`.
- **6:00 — Evidence drill-down.** The auditor clicks the SOX blocker → finding → rule ID → affected files → manifest hash. The auditor confirms the conclusion is backed by evidence and that the run's integrity is verified.
- **8:00 — Risk Acceptance & Limitations.** The CFO asks whether the SOX gap can be time-boxed. The Risk Acceptance screen shows it is *eligible for a bounded exception but not remediated* — and the Limitations screen states plainly what ManifestIQ does **not** claim (no SOX approval, no certification).
- **9:30 — Decision.** The room agrees: return for remediation, one item eligible for a bounded, attributable exception pending named review. ManifestIQ recorded none of this as approval — the humans did.

**What the meeting never had to do:** read a raw table, decode a severity taxonomy, or trust a green checkmark on faith.

## 3. Information Architecture

Five experience layers map onto ten screens. The layers are a **depth axis**: the reader descends from decision to evidence, and the further down they go, the more raw and less interpreted the material becomes.

```
                        EXECUTIVE ASSURANCE COCKPIT

  Layer 1  EXECUTIVE DECISION          [1] Executive Decision Room  ◀ landing
           - decision, score,          [2] Decision Rationale
             confidence, next action

  Layer 2  RISK & BLOCKERS             [3] Critical Blockers & Required Actions
           - what stops progress       [9] Reviewer Assignment / Required Roles

  Layer 3  DOMAIN ASSURANCE            [4] Domain Assurance Map
           - per-domain posture        [5] System Dossier View
                                        [7] Release Readiness

  Layer 4  EVIDENCE DRILLDOWN          (reached from any claim)
           - findings → rule → file    [6] Risk Acceptance & Exceptions
             → source → hash           [8] Evidence Integrity & Manifest

  Layer 5  TRUST & INTEGRITY           [8] Evidence Integrity & Manifest
           - integrity, limits,        [10] Limitations & Non-Claims
             non-claims                (persistent footer strip on every screen)
```

**Navigation model.** Two movements only:
- **Descend** — click any claim to see what supports it (decision → blocker → finding → evidence → hash).
- **Cross-cut** — jump to a domain, a role, or the integrity ledger from a persistent left rail.

**Persistent elements on every screen:**
- **The Integrity Line** (signature element, §6) — a monospace strip showing run manifest hash, scan scope digest, and integrity state.
- **The Non-Claims footer** — a fixed, never-collapsible strip naming what this view does not assert. Limitations are never below the fold.

## 4. Screen-by-Screen Specification

Each screen defines: **purpose · target users · primary question · key visual structure · required data · decision risks · warnings & missing-evidence behavior · forbidden UI behavior.**

Two conventions apply to all screens:
- **Decision-layer separation is structural.** Wherever status appears, the five layers (raw scanner decision · review readiness · risk acceptance coverage · release readiness · human approval) are shown as five distinct, labelled slots. They are never merged into one badge.
- **No unsupported green.** Positive-sentiment color is reserved for verified *facts* (integrity confirmed), never for *judgments* (approved). See §7.

---

### Screen 1 — Executive Decision Room *(landing)*

- **Purpose.** Deliver the decision and its immediate context in a single, unscrolled view.
- **Target users.** All executives; the room's shared screen.
- **Primary question.** *Can this system proceed — and if not, why not and what next?*
- **Key visual structure.** One large **Decision Card**, centered. Top: the visible decision (`Not Ready` / `Return for Remediation` / `Rejected` / `Ready for Review`) with score and confidence rendered as *bounded* indicators. Below: one-line rationale, a three-item blocker strip, one **Next Action**, and the required-reviewer chips. A **Decision-Layer Strip** runs beneath the card showing all five layers with the human-approval slot visibly empty.
- **Required data.** Visible decision; deterministic score with its scale; confidence with its basis; top blockers; next action; required review roles; run integrity state; scan scope summary.
- **Decision risks.** The single biggest risk is the card reading like an approval. Mitigated by: no green for the decision, the always-empty human-approval slot, and the word "Approved" never appearing as a ManifestIQ output.
- **Warnings & missing-evidence behavior.** If confidence is low or evidence is incomplete, the score renders in a **hatched/attenuated** state with an explicit `Insufficient Evidence` tag — the card must *look* unfinished. Missing critical evidence downgrades the visible decision to at most `Not Ready`, never higher.
- **Forbidden UI behavior.** No green "pass" hero. No single merged status pill. No auto-advance to a "looks good" state. No hiding blockers behind a tab. No confetti/success animation, ever.

---

### Screen 2 — Decision Rationale

- **Purpose.** Explain *why* the visible decision was reached, traceably.
- **Target users.** CISO, CTO, auditor, senior reviewer.
- **Primary question.** *What drove this decision, and does it hold up?*
- **Key visual structure.** A **Rationale Panel**: an ordered list of the determining factors, each a sentence plus a severity lane marker and an evidence badge. Each factor is a descend-link to its finding. A sidebar shows what *would* change the decision (the nearest blockers to clearing).
- **Required data.** Ordered decision factors; each factor's contributing findings, rule IDs, severity, and evidence references; the deterministic logic path (which conditions forced the outcome).
- **Decision risks.** Rationale that reads as narrative rather than evidence. Every rationale line must carry a traceable evidence badge; lines without one are rendered as `Assertion — Insufficient Evidence` and cannot be styled as confirmed.
- **Warnings & missing-evidence behavior.** Where a factor depended on evidence that is missing/stale, the factor is marked and the dependency named. Rationale must disclose when the decision is conservative *because* of missing evidence.
- **Forbidden UI behavior.** No prose-only rationale without evidence links. No AI-style "explanation" phrasing implying inference beyond the deterministic rules. No reordering that hides the decisive blocker.

---

### Screen 3 — Critical Blockers & Required Actions

- **Purpose.** Enumerate what stops progress and what must happen for each.
- **Target users.** DevOps lead, CTO, GRC Manager.
- **Primary question.** *What is blocking approval, and what is the required action for each?*
- **Key visual structure.** **Severity lanes** (Critical / High / Mandatory Review / Material Gap) as horizontal bands. Each blocker is a card in its lane showing: title, business/release impact, disposition — **Remediable**, **Review-Gated**, or **Exception-Eligible (bounded)** — and a descend-link to evidence. A **Blocker Timeline** shows sequence/dependency between blockers where one gates another.
- **Required data.** Per blocker: severity, domain, business/release impact, disposition, contributing findings and rule IDs, evidence references, required reviewer role.
- **Decision risks.** "Exception-Eligible" being read as "resolved." The disposition chip for exceptions must visually differ from any remediation state and carry the label "bounded evidence — not remediation."
- **Warnings & missing-evidence behavior.** A **Material Gap** (missing evidence that blocks) is a first-class blocker lane, not an absence. Blockers derived from missing evidence say so explicitly.
- **Forbidden UI behavior.** No collapsing critical blockers by default. No merging distinct blockers into a count-only summary that hides them. No disposition that implies remediation was performed when it was not.

---

### Screen 4 — Domain Assurance Map

- **Purpose.** Show posture across all assurance domains at a glance, with drill-down.
- **Target users.** CISO, CTO, Enterprise Architecture, auditor.
- **Primary question.** *Where is the risk concentrated, and what is unknown?*
- **Key visual structure.** A **domain map** (not a table): tiles for Architecture, Security, Data Protection, SOX/Finance, AI/Model Risk, Supply Chain, License, Operations, Delivery, Governance. Each tile shows domain state (Clear-with-Evidence / Caution / Blocker / `Insufficient Evidence`), a small evidence-coverage meter, and blocker count. Tiles are descend-links.
- **Required data.** Per domain: state, contributing findings, evidence coverage ratio, blocker count, integrity state of that domain's evidence.
- **Decision risks.** A domain with no findings read as "safe." A domain with insufficient evidence must render in a distinct **neutral-unknown** treatment, never in the positive-fact treatment. Absence of findings is not rendered as a pass.
- **Warnings & missing-evidence behavior.** `Insufficient Evidence` and `Missing Evidence` are explicit tile states with their own visual language (attenuated, hatched), visibly different from a low-risk verified state.
- **Forbidden UI behavior.** No green tile for "no findings." No numeric-only heatmap that hides the unknown state. No hiding an empty/uncovered domain.

---

### Screen 5 — System Dossier View

- **Purpose.** Present the scanned system's composition and scope — what was actually examined.
- **Target users.** Enterprise Architecture, CTO, auditor.
- **Primary question.** *What was scanned, and what was in and out of scope?*
- **Key visual structure.** A **composition panel**: system identity, components/modules, declared scope, and — critically — **out-of-scope and unscanned regions** shown with equal prominence. A scope digest ties to the manifest.
- **Required data.** System identity; component inventory as observed; in-scope vs out-of-scope; scan coverage; scope digest/hash; timestamps and tool version (provenance).
- **Decision risks.** Implying full coverage when coverage was partial. Coverage is always shown as a ratio against declared scope, and unscanned regions are named.
- **Warnings & missing-evidence behavior.** Partial or interrupted scans are labelled `Partial` at the dossier level and propagate that label upward to the decision. Uncovered components are listed, not omitted.
- **Forbidden UI behavior.** No "100%"-style completeness visual unless coverage is genuinely complete and integrity-verified. No hiding out-of-scope items. No treating unscanned as clean.

---

### Screen 6 — Risk Acceptance & Exceptions

- **Purpose.** Show where bounded exceptions apply, their scope, and their validity — without ever implying remediation or approval.
- **Target users.** GRC Manager, CISO, CFO, auditor.
- **Primary question.** *What has a bounded exception, on what basis, and for how long?*
- **Key visual structure.** An **exception ledger** (card list, not an editable table): each exception shows the underlying raw finding *still fully visible beside it*, scope, validity window, attribution, and state (Valid / Expired / Draft / Revoked / Rejected / Scope-Mismatch). Invalid states are struck and provide no coverage.
- **Required data.** Per exception: linked raw finding (unmodified), scope, validity window, attribution, state, evidence references.
- **Decision risks.** An exception reading as a fix. The raw finding is always co-displayed; the exception never replaces, reduces, hides, or recolors it. The word "Remediated" must not appear on this screen.
- **Warnings & missing-evidence behavior.** Expired/invalid/draft/revoked/rejected/scope-mismatched exceptions render as **no coverage** and are surfaced as limitations upstream. An exception with missing supporting evidence provides no coverage.
- **Forbidden UI behavior.** No editing/creation workflow (out of scope). No reducing the count or severity of the underlying finding. No approval styling. No presenting acceptance as closure.

---

### Screen 7 — Release Readiness

- **Purpose.** Present release-candidate readiness *evidence* — explicitly distinct from release approval.
- **Target users.** CTO, DevOps lead, CFO, release reviewer.
- **Primary question.** *Is the candidate's evidence sufficient to be considered for a release decision?*
- **Key visual structure.** A **readiness assembly**: readiness criteria as a checklist of *evidence states* (met-with-evidence / not-met / unknown), plus outstanding blockers. A prominent, fixed banner: "Release readiness is not release approval." The human-approval slot is shown empty.
- **Required data.** Readiness criteria and their evidence states; outstanding blockers; integrity state; required reviewer roles for release.
- **Decision risks.** The single highest-risk screen for false confidence. "Ready" must never render as "approved" or "safe." Readiness uses the neutral-positive (slate-blue) treatment, never the verified-fact green and never an approval affordance.
- **Warnings & missing-evidence behavior.** Any unmet or unknown criterion caps readiness at `Not Ready`. Missing evidence blocks readiness rather than being averaged away.
- **Forbidden UI behavior.** No "Release Approved" state. No green success screen. No button implying the release is authorized. No collapsing outstanding blockers.

---

### Screen 8 — Evidence Integrity & Manifest

- **Purpose.** Prove the run's evidence is intact, reproducible, and traceable.
- **Target users.** Auditor, CISO, GRC Manager.
- **Primary question.** *Can I trust that this evidence is intact and this run is reproducible?*
- **Key visual structure.** The **Integrity Ledger**: run manifest hash, per-artifact content hashes, provenance (tool version, config, scope, timestamps), and integrity state per artifact (Verified / Missing / Stale / Corrupted). A monospace, evidence-grade layout — this screen deliberately looks like a ledger, not a dashboard.
- **Required data.** Run manifest; per-artifact integrity values; provenance record; raw-to-derived traceability links; integrity verification results.
- **Decision risks.** Presenting integrity as assured when an artifact failed verification. Any Missing/Stale/Corrupted artifact is shown prominently and propagates a limitation upward; it is never summarized away.
- **Warnings & missing-evidence behavior.** Corrupted or missing artifacts fail closed: affected conclusions upstream are downgraded and flagged. Integrity "Verified" is the only place the verified-fact green appears.
- **Forbidden UI behavior.** No overall green "integrity OK" if any artifact failed. No hiding failed artifacts. No approximate/"looks the same" reproduction claim — matching is by integrity value only.

---

### Screen 9 — Reviewer Assignment / Required Review Roles

- **Purpose.** Make explicit who must review before any human approval could occur.
- **Target users.** GRC Manager, CISO, CTO.
- **Primary question.** *Who must act, on what, before this can move?*
- **Key visual structure.** **Reviewer role chips** mapped to the blockers/domains that require them (e.g., SOX reviewer → SOX blocker; AppSec → security findings). A matrix of required-role × outstanding-item, showing what each role must examine. Assignment is *required-review signalling*, not an approval workflow.
- **Required data.** Required review roles per blocker/domain; the items each role must review; current review-readiness state per item.
- **Decision risks.** Implying that assignment equals sign-off. Chips show "review required," never "reviewed/approved." No state on this screen records or infers approval.
- **Warnings & missing-evidence behavior.** Items needing review due to missing/ambiguous evidence are marked `Mandatory Review` and cannot be cleared by the interface.
- **Forbidden UI behavior.** No approval buttons, no sign-off capture, no attribution of a human decision (approval workflows are out of scope). No implying review is complete.

---

### Screen 10 — Limitations & Non-Claims

- **Purpose.** State plainly what ManifestIQ does not claim and what it could not establish.
- **Target users.** Everyone; especially auditor, Legal/Privacy, CFO.
- **Primary question.** *What is ManifestIQ explicitly not asserting here?*
- **Key visual structure.** Two columns: **Limitations** (what this run could not establish — missing/stale/ambiguous evidence, out-of-scope areas) and **Non-Claims** (the standing denials: no certification, no compliance signoff, no SOX/privacy/legal approval, no penetration-testing completion, no production or release approval, no safety claim). A condensed version of this is the persistent footer strip on every screen.
- **Required data.** Run-specific limitations derived from evidence gaps; the standing non-claims list from [`TRUST_BOUNDARY_AND_NON_CLAIMS`](../internal/TRUST_BOUNDARY_AND_NON_CLAIMS.md).
- **Decision risks.** Limitations being ignored because they are buried. They are never collapsible and never below the fold; a condensed strip is always visible.
- **Warnings & missing-evidence behavior.** This screen *is* the missing-evidence surface of record: every material gap elsewhere has a corresponding limitation entry here.
- **Forbidden UI behavior.** No collapsing/hiding non-claims. No positive-claim language. No framing a limitation as resolved.

## 5. Decision-First Landing Page Design

The Executive Decision Room is the landing surface. Its layout, top to bottom, on first paint with no scroll:

```
┌───────────────────────────────────────────────────────────────────────────┐
│  ManifestIQ · Executive Assurance Cockpit          [scope: 2,318 files]     │
│  INTEGRITY LINE  manifest ⌗ 9f2a…c1  · provenance vX.Y · integrity VERIFIED │  ← signature strip
├───────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│        VISIBLE DECISION                                                      │
│        ┌─────────────────────────────────────────────────────────────┐     │
│        │   NOT READY — RETURN FOR REMEDIATION                         │     │
│        │   score  62 / 100  (deterministic)   confidence  MODERATE    │     │
│        │   ▓▓▓▓▓▓▓▓▓▓▓░░░░░  ← bounded, attenuated if evidence thin    │     │
│        │                                                              │     │
│        │   Rationale — 2 critical blockers force Not Ready; SOX       │     │
│        │   control gap is unremediated. → see rationale               │     │
│        │                                                              │     │
│        │   TOP BLOCKERS   ▸ SOX control gap (Material)                │     │
│        │                  ▸ Supply-chain integrity gap (Critical)     │     │
│        │                  ▸ Data-protection finding (High)            │     │
│        │                                                              │     │
│        │   NEXT ACTION    Remediate SOX + supply-chain; 1 item        │     │
│        │                  exception-eligible pending named review     │     │
│        │   REVIEW ROLES   [SOX reviewer] [AppSec] [Architecture]      │     │
│        └─────────────────────────────────────────────────────────────┘     │
│                                                                             │
│   DECISION LAYERS  (never merged)                                           │
│   ┌ raw scanner ┐ ┌ review ┐ ┌ risk accept ┐ ┌ release ┐ ┌ human approval ┐ │
│   │  Not Ready  │ │Ready…* │ │ 1 bounded   │ │Not Ready│ │  — not present │ │
│   └─────────────┘ └────────┘ └─────────────┘ └─────────┘ └────────────────┘ │
│      * "Ready for Review" ≠ approval                    (empty by design)    │
├───────────────────────────────────────────────────────────────────────────┤
│  NON-CLAIMS  Not certified · no SOX/privacy/legal approval · not a release  │  ← persistent
│              approval · no safety claim · human approval not inferred        │     footer
└───────────────────────────────────────────────────────────────────────────┘
```

Design rules for the landing page:
- **The five decision layers are always co-visible.** The human-approval slot is rendered as a permanently empty, un-fillable slot labelled "not present — human approval is not inferred." This empty slot is the product's most important pixel.
- **The score is bounded and honest.** It carries its scale and its confidence, and attenuates (hatched) when evidence is thin. It is never a lone number implying precision it lacks.
- **Nothing green in the decision.** The decision, layers, and score use the neutral/signal palette. The only green on the page, if present, is the integrity strip's `VERIFIED` — a fact about evidence, not a judgment about the system.
- **Limitations are on-screen at first paint** via the non-claims footer.

## 6. Visual Language & Component System

**Design world.** The reference is not a SaaS dashboard; it is a **precision instrument crossed with a legal evidence dossier**. The materials of ManifestIQ's own domain — manifests, content hashes, provenance records, chain-of-custody — are the aesthetic. This deliberately avoids the three common AI-design defaults (cream/serif/terracotta; near-black + acid accent; broadsheet hairlines).

**Signature element — the Integrity Line & the Empty Approval Slot.** Two paired signatures:
- The **Integrity Line**: a monospace chain-of-custody strip fixed at the top of every surface, carrying the manifest hash, provenance, and integrity state. It ties every screen to its evidence and makes tampering visible. Monospace is thematically core here (hashes, rule IDs, manifests) — the one place the "data" typeface becomes the star.
- The **Empty Approval Slot**: the fifth decision-layer slot, always visibly empty. The interface's boldest move is a refusal — it shows the last mile and declines to fake it.

**Typography (three roles).**
- **Display** — a restrained, precise industrial/humanist sans (e.g., a grotesque with real character but boardroom composure). Used sparingly for decision headlines only.
- **Body** — a highly legible neutral sans for rationale, labels, and descriptions.
- **Data/utility** — a monospace for hashes, rule IDs, manifests, file paths, scope digests. This is not decorative; it is the evidence typeface and it recurs everywhere raw truth is shown.

**Layout system.** Generous, calm spacing; a single decision focal point per screen; severity encoded by lane position (structure), not by color alone. Progressive disclosure is the core interaction: descend to reveal, never a wall of tables up front. Zero playful ornament.

**Core components.**
- **Decision Card** — the focal object; bounded score, confidence, rationale line, blockers, next action, review roles.
- **Decision-Layer Strip** — five labelled slots; never merged.
- **Severity Lanes** — Critical / High / Mandatory Review / Material Gap bands.
- **Evidence Badge** — attached to every claim; click to descend; a claim without one renders as an assertion/limitation.
- **Domain Tile** — state + coverage meter + blocker count; unknown states are visually distinct.
- **Exception Card** — exception + co-displayed unmodified raw finding.
- **Integrity Ledger Row** — artifact + hash + integrity state.
- **Reviewer Role Chip** — required-review signalling only.
- **Rationale Panel** — ordered, evidence-linked factors.
- **Blocker Timeline** — dependency/sequence between blockers.
- **Non-Claims Footer** — persistent, non-collapsible.

**Motion.** Minimal and functional: descend/reveal transitions and focus states only. No success animation, no celebratory motion — ever. Respect reduced-motion.

**Quality floor.** Responsive to boardroom displays and laptops; visible keyboard focus; sufficient contrast in light and dark; no meaning conveyed by color alone (lane position and labels always carry it too).

## 7. Status / Color Semantics

Color encodes **evidence state and severity**, never sentiment or approval. The governing rule: **there is no "approved green," because ManifestIQ never approves.**

| Token | Meaning | Where it may appear | Never used for |
|---|---|---|---|
| **Ink / Graphite** (neutral surface) | Calm baseline | All surfaces | — |
| **Signal Red** (deep, not neon) | Critical blocker / corrupted integrity | Blockers, integrity failures | Decoration |
| **Amber** | Caution / high risk / stale evidence | Domains, findings, staleness | A pass |
| **Slate-Blue** (neutral-positive) | Review readiness / release readiness | `Ready for Review`, `Release Readiness` | Approval, safety, "done" |
| **Hatched / Attenuated Neutral** | Unknown / missing / insufficient evidence | Unknown states, thin confidence | Hiding gaps |
| **Verified Teal-Green** | **Integrity verified — a fact about evidence** | Integrity Ledger `VERIFIED` only | Decisions, approval, readiness |

Hard semantics:
- **`Ready for Review` uses Slate-Blue, never green, never an approval affordance.** It is readiness, not consent.
- **Risk acceptance never uses a remediation/positive treatment.** It is styled as bounded evidence, always beside the unmodified finding.
- **Release readiness never uses green and never carries an "authorized" affordance.**
- **Green exists only as verified-integrity fact**, isolated to the Integrity Line/Ledger. It says "the evidence is intact," not "the system is good."
- **The five decision layers are visually separated** at every appearance; a single blended status pill is forbidden.

## 8. Evidence Drilldown Model

Every headline is the top of a fixed descent chain. The chain is the same everywhere, so users learn it once:

```
Visible Decision
   └▸ Decision Factor (rationale line)
        └▸ Blocker / Domain item
             └▸ Finding
                  └▸ Rule ID  +  Severity
                       └▸ Evidence Reference
                            └▸ Affected File(s)  +  Source Artifact
                                 └▸ Manifest / Content Hash  (integrity-verified)
```

Rules of the model:
- **Traceability is mandatory.** A node that cannot reach a hash-anchored evidence reference is not shown as a confirmed claim; it is shown as `Assertion — Insufficient Evidence` or a limitation.
- **Raw and derived stay separated.** At every level the derived summary links to, but never overwrites, the raw finding. The raw finding is always recoverable and always shown unmodified in exception contexts.
- **Integrity gates the chain.** If any artifact in a claim's chain is Missing/Stale/Corrupted, the claim is downgraded and flagged, and the failure is surfaced (not summarized away).
- **Deterministic and reproducible.** Every evidence reference resolves to the same content under the same run manifest; reproduction is confirmed by matching integrity values, never by resemblance.
- **Drill-down is read-only.** No editing of findings, evidence, or exceptions in any view.

## 9. How the GUI Supports Sales Without Overclaiming

The Cockpit sells by **demonstrating discipline**, not by showing green. Its commercial argument is credibility.

- **The ten-minute meeting is the demo.** A prospect watching an executive reach a defensible decision in ten minutes — with every claim traceable to a hash — experiences the value directly. That is more persuasive to a CISO/auditor than any success screen.
- **The empty approval slot is a selling point.** To a security-literate buyer, a tool that visibly refuses to fabricate approval is *more* trustworthy, not less. Restraint is the differentiator.
- **Evidence-grade integrity ledger signals seriousness.** Hashes, provenance, and reproducibility on screen communicate that this is an assurance instrument, not a dashboard.
- **Non-claims are a feature, shown proudly.** Stating limitations plainly is what auditors and legal reviewers want to see; it de-risks adoption.
- **No marketing language in the product.** The interface never says "safe," "approved," "compliant," or "certified." Its persuasiveness comes from what it will not say.

The sales narrative is: *progress and control are not opposites — here is repeatable, local, evidence-backed assurance that a boardroom can act on without being misled.*

## 10. How the GUI Prevents False Confidence

False confidence is designed *out* structurally, not warned against:

- **No unsupported green.** Approval-green does not exist in the palette; green is confined to verified-integrity facts.
- **The decision can never render as approval.** No "Approved" output, no green pass hero, and the human-approval slot is permanently empty and labelled.
- **Missing evidence looks missing.** Attenuated/hatched treatments make thin or absent evidence visually incomplete; `Insufficient Evidence` is a first-class state on decision, domains, and readiness.
- **Absence of findings is never a pass.** Uncovered/unknown domains and out-of-scope regions are shown with equal prominence to findings.
- **Layers cannot be conflated.** Raw decision, review readiness, risk acceptance, release readiness, and human approval are always five separate slots.
- **Exceptions cannot masquerade as fixes.** The unmodified raw finding is always co-displayed; invalid exceptions provide no coverage.
- **Readiness cannot masquerade as approval.** `Ready for Review` and release readiness use neutral-positive styling and carry explicit "not approval" statements.
- **Partial cannot masquerade as complete.** Partial/failed/interrupted runs are labelled and cap the decision.
- **Limitations are never hidden.** The non-claims strip is persistent and non-collapsible; limitations are never below the fold.
- **Integrity failures fail closed.** Any Missing/Stale/Corrupted artifact downgrades and flags affected conclusions.

## 11. First Implementation Boundary

The first build is a **read-only, local, deterministic decision surface over an already-generated ManifestIQ report.** Explicit boundary:

**In scope (v1):**
- Local rendering of an existing report/manifest bundle (no scanning inside the GUI).
- Screens 1, 3, 4, 8, 10 (Decision Room, Blockers, Domain Map, Integrity & Manifest, Limitations & Non-Claims) — the minimum that answers "can this proceed, why not, what's missing, what's not claimed."
- The full evidence descent chain (§8) as read-only navigation.
- The Integrity Line and Non-Claims footer as persistent elements.
- Decision-layer separation and status/color semantics (§7).

**Explicitly out of scope (v1):**
- No editing of findings, evidence, or exceptions.
- No approval capture or approval workflow.
- No exception creation/authoring (Screen 6 is read-only display when added).
- No rule builder.
- No cloud, SaaS, accounts, or external services.
- No AI/LLM, telemetry, embeddings, external enrichment, or any external transmission.
- No writing back to the report; the GUI is a viewer over immutable local evidence.

**Data contract assumption.** The GUI consumes a local, integrity-manifested report bundle produced by the existing engine, per [`EVIDENCE_INTEGRITY_STANDARD`](../internal/EVIDENCE_INTEGRITY_STANDARD.md). It verifies integrity on load and fails closed on mismatch.

## 12. Recommended Codex Implementation Phase

A staged plan for later implementation. Each phase is independently reviewable and preserves the constraints above.

- **Phase A — Local read model & integrity gate.** Define and load the local report bundle; verify manifest and content hashes on open; fail closed on Missing/Stale/Corrupted. No UI beyond a load/verify result. *Exit:* a bundle either verifies or is refused, deterministically.
- **Phase B — Executive Decision Room (Screen 1) + persistent frames.** Decision Card, bounded score/confidence, decision-layer strip with empty approval slot, Integrity Line, Non-Claims footer. Status/color semantics (§7) enforced. *Exit:* the ten-minute landing answers "can this proceed / why not / what next," with no green pass and no merged status.
- **Phase C — Descent chain (§8) + Blockers (Screen 3) + Domain Map (Screen 4).** Read-only drill-down from decision → finding → rule → file → hash; severity lanes; domain tiles with unknown-state treatment. *Exit:* every headline traces to a hash; unknown/missing states render distinctly.
- **Phase D — Integrity & Manifest (Screen 8) + Limitations & Non-Claims (Screen 10) full views.** Integrity Ledger; run-specific limitations tied to evidence gaps. *Exit:* an auditor can confirm reproducibility and see every gap as a limitation.
- **Phase E — Rationale (2), Dossier (5), Release Readiness (7), Risk Acceptance (6, read-only), Reviewer Roles (9).** Complete the layer set; enforce readiness≠approval and exception≠remediation semantics. *Exit:* full ten-screen surface, all decision-layer separations intact.
- **Phase F — Accessibility, theming, and boardroom polish.** Contrast in light/dark, keyboard focus, reduced motion, large-display legibility; visual-language consistency pass. *Exit:* meets the quality floor; no meaning by color alone.

Each phase must pass a doctrine check: no unsupported green, layers never merged, limitations never hidden, everything read-only, nothing transmitted. No implementation code is specified here; this is the sequencing contract for that later work.

---

*This document is design architecture only. It introduces no product claims beyond those permitted by the trust doctrine, asserts no certification/compliance/approval/safety, and does not weaken the local-first, deterministic, non-AI, non-cloud, evidence-backed constraints.*
