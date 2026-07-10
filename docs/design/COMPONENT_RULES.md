# ManifestIQ Component Rules

**Status:** Component standard. Documentation only — not implementation.
**Companion:** [UI_FOUNDATIONS](UI_FOUNDATIONS.md) (philosophy) · [DESIGN_TOKENS](DESIGN_TOKENS.md) (values) · [MANIFESTIQ_DESIGN_SKILL_PACK](MANIFESTIQ_DESIGN_SKILL_PACK.md) (rooms) · governed by [`docs/internal/`](../internal/README.md).

Anatomy and rules for every reusable component. Governing rule: **one component has one meaning.** All values referenced (`--token`) are defined in [DESIGN_TOKENS](DESIGN_TOKENS.md). Where a component and the doctrine conflict, the doctrine wins.

Each component is specified as:

```text
Purpose · Where it is used · Required content · Visual rules · Forbidden misuse
```

---

## 1. Top Bar

- **Purpose.** Orient the user and anchor every screen to its evidence (the persistent shell, top).
- **Where used.** Every screen.
- **Required content.** Wordmark; current room name + its dominant question; scope chip (files/components); the **Integrity Line** (manifest hash, provenance, scan time, integrity state) directly beneath.
- **Visual rules.** `--color-surface` with a bottom hairline; wordmark may use `--color-brand-gold`; Integrity Line uses `--font-mono` at `--text-sm`, `--color-text-muted`. Integrity state uses `--color-integrity-green` **only** for VERIFIED (a fact).
- **Forbidden misuse.** No approval status here. No green other than integrity-verified. No hiding the room name or scope. Not a navigation dumping ground.

## 2. Footer Non-Claims Strip

- **Purpose.** Keep what the product does *not* assert permanently visible.
- **Where used.** Every screen, fixed at bottom.
- **Required content.** Label "Non-Claims" + the standing denials: not certified; no SOX/privacy/legal approval; not a release approval; no safety claim; human approval not inferred.
- **Visual rules.** Fixed, `--color-surface` with a strong top border; label in `--color-critical-red` eyebrow; items in `--color-text-muted` at `--text-xs`–`--text-sm`. Always visible; never below the fold.
- **Forbidden misuse.** Never collapsible, never dismissible, never scrolled away. No positive claims. Not used for marketing copy.

## 3. Hero Decision Area

- **Purpose.** Deliver the visible decision and its immediate context — the focal surface of the Board Verdict Room.
- **Where used.** Board Verdict Room (the one hero per screen).
- **Required content.** Eyebrow "Visible decision"; verdict headline; explicit "not an approval" sub-line; bounded score (with scale) + confidence; one-line rationale; top blockers; one next action; required reviewer chips.
- **Visual rules.** Single `--color-surface` card, `--shadow-1`, severity-colored left border; verdict in `--font-display` `--text-2xl`; score meter is **bounded and attenuates** (hatch) when evidence is thin. Never green.
- **Forbidden misuse.** No "Approved" text as output. No green pass hero. No merged status pill. No second hero on the same screen. No success animation.

## 4. Five-Layer Trust Strip

- **Purpose.** Show the five decision layers as separate, non-promotable slots.
- **Where used.** Board Verdict Room and anywhere decision status is summarized.
- **Required content.** Five labelled slots in order: (1) Raw scanner decision, (2) Review readiness, (3) Risk acceptance coverage, (4) Release readiness, (5) Human approval — the fifth **empty and labelled "Human approval is not inferred."**
- **Visual rules.** Equal-weight slots; slot 1 severity-colored; slots 2/4 review-slate; slot 3 review-slate as bounded evidence; slot 5 dashed border + hatch + `--color-unknown-gray`, italic "— not present —" with the empty tag.
- **Forbidden misuse.** Never merge into one pill. Never fill the human-approval slot. Never color any slot with integrity green or brand gold. Never reorder to imply promotion.

## 5. Blocker Card

- **Purpose.** Present one blocker with its impact, disposition, and evidence route.
- **Where used.** Board Verdict Room (top blockers), Remediation Path, Decision Rationale.
- **Required content.** Severity lane tag (Critical/High/Material/Mandatory Review); title; business/release impact; disposition (**Remediable / Review-Gated / Exception-Eligible (bounded)**); evidence badge (rule → finding → hash).
- **Visual rules.** `--color-surface-2` card; severity via `--color-critical-red`/`--color-caution-amber` on the lane tag; expandable (native disclosure) for detail. Exception-eligible disposition uses review-slate and reads "bounded evidence — not remediation."
- **Forbidden misuse.** Never style an exception as a fix. Never mark an unremediated item "resolved." Never hide/mutate/downgrade the underlying raw finding. No editing.

