# Enterprise White-Box Code Assurance Scanner — Design System

**Version:** 0.1  
**Status:** Design baseline  
**Audience:** CISO, CTO, AppSec, Security Engineering, DevSecOps, Code Reviewers, Enterprise Architecture, ITGC  
**Product posture:** Technical, deterministic, evidence-first, conservative, enterprise-grade  
**Language:** English only

---

## 1. Design Intent

The interface is a **Technical Assurance Cockpit**, not a business dashboard.

It must help senior technical reviewers answer, quickly and defensibly:

1. What was scanned?
2. What blocked approval?
3. What evidence supports the finding?
4. Which rules fired?
5. Which analyzers failed or were skipped?
6. Are hidden AI/model components present?
7. Is the project structurally enterprise-grade?
8. Can the system move forward, or must it be blocked?

The design must support deep technical review without visual chaos.

### Design Principles

| Principle | Meaning |
|---|---|
| Evidence-first | Every decision links to a finding, rule, file, line, analyzer, or hash |
| Gate-first | Blocking gates appear before scores, charts, and summaries |
| Technical density | Tables and drawers are allowed; avoid shallow executive-only cards |
| Progressive disclosure | Show the decisive summary first, reveal evidence on click |
| Conservative clarity | Critical/high risks must be visually unmistakable but not theatrical |
| Deterministic trust | Version, ruleset, hash, profile, and analyzer status are always visible |
| No decorative complexity | Charts exist only when they improve technical decision-making |
| No marketing language | Use precise technical language, not sales copy |

---

## 2. Product Personality

### Visual Personality

| Attribute | Direction |
|---|---|
| Serious | Security-grade, governance-grade, not playful |
| Modern | Clean, sharp, intelligent, not legacy enterprise gray-on-gray |
| Technical | Tables, code snippets, hashes, rules, line references |
| Calm | High-risk signals are clear but controlled |
| Dense where useful | Findings and rules screens may be dense, but structured |
| Audit-ready | Evidence integrity and traceability are visible throughout |

### Avoid

- Marketing-style hero art
- Decorative 3D graphics
- Excessive donut charts
- Random illustrations
- Stock human avatars
- Overly soft pastel UI
- Consumer-app styling
- Business-only summaries without evidence
- Ambiguous statuses such as “Looks good”

---

## 3. Information Architecture

### Primary Navigation

Left sidebar, fixed.

| Order | Screen | Purpose |
|---:|---|---|
| 1 | Dashboard | Technical assurance overview and active risk posture |
| 2 | New Scan | Start Git/folder/ZIP scan |
| 3 | Scan Progress | Live analyzer execution and counters |
| 4 | Scan History | Historical scans, comparison, reproducibility |
| 5 | Findings | Primary review workspace |
| 6 | Evidence | Evidence package, manifest, SHA256 verification |
| 7 | Rules | Baseline/custom rules and decision logic |
| 8 | Rulesets | Versioned ruleset governance, activation, rollback |
| 9 | Profiles | Scan profiles and gating thresholds |
| 10 | Baseline Exceptions | Disabled baseline rules and risk acceptances |
| 11 | Settings | Local scanner configuration |

### Recommended Navigation Labels

Use short, technical labels:

```text
Dashboard
New Scan
Progress
History
Findings
Evidence
Rules
Rulesets
Profiles
Exceptions
Settings
```

---

## 4. Layout System

### Base Canvas

Design primarily for desktop technical review.

| Token | Value |
|---|---:|
| Minimum supported width | 1280px |
| Primary design width | 1440px |
| Large desktop width | 1728px |
| Minimum supported height | 800px |
| Base grid | 4px |
| Content grid | 12 columns |
| Main content max width | Fluid, no hard max for data screens |

### Shell Dimensions

| Element | Desktop px | Notes |
|---|---:|---|
| Sidebar width | 264px | Fixed expanded |
| Sidebar collapsed width | 72px | Icons only |
| Top header height | 64px | Fixed |
| Main content padding | 32px | 24px at 1280px |
| Card padding | 24px | 20px for compact cards |
| Table row height | 56px | 48px in dense mode |
| Detail drawer width | 480px | 560px for evidence-heavy views |
| Right insight panel | 360px | Optional screen-specific panel |
| Filter bar height | 64px | Can wrap at smaller widths |
| Footer action bar height | 72px | For forms/settings |

### Page Layout Patterns

#### Pattern A — Overview Grid

Used for Dashboard and Scan Summary.

```text
Sidebar 264
Header 64
Main content 32px padding

[Page Header + Actions]
[Gate / Decision Strip]
[KPI Row]
[Main 2-column grid]
[Metadata / Evidence strip]
```

#### Pattern B — Review Table + Drawer

Used for Findings, Rules, Rulesets, Exceptions.

```text
[Page Header]
[Filter Bar]
[Table: flexible width]
[Right Drawer: selected item details]
```

