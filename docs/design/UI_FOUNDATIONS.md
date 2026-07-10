# ManifestIQ UI Foundations

**Status:** Visual foundation standard. Documentation only — not implementation.
**Audience:** Product design, engineering (later implementation), reviewers.
**Governed by:** the internal trust doctrine in [`docs/internal/`](../internal/README.md). Companion documents: [DESIGN_TOKENS](DESIGN_TOKENS.md) (values) and [COMPONENT_RULES](COMPONENT_RULES.md) (anatomy). Screen standard: [MANIFESTIQ_DESIGN_SKILL_PACK](MANIFESTIQ_DESIGN_SKILL_PACK.md). Where any of these conflict with the doctrine, the doctrine wins.

This document defines *philosophy and rules*. Concrete values live in [DESIGN_TOKENS](DESIGN_TOKENS.md); do not hard-code values here that contradict the token file.

---

## 1. Design North Star

ManifestIQ is **not a dashboard**. It is a **luxury enterprise assurance decision instrument**.

The visual system exists to support: low cognitive load, high trust, boardroom readiness, evidence-backed clarity, premium restraint, strong hierarchy, minimal repetition, and — above all — **no false confidence**. Restraint is the aesthetic: the instrument earns trust by what it refuses to show as much as by what it shows.

Two rules frame everything below:

- **One screen has one dominant question.**
- **One component has one meaning.**

## 2. Color Philosophy

Color encodes **evidence state and severity**, never sentiment or approval.

- **Neutral by default.** The instrument is mostly ink-on-paper (or ink-on-graphite in dark). Color is spent deliberately, not decoratively.
- **There is no "approved green."** Green is reserved exclusively for **evidence-integrity facts** ("this evidence is intact") and never for a decision, readiness, or approval.
- **Brand gold is identity, not status.** Gold marks the wordmark and rare premium accents. It is never a status, never a success signal, never applied to data.
- **Severity has a fixed vocabulary:** critical red, caution amber, review slate (neutral-positive), unknown gray (hatched/attenuated), integrity green (facts only).
- **Meaning is never color-only.** Every colored state is also carried by label and/or position (lane), so it survives color-blindness and grayscale.

## 3. Typography Philosophy

Three roles, no external fonts (system stacks only):

- **Display** — decision headlines and hero verdict. Used sparingly, tight tracking, heavier weight.
- **Body** — rationale, labels, descriptions. The workhorse; must be legible at a glance.
- **Data/Mono** — hashes, rule IDs, manifests, file paths, provenance. The **evidence typeface**; it recurs wherever raw truth appears and signals "this is verifiable fact."

Rules:

- **Primary content is never tiny.** Body/primary content uses `text-base` (14px) or larger. Micro sizes (`text-2xs`, `text-xs`) are for secondary labels, eyebrows, and chip text only — never for the primary answer to a screen's question.
- **Hierarchy through size and weight, not color.** Color is for status; hierarchy is for structure.
- **Monospace means evidence.** Do not use the mono face for decoration or ordinary prose.

## 4. Layout and Grid Principles

- **One focal point per screen.** The dominant visual (a Decision Card, a ledger, a domain map) owns the screen; everything else is subordinate.
- **Content max width** keeps a boardroom-legible measure (see `--layout-max`). Reading text respects a comfortable measure (~72ch); wide data (ledgers, matrices) scrolls inside its own container rather than stretching the page.
- **Two-region shell:** persistent frame (top bar / Integrity Line, non-claims footer) + a changing content region. Optional left rail for cross-room navigation.
- **Above-the-fold answers the question.** The dominant question is answerable on first paint, unscrolled.
- **No table-first landing.** Raw tables are a drill-down, not an entry surface.

## 5. Spacing System

- **4px base unit.** All spacing derives from the scale in [DESIGN_TOKENS](DESIGN_TOKENS.md) (`--space-1`…`--space-8`).
- **Generous by default.** Premium restraint means whitespace, not density, is the default; the eye is guided by space before it is guided by lines.
- **Consistent rhythm.** Vertical spacing between sections uses the larger steps (`--space-5`/`--space-6`); intra-component padding uses the smaller steps.
- **No arbitrary values.** If a spacing need is not on the scale, the scale is wrong — do not inline a one-off pixel value.

## 6. Iconography Rules

- **Line icons, monochrome, stroke-based.** Icons inherit text color; they do not carry status color.
- **Icons support, never replace, labels.** Status is never conveyed by icon alone.
- **Three sizes only** (`--icon-sm/md/lg`); align to the text baseline.
- **No illustration, no mascots, no filled/branded pictograms, no emoji** in decision surfaces. The evidence world (locks, ledgers, fingerprints, seals) is the visual metaphor, rendered as restrained line marks.

## 7. Density Modes

Two modes; every surface declares which it uses.

- **Comfortable (default).** Boardroom and executive rooms. Larger row heights, generous padding. Verdict/hero surfaces are **always** Comfortable.
- **Compact.** Analyst/auditor deep surfaces (integrity ledger, reviewer matrix, portfolio rows) where scanning many rows is the job. Compact reduces row height and padding but **never** reduces primary text below `text-base`.

Density changes spacing and row height only. It never changes color semantics, hides risk, or drops non-claims/limitations.

## 8. Row Heights

