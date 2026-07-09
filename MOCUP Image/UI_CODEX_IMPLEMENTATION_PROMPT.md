# UI Implementation Prompt for Codex

You are working inside the `enterprise-whitebox-scanner` repository.

Read these files first:

1. `MASTER_SPEC.md`
2. `CISO_CTO_ASSURANCE_SPEC.md` if it exists
3. `DESIGN_SYSTEM.md`
4. `CODEX_CLAUDE_PROMPT.md`

Your task is to implement or document the UI according to `DESIGN_SYSTEM.md`.

The UI must be:

- English-only
- CISO/CTO-grade
- Technical and evidence-first
- Local-first
- No AI usage by the scanner
- No cloud-upload implication
- Conservative by default
- Professional, modern, dense where useful, but not visually overloaded

Do not create a marketing dashboard. Create a technical assurance cockpit.

## Required UI Priorities

Implement in this order if a UI framework exists:

1. AppShell, SidebarNav, TopHeader, design tokens
2. Scan Summary screen
3. Findings Explorer with right-side Finding Drawer
4. Evidence Package screen with manifest and SHA256 verification
5. Rules screen with baseline/custom rules and locked baseline states
6. Profiles screen
7. New Scan screen
8. Scan Progress screen
9. Rulesets screen
10. Baseline Exceptions screen
11. Settings screen
12. Dashboard screen

If no UI framework exists, create a UI specification only and do not add a framework without approval.

## Must-Have Design Behaviors

- Critical gates appear above score.
- Hidden AI/model risk has a dedicated section.
- Analyzer failures are visible.
- Baseline rules are visibly locked and read-only.
- Disabling baseline rules requires strong warning flow.
- Disabled baseline rules appear in reports/evidence/governance warnings.
- Every finding links to evidence.
- Evidence hashes use monospace font.
- File paths use monospace font.
- Severity uses text + icon + color, never color alone.
- No stock user photos; use initials avatar.
- Charts are secondary to findings and evidence.

## Use These Design Tokens

Use the exact color and spacing tokens from `DESIGN_SYSTEM.md` unless there is a technical reason not to.

Core colors:

- Background: `#F8FAFC`
- Surface: `#FFFFFF`
- Sidebar: `#0B1220`
- Text primary: `#0F172A`
- Text secondary: `#475569`
- Border: `#E2E8F0`
- Primary: `#2563EB`
- Critical: `#DC2626`
- High: `#EA580C`
- Medium: `#D97706`
- Low: `#16A34A`
- AI/model risk: `#6D28D9`

Fonts:

- UI: Inter or system sans-serif fallback
- Code/hash/file paths: JetBrains Mono or system monospace fallback

## Acceptance Criteria

The UI work is acceptable only if:

1. It follows `DESIGN_SYSTEM.md`.
2. It keeps the product technical and evidence-first.
3. It does not add AI, telemetry, cloud upload, or marketing copy.
4. It shows blocking gates, hidden AI/model risk, evidence hashes, analyzer status, and baseline rule lock states clearly.
5. It remains clean, professional, readable, and suitable for CISO/CTO/AppSec review.

Start by inspecting the repository and reporting whether a UI layer currently exists. If it does not exist, create a clear implementation plan and do not add a frontend stack unless explicitly asked.
