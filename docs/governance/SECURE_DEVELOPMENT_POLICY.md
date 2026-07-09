# Secure Development Policy

## Purpose

This policy defines secure development expectations for the scanner itself. The scanner handles source code, evidence, findings, and reports that may be sensitive.

## Product Security Boundary

The scanner must preserve:

- Local/offline/non-AI operation.
- No telemetry.
- No source code upload.
- No cloud dependency.
- No AI, LLM, embedding, vector-search, or model-inference calls.
- No execution of scanned projects by default.

## Safe Handling of Scanned Source Code

- Treat scanned repositories and evidence packages as sensitive.
- Do not transmit scanned source code outside the local environment.
- Do not include full secrets in reports or logs.
- Prefer snippets only when needed for evidence.
- Preserve file paths and hashes where useful for auditability.

## Evidence Redaction Considerations

Evidence output should avoid exposing full secret values, private keys, tokens, or regulated data. Redaction must preserve enough context for reviewers to understand the finding.

## Dependency Hygiene

- Prefer minimal dependencies.
- Review dependency changes.
- Avoid runtime dependencies that introduce network calls or telemetry.
- Track dependency manifests and local SBOM output where applicable.

## Secret Handling

- Test fixtures must use fake secrets only.
- Real credentials must not be committed.
- Secret findings must redact sensitive values.
- Output directories must be handled as sensitive artifacts.

## Test Fixture Safety

Fixtures may contain synthetic risky patterns but must not contain usable credentials, real private data, or production source code.

## Report Sensitivity

Reports can reveal architecture, vulnerabilities, dependencies, ownership gaps, SOX indicators, AI/model usage, and delivery weaknesses. Reports should be stored and shared under appropriate access controls.

## Output Directory Handling

Output directories may contain evidence packages, manifests, hashes, SBOMs, findings, and reports. They should be cleaned, archived, or protected according to the user's governance process.