#### Pattern C — Wizard Form

Used for New Scan.

```text
[Page Header]
[Stepper]
[Main Form Card 2/3 width] [Context Panel 1/3 width]
[Sticky bottom action row]
```

#### Pattern D — Evidence Split View

Used for Evidence Package.

```text
[Status Strip]
[File Tree 280px] [Manifest / Preview / Verification area]
```

---

## 5. Color System

The palette must communicate technical trust, not consumer friendliness.

### Core Palette

| Token | Hex | Usage |
|---|---|---|
| `color-bg` | `#F8FAFC` | App background |
| `color-surface` | `#FFFFFF` | Cards, panels, tables |
| `color-surface-muted` | `#F1F5F9` | Secondary panels |
| `color-sidebar` | `#0B1220` | Sidebar background |
| `color-sidebar-elevated` | `#111827` | Sidebar active/hover depth |
| `color-header` | `#FFFFFF` | Top header |
| `color-border` | `#E2E8F0` | Default borders |
| `color-border-strong` | `#CBD5E1` | Tables and drawers |
| `color-text-primary` | `#0F172A` | Primary text |
| `color-text-secondary` | `#475569` | Secondary text |
| `color-text-muted` | `#64748B` | Helper text |
| `color-text-inverse` | `#F8FAFC` | Sidebar text |
| `color-primary` | `#2563EB` | Primary action, active nav |
| `color-primary-hover` | `#1D4ED8` | Primary hover |
| `color-primary-subtle` | `#EFF6FF` | Selected row/card background |
| `color-focus` | `#3B82F6` | Focus ring |

### Risk / Severity Palette

Severity colors are functional signals. Use them sparingly and consistently.

| Severity | Text/Icon | Subtle BG | Border | Meaning |
|---|---|---|---|---|
| Critical | `#DC2626` | `#FEF2F2` | `#FCA5A5` | Blocks approval |
| High | `#EA580C` | `#FFF7ED` | `#FDBA74` | Requires remediation/review |
| Medium | `#D97706` | `#FFFBEB` | `#FCD34D` | Conditional or tracked risk |
| Low | `#16A34A` | `#F0FDF4` | `#86EFAC` | Low risk / informational improvement |
| Info | `#2563EB` | `#EFF6FF` | `#93C5FD` | Non-risk system information |

### Decision Palette

| Decision | Token | Text | Background | Border |
|---|---|---|---|---|
| Approved | `decision-approved` | `#15803D` | `#F0FDF4` | `#86EFAC` |
| Conditional Approval | `decision-conditional` | `#B45309` | `#FFFBEB` | `#FCD34D` |
| Mandatory Review | `decision-review` | `#7C3AED` | `#F5F3FF` | `#C4B5FD` |
| Remediation Required | `decision-remediation` | `#C2410C` | `#FFF7ED` | `#FDBA74` |
| Rejected / Not Approved | `decision-rejected` | `#B91C1C` | `#FEF2F2` | `#FCA5A5` |
| Pilot Only | `decision-pilot` | `#0369A1` | `#F0F9FF` | `#7DD3FC` |

### Analyzer Status Palette

| Status | Color | Use |
|---|---|---|
| Completed | `#16A34A` | Analyzer finished successfully |
| Running | `#2563EB` | Active analyzer |
| Pending | `#94A3B8` | Not started |
| Failed | `#DC2626` | Analyzer failed; must generate finding |
| Skipped | `#D97706` | Analyzer skipped; requires visible reason |

### Color Rules

1. Never use red/orange/yellow for decoration.
2. Critical red should appear only for actual critical findings, blockers, or failed analyzers.
3. Use blue for navigation, active selection, links, and neutral technical actions.
4. Use green only for verified, passed, resolved, or approved states.
5. Avoid large saturated colored backgrounds; prefer subtle tints with colored text/border.

---

## 6. Typography

### Font Stack

Use open, modern, technical fonts.

```css
--font-sans: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
--font-mono: "JetBrains Mono", "SFMono-Regular", Consolas, "Liberation Mono", monospace;
```

### Type Scale

| Token | Size | Line Height | Weight | Usage |
|---|---:|---:|---:|---|
| `display-sm` | 32px | 40px | 700 | Major page title only |
| `heading-lg` | 24px | 32px | 700 | Screen title |
| `heading-md` | 20px | 28px | 650 | Card title, drawer title |
| `heading-sm` | 16px | 24px | 650 | Section title |
| `body-md` | 14px | 22px | 400 | Default body/table text |
| `body-sm` | 13px | 20px | 400 | Helper text, metadata |
| `caption` | 12px | 16px | 500 | Labels, badges |
| `mono-md` | 13px | 20px | 400 | Code, hashes, file paths |
| `mono-sm` | 12px | 18px | 400 | Dense code snippets/logs |

### Typography Rules

