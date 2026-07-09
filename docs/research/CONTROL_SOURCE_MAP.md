# Control Source Map

This document maps the scanner's assurance domains to real-world enterprise security, SaaS assurance, secure SDLC, supply chain, AI governance, vendor review, and operational review practices.

The scanner aligns to these sources as design inputs. It does not certify compliance, produce an attestation, replace audit work, or claim conformance to any external framework.

## Product Constraints

- Local-first: all analysis runs on local source and evidence.
- Deterministic: the same input and rules produce the same evidence.
- Offline-capable: no external service is required during scanning.
- Non-AI: no LLM, model inference, embedding, or cloud AI call is used.
- Evidence-first: claims must be backed by local files, metadata, analyzer output, or explicit absence of required evidence.
- Conservative by default: missing enterprise evidence becomes a gap, not an inferred pass.
- English-only: generated artifacts and user-facing text must be in English.

## Source Map

| Domain | Why The Domain Matters | External Source / Framework | Scanner Should Detect | Evidence To Collect | Final Report | Deep Evidence Only |
|---|---|---|---|---|---|---|
| Secure SDLC | Enterprise reviewers need evidence that software was built with repeatable security practices, ownership, review, and remediation discipline. | NIST SSDF SP 800-218, OWASP SAMM | Missing owner metadata, missing test evidence, missing CI/CD, missing secure build/release evidence, missing remediation paths | Inventory, source metadata, ownership files, CI/CD files, test files, rule evaluation results | SDLC readiness status, blocking gaps, required remediation | Full file inventory, analyzer metrics, all low-level missing evidence checks |
| Application Security | Application flaws can create direct confidentiality, integrity, and availability risk. | OWASP ASVS, OWASP Top 10, CIS Controls | Secrets, unsafe code patterns, risky configuration, weak transport/security indicators, insecure deserialization, command/SQL injection patterns | Finding records with file path, line where available, safe snippet, rule ID, severity, confidence | Critical and high application security blockers, remediation owners | Full pattern matches, analyzer result JSON, normalized findings |
| Software Assurance Maturity | Assurance maturity is not only bug detection. It includes governance, design, implementation, verification, deployment, and operations practices. | OWASP SAMM, NIST SSDF | Presence or absence of governance, architecture, implementation, verification, deployment, and operations artifacts | Control context, signal set, claims, gap explanations, acceptance matrix | Domain matrix and concise gaps | Raw signal list, rule contract validation, evidence graph |
| Supply Chain / SBOM | Dependencies, lock files, binary artifacts, vendored code, and provenance affect trust in the delivered package. | SLSA, OWASP CycloneDX, SPDX, NIST SSDF | Missing lock files, unpinned dependencies, local SBOM evidence, binary/archive artifacts, vendored dependencies | Dependency manifests, lock files, local SBOM-style evidence, component/license metadata, artifact inventory | Supply chain status, high-risk dependency/package blockers | Full component inventory, all dependency records, graph nodes |
| Code Quality / Maintainability | Maintainability affects long-term ownership, security fix velocity, and production change risk. | CIS Controls as cyber hygiene input, OWASP SAMM implementation/verification practices | Large files, long files, weak modularity indicators, missing tests, hardcoded paths | File metrics, maintainability findings, test structure signals | Maintainability status and material remediation | Detailed file metrics and low-level maintainability findings |
| Vendor Security Review | Enterprise vendor intake commonly asks whether the product has ownership, security controls, SDLC evidence, data handling, availability, and support evidence. | CSA CAIQ, SOC 2 Trust Services Criteria, NIST CSF | Missing accountability, support model, security documentation, operational evidence, data-flow evidence, control-relevant findings | Decision packet, control context, report, acceptance matrix, source metadata | Concise vendor-review-ready decision summary | Full JSON evidence package for reviewer drill-down |
| SaaS Trust / Compliance | SaaS buyers evaluate security, availability, confidentiality, processing integrity, and privacy control posture. | AICPA SOC 2 Trust Services Criteria, CSA CCM/CAIQ, NIST CSF | Security gaps, availability/operations gaps, privacy/data indicators, processing integrity/SOX indicators, owner gaps | Findings, operational readiness evidence, data/SOX signals, confidence summary | Trust-facing domain matrix and limitations | Raw analyzer output, evidence graph, all claims and gaps |
| Operations / Availability | Production use requires monitoring, health checks, incident response, backup/restore, runtime configuration, and support ownership. | NIST CSF Govern/Identify/Protect/Detect/Respond/Recover, CIS Controls, SOC 2 Availability criteria | Missing logging, monitoring, health checks, backup/restore, incident response, runtime config separation, support model | Operational analyzer metrics, docs, config files, detected runtime patterns | Operations status, blockers, remediation | Detailed operational counters and evidence snippets |
| Data Protection | Sensitive data indicators and data files can create privacy, retention, access control, and governance obligations. | NIST CSF, SOC 2 Confidentiality/Privacy criteria, CSA CAIQ | Sensitive keywords, data files, local database artifacts, missing data classification, missing data-flow docs | Data-risk findings, data files, data-flow evidence, classification docs where present | Data protection review status and mandatory review triggers | Raw sensitive term counts, file list, low-confidence keyword evidence |
| AI / Model Risk | Hidden AI/model usage creates provider, model, prompt, data-flow, privacy, explainability, and governance risk. | NIST AI RMF, CSA AI-CAIQ, OWASP CycloneDX AI/ML-BOM concepts | AI/ML dependencies, model artifacts, external AI endpoints, prompts, embeddings, vector databases, missing AI declaration | Hidden AI detector output, AI/model findings, signal list, claims, gap explanations | AI/model risk blockers and required approvals | Full indicators, model artifact inventory, graph edges |
| License / Legal Risk | Open source and proprietary license obligations can affect use, distribution, procurement, and enterprise approval. | SPDX License List, OpenChain ISO/IEC 5230, CycloneDX | Missing repository license, missing notices, unknown/restrictive/copyleft/custom licenses, binary/vendored artifacts without provenance | Local SBOM-style evidence, component license metadata, license findings, repository license files | License review status and legal blockers | Full component list, license classifications, raw dependency records |
| Enterprise Handover | A codebase must be transferable to operations, security, architecture, and business owners before enterprise adoption. | NIST SSDF, OWASP SAMM, CSA CAIQ, SOC 2 control description practices | Missing runbook, deployment guide, rollback, architecture overview, support model, changelog, ownership | Delivery readiness metrics, documentation inventory, owner evidence, acceptance matrix | Handover readiness summary and top missing artifacts | Full documentation file inventory and missing artifact checks |

