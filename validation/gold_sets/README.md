# Gold Sets

Gold sets are local, human-reviewed ground-truth files used to compare scanner output against expert judgment.

Gold set validation is for measurement and calibration. It does not replace CISO, CTO, AppSec, Architecture, DevOps, SOX, ITGC, Legal, Privacy, or Security reviewer judgment.

The scanner prepares evidence and amplifies the reviewer. The professional owns the judgment.

## Directory Contents

- `schemas/goldset.schema.json`: schema for human-reviewed ground truth.
- `schemas/reviewer_worksheet.schema.json`: schema for reviewer feedback after using scanner output.
- `schemas/comparison_report.schema.json`: schema for generated comparison reports.
- `examples/sample-goldset.json`: deterministic example gold set.
- `examples/sample-reviewer-worksheet.json`: deterministic example worksheet.

## Workflow

1. Run a local scanner scan and keep the evidence package.
2. Create or select a gold set JSON file for the reviewed repository.
3. Optionally collect reviewer worksheets.
4. Run gold set comparison locally.
5. Review matched findings, missed detectable findings, non-detectable human findings, and scanner-only findings requiring triage.

Scanner-only findings are not automatically false positives. They require reviewer triage.
