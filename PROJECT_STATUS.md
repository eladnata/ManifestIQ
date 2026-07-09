# Project Status

Repository reality audit date: 2026-07-09

This checkpoint reflects the repository state verified from local code, rules, profiles, tests, generated evidence, and the sample scan. It does not rely on prior conversation summaries.

## 1. Current Product Name

Enterprise White-Box Code Assurance Scanner.

Current product framing in `MASTER_SPEC.md`: a deterministic expert-amplification platform for enterprise system assurance.

## 2. Product Constraints

Verified product constraints from the specifications:

- Local-first.
- Deterministic.
- Offline-capable.
- Non-AI.
- No LLM, embedding, vector search, model inference, cloud dependency, or telemetry.
- Evidence-first.
- Conservative by default.
- English-only user-facing artifacts.
- Does not replace CISO, CTO, AppSec, Architecture, DevSecOps, ITGC, SOX, Legal, Privacy, or Security reviewers.
- Produces decision preparation and evidence, not autonomous final approval.

## 3. Implemented Analyzers

The orchestrator runs the following analyzer IDs. The sample `finance-sox` scan showed these analyzers as `completed`:

| Analyzer ID | Module | Sample Status | Sample Finding Count | Notes |
|---|---|---:|---:|---|
| `secrets` | `scanner/analyzers/secrets.py` | completed | 3 | Detects credential-like patterns. |
| `dependencies` | `scanner/analyzers/dependencies.py` | completed | 3 | Parses local dependency manifests and lock-file presence. |
| `sast` | `scanner/analyzers/sast.py` | completed | 2 | Deterministic pattern-based risky code checks. |
| `config` | `scanner/analyzers/config_scan.py` | completed | 6 | Detects risky configuration patterns. |
| `hidden_ai_model_detector` | `scanner/analyzers/hidden_ai_model_detector.py` | completed | 0 | Detects AI dependencies, provider/API indicators, vector DBs, and model artifacts. |
| `documentation` | `scanner/analyzers/documentation.py` | completed | 15 | Checks required documentation evidence by profile. |
| `data_risk` | `scanner/analyzers/data_risk.py` | completed | 3 | Detects sensitive data files and keywords. |
| `sox_detector` | `scanner/analyzers/sox_detector.py` | completed | 1 | Detects finance/SOX terms. |
| `maintainability` | `scanner/analyzers/maintainability.py` | completed | 2 | Checks file size, long files, tests, and logging indicators. |
| `operational` | `scanner/analyzers/operational.py` | completed | 7 | Checks logging, monitoring, health, backup, incident, runtime config, network timeout, and related operational indicators. |
| `licenses` | `scanner/analyzers/licenses.py` | completed | 6 | Builds local SBOM-style evidence and license findings. |
| `project_structure` | `scanner/analyzers/project_structure.py` | completed | 5 | Checks entry points, source/test structure, CI/CD, owner metadata, binaries, archives, local DBs, and repository hygiene. |
| `delivery_readiness` | `scanner/analyzers/delivery_readiness.py` | completed | 14 | Checks deployment, rollback, runbook, architecture, support, data-flow, SOX docs, and handover evidence. |

Core inventory is implemented in `scanner/core/inventory.py` and writes `file-inventory.json`; it is not listed as an orchestrator analyzer.

## 4. Skipped / Roadmap Analyzers

The sample scan showed one placeholder analyzer:

| Analyzer ID | Module | Sample Status | Metrics |
|---|---|---|---|
| `architecture_signals` | `scanner/analyzers/architecture_signals.py` | skipped | `TODO: implement deterministic architecture signal checks` |

No other orchestrator analyzer returned `skipped` in the sample scan.

## 5. Rule Inventory

Rulebook loader result:

- Baseline rules: 83.
- Custom rules: 0.
- Disabled baseline rule requests: 0.
- Governance findings from rulebook loading: 0.
- Ruleset hash during audit: `8eee3656023d0cff02e4e161131e4736b57966cbf9cf4760a8a97f456de6066e`.

Rule files and counts:

| Rule File | Rule Count |
|---|---:|
| `rules/ai_model_risk.yml` | 4 |
| `rules/architecture.yml` | 12 |
| `rules/configuration.yml` | 5 |
| `rules/data_sox.yml` | 3 |
| `rules/delivery_readiness.yml` | 12 |
| `rules/documentation.yml` | 1 |
| `rules/governance.yml` | 3 |
| `rules/licenses.yml` | 15 |
| `rules/maintainability.yml` | 3 |
| `rules/operational.yml` | 15 |
| `rules/scan_integrity.yml` | 1 |
| `rules/security.yml` | 6 |
| `rules/supply_chain.yml` | 3 |

