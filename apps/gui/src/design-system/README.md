# ManifestIQ Frontend Design System

**This is not a component library reference. It is a traceability map.** Every token, rule, and component in this directory is a direct implementation of the Phase 15D design package. That package — not this code — is the source of truth. If this code and the doctrine ever disagree, the doctrine wins; fix the code.

Governing documents, in the order they were applied:

1. [`docs/design/VISUAL_TASTE_DOCTRINE.md`](../../../../docs/design/VISUAL_TASTE_DOCTRINE.md) — taste and feel
2. [`docs/design/UI_FOUNDATIONS.md`](../../../../docs/design/UI_FOUNDATIONS.md) — visual rules and philosophy
3. [`docs/design/DESIGN_TOKENS.md`](../../../../docs/design/DESIGN_TOKENS.md) — token values
4. [`docs/design/COMPONENT_RULES.md`](../../../../docs/design/COMPONENT_RULES.md) — component anatomy
5. [`docs/design/MANIFESTIQ_DESIGN_SKILL_PACK.md`](../../../../docs/design/MANIFESTIQ_DESIGN_SKILL_PACK.md) — screen/room contract
6. [`docs/design/SCREEN_PURPOSE_MATRIX.md`](../../../../docs/design/SCREEN_PURPOSE_MATRIX.md) — screen purpose index

The trust doctrine in [`docs/internal/`](../../../../docs/internal/README.md) outranks all of the above where they conflict.

> **Doctrine corrections applied in the Phase 16B visual rework.** Two committed token values conflicted with the binding taste doctrine and were corrected in `DESIGN_TOKENS.md` (source first), then implemented here:
> - `--color-bg` / `--color-surface` were cool `#eef1f4` / clinical `#ffffff`, contradicting `VISUAL_TASTE_DOCTRINE.md` §7 ("warm off-white … never clinical white"). Corrected to warm bone/ivory.
> - `--font-display` was a sans stack, contradicting §6 ("editorial display"). Corrected to an editorial serif (verdict headline only).

---

## 1. Tokens → `DESIGN_TOKENS.md`

[`tokens.css`](./tokens.css) is a 1:1 transcription of every token table in `DESIGN_TOKENS.md`:

| Token group in code | Source section |
|---|---|
| `--color-bg`, `--color-surface`, `--color-surface-2` | §1 Background & Surface |
| `--color-text`, `--color-text-muted`, `--color-text-faint` | §2 Text |
| `--color-border`, `--color-border-strong` | §3 Border |
| `--color-brand-gold`, `--color-critical-red`, `--color-caution-amber`, `--color-review-slate`, `--color-integrity-green`, `--color-unknown-gray` + `*-bg` variants | §4 Brand & Status |
| `--space-0`…`--space-8` | §5 Spacing Scale |
| `--text-2xs`…`--text-3xl` | §6 Typography Sizes |
| `--font-display`, `--font-sans`, `--font-mono`, `--weight-*` | §7 Typography Families & Weights |
| `--radius-sm`, `--radius`, `--radius-md`, `--radius-pill` | §8 Border Radius |
| `--shadow-0`, `--shadow-1`, `--shadow-2` | §9 Shadows |
| `--icon-sm`, `--icon-md`, `--icon-lg` | §10 Icon Sizes |
| `--row-comfortable`, `--row-compact`, `--target-min` | §11 Row Heights |
| `--layout-max`, `--layout-measure`, `--gutter` | §12 Layout Widths |
| `--motion-fast`, `--motion-base`, `--ease` | §13 Motion Tokens |

**Hard rule enforced in code:** `--color-integrity-green` is referenced in exactly one place outside its own definition — `IntegrityIndicator.tsx` / `.css` and the `status-pill--integrity` tone. It never appears on a decision, layer, or readiness surface. This is the token file's own non-negotiable rule (see its header note), carried through unchanged.

## 2. Visual rules → `UI_FOUNDATIONS.md`

| Code | Foundation section |
|---|---|
| `typography.css` — three type roles, primary content ≥ `--text-base` | §3 Typography Philosophy |
| `layout.css` — one focal point, generous spacing, no table-first landing | §4 Layout and Grid Principles, §5 Spacing System |
| `icons.tsx` — line/stroke, monochrome, evidence-world vocabulary | §6 Iconography Rules |
| `surfaces.css` — subtle elevation, one-card-one-job, restrained radius | §9 Cards and Surfaces |
| `StatusPill`, `DecisionLayerSlot` color mapping | §10 Status Language and Visual Semantics |
| `Button.tsx` primitive rules (one primary, verb-first, never green) | §11 Button Rules |
| `motion.css` — functional only, reduced-motion respected | §12 Motion Principles |
| Focus rings, contrast, ≥14px primary text, ≥44px targets | §13 Accessibility Principles |
| Design QA checklist applied to the Board Verdict Room (see room README below) | §14 Screen QA Checklist |

