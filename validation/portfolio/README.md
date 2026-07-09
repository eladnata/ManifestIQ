# Portfolio Validation

Portfolio validation aggregates multiple gold set comparison reports into reliability evidence for L4 and L5 validation maturity.

This workflow is local, deterministic, offline-capable, non-AI, evidence-first, conservative by default, and English-only.

The platform prepares evidence and amplifies reviewers. Professionals own judgment.

## Inputs

- Portfolio manifest JSON.
- One or more `goldset-comparison-report.json` files.
- Optional reviewer worksheets.
- Optional scanner-only triage files.
- Optional calibration logs.

## Outputs

- `portfolio-validation-report.json`
- Portfolio reports can be used as inputs to validation trend gates.

## Conservative Triage Rule

Scanner-only findings are not automatically false positives. They remain `triage_required` until a reviewer labels them as `valid_material`, `valid_minor`, `duplicate`, `acceptable_noise`, `false_positive`, or `needs_human_review`.

Untriaged scanner-only findings do not reduce material precision after triage.

## Trend Use

Portfolio reports should record scanner version and ruleset version so later trend comparison can detect regressions.

Regression gates should be reviewed and approved by AppSec, CISO, CTO, or delegated assurance owners. A passing gate does not replace expert review; it only indicates that configured validation metrics did not regress beyond policy thresholds.
