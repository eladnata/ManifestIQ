from __future__ import annotations

from scanner.core.signals import signal_id_set


STRICT_PROFILES = {"enterprise", "finance-sox", "ai-enabled", "production-critical"}


def _runtime_from_package_manager(package_manager: str) -> str:
    if package_manager in {"pip", "python-project", "pipenv", "poetry-lock", "pipenv-lock"}:
        return "python"
    if package_manager in {"npm", "npm-lock"}:
        return "node"
    if package_manager in {"maven", "gradle"}:
        return "jvm"
    if package_manager == "go-modules":
        return "go"
    return package_manager


def build_control_context(profile: str, inventory: dict, signals: list[dict], findings: list[dict]) -> dict:
    ids = signal_id_set(signals)
    languages = sorted(inventory.get("languages", {}).keys())
    runtimes = sorted({_runtime_from_package_manager(item) for item in inventory.get("package_managers", [])})
    data_files = inventory.get("data_files", [])
    source_files = [item["path"] for item in inventory.get("files", []) if item.get("extension") in {".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".cs", ".go"}]

    if "architecture.entry_point.detected" in ids and source_files:
        system_type = "backend_api" if any("app.py" in path or "server" in path.lower() for path in source_files) else "cli"
    elif source_files:
        system_type = "library"
    else:
        system_type = "unknown"

    architecture_style = "monolith"
    if len({path.split("/", 1)[0] for path in source_files if "/" in path}) > 1:
        architecture_style = "multi_service"
    if not source_files:
        architecture_style = "unknown"

    financial = "finance.sox_indicator.detected" in ids or any(f.get("category") == "SOX" for f in findings)
    sensitive = bool({"data.sensitive_indicator.detected", "data.sensitive_file.detected"} & ids)
    ai_usage = bool({"ai.model_usage.detected", "ai.external_provider.detected", "ai.model_artifact.detected", "ai.vector_database.detected"} & ids)
    external_egress = "egress.external_url.detected" in ids or "ai.external_provider.detected" in ids

    return {
        "profile": profile,
        "system_type": system_type,
        "architecture_style": architecture_style,
        "languages": languages,
        "frameworks": [],
        "runtimes": runtimes,
        "databases_detected": sorted(data_files),
        "external_egress_detected": external_egress,
        "ai_model_usage_detected": ai_usage,
        "financial_indicators_detected": financial,
        "sensitive_data_indicators_detected": sensitive,
        "production_readiness_required": profile in STRICT_PROFILES,
        "sox_review_required": profile == "finance-sox" or financial,
        "data_governance_review_required": sensitive or ai_usage,
        "security_architecture_review_required": profile in STRICT_PROFILES or ai_usage or external_egress,
    }
