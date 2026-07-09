from __future__ import annotations

from typing import Any


DOMAIN_BY_PREFIX = {
    "language": "platform",
    "platform": "platform",
    "framework": "architecture",
    "database": "data",
    "interface": "architecture",
    "egress": "egress",
    "ai": "ai_model",
    "ops": "operations",
    "delivery": "delivery",
    "license": "license",
    "security": "security",
    "supply_chain": "security",
    "finance": "governance",
    "governance": "governance",
    "architecture": "architecture",
    "data": "data",
    "maintainability": "maintainability",
}


def _slug(value: str) -> str:
    return (
        value.strip()
        .lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("#", "sharp")
        .replace("+", "plus")
        .replace(".", "_")
    )


def _domain(signal_id: str) -> str:
    return DOMAIN_BY_PREFIX.get(signal_id.split(".", 1)[0], "governance")


def _result_by_id(analyzer_results: list[dict]) -> dict[str, dict]:
    return {result.get("analyzer_id", ""): result for result in analyzer_results}


def _evidence(analyzer_id: str, key: str, value: Any) -> list[dict]:
    return [{"source_analyzer": analyzer_id, "metric": key, "value": value}]


def _add(
    signals: dict[str, dict],
    signal_id: str,
    *,
    value: Any = True,
    confidence: str = "High",
    source_analyzer: str,
    evidence: list[dict] | None = None,
    metadata: dict | None = None,
) -> None:
    signals[signal_id] = {
        "signal_id": signal_id,
        "name": signal_id.replace(".", " "),
        "domain": _domain(signal_id),
        "value": value,
        "confidence": confidence,
        "source_analyzer": source_analyzer,
        "evidence": evidence or [],
        "metadata": metadata or {},
    }