## 3. Components → `COMPONENT_RULES.md`

Each built component implements exactly one entry from `COMPONENT_RULES.md`. No component is a "MegaPanel" or catch-all.

| Component (code) | `COMPONENT_RULES.md` entry |
|---|---|
| `TopBar.tsx` | §1 Top Bar |
| `NonClaimsFooter.tsx` | §2 Footer Non-Claims Strip |
| `VerdictHero.tsx` | §3 Hero Decision Area |
| `FiveLayerTrustStrip.tsx` + `DecisionLayerSlot.tsx` | §4 Five-Layer Trust Strip |
| `BlockerCard.tsx` | §5 Blocker Card |
| `IntegrityIndicator.tsx` | §8 Evidence Seal, §9 Manifest Fingerprint |
| `RequiredReviewers.tsx` | §12 Reviewer Role Card / Chip |
| `StatusPill.tsx` (primitive) | §15 Status Pill |
| `EvidenceBadge.tsx` (primitive) | §16 Evidence Badge |
| `Button.tsx` (primitive) | §17 Primary Button, §18 Secondary Button, §19 Danger Button |
| `Surface.tsx` (primitive) | §9 Cards and Surfaces (structural primitive underlying the card components) |
| `IconFrame.tsx` (primitive) | supports §8/§9 seal + fingerprint icon presentation |
| `LimitationsPanel.tsx` | Cross-component invariant: "every claim carries an evidence badge or is marked insufficient" |
| `NextActionBar.tsx` | §17 Primary Button, applied as "one next action" per Hero Decision Area contract |

Components **not** built in this phase (Remediation Step, Causal Chain Card, Domain Posture Row, Finding Detail Card, Portfolio Priority Row, Assessment Launch Panel) belong to rooms outside the Board Verdict Room and are intentionally out of scope — see §4 below.

## 4. Screen contract → `MANIFESTIQ_DESIGN_SKILL_PACK.md`

The Board Verdict Room (`rooms/BoardVerdictRoom/`) is built against the **eight-part header contract** from `MANIFESTIQ_DESIGN_SKILL_PACK.md` §4, using the room's own definition in §6 (Room 1 — Board Verdict Room):

- **Primary question** — "Can this system proceed — and if not, why not and what next?" — is the only question this screen answers (§2 Core UX Rule: one dominant question per screen).
- **5-second insight** — visible decision, top blockers, next action, with human approval absent — is everything above the fold; nothing else competes for that first five seconds (§3 5-Second Screen Test).
- **Global Product Shell** (§5) — the persistent Integrity Line and Non-Claims footer are implemented as `TopBar`/`IntegrityIndicator` and `NonClaimsFooter`, present on the one room built.
- **Screen Separation Rules** (§7) — this phase implements exactly one room; no other room's content is duplicated into it.
- **Cognitive Load Rules** (§8) — one dominant visual (`VerdictHero`), detail routed via the blocker-card disclosure and evidence badges, never hidden.

## 5. Screen purpose → `SCREEN_PURPOSE_MATRIX.md`

The matrix row for **Board Verdict Room** is the literal spec for this room's "must not show" list, which is enforced directly in code (see `BoardVerdictRoom.tsx` and its tests):

> Must not show: "Approved" output · green pass hero · merged status pill · success animation

This phase renders none of the other nine matrix rows (Remediation Path, Decision Rationale, Evidence Vault, System Dossier Snapshot, Domain Heat Map, Finding Detail, Reviewer Briefing, Portfolio Command, Assessment Launch) — those remain future phases, each entitled to its own room under this same design system.

## 6. Taste → `VISUAL_TASTE_DOCTRINE.md`

| Code decision | Taste doctrine section |
|---|---|
| Light luxury mode as shipped default (warm off-white `--color-bg`, graphite `--color-text`) | §7 Color Direction |
| `--font-display` reserved for the verdict headline only, used once | §6 Typography Direction |
| No dense grids; `layout.css` `.stack` spacing rhythm; one hero + three supporting facts | §9 Density Direction, §10 Screen Composition Rules |
| No green anywhere except `IntegrityIndicator` | §7 Color Direction, §11 Status Semantics |
| `EmptySlotIcon` + dashed hatch treatment on the human-approval slot | §12 What Makes ManifestIQ Visually Different ("it refuses to fake the last mile") |
| No table, no admin-console chrome, no debug JSON view | §3 Anti-References, §13 What Would Make the Product Feel Cheap |
| `Design Acceptance Checklist` (§15) applied as the manual QA pass before calling this phase done | §15 |

---

## What is intentionally not implemented

Per the Phase 16B scope, this design system ships only what the Board Verdict Room needs. It does **not** yet include: Remediation Step, Causal Chain Card, Domain Posture Row/Tile, Finding Detail Card, Portfolio Priority Row, Assessment Launch Panel, Compact density mode, or a left navigation rail. These are reserved for the rooms that need them, built against this same token/typography/surface/icon foundation.