## 6. Remediation Step

- **Purpose.** Present one required action in an ordered path to readiness.
- **Where used.** Remediation Path.
- **Required content.** Sequence number/marker; action statement (verb-first); linked blocker(s); disposition; required reviewer role if review-gated.
- **Visual rules.** Ordered list with `--font-mono` step markers in `--color-text-faint`; hairline dividers; dependency/ordering visible where one step gates another.
- **Forbidden misuse.** No implied completion state. No approval capture. Not a checklist that records human sign-off. No editing workflow.

## 7. Causal Chain Card

- **Purpose.** Show *why* the decision holds — an ordered chain of decisive factors, each evidence-linked.
- **Where used.** Decision Rationale.
- **Required content.** Ordered decisive factors; per factor: a severity marker, a one-sentence statement, and an evidence badge that descends to the finding; a "what would change the decision" note.
- **Visual rules.** Ordered rows; evidence badge required on every factor; a factor without a traceable badge renders as `Assertion — Insufficient Evidence` (unknown-gray), never as confirmed.
- **Forbidden misuse.** No prose without evidence links. No inference-style language implying reasoning beyond the deterministic rules. No reordering that buries the decisive blocker.

## 8. Evidence Seal

- **Purpose.** Signal that a specific artifact's integrity has been verified — a fact, not a judgment.
- **Where used.** Evidence Vault, Integrity Line, alongside evidence references.
- **Required content.** Artifact identity; integrity state (Verified / Stale / Missing / Corrupted); the associated content hash reference.
- **Visual rules.** VERIFIED uses `--color-integrity-green` (the **only** sanctioned green); Stale uses amber; Missing/Corrupted use unknown-gray/critical-red with label. Mono hash reference.
- **Forbidden misuse.** Never present a seal as approval, readiness, safety, or a decision. Never show an overall "verified" seal if any artifact failed. Green here never migrates to a decision surface.

## 9. Manifest Fingerprint

- **Purpose.** Make the run's provenance and reproducibility legible at a glance.
- **Where used.** Top bar Integrity Line; Evidence Vault header.
- **Required content.** Run manifest hash; provenance (engine version, config id); scan scope digest; scan timestamp (local).
- **Visual rules.** `--font-mono`, `--text-sm`, `--color-text-muted`; hash truncated with a monospace `⌗` marker; deterministic — same run yields the same fingerprint.
- **Forbidden misuse.** No approximate/"looks the same" reproduction claim — identity is by hash. Not a decoration; not a status.

## 10. Domain Posture Row / Tile

- **Purpose.** Show one assurance domain's posture and evidence coverage.
- **Where used.** Domain Heat Map; System Dossier Snapshot summaries.
- **Required content.** Domain name; state (Clear-with-Evidence / Caution / Blocker / **Insufficient Evidence**); evidence-coverage meter; blocker count.
- **Visual rules.** State via left-border color + label; coverage meter over `--color-surface-2`; unknown/insufficient states use the hatch pattern and are visually distinct from low-risk states.
- **Forbidden misuse.** No green tile for "no findings." Absence of findings never rendered as a pass. Never hide an uncovered/unknown domain. No numeric-only heat that hides state.

## 11. Finding Detail Card

- **Purpose.** Present one finding and its full evidence chain.
- **Where used.** Finding Detail.
- **Required content.** Finding statement; rule ID; severity; evidence reference(s); affected file(s); source artifact; content hash.
- **Visual rules.** Descent chain laid out finding → rule → evidence → file → hash; mono for rule IDs, paths, hashes; raw finding shown **unmodified**.
- **Forbidden misuse.** No editing. No mutation/downgrade/suppression of the raw finding. No claim not anchored to a hash-verified evidence reference.

## 12. Reviewer Role Card / Chip

- **Purpose.** Signal a required review role and what it must examine — never a sign-off.
- **Where used.** Reviewer Briefing; Board Verdict Room (required-reviewer chips).
- **Required content.** Role name; the item(s)/domain(s) that role must review; review state (`Mandatory Review` / `Conditional Review`).
- **Visual rules.** Pill/chip with a neutral dot; `--color-text-muted` sub-label; "review required" phrasing only.
- **Forbidden misuse.** No approval button, no sign-off capture, no "reviewed/approved" state. Assignment never implies approval. Never records or infers a human decision.

