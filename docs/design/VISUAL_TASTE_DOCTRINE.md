# ManifestIQ Visual Taste Doctrine

**Status:** Taste brief. Locks visual taste and product feel before further mockups or frontend work. Documentation only.
**Audience:** Product design, design leadership, engineering (later implementation), reviewers.
**Governed by:** the internal trust doctrine in [`docs/internal/`](../internal/README.md). Companion standards: [UI_FOUNDATIONS](UI_FOUNDATIONS.md), [DESIGN_TOKENS](DESIGN_TOKENS.md), [COMPONENT_RULES](COMPONENT_RULES.md), [MANIFESTIQ_DESIGN_SKILL_PACK](MANIFESTIQ_DESIGN_SKILL_PACK.md). Where taste and doctrine conflict, the doctrine wins.

This document sets **taste and feel**. It does not choose a framework, produce a mockup, or add screens. Concrete values live in [DESIGN_TOKENS](DESIGN_TOKENS.md).

---

## 1. Taste Thesis

ManifestIQ should feel **expensive because it removes noise, not because it adds decoration.**

It is a decision instrument for people who carry consequence — the CISO who signs, the CFO who is accountable, the auditor who must defend a position. For that audience, luxury is not ornament; it is **clarity, restraint, and the visible discipline of evidence.** The product earns trust the way a private bank, a legal evidence vault, and an aerospace preflight instrument earn it: by being calm, precise, and honest about what is and is not known.

The taste is quiet on purpose. A screen that shouts is a screen that is unsure of itself. ManifestIQ is never unsure of what it knows — and never pretends to know what it does not. **It preserves truth; it does not manufacture confidence.**

## 2. Positive Taste References

References for *feel*, not layouts to copy.

- **Apple** — restraint, whitespace, confident hierarchy; one idea per view, held with authority.
- **Stripe** — clarity and information craft; complex facts presented so a serious reader trusts them immediately.
- **Linear** — sharpness, typographic precision, spacing discipline, low-friction quality; nothing wasted.
- **Vercel** — premium technical simplicity; a calm structural frame around dense subject matter.
- **Private banking / wealth interfaces** — quiet authority, conservative luxury, understatement as a signal of trust.
- **Legal evidence / deal-room products** — provenance, document seriousness, chain-of-custody, defensible review.
- **Aerospace preflight systems** — checklist discipline, readiness gates, calm treatment of critical status; red means red, and it is rare.
- **Palantir-like enterprise gravity** — only the *seriousness and operational consequence*, never the visual density.

The synthesis: **the composure of Apple, the information craft of Stripe/Linear, the provenance of a deal room, and the readiness discipline of a cockpit.**

## 3. Anti-References

If it resembles any of these, it fails:

ServiceNow · Jira · Power BI · generic GRC dashboard · audit spreadsheet · SOC dashboard · SIEM console · cyber-neon product · admin console · dense compliance portal · generic SaaS analytics dashboard.

The test: **if the screen looks like something a large enterprise already hates using, it is wrong.** These products fail by density, by panel-overload, by treating the user as a data-entry operator rather than a decision-maker. ManifestIQ is the opposite: it does the interpretation work so the human does the deciding work.

## 4. Visual Metaphor

> **Private bank × legal evidence vault × aerospace preflight instrument.**

- From the **private bank**: warm, conservative surfaces; understated authority; the sense that discretion and correctness matter more than flash.
- From the **evidence vault**: everything is provenanced; the monospace hash and the manifest fingerprint are the product's jewelry; nothing material is unsourced.
- From the **preflight instrument**: status is a gate, not a mood; critical states are calm and unambiguous; the checklist is sacred and readiness is never confused with authorization.

The material world of the product — manifests, content hashes, provenance, seals, chain-of-custody — **is** the aesthetic. We do not decorate over it; we present it beautifully.

## 5. Emotional Target

The user should feel:

> This product is serious. This product is calm. This product is expensive. This product is precise. This product does not lie to me. This product helps me decide.