Rules by category:

| Category | Rule Count |
|---|---:|
| AI Model Risk | 4 |
| Architecture | 12 |
| Configuration | 7 |
| Data Protection | 3 |
| Documentation | 1 |
| Governance | 6 |
| License Risk | 7 |
| Maintainability | 3 |
| Operations | 24 |
| SOX | 1 |
| Scan Integrity | 1 |
| Security | 6 |
| Supply Chain | 8 |

Baseline/read-only status:

- All 83 loaded rules are baseline rules.
- All loaded baseline rules are marked `baseline: true`.
- All loaded baseline rules are marked `editable: false`.
- All loaded baseline rules are marked `disable_requires_approval: true`.
- No custom rule files are currently loaded from `rules/custom/`.

## 6. Profile Inventory

Profile files:

- `profiles/ai-enabled.yml`
- `profiles/department-use.yml`
- `profiles/enterprise.yml`
- `profiles/finance-sox.yml`
- `profiles/production-critical.yml`
- `profiles/sandbox.yml`
- `profiles/team-use.yml`

Profile-required analyzers from profile YAML:

| Profile | Required Analyzers In YAML |
|---|---|
| `sandbox` | None specified. |
| `team-use` | None specified. |
| `department-use` | None specified. |
| `enterprise` | `secrets`, `dependencies`, `sast`, `config`, `hidden_ai_model_detector`, `documentation`, `data_risk`, `sox_detector`, `maintainability`, `operational`, `licenses`, `project_structure`, `delivery_readiness` |
| `finance-sox` | `secrets`, `dependencies`, `sast`, `config`, `hidden_ai_model_detector`, `documentation`, `data_risk`, `sox_detector`, `maintainability`, `operational`, `licenses`, `project_structure`, `delivery_readiness` |
| `ai-enabled` | `secrets`, `dependencies`, `sast`, `config`, `hidden_ai_model_detector`, `documentation`, `data_risk`, `maintainability`, `operational`, `licenses`, `project_structure`, `delivery_readiness` |
| `production-critical` | `secrets`, `dependencies`, `sast`, `config`, `hidden_ai_model_detector`, `documentation`, `data_risk`, `sox_detector`, `maintainability`, `operational`, `licenses`, `project_structure`, `delivery_readiness` |

Runtime note: `scanner/core/orchestrator.py` currently runs the same analyzer list for every profile, including the skipped `architecture_signals` placeholder. Profile YAML `required_analyzers` is documented metadata and is also reflected in the analyzer capability registry, but the orchestrator does not currently filter analyzers by profile.

## 7. Evidence Outputs

The audited sample scan generated 32 manifest entries:

- `analyzer-capabilities.json`
- `architecture_signals-results.json`
- `claims.json`
- `confidence-summary.json`
- `config-results.json`
- `control-context.json`
- `data_risk-results.json`
- `delivery_readiness-results.json`
- `dependencies-results.json`
- `documentation-results.json`
- `enterprise-acceptance-matrix.json`
- `evidence-graph.json`
- `file-inventory.json`
- `final-report.html`
- `findings.json`
- `gaps.json`
- `hidden_ai_model_detector-results.json`
- `licenses-results.json`
- `local-sbom.json`
- `maintainability-results.json`
- `operational-results.json`
- `project_structure-results.json`
- `rule-contract-validation.json`
- `rule-evaluation-results.json`
- `sast-results.json`
- `scan-summary.json`
- `scoring-results.json`
- `secrets-results.json`
- `signals.json`
- `source-metadata.json`
- `sox_detector-results.json`
- `system-dossier.json`

`manifest.json` and `sha256.txt` are also generated by `build_manifest`, but they are excluded from the manifest file list by design.

SBOM verification:

- `local-sbom.json` exists after the sample scan.
- `local-sbom.json` is included in `manifest.json`.
- The `licenses` analyzer reported `local_sbom_generated: true` and `local_sbom_path: local-sbom.json`.

## 8. Report Coverage

The generated `output/evidence-package/final-report.html` contains the requested report sections:

