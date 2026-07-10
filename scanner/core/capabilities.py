from __future__ import annotations


STRICT_PROFILES = ["enterprise", "finance-sox", "ai-enabled", "production-critical"]
DOMAIN_BY_SIGNAL_PREFIX = {
    "ai": "ai_model",
    "architecture": "architecture",
    "database": "data",
    "data": "data",
    "delivery": "delivery",
    "egress": "egress",
    "finance": "governance",
    "governance": "governance",
    "language": "platform",
    "license": "license",
    "maintainability": "maintainability",
    "ops": "operations",
    "platform": "platform",
    "security": "security",
    "supply_chain": "security",
}


def _domains_for_signals(signal_ids: list[str]) -> list[str]:
    domains = {
        DOMAIN_BY_SIGNAL_PREFIX.get(signal_id.split(".", 1)[0], "unknown")
        for signal_id in signal_ids
    }
    return sorted(domains or {"unknown"})


def capability_registry() -> list[dict]:
    capabilities = [
        {
            "analyzer_id": "secrets",
            "produces_signals": ["security.secret.detected"],
            "produces_evidence_files": ["secrets-results.json"],
            "required_for_profiles": STRICT_PROFILES,
        },
        {
            "analyzer_id": "dependencies",
            "produces_signals": ["supply_chain.dependencies.detected", "supply_chain.lock_file.detected"],
            "produces_evidence_files": ["dependencies-results.json"],
            "required_for_profiles": STRICT_PROFILES,
        },
        {
            "analyzer_id": "sast",
            "produces_signals": ["security.unsafe_code.detected"],
            "produces_evidence_files": ["sast-results.json"],
            "required_for_profiles": STRICT_PROFILES,
        },
        {
            "analyzer_id": "config",
            "produces_signals": ["platform.configuration.detected", "security.risky_configuration.detected"],
            "produces_evidence_files": ["config-results.json"],
            "required_for_profiles": STRICT_PROFILES,
        },
        {
            "analyzer_id": "hidden_ai_model_detector",
            "produces_signals": [
                "ai.external_provider.detected",
                "ai.model_artifact.detected",
                "ai.model_usage.detected",
                "ai.vector_database.detected",
                "governance.ai_declaration.detected",
            ],
            "produces_evidence_files": ["hidden_ai_model_detector-results.json"],
            "required_for_profiles": STRICT_PROFILES,
        },
        {
            "analyzer_id": "documentation",
            "produces_signals": ["delivery.documentation.detected"],
            "produces_evidence_files": ["documentation-results.json"],
            "required_for_profiles": STRICT_PROFILES,
        },
        {
            "analyzer_id": "data_risk",
            "produces_signals": ["data.sensitive_indicator.detected", "data.sensitive_file.detected"],
            "produces_evidence_files": ["data_risk-results.json"],
            "required_for_profiles": STRICT_PROFILES,
        },
        {
            "analyzer_id": "sox_detector",
            "produces_signals": ["finance.sox_indicator.detected"],
            "produces_evidence_files": ["sox_detector-results.json"],
            "required_for_profiles": ["finance-sox"],
        },
        {
            "analyzer_id": "maintainability",
            "produces_signals": ["maintainability.risk.detected"],
            "produces_evidence_files": ["maintainability-results.json"],
            "required_for_profiles": STRICT_PROFILES,
        },
        {
            "analyzer_id": "operational",
            "produces_signals": [
                "ops.logging.detected",
                "ops.audit_logging.detected",
                "ops.monitoring.detected",
                "ops.health_check.detected",
                "ops.backup_restore.detected",
                "ops.incident_response.detected",
                "ops.runtime_config.detected",
                "ops.data_storage.detected",
            ],
            "produces_evidence_files": ["operational-results.json"],
            "required_for_profiles": STRICT_PROFILES,
        },
        {
            "analyzer_id": "licenses",
            "produces_signals": [
                "license.repository.detected",
                "license.unknown.detected",
                "license.missing.detected",
                "license.restrictive.detected",
                "license.local_sbom.generated",
            ],
            "produces_evidence_files": ["licenses-results.json", "local-sbom.json"],
            "required_for_profiles": STRICT_PROFILES,
        },
        {
            "analyzer_id": "project_structure",
            "produces_signals": [
                "architecture.source_structure.detected",
                "architecture.source_structure.missing",
                "architecture.entry_point.detected",
                "architecture.entry_point.missing",
                "delivery.tests.detected",
                "delivery.tests.missing",
                "delivery.cicd.detected",
                "delivery.cicd.missing",
                "governance.owner_metadata.detected",
                "governance.owner_metadata.missing",
            ],
            "produces_evidence_files": ["project_structure-results.json"],
            "required_for_profiles": STRICT_PROFILES,
        },
        {
            "analyzer_id": "delivery_readiness",
            "produces_signals": [
                "delivery.runbook.detected",
                "delivery.runbook.missing",
                "delivery.deployment.detected",
                "delivery.deployment.missing",
                "delivery.data_flow.detected",
                "delivery.data_flow.missing",
                "delivery.rollback.detected",
                "delivery.rollback.missing",
            ],
            "produces_evidence_files": ["delivery_readiness-results.json"],
            "required_for_profiles": STRICT_PROFILES,
        },
        {
            "analyzer_id": "architecture_signals",
            "produces_signals": ["architecture.analysis.available"],
            "produces_evidence_files": ["architecture_signals-results.json"],
            "required_for_profiles": STRICT_PROFILES,
        },
        {
            "analyzer_id": "rulebook_governance",
            "produces_signals": ["governance.rulebook_issue.detected"],
            "produces_evidence_files": ["rule-evaluation-results.json"],
            "required_for_profiles": STRICT_PROFILES,
        },
        {
            "analyzer_id": "rule_contract",
            "produces_signals": ["governance.rule_contract_gap.detected"],
            "produces_evidence_files": ["rule-contract-validation.json"],
            "required_for_profiles": STRICT_PROFILES,
        },
    ]
    for capability in capabilities:
        capability.setdefault("domains", _domains_for_signals(capability.get("produces_signals", [])))
        capability.setdefault("limitations", [])
    return capabilities


def known_signal_ids() -> set[str]:
    signals: set[str] = {
        "language.python.detected",
        "language.javascript.detected",
        "language.typescript.detected",
        "language.java.detected",
        "language.go.detected",
        "platform.package_manager.detected",
        "platform.configuration.detected",
        "database.local_artifact.detected",
        "egress.external_url.detected",
    }
    for capability in capability_registry():
        signals.update(capability["produces_signals"])
    return signals
