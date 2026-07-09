# Gold Set Review Protocol

Gold set validation compares scanner output to human-reviewed ground truth. It proves review-preparation value and identifies scanner misses, false positives, confidence calibration issues, and report actionability gaps.

The scanner does not replace experts. It prepares evidence and amplifies reviewers. The professional owns the judgment.

Gold set comparison must separate findings that are expected to be detectable from static repository evidence from findings that require human business, legal, privacy, operational, or risk-acceptance judgment outside the repository. The scanner must not be penalized in recall for human findings marked `expected_scanner_detectable: false`.

Single-repository comparison is not sufficient for L4 maturity. L4 requires portfolio-level aggregation across multiple human-reviewed repositories, tied to scanner version and ruleset version.

## Protocol

1. Select 10-30 representative repositories.
2. Have AppSec, CTO, DevOps, SOX, Legal, Privacy, Architecture, and Security reviewers manually review the applicable repositories.
3. Record ground-truth findings.
4. Run the scanner.
5. Compare scanner outputs to ground truth.
6. Measure precision, recall, critical misses, reviewer agreement, top blocker agreement, and time saved.
7. Calibrate rules and confidence.
8. Repeat after each major ruleset version.

## Repository Selection

The gold set should include:

- Small services.
- Larger services.
- Libraries.
- Internal tools.
- Data-processing repositories.
- Finance/SOX-relevant repositories.
- AI/model-related repositories where applicable.
- Clean examples.
- Risky examples.
- Repositories with incomplete evidence.

Do not include repositories whose source cannot be reviewed locally under the validation program.

## Human Review Ground Truth

Ground truth should record:

- Finding ID assigned by the review team.
- Domain.
- Rule ID where applicable.
- Severity.
- Description.
- Evidence.
- Required remediation.
- Reviewer role.
- Whether the finding should block, require mandatory review, be conditional, or be advisory.
- Whether the finding is critical.
- Whether the finding is expected to be detectable from static repository evidence.

## Comparison Rules

The scanner output should be compared by:

- Rule ID when available.
- Severity.
- Domain.
- Finding title or issue class.
- File path where available.
- Decision impact.
- Evidence traceability.

Exact line-level matching is useful but should not be required for every gold set comparison. Material issue-class matching is the primary validation target.

Scanner-only material findings must be marked `triage_required` unless a reviewer worksheet labels them as false positives or valid scanner-only findings. Scanner-only findings are not automatically false positives.

Portfolio validation should use scanner-only triage files to calculate material precision after triage. Untriaged scanner-only findings remain open review items.

## Metrics

Gold set validation should measure:

- Material precision, scoped to matched material findings and reviewer-labeled false positives.
- Detectable recall.
- Critical Miss Rate.
- Evidence Traceability.
- Determinism.
- Reviewer Agreement.
- Review Preparation Acceleration.
- Report Actionability.
- Confidence Calibration.
- Domain Coverage.
- Top Blocker Agreement.

## Calibration

Calibration may change:

- Rule severity.
- Decision impact.
- Confidence policy.
- Analyzer pattern coverage.
- Report compression.
- Gap templates.
- Expected evidence requirements.

Calibration must not hide critical risk to improve pass rates.

## Repeatability

Gold set validation must be repeated:

- After major analyzer changes.
- After major ruleset changes.
- After changes to scoring or decision logic.
- Before production pilot expansion.

## Output

Each gold set run should produce:

- `goldset-comparison-report.json`.
- Miss analysis.
- Scanner-only finding triage list.
- Reviewer agreement summary.
- Calibration decision log.
- Known limitations.

Portfolio validation should aggregate comparison reports into `portfolio-validation-report.json` with metrics by domain, rule family, and profile.

Portfolio trend validation should compare portfolio reports across scanner and ruleset versions. Trend gates protect against silent degradation in detectable recall, critical miss rate, evidence traceability, material precision after triage, top blocker agreement, review acceleration, and scanner-only triage burden.

Trend comparison does not prove product quality by itself. It detects measured regression in the validation evidence available to the portfolio.

## Calibration Logs

Calibration changes must be logged when validation leads to changes in:

- Rule thresholds.
- Severity.
- Confidence policy.
- Report compression.
- Documentation only.
- No-change decisions after review.

Calibration logs must include evidence, reason, decision type, and approving role. Calibration must not hide critical risk to improve pass rates.

## Reviewer Worksheets

Reviewer worksheets capture whether the scanner-prepared report was useful, clear, and evidence-backed.

Worksheets may label:

- Missed material findings.
- False positive scanner findings.
- Valid scanner-only findings.
- Top blocker agreement.
- Estimated preparation time saved.

Worksheet data supports confidence calibration and review preparation acceleration measurement. It does not automate final judgment.