- Page title: 24–32px, never more.
- Table text: 13–14px.
- Hashes and file paths: monospace.
- Rule IDs: monospace or semi-mono badge.
- Do not center-align technical content.
- Use sentence case, not title case everywhere.

### Examples

| Element | Example |
|---|---|
| Page title | `Findings` |
| Card title | `Blocking gates` |
| Rule ID | `SEC-001` |
| File path | `/src/config/settings.py` |
| Hash | `7f3c2d1a5e9b...` |

---

## 7. Spacing, Radius, Elevation

### Spacing Scale

Use a 4px grid.

| Token | px | Usage |
|---|---:|---|
| `space-1` | 4 | Tight icon gaps |
| `space-2` | 8 | Badge/icon text gap |
| `space-3` | 12 | Compact row gaps |
| `space-4` | 16 | Default component spacing |
| `space-5` | 20 | Form field groups |
| `space-6` | 24 | Card padding |
| `space-8` | 32 | Page section spacing |
| `space-10` | 40 | Major page rhythm |
| `space-12` | 48 | Large screen breaks |

### Radius

| Token | px | Usage |
|---|---:|---|
| `radius-sm` | 6 | Inputs, badges |
| `radius-md` | 8 | Buttons, table rows |
| `radius-lg` | 12 | Cards, panels |
| `radius-xl` | 16 | Major containers only |
| `radius-full` | 999 | Pills, avatar |

### Elevation

Use subtle elevation. The product should feel precise, not floaty.

| Token | Value | Usage |
|---|---|---|
| `shadow-none` | none | Tables and flat panels |
| `shadow-sm` | `0 1px 2px rgba(15,23,42,0.06)` | Cards |
| `shadow-md` | `0 8px 24px rgba(15,23,42,0.08)` | Drawers, modals |
| `shadow-focus` | `0 0 0 3px rgba(37,99,235,0.25)` | Focus states |

---

## 8. Iconography

### Icon Set

Recommended: **Lucide** or equivalent 24px outline icon set.

| Property | Value |
|---|---|
| Default size | 18px |
| Large icon size | 24px |
| Stroke width | 1.75px |
| Sidebar icons | 18px |
| Table action icons | 16px |
| Empty state icons | 40px max |

### Icon Mapping

| Concept | Icon Direction |
|---|---|
| Dashboard | Gauge / Layout dashboard |
| New Scan | Plus circle / Scan line |
| Progress | Activity / Loader |
| History | Clock / History |
| Findings | Alert triangle |
| Evidence | File check / Archive |
| Rules | List checks / Scale |
| Rulesets | Git branch / Layers |
| Profiles | Shield / Sliders |
| Exceptions | Shield alert |
| Settings | Settings gear |
| Secrets | Key / Lock keyhole |
| Hidden AI/Model | Brain circuit / Cpu / Box hidden |
| Hash verified | Shield check |
| Failed analyzer | Circle alert |
| Source code | Code 2 |
| Dependency | Package |
| File path | File code |

### Icon Rules

- Icons support labels; icons do not replace labels in core workflows.
- Avoid colorful icon sets.
- Severity icons inherit severity color.
- Default icons use `#64748B` or sidebar inverse text.

---

## 9. Data Density Modes

The product should support technical review without overwhelming new users.

| Mode | Default For | Row Height | Use |
|---|---|---:|---|
| Comfortable | Dashboard, New Scan, Summary | 56px | Balanced readability |
| Analyst | Findings, Rules, Evidence | 48px | Technical data review |
| Dense | Optional user setting | 40px | Power users / large repositories |

Default mode: **Analyst** for technical tables, **Comfortable** for overview screens.

---

## 10. Component Specifications

## 10.1 App Shell

### Sidebar

| Property | Value |
|---|---:|
| Width | 264px |
| Collapsed width | 72px |
| Background | `#0B1220` |
| Active item bg | `#1E3A8A` or `#2563EB` |
| Item height | 44px |
| Item radius | 8px |
| Item horizontal padding | 16px |
| Logo area height | 64px |

Sidebar behavior:

- Active section is persistent.
- Collapsed sidebar keeps tooltips.
- Use initials/avatar only; avoid stock profile photos.
- Sidebar footer may show scanner status: `Local mode`, `Offline`, `Ruleset active`.

### Top Header

| Property | Value |
|---|---:|
| Height | 64px |
| Background | `#FFFFFF` |
| Border bottom | `1px #E2E8F0` |
| Left content | Breadcrumb or current context |
| Right content | Environment, scanner mode, user initials |

Recommended header metadata:

```text
Environment: Local
Mode: Offline-capable
Ruleset: 2026.07.001
```

Do not make the environment look like a cloud SaaS dependency. The product is local-first.

---

## 10.2 Buttons

### Sizes

| Size | Height | Padding | Font |
|---|---:|---:|---:|
| Small | 32px | 12px | 13px |
| Medium | 40px | 16px | 14px |
| Large | 44px | 18px | 14px |

### Variants

