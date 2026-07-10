# Risk Acceptance Exception Policy

## Purpose

This policy defines how ManifestIQ evaluates local risk acceptance and exception records. The exception register adds a deterministic evidence layer that shows whether material findings or gaps are covered by valid, scoped, non-expired exception records.

## Scope

The policy applies to local JSON exception registers supplied during a scan with `--exception-register` or applied afterward with `apply-exceptions`.

Records may scope to profiles, source paths, rule IDs, finding IDs, gap IDs, and domains. Raw scanner findings, raw scanner score, and raw scanner decision are preserved.

## Non-Goals

Risk acceptance does not:

- Certify compliance.
- Grant production approval.
- Replace CISO, CTO, AppSec, Architecture, ITGC, SOX, Legal, Privacy, or Security review.
- Remove, hide, suppress, downgrade, or modify raw findings.
- Change raw scanner scoring or raw scanner decision.

## Required Fields

Each record must include:

- `exception_id`
- `status`
- `scope`
- `reason`
- `risk_statement`
- `owner`
- `approved_by`
- `approved_role`
- `approved_at`
- `expires_at`

At least one scope selector must exist: `rule_ids`, `finding_ids`, `gap_ids`, or `domains`.

## Approval Role Logic

Records are evaluated conservatively:

- Critical security findings require `CISO` or `AppSec`.
- SOX / Finance findings require `ITGC / SOX Reviewer` or `CISO`.
- AI/model risk findings require `CISO`, `Data Governance`, or `Security Architecture`.
- License findings require `Legal / Open Source Review` or `CISO`.
- Architecture findings require `CTO / Enterprise Architecture` or `Security Architecture`.
- Operational readiness findings require `DevOps / SRE` or `Release Manager / Control Owner`.

If the role is insufficient for a matched material finding or gap, the record is invalid and does not cover that risk.

## Expiration Behavior

Only `approved` records can provide coverage. Approved records with `expires_at` in the past are marked `expired` and do not cover findings or gaps.

Draft, rejected, and revoked records never provide coverage.

## Scope Matching Behavior

Profile and source path scope are filters. If present, they must match the current scan profile and source path.

Rule ID, finding ID, gap ID, and domain selectors determine coverage:

- Findings can match by `finding_id`, `rule_id`, finding category, or derived acceptance domain.
- Gaps can match by `gap_id`, related rule IDs, or gap domain.
- Scope mismatches are recorded but do not provide coverage.

## Impact on Decision Packet

When a register is processed, `decision-packet.json` includes a `risk_acceptance` summary with review status, covered/uncovered material findings and gaps, expired or invalid exception IDs, and a non-claim.

The raw decision in the packet remains the scanner decision.

## Non-Claims

Every risk acceptance review states:

- Risk acceptance coverage does not grant production approval by itself.
- Risk acceptance coverage does not change raw findings, raw score, or raw scanner decision.
- Risk acceptance coverage does not certify compliance or replace expert review.

## Examples

Run a scan with a local exception register:

```bash
python -m scanner scan-folder --path tests/sample_projects/insecure-python --output output --profile finance-sox --exception-register governance/examples/sample-exception-register.json
```

Apply exceptions to an existing evidence package:

```bash
python -m scanner apply-exceptions --evidence-package output/evidence-package --exception-register governance/examples/sample-exception-register.json --output output/evidence-package
```

## Acceptance Criteria

- `exception-register-normalized.json` is generated when a register is processed.
- `risk-acceptance-review.json` is generated when a register is processed.
- `risk-acceptance-review.md` is generated when Markdown output is enabled.
- Generated artifacts are included in `manifest.json`.
- Raw findings, raw score, and raw decision are unchanged.
- Decision packet includes a concise risk acceptance summary.
- HTML report includes a concise Risk Acceptance section.
- Expired, invalid, draft, rejected, revoked, and scope-mismatched records do not cover risk.
