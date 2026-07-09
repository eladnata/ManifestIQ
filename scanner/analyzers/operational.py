from __future__ import annotations

import re
from pathlib import Path

from scanner.analyzers.base import AnalyzerContext, iter_text_files, make_finding

STRICT_PROFILES = {"enterprise", "finance-sox", "production-critical", "ai-enabled"}
PRODUCTION_PROFILES = {"production-critical"}
FINANCE_PROFILES = {"finance-sox"}
CODE_EXTENSIONS = {".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".cs", ".go", ".rb", ".php"}
DATA_EXTENSIONS = {".sqlite", ".sqlite3", ".db", ".mdb", ".sql", ".dump", ".bak", ".csv", ".xlsx", ".xls"}
CONTAINER_FILES = {"dockerfile", "docker-compose.yml", "docker-compose.yaml"}
K8S_TOKENS = {"kind: deployment", "readinessprobe", "livenessprobe"}
ENV_TEMPLATE_NAMES = {".env.example", ".env.template", "config.example.yml", "config.example.yaml", "settings.example.toml"}
LOG_CONFIG_NAMES = {"logging.yml", "logging.yaml", "log4j.properties", "logback.xml", "nlog.config", "serilog.json"}
SUPPORT_MARKERS = {"support.md", "support-model.md", "owners.md", "owner.md", "codeowners", ".github/codeowners", "maintainers.md"}
RUNBOOK_MARKERS = {"runbook.md", "docs/runbook.md", "operations.md"}
BACKUP_MARKERS = {"backup-restore.md", "backup.md", "restore.md", "docs/backup-restore.md", "docs/backup.md", "docs/restore.md"}
INCIDENT_MARKERS = {"incident-response.md", "docs/incident-response.md", "postmortem.md", "docs/postmortem.md"}
MONITORING_MARKERS = {"monitoring.md", "docs/monitoring.md", "health-check.md", "docs/health-check.md", "observability.md", "docs/observability.md"}
CONFIG_DOC_MARKERS = {"configuration.md", "config-management.md", "environment.md", "environments.md", "docs/configuration.md", "docs/environment.md"}
DEPLOYMENT_MARKERS = {"deployment.md", "deploy.md", "docs/deployment.md", "docs/deploy.md"}
ROLLBACK_MARKERS = {"rollback.md", "docs/rollback.md"}
AI_INDICATORS = {"openai", "anthropic", "gemini", "gpt-", "claude-", "embeddings", "model="}
LOGGING_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\blogging\b", r"\blogger\b", r"log\.(info|error|warning|warn|debug|exception)",
        r"\bwinston\b", r"\bpino\b", r"\blog4j\b", r"\bserilog\b", r"\bnlog\b",
        r"structured logging", r"correlation_id", r"trace_id", r"request_id",
    ]
]
AUDIT_LOGGING_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [r"audit_log", r"audittrail", r"audit_event", r"audit logging", r"security event", r"control event"]
]
PRINT_ONLY_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in [r"\bprint\s*\(", r"console\.log\s*\("]]
MONITORING_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\bmonitoring\b", r"\bmetrics\b", r"\bobservability\b", r"\bprometheus\b", r"\bgrafana\b",
        r"opentelemetry", r"application insights", r"\bdatadog\b", r"new relic", r"cloudwatch",
        r"\bsplunk\b", r"\belk\b", r"\balerts?\b", r"\bdashboards?\b",
    ]
]
ALERTING_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in [r"\balerts?\b", r"\bpager\b", r"on-call", r"threshold", r"notification"]]
HEALTH_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [r"/health\b", r"/ready\b", r"/live\b", r"healthcheck", r"readinessprobe", r"livenessprobe", r"\bHEALTHCHECK\b"]
]
BACKUP_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [r"\bbackup\b", r"\brestore\b", r"\brecovery\b", r"retention policy", r"\brpo\b", r"\brto\b", r"disaster recovery", r"business continuity", r"export/import"]
]
INCIDENT_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [r"incident response", r"escalation", r"on-call", r"support rota", r"\bpager\b", r"severity model", r"contact matrix", r"postmortem"]
]
RUNTIME_CONFIG_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [r"environment variables?", r"\bos\.environ\b", r"process\.env", r"configmap", r"secrets manager", r"parameter store", r"\bvault\b", r"feature flags?", r"dev/test/prod"]
]
DEPLOYMENT_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [r"\bdeploy\b", r"\bdeployment\b", r"\bdockerfile\b", r"docker-compose", r"\bkubernetes\b", r"\bhelm\b", r"\bsystemd\b", r"\bterraform\b", r"\bansible\b"]
]
ERROR_HANDLING_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\btry\s*:", r"\bexcept\b", r"\bcatch\s*\(", r"\bfinally\b", r"\bretry\b", r"\btimeout\b",
        r"circuit breaker", r"graceful shutdown", r"transaction rollback", r"\bidempotenc", r"dead-letter",
        r"\bbackoff\b", r"failure handling",
    ]
]
NETWORK_CALL_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [r"requests\.(get|post|put|delete)\s*\(", r"fetch\s*\(", r"axios\.", r"httpclient", r"urllib\.request", r"http\.get", r"http\.post"]
]
TIMEOUT_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in [r"\btimeout\s*=", r"\btimeout\b", r"AbortController", r"setTimeout"]]
SENSITIVE_LOG_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"log\.(info|error|warning|warn|debug|exception).*password",
        r"log\.(info|error|warning|warn|debug|exception).*token",
        r"log\.(info|error|warning|warn|debug|exception).*secret",
        r"console\.log\s*\(.*(password|token|secret|api[_-]?key)",
        r"print\s*\(.*(password|token|secret|api[_-]?key)",
    ]
]
PRODUCTION_CONFIG_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [r"environment\s*[:=]\s*production", r"app_env\s*[:=]\s*prod", r"node_env\s*[:=]\s*production", r"debug\s*[:=]\s*false"]
]