| Variant | Use |
|---|---|
| Primary | Run Scan, Export Report, Verify Integrity |
| Secondary | Download Evidence, Compare Scans |
| Ghost | Table actions, drawer actions |
| Danger | Cancel Scan, Disable Baseline Rule |
| Warning | Accept Risk, Disable Rule |

Primary button:

```css
background: #2563EB;
color: #FFFFFF;
border-radius: 8px;
font-weight: 600;
```

Danger button:

```css
background: #DC2626;
color: #FFFFFF;
```

Warning actions must require confirmation when they affect baseline rules.

---

## 10.3 Cards / Panels

| Property | Value |
|---|---:|
| Background | `#FFFFFF` |
| Border | `1px solid #E2E8F0` |
| Radius | 12px |
| Padding | 24px |
| Shadow | `shadow-sm` |

Card types:

| Type | Use |
|---|---|
| Decision card | Final decision, score, gate summary |
| Risk card | Critical/high counters |
| Metadata card | Scanner, ruleset, hash, commit |
| Evidence card | Hash verification, files, manifest |
| Analyzer card | Analyzer status and timings |
| Rule card | Rule details and YAML preview |

---

## 10.4 Tables

Tables are central to the product.

### Table Base

| Property | Value |
|---|---:|
| Header height | 44px |
| Row height comfortable | 56px |
| Row height analyst | 48px |
| Row height dense | 40px |
| Header bg | `#F8FAFC` |
| Row border | `1px solid #E2E8F0` |
| Selected row bg | `#EFF6FF` |
| Hover row bg | `#F8FAFC` |
| Cell padding x | 16px |
| Font size | 13–14px |

### Table Behavior

- Sticky header for long tables.
- Column resize for Findings and Evidence tables.
- Right-side drawer opens on row selection.
- Row selection should not navigate away by default.
- Critical rows may have a thin 3px left border in severity color.
- Use monospace for IDs, file paths, rule IDs, hashes.

### Required Table Features

| Screen | Required Table Capabilities |
|---|---|
| Findings | Filter, sort, severity, category, rule, status, export |
| Rules | Baseline/custom filter, severity, profile, status, locked |
| Evidence | File path, size, SHA256, verification status |
| History | Date range, profile, decision, compare |
| Exceptions | Expiry date, approver, disabled baseline rule, status |

---

## 10.5 Badges / Pills

### Base Badge

| Property | Value |
|---|---:|
| Height | 24px |
| Padding | 8px x-axis |
| Radius | 999px |
| Font size | 12px |
| Font weight | 600 |

Badge examples:

```text
Critical
High
Baseline
Locked
Disabled
Mandatory Review
Verified
Analyzer Failed
```

### Rule Badge Behavior

| Badge | Visual |
|---|---|
| Baseline | Blue-gray subtle bg, lock icon |
| Custom | Blue subtle bg, plus icon |
| Locked | Slate bg, lock icon |
| Disabled baseline | Critical subtle bg, alert icon |
| Active ruleset | Green subtle bg, check icon |
| Draft ruleset | Blue subtle bg |

---

## 10.6 Drawers

Right-side drawers are the primary deep-review pattern.

| Property | Value |
|---|---:|
| Width default | 480px |
| Width evidence-heavy | 560px |
| Background | `#FFFFFF` |
| Border left | `1px solid #E2E8F0` |
| Shadow | `shadow-md` |
| Header height | 72px min |
| Body padding | 24px |

Drawer tabs:

```text
Overview
Evidence
Remediation
Rule
History
```

Drawer rules:

- Keep the user in the table context.
- Show critical metadata at top.
- Evidence snippet appears before remediation for technical users.
- Copy buttons for file paths, hashes, rule IDs.

---

## 10.7 Code / Evidence Snippets

Used for findings, rules, logs, hashes, manifest preview.

| Property | Value |
|---|---:|
| Font | JetBrains Mono / mono stack |
| Font size | 12–13px |
| Line height | 18–20px |
| Background | `#0F172A` for code, or `#F8FAFC` for light snippets |
| Text | `#E5E7EB` dark mode code, `#0F172A` light mode |
| Radius | 8px |
| Padding | 16px |

For sensitive findings:

- Mask secrets by default.
- Show only partial evidence.
- Provide `Reveal` only for authorized role, if UI ever supports auth.
- In local MVP, default to masked evidence.

Example masked secret:

```text
API_KEY = "sk_live_51H8...e9f3"
```

---

## 10.8 Forms

### Form Field Dimensions

| Element | Height | Radius |
|---|---:|---:|
| Input | 40px | 8px |
| Textarea | 96px min | 8px |
| Select | 40px | 8px |
| Checkbox | 16px | 4px |
| Toggle | 36 x 20px | 999px |

### Form Rules

- Label above input.
- Helper text below input.
- Validation text below helper, in severity color.
- Required fields use `Required` text, not only `*`.
- Sensitive fields default masked.
- File path fields use monospace value.

