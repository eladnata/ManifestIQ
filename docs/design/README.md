# ManifestIQ Design — Index

**Status:** Design index and orientation. Not implementation.
**Audience:** CISO, CTO, CIO, CFO, DevOps lead, GRC Manager, auditor, Legal / Privacy reviewers, senior engineering.
**Governed by:** the internal trust doctrine in [`docs/internal/`](../internal/README.md). Where design and doctrine appear to conflict, the doctrine wins.

---

## Purpose

This directory holds the product experience architecture for ManifestIQ's first GUI. It is an index and orientation guide; the referenced specification governs.

- [EXECUTIVE_ASSURANCE_COCKPIT](EXECUTIVE_ASSURANCE_COCKPIT.md) — the authoritative screen-by-screen specification.

## What the GUI Is

- The GUI is an **executive decision surface**, not a generic dashboard, not a table-first GRC console, not an admin panel.
- It **reduces cognitive load without hiding risk**: one decision focal point per screen, with every claim one interaction away from its evidence.
- It is **evidence-backed and read-only in v1**: a local viewer over an already-generated, integrity-manifested report. It does not scan, edit, approve, or transmit.

## Non-Negotiable Design Rules

### The five decision layers remain visually separate
The interface must never merge these into a single status. Each is a distinct, labelled slot wherever status appears:

1. Raw scanner decision
2. Review readiness
3. Risk acceptance coverage
4. Release readiness
5. Human approval

### Separation semantics
- **`Ready for Review` is not approval.**
- **Risk acceptance is bounded evidence, not remediation or approval.**
- **Release readiness is not release approval.**
- **Human approval is never inferred.** The human-approval slot is rendered permanently empty and labelled as such. This empty slot is the primary trust signal.

### Evidence vs. judgment
- **Evidence integrity may be verified**, and that verification may be shown as a fact.
- **System approval is never inferred** from verified integrity, from an absence of findings, or from any combination of statuses.
- There is **no "approved green."** Positive-sentiment color is reserved for verified-integrity facts, never for decisions, readiness, or approval.

## Commercial Intent Without Overclaiming

The design must **support sales and executive clarity without manufacturing confidence.** Its persuasiveness comes from demonstrated discipline — traceable claims, visible limitations, and a visible refusal to fabricate approval — not from success visuals. The interface makes no claim of certification, compliance signoff, SOX / privacy / legal approval, penetration-testing completion, production or release approval, or safety.

## Related

- [`docs/internal/README.md`](../internal/README.md) — internal trust doctrine index.
- [`TRUST_BOUNDARY_AND_NON_CLAIMS`](../internal/TRUST_BOUNDARY_AND_NON_CLAIMS.md) — authoritative non-claims and forbidden-language control.
- [`DECISION_SEMANTICS_STANDARD`](../internal/DECISION_SEMANTICS_STANDARD.md) — authoritative decision-layer separation and misuse controls.
