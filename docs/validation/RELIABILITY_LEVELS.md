# Reliability Levels

Reliability levels describe maturity of scanner validation. They are not certifications and do not replace expert judgment.

## L0: Runs Successfully

Requirements:

- CLI runs on supported input types.
- Evidence package is generated.
- Analyzer failures are visible.

Evidence:

- Sample scan output.
- Evidence package files.
- Manifest and SHA256.

Metrics:

- Successful run rate.
- Evidence package completeness.
- Analyzer failure visibility.

Exit criteria:

- The scanner runs on the baseline sample projects.
- Required evidence files are produced.
- Failures produce scan integrity findings.

## L1: Unit-Tested Analyzers

Requirements:

- Analyzer unit tests exist.
- Core scoring, findings, rules, and evidence utilities are covered.
- Known analyzer contracts are validated.

Evidence:

- Unit test results.
- Analyzer-specific fixtures.
- Contract validation tests.

Metrics:

- Unit test pass rate.
- Analyzer contract pass rate.
- Rule normalization pass rate.

Exit criteria:

- Analyzer unit tests pass.
- Analyzer outputs conform to the analyzer contract.
- Normalized findings include required fields.

## L2: Seeded Test Suite Coverage

Requirements:

- Seeded repositories contain known vulnerabilities, gaps, and control failures.
- Expected findings metadata exists.
- Validation harness compares expected and actual findings.

Evidence:

- Seeded fixtures.
- Expected findings metadata.
- Validation report.

Metrics:

- Precision.
- Recall.
- Critical miss rate.
- Evidence traceability.
- Determinism.

Exit criteria:

- Critical expected findings are detected.
- Determinism passes.
- Material findings have evidence traceability.

## L3: Adversarial Suite Coverage

Requirements:

- Repositories include adversarial patterns such as split secrets, hidden AI/model usage, misleading documentation, fake health checks, committed binaries, local databases, mixed applications, and license ambiguity.
- Validation report records misses and unexpected findings.

Evidence:

- Adversarial fixtures.
- Expected findings metadata.
- Validation report.
- Regression history.

Metrics:

- Adversarial recall.
- Critical miss rate.
- False positive rate.
- Traceability.
- Report actionability.

Exit criteria:

- No critical seeded adversarial finding is missed.
- Misleading documentation does not suppress real gaps.
- Deterministic re-run passes.

## L4: Human-Reviewed Gold Set Validation

Requirements:

- 10-30 representative repositories are reviewed by human experts.
- Ground-truth findings are recorded.
- Scanner outputs are compared against expert review.
- Ground truth marks each finding with `expected_scanner_detectable`.
- Scanner-only findings are triaged before they are counted as false positives.
- Multiple gold set comparison reports are aggregated into portfolio-level validation evidence.
- Portfolio metrics are tied to scanner version and ruleset version.

Evidence:

- Gold set repository list.
- Human review notes.
- Ground-truth finding file.
- Gold set comparison reports.
- Portfolio validation report.
- Validation trend report.
- Scanner-only triage files.
- Calibration logs where rule or report changes are proposed.
- Calibration decisions.

Metrics:

- Precision.
- Detectable recall.
- Critical miss rate.
- Reviewer agreement.
- Top blocker agreement.
- Confidence calibration.
- Review preparation acceleration.
- Domain, rule-family, and profile-level metrics.
- Regression gate status across scanner and ruleset versions.

Exit criteria:

- Critical miss rate is within the accepted pilot threshold.
- Detectable findings are measured separately from non-detectable human judgment.
- Material precision is calculated after scanner-only triage.
- Reviewers agree that top blockers are materially useful.
- Rules and confidence are calibrated.
- Calibration changes are logged.
- Regression gates do not show blocking degradation for candidate scanner/ruleset releases.

## L5: Production Pilot Validation

Requirements:

- Scanner is used in real review workflows under expert supervision.
- Time savings and reviewer agreement are measured.
- Critical misses are tracked after expert review.
- Reviewer worksheets capture usefulness, clarity, evidence quality, top blocker agreement, false positives, scanner-only valid findings, and estimated time saved.
- Portfolio reports track trends across scanner version and ruleset version.
- Gate thresholds are approved by accountable security and assurance stakeholders.

Evidence:

- Pilot validation reports.
- Reviewer feedback.
- Time-to-decision-preparation measurements.
- Miss and false-positive analysis.
- Reviewer worksheets.

Metrics:

- 70-80% initial review preparation acceleration target.
- 80%+ reviewer agreement on top blockers during pilot.
- Near-zero critical miss target for covered categories.
- 0% replacement of final expert judgment.

Exit criteria:

- Pilot reviewers accept the decision packet as useful preparation.
- Material misses are triaged and remediated.
- The scanner remains an expert-amplification tool, not an automated approval system.