---

## 10.9 Progress / Analyzer Timeline

Used in Scan Progress screen.

### Analyzer Row

| Element | Specs |
|---|---|
| Row height | 64px |
| Status icon | 20px |
| Analyzer title | 14px / 600 |
| Analyzer description | 13px / muted |
| Duration | mono 12px |
| Status pill | 24px |

Analyzer statuses:

```text
Completed
Running
Pending
Failed
Skipped
```

Failed mandatory analyzer behavior:

- Red status.
- Opens drawer with failure evidence.
- Generates finding.
- Appears in final report.

---

## 10.10 Charts

Charts are secondary.

Allowed charts:

| Chart | Use |
|---|---|
| Horizontal bar | Category scores, severity distribution |
| Small trend line | Scan history trend |
| Stacked bar | Findings by category/severity |
| Donut | Only on dashboard, never primary |

Avoid:

- Decorative 3D charts
- Pie charts with many categories
- Animated chart gimmicks
- Large charts that push findings below the fold

---

## 11. Screen Specifications

## 11.1 Dashboard — Technical Assurance Overview

Purpose: Current technical risk posture, not business performance.

### Required Content

1. Active blocking gates count
2. Critical findings count
3. Hidden AI/model risk count
4. Failed analyzers count
5. Recent scans table
6. High-risk systems list
7. Active ruleset and scanner version
8. Baseline rules disabled warning, if any

### Layout

```text
[Header: Technical Assurance Overview] [Start New Scan]
[Blocking Gates] [Critical Findings] [AI/Model Risk] [Failed Analyzers]
[Recent Scans Table] [High-Risk Attention Panel]
[Ruleset / Scanner / Evidence Status Strip]
```

### Improvements over initial mockup

- Reduce decorative risk chart size.
- Add `Blocking gates` before generic score cards.
- Add `Hidden AI/model risk` as first-class KPI.
- Replace user photo avatar with initials.

Reference mockup:

![Dashboard Overview](docs/design-assets/mockups/01-dashboard-overview.png)

---

## 11.2 New Scan

Purpose: Start a controlled deterministic scan.

### Required Inputs

| Field | Required | Notes |
|---|---:|---|
| Source type | Yes | Git, folder, ZIP |
| Repository URL / path | Yes | Monospace input |
| Branch / tag / commit | Conditional | Git only |
| Auth token | Optional | Masked; never logged |
| Profile | Yes | enterprise default for technical use |
| Ruleset version | Yes | Active locked ruleset by default |
| Output folder | Yes | Local path |
| Offline mode | Optional | Clear behavior |
| Include SBOM | Recommended | On by default for enterprise+ |
| Include hidden AI/model scan | Always on | Cannot be disabled in strict profiles |

### Layout

```text
[Page title]
[Stepper: Source > Configure > Review]
[Source cards]
[Configuration form] [Profile + Ruleset summary]
[Run Scan]
```

Reference mockup:

![New Scan](docs/design-assets/mockups/02-new-scan.png)

---

## 11.3 Scan Progress

Purpose: Make analyzer execution transparent.

### Required Content

- Overall progress
- Current analyzer
- Analyzer timeline
- Live counters by severity
- Analyzer duration
- Failed/skipped analyzer visibility
- Live log
- Partial results

### Critical UI Rule

Analyzer failure must never be visually hidden. Failed mandatory analyzer = visible red status + generated finding.

Reference mockup:

![Scan Progress](docs/design-assets/mockups/03-scan-progress.png)

---

## 11.4 Scan Summary

Purpose: CISO/CTO technical decision page.

### Page Hierarchy

1. Final decision
2. Blocking gates
3. Critical findings
4. Hidden AI/model risk
5. Analyzer failures/skips
6. Category scores
7. Required remediation
8. Evidence hash and metadata

### Required Panels

| Panel | Priority |
|---|---:|
| Final decision and score | P0 |
| Blocking gates | P0 |
| Critical/high findings | P0 |
| Hidden AI/model risk | P0 |
| Required before approval | P0 |
| Analyzer status | P0 |
| Category breakdown | P1 |
| Scan metadata | P0 |
| Evidence SHA256 | P0 |

### Decision Banner

Use strong but controlled visual treatment:

| Decision | Banner Style |
|---|---|
| Approved | Green subtle |
| Conditional | Amber subtle |
| Mandatory Review | Purple subtle |
| Not Approved / Rejected | Red subtle with left border |

Reference mockup:

![Scan Summary](docs/design-assets/mockups/04-scan-summary.png)

---

## 11.5 Findings Explorer

Purpose: Main technical review surface.

### Required Columns

| Column | Width | Notes |
|---|---:|---|
| Finding ID | 112px | Monospace |
| Severity | 112px | Badge |
| Category | 144px | Security, AI Model Risk, etc. |
| Rule ID | 112px | Monospace |
| Title | Flexible | Primary content |
| File | 240px | Truncated path, monospace |
| Owner Role | 152px | AppSec, Engineering, SOX |
| Decision Impact | 144px | Block, Review, Conditional |
| Status | 112px | Open, In Review, Accepted |
| Updated | 128px | Date/time |