def build_signals(inventory: dict, analyzer_results: list[dict], findings: list[dict]) -> list[dict]:
    signals: dict[str, dict] = {}
    by_id = _result_by_id(analyzer_results)

    for language in sorted(inventory.get("languages", {})):
        _add(
            signals,
            f"language.{_slug(language)}.detected",
            value=inventory["languages"][language],
            source_analyzer="inventory",
            evidence=[{"source_analyzer": "inventory", "metric": "languages", "language": language}],
        )
    for package_manager in sorted(inventory.get("package_managers", [])):
        _add(
            signals,
            "platform.package_manager.detected",
            value=sorted(inventory.get("package_managers", [])),
            source_analyzer="inventory",
            evidence=[{"source_analyzer": "inventory", "metric": "package_managers"}],
        )
    if inventory.get("config_files"):
        _add(signals, "platform.configuration.detected", value=inventory["config_files"], source_analyzer="inventory", evidence=_evidence("inventory", "config_files", inventory["config_files"]))
    if inventory.get("data_files"):
        _add(signals, "database.local_artifact.detected", value=inventory["data_files"], source_analyzer="inventory", evidence=_evidence("inventory", "data_files", inventory["data_files"]))

    ai_metrics = by_id.get("hidden_ai_model_detector", {}).get("metrics", {})
    if ai_metrics.get("ai_library_indicators") or ai_metrics.get("ai_api_indicators") or ai_metrics.get("model_artifact_count"):
        _add(signals, "ai.model_usage.detected", value=True, source_analyzer="hidden_ai_model_detector", evidence=_evidence("hidden_ai_model_detector", "ai_metrics", ai_metrics))
    if ai_metrics.get("ai_api_indicators"):
        _add(signals, "ai.external_provider.detected", value=ai_metrics["ai_api_indicators"], source_analyzer="hidden_ai_model_detector", evidence=_evidence("hidden_ai_model_detector", "ai_api_indicators", ai_metrics["ai_api_indicators"]))
        _add(signals, "egress.external_url.detected", value=ai_metrics["ai_api_indicators"], source_analyzer="hidden_ai_model_detector", evidence=_evidence("hidden_ai_model_detector", "ai_api_indicators", ai_metrics["ai_api_indicators"]))
    if ai_metrics.get("model_artifact_count", 0) > 0:
        _add(signals, "ai.model_artifact.detected", value=ai_metrics.get("model_artifacts", []), source_analyzer="hidden_ai_model_detector", evidence=_evidence("hidden_ai_model_detector", "model_artifacts", ai_metrics.get("model_artifacts", [])))
    if any(item in {"chromadb", "pinecone", "faiss", "weaviate", "qdrant"} for item in ai_metrics.get("ai_library_indicators", [])):
        _add(signals, "ai.vector_database.detected", value=True, source_analyzer="hidden_ai_model_detector", evidence=_evidence("hidden_ai_model_detector", "ai_library_indicators", ai_metrics.get("ai_library_indicators", [])))
    if ai_metrics.get("ai_declaration_detected"):
        _add(signals, "governance.ai_declaration.detected", value=True, source_analyzer="hidden_ai_model_detector", evidence=_evidence("hidden_ai_model_detector", "ai_declaration_detected", True))

    data_metrics = by_id.get("data_risk", {}).get("metrics", {})
    if data_metrics.get("sensitive_keyword_hits", 0) > 0:
        _add(signals, "data.sensitive_indicator.detected", value=data_metrics.get("unique_terms", []), confidence="Medium", source_analyzer="data_risk", evidence=_evidence("data_risk", "unique_terms", data_metrics.get("unique_terms", [])))
    if any(finding.get("rule_id") == "DATA-001" for finding in findings):
        _add(signals, "data.sensitive_file.detected", value=True, confidence="Medium", source_analyzer="data_risk", evidence=[{"source_analyzer": "data_risk", "rule_id": "DATA-001"}])

    sox_metrics = by_id.get("sox_detector", {}).get("metrics", {})
    if sox_metrics.get("sox_finance_impact") == "potential":
        _add(signals, "finance.sox_indicator.detected", value=sox_metrics.get("matched_terms", []), confidence="Medium", source_analyzer="sox_detector", evidence=_evidence("sox_detector", "matched_terms", sox_metrics.get("matched_terms", [])))

    ops_metrics = by_id.get("operational", {}).get("metrics", {})
    ops_map = {
        "ops.logging.detected": ("logging_indicators_count", lambda v: v > 0),
        "ops.audit_logging.detected": ("audit_logging_indicators_count", lambda v: v > 0),
        "ops.monitoring.detected": ("monitoring_indicators_count", lambda v: v > 0),
        "ops.health_check.detected": ("health_check_indicators_count", lambda v: v > 0),
        "ops.backup_restore.detected": ("backup_restore_documentation_detected", bool),
        "ops.incident_response.detected": ("incident_response_documentation_detected", bool),
        "ops.runtime_config.detected": ("runtime_config_separation_detected", bool),
        "ops.data_storage.detected": ("data_storage_detected", bool),
    }
    for signal_id, (metric, predicate) in ops_map.items():
        value = ops_metrics.get(metric)
        if predicate(value):
            _add(signals, signal_id, value=value, source_analyzer="operational", evidence=_evidence("operational", metric, value))

    project_metrics = by_id.get("project_structure", {}).get("metrics", {})
    project_pairs = [
        ("architecture.source_structure", "source_directory_detected"),
        ("delivery.tests", "test_directory_detected"),
        ("delivery.cicd", "ci_cd_detected"),
        ("governance.owner_metadata", "owner_files_detected"),
    ]
    for prefix, metric in project_pairs:
        value = project_metrics.get(metric)
        state = "detected" if bool(value) else "missing"
        _add(signals, f"{prefix}.{state}", value=value, source_analyzer="project_structure", evidence=_evidence("project_structure", metric, value))
    entry_points = project_metrics.get("entry_points_detected", [])
    _add(signals, f"architecture.entry_point.{'detected' if entry_points else 'missing'}", value=entry_points, source_analyzer="project_structure", evidence=_evidence("project_structure", "entry_points_detected", entry_points))

    delivery_metrics = by_id.get("delivery_readiness", {}).get("metrics", {})
    for prefix, metric in [
        ("delivery.runbook", "runbook_present"),
        ("delivery.deployment", "deployment_guide_present"),
        ("delivery.data_flow", "data_flow_documentation_present"),
        ("delivery.rollback", "rollback_guide_present"),
    ]:
        value = delivery_metrics.get(metric)
        state = "detected" if bool(value) else "missing"
        _add(signals, f"{prefix}.{state}", value=value, source_analyzer="delivery_readiness", evidence=_evidence("delivery_readiness", metric, value))

    license_metrics = by_id.get("licenses", {}).get("metrics", {})
    license_pairs = [
        ("license.repository.detected", "repository_license_present", bool),
        ("license.unknown.detected", "components_unknown_license", lambda v: v > 0),
        ("license.missing.detected", "components_missing_license", lambda v: v > 0),
        ("license.restrictive.detected", "components_restrictive_license", lambda v: v > 0),
        ("license.local_sbom.generated", "local_sbom_generated", bool),
    ]
    for signal_id, metric, predicate in license_pairs:
        value = license_metrics.get(metric, 0)
        if predicate(value):
            _add(signals, signal_id, value=value, source_analyzer="licenses", evidence=_evidence("licenses", metric, value))

    if any(finding.get("rule_id") == "SEC-001" for finding in findings):
        _add(signals, "security.secret.detected", value=True, source_analyzer="secrets", evidence=[{"source_analyzer": "secrets", "rule_id": "SEC-001"}])
    if any(finding.get("category") == "Maintainability" for finding in findings):
        _add(signals, "maintainability.risk.detected", value=True, source_analyzer="maintainability", evidence=[{"source_analyzer": "maintainability", "category": "Maintainability"}])
    if any(finding.get("category") == "Governance" and str(finding.get("rule_id", "")).startswith("GOV-") for finding in findings):
        _add(signals, "governance.rulebook_issue.detected", value=True, source_analyzer="rulebook_governance", evidence=[{"source_analyzer": "rulebook_governance"}])

    return [signals[key] for key in sorted(signals)]


def signal_id_set(signals: list[dict]) -> set[str]:
    return {signal["signal_id"] for signal in signals}
