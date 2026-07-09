# Enterprise Acceptance Taxonomy

This taxonomy defines the scanner's enterprise acceptance domains and how many local signals are compressed into a concise technical decision.

The taxonomy aligns to common enterprise practices from secure SDLC, application security, software assurance maturity, supply chain, SaaS/vendor review, operations, data protection, AI governance, and open source license compliance. It does not certify compliance with any framework.

## Status Values

- Passed: no material gap was detected and evidence confidence is sufficient.
- Conditional: remediation is required, but no blocker or mandatory-review condition was detected.
- Mandatory Review: a human control owner must review before approval.
- Blocked: the domain prevents approval under the selected profile.
- Unknown: evidence is insufficient to make a positive claim.

## Domain Taxonomy

### Architecture

- Purpose: Verify that the codebase has understandable structure, ownership boundaries, entry points, and reviewable architecture.
- Evidence sources: file inventory, source roots, entry points, architecture documentation, project structure analyzer, claims, evidence graph.
- Required controls: clear entry point, recognizable source structure, architecture overview for strict profiles, no mixed unrelated applications without documentation.
- Blocking conditions: no clear entry point for production-critical use, committed local database artifacts, severe structure ambiguity affecting review.
- Mandatory review conditions: multiple application roots, mixed stacks, architecture ownership gaps.
- Typical remediation: document architecture, identify entry points, separate unrelated applications, add ownership metadata.
- Confidence logic: high when source structure and docs agree; medium when only file patterns exist; low when structure is ambiguous.
- Report compression rule: show only architecture status and top structural blockers; keep full file structure in inventory JSON.

### Platform

- Purpose: Verify runtime, package, build, and configuration posture.
- Evidence sources: package managers, config files, build files, environment templates, runtime configuration findings.
- Required controls: build/package descriptor, sanitized config template, environment separation evidence, reproducible setup.
- Blocking conditions: committed production secrets/configuration, high-risk runtime configuration exposure.
- Mandatory review conditions: missing runtime configuration separation in strict profiles, unclear build/runtime ownership.
- Typical remediation: add environment template, document runtime configuration, remove committed runtime files, define build commands.
- Confidence logic: high when manifests/config templates exist; medium for inferred runtime from file extensions; low when no package/build evidence exists.
- Report compression rule: summarize runtime/config readiness; leave all config-file details in deep evidence.

### Interfaces

- Purpose: Identify externally reachable or integration-facing surfaces that may need authentication, authorization, and data-flow review.
- Evidence sources: code patterns, route indicators, API files, documentation, future interface analyzers.
- Required controls: documented interface purpose, auth expectations, data-flow evidence for strict profiles.
- Blocking conditions: critical security issue on exposed interface, unauthenticated sensitive interface when detectable.
- Mandatory review conditions: API indicators without architecture or data-flow documentation.
- Typical remediation: document interface contracts, add auth evidence, add data-flow notes, review external integrations.
- Confidence logic: high when explicit routes or framework metadata are detected; medium for naming patterns; low when no interface analyzer evidence exists.
- Report compression rule: show Unknown when interface evidence is insufficient instead of inferring no interfaces.

### Database and Storage

- Purpose: Verify whether storage artifacts or data persistence create recovery, retention, and data governance obligations.
- Evidence sources: data files, local database files, operational data storage metrics, data-flow docs, backup/restore docs.
- Required controls: storage inventory, backup/restore evidence, data classification, retention and recovery ownership.
- Blocking conditions: committed database with sensitive or finance context, production-critical storage without recovery evidence.
- Mandatory review conditions: data storage without backup/restore, unclear storage classification.
- Typical remediation: remove local database files, add sanitized fixtures, document storage and recovery, add classification.
- Confidence logic: high for explicit database/data files; medium for dependency or config indicators; low when storage cannot be determined.
- Report compression rule: show storage status and recovery gap; keep file list in inventory and operational evidence.

### External Egress

- Purpose: Identify outbound connections that may create vendor, data transfer, privacy, and availability risk.
- Evidence sources: URL/API indicators, AI provider indicators, network call findings, future egress analyzers.
- Required controls: egress inventory, timeout/retry evidence, vendor/data-flow documentation, approval where required.
- Blocking conditions: external AI API use without declaration in strict profiles, critical unreviewed data egress.
- Mandatory review conditions: network calls without timeout evidence, egress without data-flow docs.
- Typical remediation: document endpoints, add timeouts, add vendor review, add data-flow and approval records.
- Confidence logic: high for explicit URLs/providers; medium for network client patterns; low when no egress analyzer is available.
- Report compression rule: show top egress risk only; keep full endpoint evidence in analyzer output.

### Application Security

