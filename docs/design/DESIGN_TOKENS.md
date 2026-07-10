# ManifestIQ Design Tokens

**Status:** Token reference. Documentation only — not implementation.
**Companion:** [UI_FOUNDATIONS](UI_FOUNDATIONS.md) (philosophy) · [COMPONENT_RULES](COMPONENT_RULES.md) (anatomy) · governed by [`docs/internal/`](../internal/README.md).

Token names, suggested values, and usage rules. Values are aligned to the reference mockup [`mockups/executive-decision-room.html`](mockups/executive-decision-room.html) so future work stays consistent. Suggested values are a starting contract; if a value changes, change it here first, not inline.

> **Green rule (non-negotiable):** `--color-integrity-green` may represent **only evidence-integrity facts**, never system approval, readiness, or a decision.

---

## 1. Color — Background & Surface

| Token | Light | Dark | Usage |
|---|---|---|---|
| `--color-bg` | `#eef1f4` | `#0f151b` | Page background |
| `--color-surface` | `#ffffff` | `#151d25` | Cards, panels |
| `--color-surface-2` | `#f7f9fb` | `#111820` | Insets, nested rows, meters |

## 2. Color — Text

| Token | Light | Dark | Usage |
|---|---|---|---|
| `--color-text` | `#16202b` | `#e7edf3` | Primary text (ink) |
| `--color-text-muted` | `#5b6b7a` | `#9fb0bf` | Secondary text |
| `--color-text-faint` | `#8a98a6` | `#6f8091` | Labels, eyebrows, captions |

Usage: primary content uses `--color-text`. Muted/faint are for secondary and label content only — never for the primary answer to a screen's question.

## 3. Color — Border

| Token | Light | Dark | Usage |
|---|---|---|---|
| `--color-border` | `#d7dee5` | `#25313c` | Hairline dividers, card borders |
| `--color-border-strong` | `#c2ccd6` | `#324150` | Emphasis borders, meter frames |

## 4. Color — Brand & Status

| Token | Light | Dark | Meaning | Never used for |
|---|---|---|---|---|
| `--color-brand-gold` | `#9a7b34` | `#c9a75a` | **Brand identity accent only** (wordmark, rare premium accent) | Any status; success; approval; data |
| `--color-critical-red` | `#9c2027` | `#e07b82` | Critical blocker / corrupted integrity | Decoration |
| `--color-caution-amber` | `#8a5d00` | `#d7a94b` | Caution / high risk / stale evidence | A pass |
| `--color-review-slate` | `#2f5b8a` | `#8fb4dc` | Review readiness / release readiness (neutral-positive) | Approval, safety, "done" |
| `--color-integrity-green` | `#1f7a5a` | `#6fc4a0` | **Evidence-integrity verified — a fact** | Decisions, readiness, approval |
| `--color-unknown-gray` | `#6a7885` | `#8496a4` | Unknown / missing / insufficient (with hatch) | Hiding a gap |

Status background tints (subtle fills behind pills/lanes), light / dark:

| Token | Light | Dark |
|---|---|---|
| `--color-critical-bg` | `#f7e9ea` | `#2a171a` |
| `--color-caution-bg` | `#f7efdd` | `#241d10` |
| `--color-review-bg` | `#e7eff7` | `#14202c` |
| `--color-integrity-bg` | `#e4f1eb` | `#122019` |

**Hatch pattern** (`--pattern-unknown`) for unknown/missing/attenuated states:
`repeating-linear-gradient(45deg, transparent 0 8px, rgba(120,135,150,.12) 8px 9px)` over `--color-surface-2`.

## 5. Spacing Scale (4px base)

| Token | Value | Usage |
|---|---|---|
| `--space-0` | 0 | Reset |
| `--space-1` | 4px | Tight intra-element |
| `--space-2` | 8px | Chip/badge padding |
| `--space-3` | 12px | Card inner padding (compact) |
| `--space-4` | 16px | Card inner padding (default) |
| `--space-5` | 24px | Between grouped elements |
| `--space-6` | 32px | Between sections |
| `--space-7` | 48px | Major section separation |
| `--space-8` | 64px | Page-level rhythm |

Rule: use only scale steps. No inline one-off spacing.

## 6. Typography — Sizes