### Filters

- Search
- Severity
- Category
- Rule ID
- Profile
- Analyzer
- Decision impact
- Status
- Baseline/custom rule
- Hidden AI/model only
- Blocking gates only

### Detail Drawer Tabs

```text
Overview
Evidence
Rule
Remediation
History
```

Reference mockup:

![Findings Explorer](docs/design-assets/mockups/05-findings-explorer.png)

---

## 11.6 Scan History

Purpose: Historical evidence, trend, and comparison.

### Required Capabilities

- Compare two scans
- Show ruleset version per scan
- Show scanner version per scan
- Show decision change
- Show critical finding delta
- Show hidden AI/model risk delta
- Show evidence hash per scan

Reference mockup:

![Scan History](docs/design-assets/mockups/06-scan-history.png)

---

## 11.7 Evidence Package

Purpose: Audit-grade artifact verification.

### Required Content

- Current scan
- Decision
- Evidence status: Verified / Modified / Missing / Not generated
- File tree
- Manifest table
- SHA256 hashes
- Scanner version
- Ruleset version
- Generated timestamp
- Verify integrity action

### Layout

```text
[Evidence Status Strip]
[Package Contents Tree] [Manifest Details Table]
[Package Verification Panel]
```

### Evidence States

| State | Visual |
|---|---|
| Verified | Green shield check |
| Modified | Red alert |
| Missing file | Red alert |
| Hash mismatch | Red alert |
| Not verified | Amber warning |

Reference mockup:

![Evidence Package](docs/design-assets/mockups/07-evidence-package.png)

---

## 11.8 Profiles

Purpose: Profile requirements and gating thresholds.

### Required Profiles

- sandbox
- team-use
- department-use
- enterprise
- finance-sox
- ai-enabled
- production-critical

### Profile Detail Must Show

- Mandatory analyzers
- Mandatory baseline rules
- Required documents
- Blocking gates
- Minimum score
- Required approvers
- Whether hidden AI/model scan is mandatory

Reference mockup:

![Profiles](docs/design-assets/mockups/08-profiles.png)

---

## 11.9 Rules

Purpose: Baseline/custom rule review, not freeform editing.

### Required Columns

| Column | Notes |
|---|---|
| Rule ID | Monospace |
| Name | Clear rule name |
| Type | Baseline / Custom |
| Category | Security, AI Model Risk, etc. |
| Severity | Badge |
| Decision | Block, Review, Conditional |
| Applies To | Profiles |
| Status | Active, Disabled, Deprecated |
| Locked | Yes/No |

### Baseline Rule Behavior

- Baseline rules are read-only.
- Baseline rules show lock icon.
- Disable action requires warning modal.
- Disabled baseline rules create governance findings.

### Rule Detail Drawer

Tabs:

```text
Overview
Condition
YAML
Profiles
History
```

Reference mockup:

![Rules](docs/design-assets/mockups/09-rules.png)

---

## 11.10 Rulesets

Purpose: Versioned policy-as-code governance.

### Required Content

- Active ruleset
- Draft rulesets
- Locked rulesets
- SHA256 of ruleset
- Approval status
- Diff between rulesets
- Rollback action
- Disabled baseline rules included in ruleset

### Ruleset Statuses

| Status | Meaning |
|---|---|
| Draft | Editable |
| In Review | Awaiting approval |
| Active | Used by default |
| Locked | Immutable |
| Deprecated | Not used for new scans |
| Rolled Back | Superseded by rollback |

---

## 11.11 Baseline Exceptions

Purpose: Make disabled baseline rules visible and uncomfortable.

### Required Columns

| Column | Notes |
|---|---|
| Exception ID | Monospace |
| Baseline Rule | Rule ID + name |
| Severity | Original rule severity |
| Reason | Required |
| Approved By | Required |
| Expiry Date | Required |
| Affected Profiles | Profiles |
| Status | Active, Expired, Revoked |

### Warning Copy

```text
Disabling a baseline rule weakens the enterprise assurance baseline.
This action must be approved, time-bound, and visible in every affected scan report.
```

---

## 11.12 Settings

Purpose: Local scanner configuration.

Settings must be technical and local-first.

### Required Settings

- Default output directory
- Default profile
- Active ruleset
- Offline mode
- Analyzer timeout
- Parallelism
- Evidence hash verification
- Store scan history locally
- External tool paths
- Git credential helper
- Mask evidence snippets
- Strict mode default

Reference mockup:

![Settings](docs/design-assets/mockups/10-settings.png)

---

## 12. Hidden AI / Model Risk UI

This is a first-class risk category.

### Dedicated Section in Scan Summary

Title:

