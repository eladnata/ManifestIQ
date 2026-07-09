# ADR Policy

## Purpose

Architecture Decision Records preserve important design decisions, alternatives, consequences, and validation impact. ADRs are required when a change affects the scanner's architecture, evidence model, governance model, or product boundary.

## ADR Required For

- Architecture changes.
- New core pipeline stages.
- Schema changes.
- Rule contract changes.
- Validation methodology changes.
- Decision logic changes.
- Security posture changes.
- Local/offline/non-AI boundary decisions.

## ADR Format

```text
Title
Status
Date
Context
Decision
Consequences
Alternatives Considered
Validation Impact
Related Files
```

## Status Values

- Proposed.
- Accepted.
- Superseded.
- Deprecated.

## Review

ADRs should be reviewed by the Engineering Maintainer and any accountable domain reviewer before the associated implementation is considered done.

## Storage

ADRs are stored under:

```text
docs/adr/
```

ADR filenames should use a stable numeric prefix and a short lowercase title, for example:

```text
ADR-0001-local-deterministic-non-ai.md
```
