# Validation Program

This program defines how Enterprise White-Box Code Assurance Scanner proves that it does what it claims to do.

The scanner is a deterministic expert-amplification platform for enterprise system assurance. It does not replace CISO, CTO, AppSec, Architecture, DevSecOps, ITGC, SOX, Legal, Privacy, or Security reviewers. It amplifies them by preparing evidence, structuring review, evaluating deterministic controls, and preserving audit-ready outputs.

The system prepares the evidence and amplifies the reviewer. The professional owns the judgment.

## Product Constraints

- Local-first.
- Deterministic.
- Offline-capable.
- Non-AI.
- Evidence-first.
- Conservative by default.
- English-only.

## Validation Objectives

Validation must measure:

- Accuracy.
- Coverage.
- Determinism.
- Evidence traceability.
- False positives.
- False negatives.
- Critical miss rate.
- Report trustworthiness.
- Handling of adversarial and difficult repositories.

## Validation Sources

Raw scanner capability must be proven using:

- Unit tests for analyzers, rules, scoring, evidence packaging, and validation metrics.
- Integration tests that run complete scans.
- Seeded vulnerabilities and gaps with expected findings metadata.
- Adversarial repositories designed to bypass naive static checks.
- Public benchmarks where applicable and license-compatible.
- Internal gold sets reviewed by humans.
- Shadow human review comparing scanner output to expert findings.
- Regression tests after analyzer and rule changes.
- Deterministic re-run checks.

## Validation Layers

1. Static unit validation: individual analyzers and core modules produce expected output for controlled input.
2. Seeded fixture validation: known seeded issues are detected and mapped to rule IDs.
3. Adversarial validation: intentionally misleading or evasive repositories still produce findings or gaps.
4. Gold set validation: human-reviewed repositories establish ground truth and separate detectable static findings from non-detectable expert judgment.
5. Portfolio gold set aggregation: multiple comparison reports are aggregated by scanner version, ruleset version, profile, domain, and rule family.
6. Validation trend gates: portfolio reports are compared across scanner and ruleset versions to detect reliability regression.
7. Pilot validation: production-like review measures preparation acceleration, reviewer agreement, top blocker agreement, and critical misses.

## Evidence Required For Validation

Every validation run should preserve:

- Suite name and version.
- Fixtures scanned.
- Expected findings.
- Detected expected findings.
- Missed expected findings.
- Unexpected findings.
- Precision and recall.
- Critical miss rate.
- Evidence traceability.
- Determinism result.
- Validation report hash or file path where applicable.
- Detectable versus non-detectable human findings for gold sets.
- Scanner-only material findings requiring triage.
- Scanner-only triage labels before calculating material precision.
- Scanner version and ruleset version for trend tracking.
- Calibration decision logs when rules, severities, confidence policies, or report compression are changed.
- Trend reports comparing baseline and candidate portfolio validation reports.
- Gate policies with thresholds approved by AppSec, CISO, CTO, or delegated assurance owners.

## Pass / Fail Philosophy

Validation should be conservative:

- Critical expected findings must not be missed.
- Determinism failures fail the validation run.
- Material findings must have traceable evidence.
- Misleading documentation must not suppress real code, configuration, supply chain, data, or operations gaps.
- Unknown evidence must remain unknown or become a gap where required.
- Scanner-only findings require reviewer triage before being counted as false positives.
- Non-detectable human findings must not reduce scanner recall.
- Portfolio metrics must remain tied to scanner version and ruleset version.
- Calibration changes must be logged with evidence and approval role.
- Blocking validation regressions must prevent release until reviewed or remediated.
- Trend comparison detects measured regression; it does not prove product quality by itself.

## Expert Review Boundary

Validation proves scanner behavior. It does not prove that the scanner can replace experts.

Human reviewers still own:

- Final risk judgment.
- Business context.
- Legal interpretation.
- Privacy impact.
- SOX control determination.
- Production approval.
- Risk acceptance.

## Regression Policy

After each major ruleset or analyzer version:

- Re-run seeded validation.
- Re-run adversarial validation.
- Re-run determinism checks.
- Compare against previous validation reports.
- Investigate critical misses and material recall drops.
- Update expected findings only when rule behavior intentionally changes and the change is reviewed.