```text
Hidden AI / Model Risk
```

Required fields:

| Field | Example |
|---|---|
| AI libraries detected | `langchain`, `transformers`, `openai` |
| External AI endpoints | `api.openai.com` |
| Model artifacts | `model.pkl`, `weights.safetensors` |
| Vector DB indicators | `chromadb`, `faiss`, `pinecone` |
| Prompt files | `prompts/system_prompt.txt` |
| Declaration status | Declared / Undeclared |
| Decision impact | Mandatory Review / Block |

### Badge

Use category color purple/blue, not severity color unless the finding is high/critical.

| Token | Value |
|---|---|
| AI category text | `#6D28D9` |
| AI category bg | `#F5F3FF` |
| AI category border | `#C4B5FD` |

---

## 13. Baseline Rule Disable Modal

This modal must be intentionally strict.

### Modal Title

```text
Disable baseline rule?
```

### Required Body

```text
This is a baseline enterprise assurance rule. Disabling it may reduce security coverage and will be recorded in scan reports, evidence packages, and governance findings.
```

### Required Fields

- Reason
- Approver
- Expiration date
- Affected profiles
- Compensating control
- Confirmation phrase: `DISABLE BASELINE RULE`

### Buttons

| Button | Variant |
|---|---|
| Cancel | Secondary |
| Disable baseline rule | Danger |

---

## 14. Empty States

Empty states must be technical and action-oriented.

### Examples

| Screen | Empty State Copy |
|---|---|
| Findings | `No findings match the current filters.` |
| Evidence | `No evidence package has been generated for this scan.` |
| Rulesets | `No draft rulesets exist.` |
| History | `No scans have been run on this machine.` |

Avoid “Great job!” or playful language.

---

## 15. Error States

Errors must be explicit and useful.

### Error Pattern

```text
[Error title]
What happened
Why it matters
How to resolve
Technical details
```

### Example

```text
Mandatory analyzer failed
The dependency analyzer could not parse package-lock.json.
This may reduce supply-chain coverage and prevents enterprise approval.
Resolve the manifest issue or attach a formal exception, then re-run the scan.
```

---

## 16. Accessibility

### Requirements

| Requirement | Target |
|---|---|
| Text contrast | WCAG AA minimum |
| Focus states | Visible for every interactive element |
| Keyboard navigation | Required for tables, drawers, modals |
| Color independence | Severity must include text/icon, not color only |
| Hit target | 32px minimum, 40px preferred |
| Motion | Minimal and reducible |

### Severity Accessibility

Never rely only on color. Always include label:

```text
Critical
High
Medium
Low
```

---

## 17. Motion and Microinteractions

Motion should clarify state, not entertain.

| Interaction | Motion |
|---|---|
| Drawer open | 160ms ease-out |
| Modal open | 120ms fade + scale 98→100 |
| Table hover | No movement; background only |
| Progress | Smooth linear update |
| Toast | Slide/fade, 200ms |
| Spinner | Only for active analyzer |

Avoid large page transitions.

---

## 18. Content and Copy Rules

### Tone

- Technical
- Direct
- Conservative
- Evidence-based
- No fluff

### Preferred Terms

| Use | Avoid |
|---|---|
| `Not Approved` | `Failed badly` |
| `Mandatory Review` | `Needs a look` |
| `Blocking finding` | `Problem` |
| `Evidence package` | `Export bundle` |
| `Ruleset` | `Settings` |
| `Analyzer failed` | `Something went wrong` |
| `Undeclared AI/model usage` | `AI stuff` |

### Finding Titles

Good:

```text
Hardcoded Secret Detected
Undeclared External AI API Usage
Baseline Rule Disabled
Missing Technical Owner
Critical Dependency Vulnerability
```

Bad:

```text
Security issue found
AI detected maybe
This needs fixing
```

---

## 19. Design Tokens — CSS Variables

```css
:root {
  --font-sans: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-mono: "JetBrains Mono", "SFMono-Regular", Consolas, "Liberation Mono", monospace;

  --color-bg: #F8FAFC;
  --color-surface: #FFFFFF;
  --color-surface-muted: #F1F5F9;
  --color-sidebar: #0B1220;
  --color-sidebar-elevated: #111827;
  --color-border: #E2E8F0;
  --color-border-strong: #CBD5E1;

  --color-text-primary: #0F172A;
  --color-text-secondary: #475569;
  --color-text-muted: #64748B;
  --color-text-inverse: #F8FAFC;

  --color-primary: #2563EB;
  --color-primary-hover: #1D4ED8;
  --color-primary-subtle: #EFF6FF;
  --color-focus: #3B82F6;

  --severity-critical: #DC2626;
  --severity-critical-bg: #FEF2F2;
  --severity-critical-border: #FCA5A5;

  --severity-high: #EA580C;
  --severity-high-bg: #FFF7ED;
  --severity-high-border: #FDBA74;

  --severity-medium: #D97706;
  --severity-medium-bg: #FFFBEB;
  --severity-medium-border: #FCD34D;

  --severity-low: #16A34A;
  --severity-low-bg: #F0FDF4;
  --severity-low-border: #86EFAC;

  --severity-info: #2563EB;
  --severity-info-bg: #EFF6FF;
  --severity-info-border: #93C5FD;

  --ai-risk: #6D28D9;
  --ai-risk-bg: #F5F3FF;
  --ai-risk-border: #C4B5FD;

  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;

  --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.06);
  --shadow-md: 0 8px 24px rgba(15, 23, 42, 0.08);
  --shadow-focus: 0 0 0 3px rgba(37, 99, 235, 0.25);
}
```