The user must never feel:

> I am reading another report. I am lost in a dashboard. I have too many panels to interpret. This is impressing me with noise. This is hiding risk. This is pretending to approve something.

Every design decision is measured against these two lists. If a choice moves the user toward the second list, it is removed.

## 6. Typography Direction

Typography carries the product's composure. Three roles, no external/webfonts (system stacks; see [DESIGN_TOKENS](DESIGN_TOKENS.md)).

- **Editorial display** — for major decisions only (the verdict headline, a room's dominant statement). Larger, tighter, confident. This is where the product speaks. Used rarely and with air around it.
- **Operational UI text** — clean, neutral, highly legible for rationale, labels, and supporting facts. The workhorse; calm, never cramped.
- **Monospace** — **only** for hashes, rule IDs, evidence IDs, and manifests. It is the evidence typeface and it signals "this is verifiable fact." It never appears as decoration or ordinary prose.

Rules: strong hierarchy through **size and weight**, not color. **Primary content is never tiny** (≥14px). Generous line spacing. One editorial moment per screen — competing headlines destroy composure.

## 7. Color Direction

Color is spent, not scattered. The default screen is warm off-white and graphite; color appears only to carry meaning.

- **Warm off-white** backgrounds — calm, premium, never clinical white, never dark-cyber.
- **Graphite** text — authoritative, easy on the eye.
- **Muted gold** — the brand accent, used sparingly for identity and rare premium emphasis. **Never a status, never success, never applied to data.**
- **Restrained deep red** — blockers only. Rare, calm, unambiguous. Red is precious; overuse destroys its meaning.
- **Amber** — caution and stale evidence.
- **Slate blue** — review and neutral states (`Ready for Review`, release readiness). The strongest "positive" the product shows for a judgment — and it is deliberately not green.
- **Green** — **only** for evidence-integrity facts ("this evidence is intact"). Never a decision, never readiness, never approval. There is no "approved green."

The palette is conservative by intent. Bright green success, cyber gradients, and neon are forbidden. See [DESIGN_TOKENS](DESIGN_TOKENS.md) for exact values.

## 8. Iconography Direction

- **Refined line icons**, monochrome, stroke-based; they inherit text color and never carry status color.
- Icons **support, never replace, labels**; status is never an icon alone.
- The icon vocabulary comes from the evidence world — seals, locks, ledgers, fingerprints, checkmarks-as-integrity — rendered as restrained marks.
- **No illustration, mascots, filled/branded pictograms, or emoji** on decision surfaces. Nothing playful.

## 9. Density Direction

Density is the enemy of trust here. The product feels expensive because of **space**, not because of how much it crams in.

- **Large whitespace and calm compositions** are the default. Air is a feature.
- **Few surfaces per screen.** One dominant visual; a small number of supporting facts; one next action.
- **No dense grids, no card fields, no wall of chips/badges/filters.** Repetition (repeated score panels, repeated badges) reads as cheap and is removed.
- A **Compact density mode exists only for genuinely dense evidence** (the integrity ledger, a reviewer matrix) — and even there, spacing stays disciplined and primary text stays legible.
- If a screen needs many tables and filters to do its job, the screen's job is wrong — split it or route the detail into a drill-down.

## 10. Screen Composition Rules

**Each screen is a room. Each room has one job. Each screen answers one dominant question within 5 seconds.**

Every screen is designed against this contract:

```text
Screen name
Primary question
Primary user
5-second insight
Dominant visual
Three supporting facts
One next action
What must not appear
```

Composition rules:

- **One dominant question, answerable unscrolled.** If it needs a table read or scrolling, it fails.
- **One dominant visual** owns the screen; everything else is subordinate.
- **Exactly three supporting facts** — enough to justify the insight, few enough to stay calm. Not ten; not a panel farm.
- **One next action.** One primary path out of the room. No competing calls to action.
- **Persistent shell:** the Integrity Line (top) and the non-collapsible Non-Claims footer (bottom) are always present; limitations are never below the fold.
- **No screen is a dashboard.** No screen includes content merely because it exists.

## 11. Status Semantics

Authoritative and non-negotiable (mirrors the doctrine and [UI_FOUNDATIONS §10](UI_FOUNDATIONS.md)):

- **No approval is inferred.** The five decision layers (raw scanner · review readiness · risk acceptance · release readiness · human approval) are always separate; the **human-approval slot is empty and labelled unless an accountable human explicitly supplies it.**
- **`Ready for Review` is not approval** — slate blue, never green, never an approval affordance.
- **Release readiness is not release approval** — neutral styling, explicit "not approval," no "authorized" affordance.
- **Risk acceptance is bounded evidence, not remediation** — styled distinctly, always beside the unmodified raw finding.
- **Green is only for evidence integrity.** No "approved green."
- **No visual language that implies certification, compliance approval, safety, or production readiness.** Forbidden positive claims never appear as claims.
- **Allowed conservative statuses only** for negative/unknown states: `Missing Evidence`, `Insufficient Evidence`, `Mandatory Review`, `Conditional Review`, `Not Ready`, `Not Approved`, `Unknown`, `Limitation`, `Ready for Review`.

## 12. What Makes ManifestIQ Visually Different

- **It refuses to fake the last mile.** The permanently empty, labelled human-approval slot is a design signature no dashboard would dare show. Restraint as differentiation.
- **Evidence is the jewelry.** Monospace hashes, the manifest fingerprint, and the integrity seal are treated with the care other products give to hero graphics.
- **Red is rare and calm.** Criticality is communicated with composure, like a cockpit annunciator, not with alarm-red density.
- **One question per room.** The product respects the executive's attention; it interprets so they can decide.
- **Green means "intact," not "good."** A disciplined color language that most tools get wrong.
- **Space signals value.** The product is confident enough to leave room empty.

## 13. What Would Make the Product Feel Cheap

Any of these is a taste failure:

- Bright/celebratory green success states, or any "approved green."
- Cyber gradients, neon, or a black-hacker aesthetic.
- Dense grids, card fields, and panel farms; repeated score panels and repeated badges.
- Too many tables, filters, or chips; a table as the landing surface.
- Tiny text as primary content.
- Decorative charts or visuals with no decision value.
- A screen that answers more than one question, or that includes content "because it exists."
- Anything that resembles ServiceNow / Jira / Power BI / a generic GRC or SIEM console.
- Any visual that implies approval, certification, compliance, safety, or production readiness where none exists.

## 14. First Five Screen Taste Notes

Taste guidance only. Full screen specs live in [MANIFESTIQ_DESIGN_SKILL_PACK](MANIFESTIQ_DESIGN_SKILL_PACK.md); do not expand beyond these five here.

### 1. Board Verdict Room — *Can this system proceed?*
- **Primary user:** CISO, CTO, CIO, CFO (boardroom).
- **5-second insight:** the visible decision, its reason, and the single next step — with human approval visibly absent.
- **Dominant visual:** one editorial Decision Card + the five separated decision-layer slots (5th empty).
- **Three supporting facts:** top blocker, bounded score + confidence, required reviewers.
- **One next action:** open the Remediation Path.
- **Must not appear:** "Approved" output, green pass hero, merged status pill, success motion, hidden blockers.
- **Taste note:** this is the product's most editorial, most confident, most spacious room. It should feel like a private-bank statement of position, not a dashboard.

### 2. Remediation Path — *What must change to move the decision?*
- **Primary user:** DevOps lead, engineering owner, GRC Manager.
- **5-second insight:** the ordered set of required changes and what gates what.
- **Dominant visual:** a calm, sequenced set of remediation steps in severity order.
- **Three supporting facts:** what is remediable, what is review-gated, what is exception-eligible (bounded).
- **One next action:** route an item to its required reviewer.
- **Must not appear:** an exception styled as a fix; "resolved" on an unremediated item; editing/approval capture.
- **Taste note:** a preflight checklist, not a ticket queue. Discipline and order, not Jira density.

### 3. Evidence Vault — *Can we trust the evidence package?*
- **Primary user:** auditor, CISO, GRC Manager.
- **5-second insight:** integrity state of the run — verified vs. missing/stale/corrupted.
- **Dominant visual:** the integrity ledger (per-artifact hashes + provenance); the only room where green appears.
- **Three supporting facts:** manifest fingerprint, provenance (engine/config), any failed/stale artifact.
- **One next action:** investigate a failed or stale artifact.
- **Must not appear:** an overall "verified" seal if anything failed; hidden failed artifacts; "looks the same" reproduction.
- **Taste note:** a legal evidence vault. Monospace, serious, provenanced. Green here is a fact, never a compliment.

### 4. System Dossier Snapshot — *What is this system?*
- **Primary user:** Enterprise Architecture, CTO, auditor.
- **5-second insight:** the system's identity, composition, and coverage vs. declared scope.
- **Dominant visual:** a composition panel with in-scope vs. out-of-scope shown at equal weight.
- **Three supporting facts:** coverage ratio, named unscanned/out-of-scope regions, scope digest.
- **One next action:** open the Domain Heat Map.
- **Must not appear:** a "100%/complete" flourish unless truly complete; hidden out-of-scope; unscanned treated as clean.
- **Taste note:** an executive briefing memo — calm, factual, honest about its own edges.

### 5. Domain Heat Map — *Where is the system weak?*
- **Primary user:** CISO, CTO, Enterprise Architecture, auditor.
- **5-second insight:** per-domain posture across all domains, with the unknown visibly distinct.
- **Dominant visual:** a restrained domain map (not a heat-grid) with state + evidence-coverage.
- **Three supporting facts:** where risk concentrates, which domains are blockers, which are insufficient-evidence.
- **One next action:** enter a domain toward its findings.
- **Must not appear:** a green tile for "no findings"; a numeric-only heatmap that hides the unknown; hidden uncovered domains.
- **Taste note:** a preflight annunciator panel — calm, categorical, honest that "unknown" is not "clear."

## 15. Design Acceptance Checklist

A screen or mockup is not accepted until every item passes:

- [ ] It feels like **private bank × evidence vault × preflight instrument** — not like any anti-reference.
- [ ] It reads **calm, serious, expensive, precise** — noise removed, not decoration added.
- [ ] **One dominant question, answerable in 5 seconds, unscrolled.**
- [ ] **One dominant visual; exactly three supporting facts; one next action.**
- [ ] **Warm off-white + graphite** base; color spent only for meaning.
- [ ] **No approved green; green only for evidence integrity.** No bright/celebratory success states.
- [ ] **Gold is brand only**, never status/success/data.
- [ ] **Red is rare, calm, blockers only.**
- [ ] **Editorial type for the decision; clean UI type for operations; monospace only for evidence identifiers.**
- [ ] **Primary content ≥ 14px**; no tiny text as primary content.
- [ ] **Large whitespace; no dense grids, panel farms, repeated badges/score panels, or table-as-landing.**
- [ ] **Five decision layers separate; human-approval slot empty and labelled** unless an accountable human supplies it.
- [ ] **`Ready for Review` / release readiness / risk acceptance** do not read as approval / release approval / remediation.
- [ ] **No implication of certification, compliance, safety, or production readiness.**
- [ ] **Integrity Line (top) and Non-Claims footer (bottom, non-collapsible) present.**
- [ ] Values reference [DESIGN_TOKENS](DESIGN_TOKENS.md); no one-off values; **no cloud/telemetry/AI/external** affordance.

---

*Documentation only. Taste brief; introduces no product claims beyond those permitted by the trust doctrine, asserts no certification/compliance/approval/safety, and does not weaken the local-first, deterministic, non-AI, non-cloud, evidence-backed constraints. Introduces no new screens beyond the five prioritized. Existing mockups are unchanged.*