## Report Boundary

The final report should summarize the decision, domain matrix, top blockers, required remediation, evidence confidence, and limitations. It should not attempt to reproduce every analyzer detail. Full evidence belongs in JSON artifacts and HTML drill-down sections.

## Deep Evidence Boundary

Deep evidence includes:

- Raw analyzer result JSON.
- Full file inventory.
- Full signal list.
- Rule contract validation.
- Evidence graph nodes and edges.
- Full claims and gaps.
- Local SBOM-style evidence.
- Detailed finding records.

Deep evidence supports auditability, replay, reviewer drill-down, and future automation. It is not the primary executive or vendor-review packet.

## Reference Sources

- NIST SP 800-218 Secure Software Development Framework: https://csrc.nist.gov/pubs/sp/800/218/final
- NIST Cybersecurity Framework: https://www.nist.gov/cyberframework
- NIST AI Risk Management Framework: https://www.nist.gov/itl/ai-risk-management-framework
- OWASP SAMM: https://owasp.org/www-project-samm/
- OWASP ASVS: https://owasp.org/www-project-application-security-verification-standard/
- OWASP CycloneDX: https://cyclonedx.org/
- SLSA: https://slsa.dev/
- SPDX: https://spdx.dev/
- SPDX License List: https://spdx.org/licenses
- CSA CAIQ: https://cloudsecurityalliance.org/artifacts/star-level-1-security-questionnaire-caiq-v4
- CSA AI-CAIQ: https://cloudsecurityalliance.org/artifacts/ai-consensus-assessments-initiative-questionnaire-ai-caiq
- AICPA Trust Services Criteria: https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022
- CIS Critical Security Controls: https://www.cisecurity.org/controls/v8
- OpenChain ISO/IEC 5230: https://openchainproject.org/license-compliance