---

## 20. Tailwind Token Mapping

If using Tailwind, map tokens explicitly.

```ts
export const designTokens = {
  colors: {
    bg: '#F8FAFC',
    surface: '#FFFFFF',
    sidebar: '#0B1220',
    primary: '#2563EB',
    text: {
      primary: '#0F172A',
      secondary: '#475569',
      muted: '#64748B',
      inverse: '#F8FAFC',
    },
    severity: {
      critical: '#DC2626',
      high: '#EA580C',
      medium: '#D97706',
      low: '#16A34A',
      info: '#2563EB',
    },
    aiRisk: '#6D28D9',
  },
  borderRadius: {
    sm: '6px',
    md: '8px',
    lg: '12px',
    xl: '16px',
  },
  spacingBase: 4,
};
```

---

## 21. Component Naming

Use predictable component names.

```text
AppShell
SidebarNav
TopHeader
PageHeader
DecisionBanner
GateStack
SeverityBadge
DecisionBadge
AnalyzerStatusPill
TechnicalTable
FilterBar
FindingDrawer
EvidenceSnippet
HashBlock
RuleYamlBlock
EvidenceManifestTable
ProfileRequirementPanel
BaselineDisableModal
RulesetDiffPanel
```

---

## 22. GUI Implementation Priorities

If implementing UI after CLI maturity, build in this order:

| Priority | Component / Screen | Reason |
|---:|---|---|
| P0 | AppShell + tokens | Foundation |
| P0 | Scan Summary | Main value screen |
| P0 | Findings Explorer + drawer | Core reviewer workflow |
| P0 | Evidence Package | Audit trust |
| P0 | Rules + baseline lock states | Governance trust |
| P1 | New Scan | Usability |
| P1 | Scan Progress | Transparency |
| P1 | Profiles | Configuration |
| P1 | Rulesets | Version governance |
| P2 | Dashboard | Overview |
| P2 | Settings | Local config |
| P2 | Exceptions | Enterprise governance |

Rationale: The system should first prove technical review value, not dashboard aesthetics.

---

## 23. Design QA Checklist

Before accepting any UI implementation, verify:

| Check | Required |
|---|---:|
| All text is English | Yes |
| Critical gates appear above scores | Yes |
| Hidden AI/model risk has dedicated visibility | Yes |
| Evidence links exist from findings | Yes |
| Baseline rules are visibly locked | Yes |
| Disabled baseline rules show warnings | Yes |
| Analyzer failures are visible | Yes |
| SHA256 evidence hash is visible | Yes |
| File paths and hashes use mono font | Yes |
| No stock human photos | Yes |
| No decorative charts replacing findings | Yes |
| Tables support filtering and sorting | Yes |
| Drawer preserves context | Yes |
| Color is not the only severity signal | Yes |
| UI does not imply cloud upload | Yes |
| UI does not imply AI usage by the scanner | Yes |

---

## 24. Reference Mockup Assets

These assets are visual references only. The implementation should follow this design system even when improving details.

| Screen | Asset |
|---|---|
| Dashboard | `docs/design-assets/mockups/01-dashboard-overview.png` |
| New Scan | `docs/design-assets/mockups/02-new-scan.png` |
| Scan Progress | `docs/design-assets/mockups/03-scan-progress.png` |
| Scan Summary | `docs/design-assets/mockups/04-scan-summary.png` |
| Findings Explorer | `docs/design-assets/mockups/05-findings-explorer.png` |
| Scan History | `docs/design-assets/mockups/06-scan-history.png` |
| Evidence Package | `docs/design-assets/mockups/07-evidence-package.png` |
| Profiles | `docs/design-assets/mockups/08-profiles.png` |
| Rules | `docs/design-assets/mockups/09-rules.png` |
| Settings | `docs/design-assets/mockups/10-settings.png` |

---

## 25. Final Design Position

The interface must feel like a professional security/code-assurance workstation:

```text
Precise enough for AppSec.
Strict enough for CISO.
Structured enough for CTO.
Traceable enough for Audit.
Clear enough for engineering teams to remediate.
```

The product should not look like a generic SaaS dashboard. It should look like a serious local enterprise assurance system where every pixel supports review, evidence, and decision quality.