| Token | Value | Line height | Usage | Primary content? |
|---|---|---|---|---|
| `--text-2xs` | 10px | 1.3 | Micro-labels, empty-slot tag | **Never** |
| `--text-xs` | 11px | 1.4 | Eyebrows, chip labels | **Never** |
| `--text-sm` | 12px | 1.45 | Mono meta, ledger cells (secondary) | No |
| `--text-base` | 14px | 1.5 | **Body / primary content minimum** | Yes |
| `--text-md` | 15px | 1.5 | Emphasis body | Yes |
| `--text-lg` | 18px | 1.4 | Sub-headings | Yes |
| `--text-xl` | 22px | 1.25 | Metrics (score, counts) | Yes |
| `--text-2xl` | 26px | 1.15 | Verdict headline | Yes |
| `--text-3xl` | 32px | 1.1 | Hero (rare) | Yes |

Rule: **primary content is ≥ `--text-base` (14px).** `--text-2xs`/`--text-xs` are secondary labels only.

## 7. Typography — Families & Weights

| Token | Value |
|---|---|
| `--font-display` | `system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif` (tight tracking, weight 700–750) |
| `--font-sans` | `system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif` |
| `--font-mono` | `ui-monospace, "Cascadia Mono", "Cascadia Code", Consolas, "Liberation Mono", Menlo, monospace` |

| Token | Value | Usage |
|---|---|---|
| `--weight-regular` | 400 | Body |
| `--weight-medium` | 600 | Labels, emphasis |
| `--weight-bold` | 700 | Headlines, status words |

Rule: **no external/webfonts.** Mono is the evidence typeface (hashes, rule IDs, manifests, paths) — not for decoration.

## 8. Border Radius

| Token | Value | Usage |
|---|---|---|
| `--radius-sm` | 3px | Tags, small chips |
| `--radius` | 4px | Cards, panels, buttons (default) |
| `--radius-md` | 6px | Larger surfaces |
| `--radius-pill` | 100px | Status pills, role chips, scope chip |

Rule: restrained corners only; no large playful radii.

## 9. Shadows (premium restraint)

| Token | Value | Usage |
|---|---|---|
| `--shadow-0` | `none` | Flush surfaces |
| `--shadow-1` | `0 1px 2px rgba(16,32,43,.06)` | Cards (default subtle) |
| `--shadow-2` | `0 2px 8px rgba(16,32,43,.08)` | Raised/focal (sparse) |

Rule: no heavy drop shadows, glow, or glassmorphism. Elevation is a hint, not a spectacle.

## 10. Icon Sizes

| Token | Value | Usage |
|---|---|---|
| `--icon-sm` | 14px | Inline with `--text-sm`/`base` |
| `--icon-md` | 16px | Default UI icons |
| `--icon-lg` | 20px | Section markers |

Rule: line/stroke icons, monochrome, inherit text color. Icons never carry status color and never replace a label.

## 11. Row Heights

| Token | Value | Usage |
|---|---|---|
| `--row-comfortable` | 44px | Executive rows (domains, reviewers, portfolio) |
| `--row-compact` | 36px | Dense surfaces (integrity ledger, matrices) |
| `--target-min` | 44px | Minimum interactive hit target (all modes) |

Rule: hairline dividers only; no zebra striping; Compact never reduces primary text below `--text-base`.

## 12. Layout Widths

| Token | Value | Usage |
|---|---|---|
| `--layout-max` | 1180px | Content max width |
| `--layout-measure` | 72ch | Max reading measure for prose |
| `--rail-width` | 240px | Optional cross-room navigation rail |
| `--card-focal-min` | 280px | Minimum width of the hero Decision Card column |
| `--gutter` | `--space-5` (24px) | Page side padding / grid gutter |

Rule: wide data (ledgers, matrices) scrolls inside its own `overflow-x:auto` container; the page body never scrolls horizontally.

## 13. Motion Tokens

| Token | Value | Usage |
|---|---|---|
| `--motion-fast` | 120ms | Focus, hover |
| `--motion-base` | 180ms | Disclosure/reveal |
| `--ease` | `cubic-bezier(.2,.6,.2,1)` | Default easing |

Rule: functional motion only; all non-essential motion removed under `prefers-reduced-motion`. No success/celebratory motion.

---

## Token usage rules (summary)

1. **Never inline a raw value** that a token covers — reference the token.
2. **Green = integrity fact only.** `--color-integrity-green`/`-bg` appear only on the Integrity Line and Evidence Vault, never on decisions, readiness, or approval.
3. **Gold = brand only.** `--color-brand-gold` is identity, never status, never success.
4. **Primary content ≥ `--text-base`.** Micro sizes are secondary labels only.
5. **Status is color + label (+ position).** Never color alone.
6. **Spacing/radius/shadow/row-height** come from the scales above; no one-offs.

*Documentation only. No implementation, no framework choice, no external dependency, no change to existing mockups.*