def _path_present(lower_paths: set[str], markers: set[str]) -> bool:
    return any(path in markers or any(path.endswith("/" + marker) for marker in markers) for path in lower_paths)


def _count_matches(patterns: list[re.Pattern], text: str) -> int:
    return sum(1 for pattern in patterns if pattern.search(text))


def _snippet(line: str) -> str:
    return line.strip()[:240]


def _finding(
    rule_id: str,
    severity: str,
    title: str,
    description: str,
    *,
    evidence_value: str,
    decision_impact: str = "Conditional",
    remediation: list[str],
    file_path: str | None = None,
    line_no: int | None = None,
    evidence_type: str = "metadata",
    category: str = "Operations",
    owner_role: str = "DevOps",
    requires_approval_from: list[str] | None = None,
    evidence_snippet: str | None = None,
) -> dict:
    finding = make_finding(
        rule_id=rule_id,
        category=category,
        severity=severity,
        title=title,
        description=description,
        file_path=file_path,
        line_start=line_no,
        line_end=line_no,
        evidence_type=evidence_type,
        confidence="High",
        remediation=remediation,
        owner_role=owner_role,
    )
    finding.update({
        "decision_impact": decision_impact,
        "requires_approval_from": requires_approval_from or ["Operations"],
        "evidence_value": evidence_value,
        "evidence_snippet": evidence_snippet or evidence_value,
    })
    return finding


def _severity_for_missing(profile: str, production_severity: str = "High", strict_severity: str = "High") -> str:
    if profile in PRODUCTION_PROFILES:
        return production_severity
    if profile in STRICT_PROFILES:
        return strict_severity
    return "Medium"