## 13. Portfolio Priority Row

- **Purpose.** Rank one system against others by attention needed.
- **Where used.** Portfolio Command.
- **Required content.** System identity; visible decision state; open blocker count; route to that system's Board Verdict Room.
- **Visual rules.** Compact density; ordered by verdict severity then open blockers; per-system state via severity color + label; each row descends to the system.
- **Forbidden misuse.** No blended "portfolio health" green score. No roll-up that hides a failing system. No implied approval. No averaging away a blocker or unknown state.

## 14. Assessment Launch Panel

- **Purpose.** Frame what will be assessed and the standing local/deterministic guarantees before a run.
- **Where used.** Assessment Launch.
- **Required content.** Target; declared scope; the guarantees (local-only · deterministic · no external transmission); the single "Prepare run" action.
- **Visual rules.** Quiet panel; guarantees stated plainly; one primary button (verb-first); scope selection clear.
- **Forbidden misuse.** No cloud/account/upload affordance. No external enrichment option. No telemetry or "share results." No AI/inference toggle. No approval affordance.

## 15. Status Pill

- **Purpose.** Label a single state in the sanctioned status vocabulary.
- **Where used.** Everywhere a discrete status appears.
- **Required content.** A status label from the allowed set (`Missing Evidence`, `Insufficient Evidence`, `Mandatory Review`, `Conditional Review`, `Not Ready`, `Not Approved`, `Unknown`, `Limitation`, `Ready for Review`) or a severity label.
- **Visual rules.** `--radius-pill`; color + label together (never color alone); `--text-xs`/`--text-sm` label but attached to ≥`--text-base` context. `Ready for Review` uses review-slate.
- **Forbidden misuse.** Never render a forbidden positive claim (Approved, Certified, Compliant, Safe, Production Ready, SOX/Privacy/Legally Approved, Fully Secure) as a pill. Never green (integrity is a seal, not a status pill). Never gold.

## 16. Evidence Badge

- **Purpose.** Attach a traceable evidence reference to a claim and route to it.
- **Where used.** On every decisive claim, blocker, rationale factor, and finding.
- **Required content.** A reference chain marker (rule ID → finding → hash) that descends to the evidence.
- **Visual rules.** `--font-mono`, `--color-review-slate` as an interactive/descend affordance; clearly clickable/focusable.
- **Forbidden misuse.** A claim with no evidence badge must not be styled as confirmed. Never a decorative badge with no destination. Never implies approval.

## 17. Primary Button

- **Purpose.** The single next action for the screen's one question.
- **Where used.** One per screen.
- **Required content.** Verb-first label naming exactly what happens (e.g., "Open Remediation Path").
- **Visual rules.** Solid high-contrast **ink** (`--color-text`/surface inverse), `--radius`; one primary per surface.
- **Forbidden misuse.** Never green. Never labelled "Approve," "Sign off," "Certify," or "Release." No approval capture.

## 18. Secondary Button

- **Purpose.** Supporting navigation or descent into evidence.
- **Where used.** Alongside a primary action or for cross-room routes.
- **Required content.** Verb-first label.
- **Visual rules.** Outlined/quiet on `--color-surface`; subordinate to the primary.
- **Forbidden misuse.** Never competes visually with the primary. Never an approval affordance.

## 19. Danger Button

- **Purpose.** Destructive or escalation actions only.
- **Where used.** Rare; where a destructive/escalation action genuinely exists.
- **Required content.** Verb-first label naming the consequence.
- **Visual rules.** `--color-critical-red` outline or solid; visually distinct from primary; used sparingly.
- **Forbidden misuse.** Not for ordinary navigation. Never an approval/sign-off. Never the default action.

---

## Cross-component invariants

1. **No approved green** — green appears only on the Evidence Seal / Integrity Line as a verified-integrity fact.
2. **No visual implication of approval** — no component renders or implies "Approved"; the human-approval slot stays empty and labelled.
3. **Risk acceptance ≠ remediation; release readiness ≠ release approval; `Ready for Review` ≠ approval.**
4. **One component, one meaning** — no multi-purpose "everything" component.
5. **Primary content ≥ `--text-base`** — no tiny text as primary content.
6. **Every claim carries an evidence badge or is marked insufficient.**
7. **All values come from [DESIGN_TOKENS](DESIGN_TOKENS.md)** — no inline one-offs.

*Documentation only. No implementation, no framework choice, no cloud/telemetry/AI/external dependency, and no change to existing mockups.*