| Required Section | Present |
|---|---|
| Hidden AI / model risk | Yes: `Undeclared AI / Model Risk` |
| Project structure | Yes: `Project Structure Assessment`, `Project Structure Findings` |
| Delivery readiness | Yes: `Delivery Readiness Assessment`, `Missing Enterprise Delivery Artifacts` |
| Operational readiness | Yes: `Operational Readiness Assessment` |
| License / SBOM | Yes: `License and SBOM Assessment` |
| Disabled baseline rules | Yes: `Disabled Baseline Rules` |
| Analyzer status | Yes: `Analyzer Status` |
| Blocking gates | Yes: `Blocking Gates` |

The report also includes assurance sections for control context, signals, claims, confidence, gaps, evidence graph, acceptance matrix, system dossier, rule contract validation, limitations, detailed findings, and failed/skipped analyzer warnings.

## 9. Test Results

Command run:

```bash
python -m pytest
```

Result:

```text
49 passed in 30.81s
```

Test files executed:

- `tests/test_smoke.py`
- `tests/test_validation.py`

## 10. Sample Scan Result

Command run:

```bash
python -m scanner scan-folder --path tests/sample_projects/insecure-python --output output --profile finance-sox
```

Result:

| Field | Value |
|---|---|
| Scan ID | `scan_20260709_093633` |
| Profile | `finance-sox` |
| Decision | `Not Approved` |
| Score | 41 |
| Critical findings | 4 |
| High findings | 49 |
| Medium findings | 14 |
| Evidence SHA256 | `2bf99f4390b30da1b129c0336618d8e0034413cdfdc697d67d2b01240d85431f` |
| Report | `output/evidence-package/final-report.html` |

Analyzer statuses in the sample scan:

- Completed: `secrets`, `dependencies`, `sast`, `config`, `hidden_ai_model_detector`, `documentation`, `data_risk`, `sox_detector`, `maintainability`, `operational`, `licenses`, `project_structure`, `delivery_readiness`.
- Skipped: `architecture_signals`.
- Failed: none.

## 11. Known Limitations

- `architecture_signals` is still a placeholder and returns `skipped`.
- Profile YAML required analyzers are not used by the orchestrator to select analyzers; all orchestrator analyzers run for every profile.
- `architecture_signals-results.json` is generated with skipped status, so the report correctly shows a skipped analyzer warning.
- Interface/API topology, external egress beyond currently detected AI/provider and network-call patterns, deep architecture inference, split-secret detection, and content-quality validation for misleading documentation remain limited.
- Validation precision in adversarial runs can be low because the scanner intentionally reports additional material findings beyond seeded expected findings.
- The HTML report is evidence-rich and lengthy; it does not yet fully implement the short decision packet model described in documentation.

## 12. Verified Gaps

Verified gaps from this audit:

- Remaining placeholder: `scanner/analyzers/architecture_signals.py`.
- No custom rules are present in the repository at audit time.
- No disabled baseline rule file is present at audit time.
- Sandbox, team-use, and department-use profiles do not declare `required_analyzers`.
- Strict profiles declare required analyzers, but runtime analyzer execution is currently fixed in `ANALYZERS`.
- The report has the requested sections, but the final human-facing report is not yet compressed to the documented 1-page summary / 1-page matrix / 1-page blockers model.

## 13. Recommended Next Phase

Recommended next phase: implement deterministic architecture/interface/egress signal depth and align the report with the concise decision packet model.

Justification:

- The only skipped analyzer is `architecture_signals`, making it the clearest implementation gap.
- Several assurance domains currently depend on indirect findings rather than rich system topology signals.
- The evidence package is strong and complete, but the human-facing report is still verbose compared to the documented decision packet target.
- Filling architecture/interface/egress signals would improve control context, evidence graph quality, acceptance matrix confidence, and custom rule expressiveness.

Suggested order:

1. Implement `architecture_signals` with deterministic detection for interfaces, routes, services, storage references, external egress indicators, and architecture documentation linkage.
2. Add tests and adversarial fixtures for architecture/interface/egress cases.
3. Preserve current deep evidence outputs.
4. Add a concise decision packet output or compressed report mode without removing existing drill-down evidence.

## 14. Go / No-Go Recommendation For Continuing Development

Go.

Rationale:

- The current test suite passes.
- The sample scan runs end to end.
- Evidence packaging works and includes the local SBOM.
- Baseline rules are loaded as read-only and protected.
- Report sections requested by the audit exist.
- The remaining placeholder is explicit and visible in evidence.

Conditions for the next phase:

- Do not add UI yet.
- Do not remove deep evidence outputs.
- Keep the system local, deterministic, offline-capable, non-AI, conservative, evidence-first, and English-only.
- Prioritize closing the `architecture_signals` placeholder and improving concise decision readiness.
