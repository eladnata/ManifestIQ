# Assurance Engine Model

This document defines the internal model for the assurance engine. The scanner must remain local-first, deterministic, offline-capable, non-AI, evidence-first, conservative by default, and English-only.

The engine aligns to enterprise secure SDLC, software assurance, supply chain, vendor review, SaaS trust, operations, data protection, AI governance, and license review practices. It does not certify compliance with any external framework.

## Pipeline

```text
Raw Input
-> Signal Extraction
-> Evidence Graph
-> Claims
-> Control Evaluation
-> Gap Explanation
-> Confidence Scoring
-> Risk Compression
-> Decision Packet
-> Evidence Package
```

## Raw Input

Raw input is the local folder, archive, or repository checkout under review. The scanner must not transmit source code or evidence outside the local environment.

Raw input includes:

- Source files.
- Dependency manifests and lock files.
- Configuration files.
- Documentation.
- Ownership metadata.
- Build, test, CI/CD, and deployment artifacts.
- Local data-like files.
- Model artifacts or AI/provider indicators.

## Signal Model

A signal is a normalized fact produced by inventory or an analyzer.

Examples:

- `language.python.detected`
- `security.secret.detected`
- `delivery.runbook.missing`
- `license.local_sbom.generated`
- `ai.external_provider.detected`

Signals must be:

- Deterministic.
- Named consistently.
- Domain-tagged.
- Confidence-tagged.
- Traceable to analyzer output or inventory.
- Suitable for baseline and custom rule evaluation.

Signals are not conclusions. They are inputs to claims, gaps, controls, graph edges, and decision compression.

## Evidence Graph Model

The evidence graph links local evidence to the decision path.

Node types include:

- File
- Technology
- Component
- Interface
- Database
- Egress
- Data indicator
- Finding
- Claim
- Gap
- Rule
- Control
- Decision

Relationships include:

- `defines`
- `uses`
- `supports`
- `triggers`
- `requires`
- `lacks`
- `evidences`
- `blocks`
- `conditions`

The graph is machine-readable evidence, not a visualization requirement. It lets reviewers answer why a decision happened without reading every analyzer result.

## Claim Model

A claim is an evidence-backed statement derived from signals, findings, rule evaluations, or analyzer output.

Examples:

- The system appears to use Python.
- Local SBOM-style evidence was generated.
- Hidden AI or model usage indicators were detected.
- Backup/restore readiness could not be established from available evidence.

Claims must:

- Avoid overstatement.
- Include confidence.
- Include supporting evidence.
- Include limitations where evidence is weak or absent.
- Use `unknown` or low confidence when evidence is insufficient.

Claims are the bridge between low-level scanner output and human review language.

## Control Evaluation Model

Controls are rules evaluated against profile, control context, signals, and findings.

Control evaluation must support:

- Baseline rules.
- Custom rules.
- Profile applicability.
- Context applicability.
- Required analyzers.
- Required signals.
- Missing evidence behavior.
- Rule contract validation.

Older rules remain valid. Rule Contract v2 fields add optional behavior without breaking existing baseline rules.

## Gap Model

A gap explains what required evidence or control posture is missing and why it matters.

Gaps must include:

- Domain.
- Severity.
- Confidence.
- Detected evidence.
- Missing evidence.
- Enterprise impact.
- Required remediation.
- Related findings and rules.
- Decision impact.

Gap language must be deterministic and template-driven. The scanner should not infer intent, maturity, or certification status from weak evidence.

## Confidence Model

Confidence is deterministic and evidence-weighted.

Typical evidence strength:

- Direct code evidence: strong.
- Configuration evidence: strong to medium.
- Dependency manifest evidence: medium.
- Documentation evidence: medium.
- Multiple-source confirmation: increases confidence.
- Keyword-only evidence: lower confidence.
- Missing context: lowers confidence.

Confidence is not a probability. It is an explainable strength-of-evidence label used to prevent overclaiming.

## Risk Compression

The scanner may produce many findings, signals, claims, and graph edges. Human reviewers need a concise answer.

Risk compression reduces detailed evidence into:

- Final decision.
- Domain acceptance matrix.
- Top blocking reasons.
- Required remediation.
- Evidence and confidence summary.
- Limitations.

Compression must preserve traceability. Every compressed report item should point back to findings, rules, claims, gaps, or evidence artifacts.

## Decision Packet

The decision packet is the concise human-facing artifact. It should be short enough for CISO, CTO, AppSec, architecture, DevOps, procurement, and vendor-review users to consume quickly.

The packet should not replace deep evidence. It should summarize the decision and point to machine-readable artifacts for drill-down.

## Evidence Package

The evidence package is the complete audit trail.

It includes:

- Source metadata.
- File inventory.
- Analyzer results.
- Normalized findings.
- Signals.
- Analyzer capabilities.
- Control context.
- Rule contract validation.
- Claims.
- Confidence summary.
- Gaps.
- Evidence graph.
- Enterprise acceptance matrix.
- System dossier.
- Scoring results.
- Rule evaluation results.
- Report.
- Manifest and package hash.

## Custom Rules In The Same Pipeline

Custom rules must not become a separate path.

A custom rule should participate in:

- Rule loading.
- Rule contract validation.
- Profile applicability.
- Context applicability.
- Required analyzer validation.
- Required signal validation.
- Finding generation.
- Gap generation.
- Claims, when a claim template exists.
- Confidence summary.
- Acceptance matrix.
- Report compression.
- Evidence manifest.

This keeps baseline and custom controls consistent.

## Why The Engine Must Not Be A Loose Analyzer Collection

A loose analyzer collection produces isolated findings but cannot reliably answer enterprise review questions:

- What system context was inferred?
- What evidence supports each conclusion?
- Which missing evidence caused the decision?
- Which rule caused a blocker?
- Which domains are acceptable, conditional, blocked, or unknown?
- What must be remediated before approval?

The assurance engine turns analyzer output into a deterministic control flow. Analyzers provide facts. The engine provides context, claims, gaps, confidence, and decision compression.

## Reference Sources

- NIST SSDF SP 800-218: https://csrc.nist.gov/pubs/sp/800/218/final
- OWASP SAMM: https://owasp.org/www-project-samm/
- OWASP ASVS: https://owasp.org/www-project-application-security-verification-standard/
- SLSA: https://slsa.dev/
- OWASP CycloneDX: https://cyclonedx.org/
- NIST AI RMF: https://www.nist.gov/itl/ai-risk-management-framework