- Purpose: Detect source-level and configuration-level security risks.
- Evidence sources: secrets analyzer, SAST-style analyzer, config analyzer, normalized findings.
- Required controls: no hardcoded secrets, no critical unsafe code patterns, safe configuration defaults, remediation ownership.
- Blocking conditions: hardcoded secrets, private keys, critical injection/deserialization/execution patterns, disabled TLS verification.
- Mandatory review conditions: high security findings without complete remediation evidence.
- Typical remediation: remove secrets, rotate credentials, fix unsafe code, document compensating controls, re-run scan.
- Confidence logic: high for direct code/config evidence; medium for pattern-only findings; low for weak keyword-only evidence.
- Report compression rule: show critical and high security blockers first; suppress low-level pattern volume into deep evidence.

### Supply Chain

- Purpose: Assess dependency integrity, reproducibility, provenance, and artifact hygiene.
- Evidence sources: dependency manifests, lock files, local SBOM-style evidence, binary/archive findings, vendored directories.
- Required controls: lock files, pinned dependencies, SBOM evidence, no unmanaged binaries or vendored code without provenance.
- Blocking conditions: critical supply chain finding, severe unreviewed binary/provenance issue in strict profile.
- Mandatory review conditions: missing lock files, unpinned dependencies, vendored dependencies, unmanaged binary artifacts.
- Typical remediation: commit lock files, pin dependencies, remove binaries, document provenance, regenerate SBOM evidence.
- Confidence logic: high with manifests and lock files; medium with manifest only; low when dependencies cannot be enumerated.
- Report compression rule: summarize reproducibility and artifact risk; keep full component data in SBOM/dependency JSON.

### License

- Purpose: Identify open source and proprietary license obligations that may affect enterprise use or distribution.
- Evidence sources: local SBOM-style evidence, package metadata, repository license files, third-party notices, SPDX license IDs.
- Required controls: repository license, third-party notices, known dependency licenses, review of restrictive/custom/copyleft licenses.
- Blocking conditions: restrictive license requiring block under strict policy, severe unknown license posture for critical components.
- Mandatory review conditions: missing, unknown, ambiguous, strong copyleft, custom, or proprietary license evidence.
- Typical remediation: add license metadata, add notices, replace dependency, obtain legal approval.
- Confidence logic: high for explicit local metadata; medium for partial package metadata; low when license evidence is absent.
- Report compression rule: show legal-review blockers and counts; keep component-level license inventory in deep evidence.

### Data Protection

- Purpose: Detect sensitive data indicators and data handling evidence gaps.
- Evidence sources: data-risk analyzer, data files, data-flow docs, classification docs, operational findings.
- Required controls: data classification, sanitized test data, data-flow documentation, sensitive logging controls.
- Blocking conditions: sensitive data logging, committed sensitive data with critical context, data exposure indicators.
- Mandatory review conditions: sensitive indicators without classification or data-flow evidence.
- Typical remediation: remove sensitive data, sanitize fixtures, add classification, mask logs, document data flow.
- Confidence logic: high for explicit data files or direct code evidence; medium for repeated keywords; low for isolated keyword-only evidence.
- Report compression rule: summarize sensitivity and required review; keep term-level evidence in JSON.

### SOX / Finance

- Purpose: Identify finance/control indicators that may require SOX, ITGC, or business control review.
- Evidence sources: SOX detector, finance terms, data-flow docs, audit logging evidence, approval workflow docs.
- Required controls: SOX impact assessment, audit logging evidence, access/control documentation, change management evidence.
- Blocking conditions: critical finance data/storage/control gaps under finance profile.
- Mandatory review conditions: finance indicators without SOX impact assessment or audit/control documentation.
- Typical remediation: add SOX impact note, identify control owners, document audit logging, obtain SOX/ITGC review.
- Confidence logic: high when finance docs or explicit SOX terms are present; medium for keyword matches; low for isolated terms.
- Report compression rule: show SOX review requirement and missing controls; keep matched terms in deep evidence.

### AI / Model Risk

- Purpose: Detect hidden or undeclared AI/model usage and required governance evidence.
- Evidence sources: AI/model detector, dependency manifests, model artifacts, AI provider endpoints, prompts, embeddings/vector indicators.
- Required controls: AI declaration, model/provider inventory, data-flow documentation, governance approval, monitoring where applicable.
- Blocking conditions: external AI API or local model artifact without declaration/approval in strict profiles.
- Mandatory review conditions: AI/ML dependencies, vector database use, embeddings, prompt/model indicators without complete governance evidence.
- Typical remediation: declare AI usage, add provider/model inventory, document data flow, obtain Security Architecture, Data Governance, and CISO review.
- Confidence logic: high for explicit provider endpoints or model artifacts; medium for dependencies; low for weak prompt keywords.
- Report compression rule: place hidden AI/model blockers near the top; keep full indicator list in detector output.

