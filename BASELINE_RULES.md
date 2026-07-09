# Baseline Rules

Baseline rules are the built-in enterprise assurance controls shipped with the scanner.

## Security

- Hardcoded secrets
- Private keys
- Unsafe dynamic execution
- Command injection indicators
- SQL injection patterns
- Weak cryptography
- Unsafe deserialization
- Debug mode enabled
- Default credentials
- Disabled TLS verification
- Open CORS

## Supply Chain

- Missing lock file
- Unbounded dependency versions
- Unpinned dependencies
- Suspicious or unmanaged binary artifacts
- Missing dependency evidence for strict profiles

## License Risk

- Missing repository license file
- Missing third-party notices
- Dependency missing license evidence
- Unknown dependency license
- Restrictive license detected
- Strong copyleft license requiring review
- AGPL/SSPL requiring enterprise review
- Ambiguous license expression
- Binary artifact without license evidence
- Vendored dependency without attribution
- Dependency manifest without lock file
- Lock file without matching manifest
- Missing local SBOM evidence
- Custom license requiring review

## Governance

- Missing owner evidence
- Custom rule attempted baseline override
- Baseline rule disabled
- Missing accountability evidence

## Documentation

- Missing README
- Missing architecture overview
- Missing deployment guide
- Missing runbook
- Missing rollback procedure
- Missing data flow
- Missing security notes
- Missing changelog

## Architecture

- No clear entry point
- Missing recognizable source structure
- Mixed unrelated applications
- Excessive root-level files
- Suspicious hidden directories
- Committed binary artifacts
- Committed archive artifacts
- Committed local database files
- Missing test structure
- Missing CI/CD definition
- Missing owner metadata
- Excessive unmanaged scripts

## Data Protection

- Sensitive data indicators
- Sensitive data files
- Database-like artifacts
- Missing data classification evidence

## SOX

- Journal, ledger, reconciliation, invoice, billing, payment, vendor, revenue, posting, approval, control, SAP, and segregation-of-duties indicators
- Missing SOX impact assessment in strict profiles

## AI Model Risk

- Undeclared AI/ML dependency
- External AI API call or prompt indicator
- Local model artifact or embedded weights
- Embedding or vector database usage
- Missing AI provider, model, data-flow, or governance evidence

## Operations

- Missing deployment guide
- Missing logging indicators
- Missing audit logging evidence
- Missing monitoring or health check evidence
- Missing rollback procedure
- Missing backup/restore evidence
- Missing incident response notes
- Missing runbook
- Missing support model
- Missing changelog or release notes
- Missing data flow documentation
- Missing test evidence
- Missing configuration management notes
- Containerized service without health check
- Data storage without recovery procedure
- Missing error handling evidence
- Network calls without timeout evidence
- Deployment artifacts without runbook
- Sensitive data logging indicator
- Production configuration committed

## Maintainability

- Large files
- Long files
- Missing tests
- Hardcoded paths
- Weak modularity indicators

## Scan Integrity

- Analyzer failure
- Invalid analyzer result contract