- **Comfortable row:** `--row-comfortable` (≈44px) — domain posture rows, reviewer cards, portfolio rows in executive view.
- **Compact row:** `--row-compact` (≈36px) — integrity ledger, dense matrices.
- **Touch minimum:** interactive rows keep a ≥44px hit target even in Compact (expand the target, not the visible text).
- Rows use a single hairline divider (`--border`), never heavy separators; zebra striping is avoided in favor of spacing.

## 9. Cards and Surfaces

- **Surface elevation is subtle.** Cards sit on the page with a hairline border and a minimal shadow (`--shadow-1`). No heavy drop shadows, no glassmorphism, no gradients-as-decoration.
- **One card, one job.** A card answers or supports one thing; multi-purpose "everything" cards are forbidden.
- **The Decision Card is the only hero surface** and may use a stronger left-border severity accent. All other cards are quiet.
- **Radius is restrained** (`--radius`, 4px; pills `--radius-pill`). No large playful corner radii.

## 10. Status Language and Visual Semantics

Authoritative status vocabulary (mirrors [MANIFESTIQ_DESIGN_SKILL_PACK §10](MANIFESTIQ_DESIGN_SKILL_PACK.md) and the doctrine):

| State | Token color | Carried also by | Never means |
|---|---|---|---|
| Critical blocker / corrupted integrity | critical red | lane + label | decoration |
| Caution / high risk / stale evidence | caution amber | lane + label | a pass |
| Review readiness / release readiness | review slate | label | approval, safety, done |
| Unknown / missing / insufficient | unknown gray (hatched) | hatch + label | hiding a gap |
| Integrity verified (**fact only**) | integrity green | label ("verified") | a decision or approval |
| Brand accent | brand gold | — | any status |

Hard status rules:

- **No approved green.** Green is an integrity fact, never approval.
- **`Ready for Review` is not approval** — review slate, never green, never an approval affordance.
- **Risk acceptance is bounded evidence, not remediation** — styled distinctly, always beside the unmodified raw finding.
- **Release readiness is not release approval** — neutral styling, explicit "not approval," no "authorized" affordance.
- **Human approval is never inferred** — the human-approval slot is permanently empty and labelled.
- **Allowed conservative statuses only** for negative/unknown: `Missing Evidence`, `Insufficient Evidence`, `Mandatory Review`, `Conditional Review`, `Not Ready`, `Not Approved`, `Unknown`, `Limitation`, `Ready for Review`. Forbidden positive claims (Approved, Certified, Compliant, Safe, Production Ready, SOX/Privacy/Legally Approved, Fully Secure) never appear as claims.

## 11. Button Rules

- **Primary** — one per surface, for the room's single next action. Solid, high-contrast neutral (ink), never green, never labelled as an approval.
- **Secondary** — supporting navigation/descent. Outlined or quiet.
- **Danger** — destructive or escalation actions only; critical-red outline/solid. Rare.
- **No approval buttons.** There is no "Approve," "Sign off," "Certify," or "Release" button anywhere; the product does not capture or infer human approval.
- **Verb-first, honest labels.** A button says exactly what happens ("Open Remediation Path," "Descend to evidence"), and the resulting state uses the same words.
- **One primary action per screen** reinforces one-question-per-screen.

## 12. Motion Principles

- **Functional only.** Reveal/disclosure and focus transitions; nothing else.
- **No celebratory motion, ever.** No confetti, no success pulse, no green flourish.
- **Fast and quiet.** Short durations, gentle easing; motion never delays the answer to the screen's question.
- **Respect `prefers-reduced-motion`** — all non-essential motion is removed when requested.

## 13. Accessibility Principles

- **Contrast:** text and essential UI meet WCAG AA in both light and dark; primary content targets AAA where feasible.
- **Never color-only.** Every status carries a label and/or position in addition to color.
- **Keyboard first:** all interactive elements are reachable and operable by keyboard with a visible focus ring; tab/arrow semantics for tabs and matrices.
- **Legible minimums:** primary content ≥ `text-base` (14px); interactive targets ≥ 44px.
- **Screen-reader semantics:** meaningful roles/labels; the empty human-approval slot is announced as "human approval — not present, not inferred."
- **Motion and density are user-respecting:** reduced-motion honored; density never drops primary text legibility.

## 14. Screen QA Checklist

A screen is not "designed" until every item passes:

- [ ] Exactly **one dominant question**, answerable **unscrolled** (5-second test).
- [ ] **One dominant visual**; secondary content subordinate.
- [ ] **Integrity Line** (top) and **Non-Claims footer** (bottom, non-collapsible) present.
- [ ] **Five decision layers** separate wherever status appears; **human-approval slot empty and labelled**.
- [ ] **No approved green**; green only as verified-integrity fact.
- [ ] **`Ready for Review` / risk acceptance / release readiness** do not read as approval / remediation / release approval.
- [ ] **Missing/unknown/insufficient** states visible and visually distinct; absence of findings is not a pass.
- [ ] **Primary content ≥ 14px**; no tiny text as primary content.
- [ ] **Spacing, color, type, radius, shadow, icon, row-height** values come from [DESIGN_TOKENS](DESIGN_TOKENS.md) — no one-off values.
- [ ] **One primary action**; no approval/sign-off/certify/release button.
- [ ] Meets **contrast, keyboard, focus, reduced-motion** requirements.
- [ ] **No cloud/telemetry/AI/external** affordance anywhere.

---

*Documentation only. Introduces no product claims beyond those permitted by the trust doctrine; asserts no certification/compliance/approval/safety; does not weaken the local-first, deterministic, non-AI, non-cloud, evidence-backed constraints. Existing mockups are unchanged.*