def analyze(context: AnalyzerContext) -> dict:
    files = sorted(context.inventory.get("files", []), key=lambda item: item["path"])
    rel_paths = {item["path"] for item in files}
    lower_paths = {path.lower() for path in rel_paths}
    file_names = {Path(path).name.lower() for path in rel_paths}
    strict = context.profile in STRICT_PROFILES
    production = context.profile in PRODUCTION_PROFILES
    finance = context.profile in FINANCE_PROFILES
    ai_enabled = context.profile == "ai-enabled"

    counters = {
        "logging": 0,
        "audit_logging": 0,
        "print_only_logging": 0,
        "monitoring": 0,
        "alerting": 0,
        "health": 0,
        "backup_restore": 0,
        "incident_response": 0,
        "runtime_config": 0,
        "deployment_operations": 0,
        "error_handling": 0,
        "network_calls": 0,
        "timeout": 0,
        "sensitive_logging": 0,
        "production_config": 0,
        "ai_indicators": 0,
    }
    sensitive_logging_findings = []
    env_findings = []
    production_config_findings = []
    network_without_timeout_files = []

    for path, text in iter_text_files(context.root):
        rel = path.relative_to(context.root).as_posix()
        lowered = text.lower()
        counters["logging"] += _count_matches(LOGGING_PATTERNS, text)
        counters["audit_logging"] += _count_matches(AUDIT_LOGGING_PATTERNS, text)
        counters["print_only_logging"] += _count_matches(PRINT_ONLY_PATTERNS, text)
        counters["monitoring"] += _count_matches(MONITORING_PATTERNS, text)
        counters["alerting"] += _count_matches(ALERTING_PATTERNS, text)
        counters["health"] += _count_matches(HEALTH_PATTERNS, text)
        counters["backup_restore"] += _count_matches(BACKUP_PATTERNS, text)
        counters["incident_response"] += _count_matches(INCIDENT_PATTERNS, text)
        counters["runtime_config"] += _count_matches(RUNTIME_CONFIG_PATTERNS, text)
        counters["deployment_operations"] += _count_matches(DEPLOYMENT_PATTERNS, text)
        counters["error_handling"] += _count_matches(ERROR_HANDLING_PATTERNS, text)
        counters["network_calls"] += _count_matches(NETWORK_CALL_PATTERNS, text)
        counters["timeout"] += _count_matches(TIMEOUT_PATTERNS, text)
        counters["production_config"] += _count_matches(PRODUCTION_CONFIG_PATTERNS, text)
        if any(indicator in lowered for indicator in AI_INDICATORS):
            counters["ai_indicators"] += 1

        file_has_network_call = _count_matches(NETWORK_CALL_PATTERNS, text) > 0
        file_has_timeout = _count_matches(TIMEOUT_PATTERNS, text) > 0
        if file_has_network_call and not file_has_timeout and path.suffix.lower() in CODE_EXTENSIONS:
            network_without_timeout_files.append(rel)

        for line_no, line in enumerate(text.splitlines(), start=1):
            if any(pattern.search(line) for pattern in SENSITIVE_LOG_PATTERNS):
                counters["sensitive_logging"] += 1
                sensitive_logging_findings.append((rel, line_no, _snippet(line)))
            if any(pattern.search(line) for pattern in PRODUCTION_CONFIG_PATTERNS) and path.name.lower() in {".env", "config.yml", "config.yaml", "settings.py", "settings.json"}:
                production_config_findings.append((rel, line_no, _snippet(line)))

    containerization_detected = any(Path(path).name.lower() in CONTAINER_FILES for path in lower_paths) or any(
        any(token in (context.root / path).read_text(encoding="utf-8", errors="ignore").lower() for token in K8S_TOKENS)
        for path in rel_paths
        if Path(path).suffix.lower() in {".yml", ".yaml"} and (context.root / path).is_file()
    )
    container_health_detected = counters["health"] > 0
    data_storage_files = sorted(item["path"] for item in files if item["extension"] in DATA_EXTENSIONS)
    data_storage_detected = bool(data_storage_files)
    committed_env_files = sorted(path for path in rel_paths if Path(path).name.lower() == ".env")
    env_template_detected = bool(file_names & ENV_TEMPLATE_NAMES)
    log_config_detected = bool(file_names & LOG_CONFIG_NAMES)
    support_model_detected = _path_present(lower_paths, SUPPORT_MARKERS)
    runbook_detected = _path_present(lower_paths, RUNBOOK_MARKERS)
    backup_doc_detected = _path_present(lower_paths, BACKUP_MARKERS) or counters["backup_restore"] > 0
    incident_doc_detected = _path_present(lower_paths, INCIDENT_MARKERS) or counters["incident_response"] > 0
    monitoring_doc_detected = _path_present(lower_paths, MONITORING_MARKERS) or counters["monitoring"] > 0
    config_doc_detected = _path_present(lower_paths, CONFIG_DOC_MARKERS) or env_template_detected or counters["runtime_config"] > 0
    deployment_artifacts_detected = (
        _path_present(lower_paths, DEPLOYMENT_MARKERS)
        or any(Path(path).name.lower() in {"deploy.sh", "deploy.ps1", "dockerfile", "docker-compose.yml", "docker-compose.yaml"} for path in lower_paths)
        or counters["deployment_operations"] > 0
    )
    rollback_or_runbook_detected = runbook_detected or _path_present(lower_paths, ROLLBACK_MARKERS)
    logging_detected = counters["logging"] > 0 or log_config_detected
    audit_logging_detected = counters["audit_logging"] > 0 or _path_present(lower_paths, {"audit-logging.md", "docs/audit-logging.md"})
    error_handling_detected = counters["error_handling"] > 0
    timeout_detected = counters["timeout"] > 0
    alerting_detected = counters["alerting"] > 0

    findings = []
    if strict and not logging_detected:
        findings.append(_finding(
            "OPS-001",
            "Critical" if production else "High",
            "No logging evidence detected",
            "No application logging, logger configuration, or structured logging indicator was detected.",
            evidence_value="logging indicators",
            decision_impact="Block" if production else "Conditional",
            remediation=["Add application logging", "Document logging strategy and operational access"],
        ))
    elif counters["print_only_logging"] > 0 and counters["logging"] == 0:
        findings.append(_finding(
            "OPS-001",
            "Medium",
            "Only print or console logging detected",
            "Console or print statements were detected without application logging framework evidence.",
            evidence_value="print/console logging only",
            remediation=["Replace ad hoc console output with structured application logging"],
        ))

    if finance and not audit_logging_detected:
        findings.append(_finding(
            "OPS-002",
            "Critical" if data_storage_detected else "High",
            "No audit logging evidence detected",
            "Finance/SOX profile requires audit logging or control event logging evidence.",
            evidence_value="audit logging indicators",
            decision_impact="Mandatory Review",
            remediation=["Add audit logging for control-relevant events", "Document audit log retention and ownership"],
            owner_role="SOX",
            requires_approval_from=["SOX", "ITGC"],
        ))

    if strict and not monitoring_doc_detected:
        findings.append(_finding(
            "OPS-003",
            "High",
            "No monitoring evidence detected",
            "No monitoring, metrics, observability, alerting, or dashboard evidence was detected.",
            evidence_value="monitoring indicators",
            decision_impact="Block" if production else "Conditional",
            remediation=["Add monitoring or metrics evidence", "Document alert routing and dashboard ownership"],
        ))
    elif production and counters["monitoring"] > 0 and not alerting_detected:
        findings.append(_finding(
            "OPS-003",
            "High",
            "Monitoring evidence without alerting evidence",
            "Monitoring or metrics were detected, but no alerting evidence was found for production-critical use.",
            evidence_value="metrics without alerting",
            remediation=["Add alert rules, thresholds, and escalation ownership"],
        ))

    if production and not container_health_detected:
        findings.append(_finding(
            "OPS-004",
            "High",
            "No health check evidence detected",
            "Production-critical profile requires health, readiness, or liveness evidence.",
            evidence_value="health/readiness/liveness indicators",
            decision_impact="Block",
            remediation=["Add health check endpoint or script", "Connect health checks to monitoring"],
        ))

    if data_storage_detected and not backup_doc_detected:
        findings.append(_finding(
            "OPS-009",
            "Critical" if context.profile in {"finance-sox", "production-critical"} else "High",
            "Data storage without recovery procedure",
            "Data storage artifacts were detected but no backup, restore, recovery, RPO, or RTO evidence was found.",
            evidence_value=f"data_storage_files={data_storage_files}",
            decision_impact="Mandatory Review",
            remediation=["Add backup and restore procedure", "Document retention, RPO, RTO, and recovery owner"],
            owner_role="Operations",
            requires_approval_from=["Operations", "ITGC", "Data Governance"],
        ))
    elif production and not backup_doc_detected:
        findings.append(_finding(
            "OPS-005",
            "High",
            "No backup/restore evidence detected",
            "Production-critical profile requires backup and restore evidence.",
            evidence_value="backup/restore indicators",
            remediation=["Add backup and restore documentation", "Document recovery validation"],
        ))

    if production and not incident_doc_detected:
        findings.append(_finding(
            "OPS-006",
            "High",
            "No incident response evidence detected",
            "Production-critical profile requires incident response notes, escalation model, or on-call evidence.",
            evidence_value="incident response indicators",
            remediation=["Add incident response notes, escalation paths, and support contacts"],
            requires_approval_from=["Operations", "Security"],
        ))
    elif strict and not support_model_detected:
        findings.append(_finding(
            "OPS-012",
            "High",
            "No operational support model detected",
            "No support owner, on-call, CODEOWNERS, owners, or maintainers evidence was detected.",
            evidence_value="support ownership indicators",
            remediation=["Add operational support model and owner/contact evidence"],
            owner_role="Business Owner",
            requires_approval_from=["Operations", "ITGC"],
        ))

    if strict and not config_doc_detected:
        findings.append(_finding(
            "OPS-007",
            "High",
            "No runtime configuration separation evidence detected",
            "No environment template, configuration notes, environment variable, config map, or secrets manager evidence was detected.",
            evidence_value="runtime configuration separation indicators",
            remediation=["Add sanitized environment template", "Document runtime configuration and environment separation"],
            category="Configuration",
            requires_approval_from=["DevOps", "Security Architecture"],
        ))

    for env_path in committed_env_files:
        findings.append(_finding(
            "OPS-015",
            "Critical" if any(term in env_path.lower() for term in ["prod", "production"]) else "High",
            "Environment file committed",
            "A .env file is committed. Runtime environment files can contain secrets or production configuration.",
            file_path=env_path,
            evidence_type="file_presence",
            evidence_value=env_path,
            decision_impact="Block",
            remediation=["Remove committed .env file", "Add sanitized .env.example", "Rotate any exposed credentials"],
            category="Configuration",
            requires_approval_from=["Security Architecture"],
        ))

    for file_path, line_no, snippet in production_config_findings[:10]:
        findings.append(_finding(
            "OPS-015",
            "High",
            "Production configuration value committed",
            "A production environment configuration indicator was found in source-controlled configuration.",
            file_path=file_path,
            line_no=line_no,
            evidence_type="configuration",
            evidence_value="production configuration indicator",
            evidence_snippet=snippet,
            decision_impact="Conditional",
            remediation=["Move production configuration out of source control", "Use environment-specific deployment configuration"],
            category="Configuration",
            requires_approval_from=["DevOps", "Security Architecture"],
        ))

    if containerization_detected and not container_health_detected:
        findings.append(_finding(
            "OPS-008",
            "High",
            "Containerized service without health check evidence",
            "Containerization artifacts were detected but no Docker HEALTHCHECK, Kubernetes readiness/liveness probe, or health endpoint evidence was found.",
            evidence_value="containerization without health check",
            remediation=["Add container health check or Kubernetes readiness/liveness probes"],
            requires_approval_from=["Operations", "DevOps"],
        ))

    if deployment_artifacts_detected and not rollback_or_runbook_detected:
        findings.append(_finding(
            "OPS-013",
            "High",
            "Deployment artifacts without runbook or rollback alignment",
            "Deployment artifacts exist but no runbook or rollback procedure was detected.",
            evidence_value="deployment artifacts without runbook/rollback",
            remediation=["Add runbook and rollback procedure aligned to deployment artifacts"],
            requires_approval_from=["Operations", "Enterprise Architecture"],
        ))

    for file_path, line_no, snippet in sensitive_logging_findings[:20]:
        findings.append(_finding(
            "OPS-014",
            "Critical",
            "Sensitive data logging indicator detected",
            "Logging statement appears to include password, token, secret, or API key material.",
            file_path=file_path,
            line_no=line_no,
            evidence_type="pattern_match",
            evidence_value="sensitive data logging indicator",
            evidence_snippet=snippet,
            decision_impact="Block",
            remediation=["Remove sensitive values from logs", "Mask or tokenize sensitive fields", "Review log retention and access controls"],
            category="Data Protection",
            requires_approval_from=["Security", "Data Governance"],
        ))

    if strict and not error_handling_detected:
        findings.append(_finding(
            "OPS-010",
            "High" if production else "Medium",
            "No error handling evidence detected",
            "Application code exists but no exception handling, retry, timeout, rollback, idempotency, or graceful shutdown indicators were found.",
            evidence_value="error handling indicators",
            remediation=["Add error handling and resilience patterns", "Document failure behavior"],
            requires_approval_from=["Engineering Lead"],
        ))

    for file_path in sorted(set(network_without_timeout_files))[:20]:
        findings.append(_finding(
            "OPS-011",
            "High" if production else "Medium",
            "Network call without timeout evidence",
            "A network/API call was detected in application code without timeout evidence in the same file.",
            file_path=file_path,
            evidence_type="pattern_match",
            evidence_value="network call without timeout",
            remediation=["Add explicit timeout handling", "Document retry and backoff behavior"],
            requires_approval_from=["Engineering Lead", "Operations"],
        ))

    if ai_enabled and counters["ai_indicators"] > 0 and not monitoring_doc_detected:
        findings.append(_finding(
            "OPS-003",
            "High",
            "AI/model usage without observability evidence",
            "AI/model or provider indicators were detected without monitoring or observability evidence.",
            evidence_value="AI/model indicators without observability",
            decision_impact="Mandatory Review",
            remediation=["Add observability for AI/model/API usage", "Document provider failure handling and alerting"],
            requires_approval_from=["Security Architecture", "Operations"],
        ))

    signal_values = [
        logging_detected,
        audit_logging_detected or not finance,
        monitoring_doc_detected,
        container_health_detected or not production,
        backup_doc_detected or not data_storage_detected,
        incident_doc_detected or not production,
        config_doc_detected,
        not (containerization_detected and not container_health_detected),
        error_handling_detected,
        timeout_detected or counters["network_calls"] == 0,
        support_model_detected or not strict,
    ]
    readiness_score = round(sum(1 for value in signal_values if value) / len(signal_values) * 100)
    metrics = {
        "logging_indicators_count": counters["logging"],
        "audit_logging_indicators_count": counters["audit_logging"],
        "print_or_console_logging_indicators_count": counters["print_only_logging"],
        "monitoring_indicators_count": counters["monitoring"],
        "alerting_indicators_count": counters["alerting"],
        "health_check_indicators_count": counters["health"],
        "backup_restore_indicators_count": counters["backup_restore"],
        "incident_response_indicators_count": counters["incident_response"],
        "runtime_config_indicators_count": counters["runtime_config"],
        "deployment_operations_indicators_count": counters["deployment_operations"],
        "error_handling_indicators_count": counters["error_handling"],
        "network_call_indicators_count": counters["network_calls"],
        "timeout_indicators_count": counters["timeout"],
        "sensitive_data_logging_indicators_count": counters["sensitive_logging"],
        "production_configuration_indicators_count": counters["production_config"],
        "data_storage_detected": data_storage_detected,
        "data_storage_files": data_storage_files,
        "containerization_detected": containerization_detected,
        "container_health_check_detected": container_health_detected,
        "support_model_detected": support_model_detected,
        "runbook_detected": runbook_detected,
        "backup_restore_documentation_detected": backup_doc_detected,
        "incident_response_documentation_detected": incident_doc_detected,
        "runtime_config_separation_detected": config_doc_detected,
        "deployment_artifacts_detected": deployment_artifacts_detected,
        "operational_readiness_score": readiness_score,
    }
    return {"metrics": metrics, "findings": findings}