### Operations

- Purpose: Verify production supportability, observability, recovery, incident response, and runtime readiness.
- Evidence sources: operational analyzer, runbooks, monitoring docs, health checks, backup/restore docs, incident response docs.
- Required controls: logging, monitoring, health checks for production, backup/restore where storage exists, incident response, support model.
- Blocking conditions: production-critical system without health check, committed runtime secrets, critical operational data risk.
- Mandatory review conditions: data storage without recovery procedure, missing audit logging for finance profile, missing support model.
- Typical remediation: add logging/monitoring, add health endpoints, document backup/restore, add incident response and support ownership.
- Confidence logic: high for docs plus code/config indicators; medium for docs only or code only; low when operational evidence is missing.
- Report compression rule: show operations readiness and top missing controls; keep counters and raw docs inventory in deep evidence.

### Delivery

- Purpose: Verify enterprise handover readiness and repeatable deployment/release evidence.
- Evidence sources: delivery readiness analyzer, documentation inventory, CI/CD files, deployment/rollback/runbook docs.
- Required controls: deployment guide, rollback, runbook, support model, changelog, tests, data-flow docs where required.
- Blocking conditions: production-critical missing rollback, severe missing handover evidence under strict profile.
- Mandatory review conditions: missing data-flow documentation for finance/SOX context, missing runbook/support ownership.
- Typical remediation: add deployment guide, rollback, runbook, support model, changelog, test evidence, data-flow docs.
- Confidence logic: high for explicit docs; medium for script evidence; low when only filename hints exist.
- Report compression rule: list only missing enterprise handover artifacts that affect approval.

### Maintainability

- Purpose: Assess whether the codebase can be safely owned, reviewed, and changed over time.
- Evidence sources: maintainability analyzer, file metrics, test indicators, modularity signals.
- Required controls: manageable file size, test structure, clear module boundaries, limited hardcoded paths.
- Blocking conditions: maintainability alone usually should not block unless combined with critical security/operations risk.
- Mandatory review conditions: severe maintainability indicators in strict profile or ownership handoff context.
- Typical remediation: add tests, split large files, document modules, remove hardcoded paths.
- Confidence logic: high for measured file metrics; medium for structural patterns; low when language support is limited.
- Report compression rule: summarize maintainability risk and top remediation only.

### Governance

- Purpose: Verify accountability, rulebook integrity, baseline control protection, and approval workflow evidence.
- Evidence sources: owner files, rulebook governance findings, disabled baseline rule requests, rule contract validation, system dossier.
- Required controls: owner metadata, immutable baseline rules, custom rule uniqueness, approval evidence for baseline disablement, valid rule contracts.
- Blocking conditions: disabled critical baseline rule without complete approval evidence, missing owner metadata in strict blocking profiles, scan integrity failure.
- Mandatory review conditions: custom rule attempted baseline override, missing accountability, rule contract validation errors.
- Typical remediation: add owners, remove invalid custom overrides, complete risk acceptance evidence, fix rule contracts, re-run scan.
- Confidence logic: high for explicit governance files and rulebook validation; low when ownership cannot be established.
- Report compression rule: show governance blockers and rulebook integrity status; keep full validation details in JSON.

## Compression Algorithm

The scanner compresses many local signals into a concise decision:

1. Normalize local evidence into signals.
2. Build evidence-backed claims.
3. Evaluate controls and rules against profile and context.
4. Generate gaps for missing or insufficient evidence.
5. Score confidence using deterministic evidence strength.
6. Map findings and gaps to acceptance domains.
7. Apply decision precedence: blockers, mandatory review, domain status, then score.
8. Produce a short decision packet with references to deep evidence.

The algorithm must preserve traceability from every compressed report item back to evidence IDs, findings, rules, claims, gaps, or graph nodes.

## Reference Sources

- NIST SSDF SP 800-218: https://csrc.nist.gov/pubs/sp/800/218/final
- NIST Cybersecurity Framework: https://www.nist.gov/cyberframework
- OWASP ASVS: https://owasp.org/www-project-application-security-verification-standard/
- OWASP SAMM: https://owasp.org/www-project-samm/
- SLSA: https://slsa.dev/
- OWASP CycloneDX: https://cyclonedx.org/
- SPDX: https://spdx.dev/
- OpenChain ISO/IEC 5230: https://openchainproject.org/license-compliance
- NIST AI RMF: https://www.nist.gov/itl/ai-risk-management-framework
- CSA AI-CAIQ: https://cloudsecurityalliance.org/artifacts/ai-consensus-assessments-initiative-questionnaire-ai-caiq
- AICPA Trust Services Criteria: https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022
