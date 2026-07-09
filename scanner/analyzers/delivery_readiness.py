from __future__ import annotations

from pathlib import Path

from scanner.analyzers.base import AnalyzerContext, iter_text_files, make_finding

STRICT_PROFILES = {"enterprise", "finance-sox", "production-critical", "ai-enabled"}
FINANCE_PROFILES = {"finance-sox"}
PRODUCTION_PROFILES = {"production-critical"}
DOC_MARKERS = {
    "readme": {"readme.md", "readme.txt"},
    "installation": {"installation.md", "install.md", "docs/installation.md", "docs/install.md"},
    "deployment": {"deployment.md", "deploy.md", "docs/deployment.md", "docs/deploy.md"},
    "rollback": {"rollback.md", "docs/rollback.md"},
    "runbook": {"runbook.md", "docs/runbook.md", "operations.md"},
    "architecture": {"architecture.md", "architecture-overview.md", "docs/architecture.md", "docs/architecture-overview.md"},
    "data_flow": {"data-flow.md", "data_flow.md", "docs/data-flow.md", "docs/data_flow.md"},
    "security_notes": {"security.md", "security-notes.md", "docs/security.md", "docs/security-notes.md"},
    "support": {"support.md", "support-model.md", "docs/support.md", "docs/support-model.md"},
    "changelog": {"changelog.md", "change_log.md", "release-notes.md", "docs/release-notes.md"},
    "incident_response": {"incident-response.md", "docs/incident-response.md"},
    "backup_restore": {"backup-restore.md", "backup.md", "restore.md", "docs/backup-restore.md"},
    "monitoring": {"monitoring.md", "health-check.md", "healthcheck.md", "docs/monitoring.md", "docs/health-check.md"},
    "configuration_management": {"configuration.md", "config-management.md", "environment.md", "docs/configuration.md", "docs/environment.md"},
    "environment_separation": {"environments.md", "environment-separation.md", "docs/environments.md", "docs/environment-separation.md"},
    "operational_ownership": {"owners.md", "owner.md", "codeowners", ".github/codeowners", "maintainers.md"},
    "change_management": {"change-management.md", "docs/change-management.md"},
    "access_control": {"access-control.md", "docs/access-control.md"},
    "approval_workflow": {"approval-workflow.md", "docs/approval-workflow.md"},
    "audit_logging": {"audit-logging.md", "docs/audit-logging.md"},
    "sox_impact": {"sox.md", "sox-impact.md", "docs/sox-impact.md"},
}
CI_PATH_PREFIXES = {".github/workflows", ".gitlab-ci.yml", "azure-pipelines.yml", "Jenkinsfile", ".circleci", "bitbucket-pipelines.yml"}
TEST_MARKERS = {"tests", "test", "__tests__", "spec", "specs"}
TEST_FRAMEWORK_TOKENS = {"pytest", "unittest", "jest", "mocha", "vitest", "junit", "xunit", "nunit", "go test"}
DEPLOY_SCRIPT_NAMES = {"deploy.sh", "deploy.ps1", "deploy.bat", "release.sh", "release.ps1"}
ROLLBACK_SCRIPT_NAMES = {"rollback.sh", "rollback.ps1", "rollback.bat"}
HEALTH_CHECK_TOKENS = {"health", "healthcheck", "readiness", "liveness"}
LOGGING_TOKENS = {"logging.", "logger.", "console.log", "log4j", "winston", "serilog"}
FINANCE_TERMS = {
    "journal", "ledger", "reconciliation", "revenue", "billing", "invoice", "payment", "vendor",
    "posting", "approval", "control", "sap", "sox",
}


def _marker_present(lower_paths: set[str], markers: set[str]) -> bool:
    return any(path in markers or any(path.endswith("/" + marker) for marker in markers) for path in lower_paths)


def _has_ci(rel_paths: set[str]) -> bool:
    return any(
        rel in CI_PATH_PREFIXES or any(rel.startswith(prefix + "/") for prefix in CI_PATH_PREFIXES)
        for rel in rel_paths
    )


def _severity(profile: str, default: str = "High", sandbox: str = "Low") -> str:
    return sandbox if profile == "sandbox" else default


def _finding(
    rule_id: str,
    severity: str,
    title: str,
    description: str,
    *,
    evidence_value: str,
    decision_impact: str = "Conditional",
    remediation: list[str],
    owner_role: str = "DevOps",
    requires_approval_from: list[str] | None = None,
) -> dict:
    finding = make_finding(
        rule_id=rule_id,
        category="Operations",
        severity=severity,
        title=title,
        description=description,
        evidence_type="missing_file",
        confidence="High",
        remediation=remediation,
        owner_role=owner_role,
    )
    finding.update({
        "decision_impact": decision_impact,
        "requires_approval_from": requires_approval_from or ["DevOps"],
        "evidence_value": evidence_value,
        "evidence_snippet": evidence_value,
    })
    return finding


def _text_indicators(context: AnalyzerContext) -> dict[str, bool]:
    found = {
        "test_framework": False,
        "health_check": False,
        "logging": False,
        "finance_terms": False,
        "versioning": False,
    }
    for _path, text in iter_text_files(context.root):
        lowered = text.lower()
        if any(token in lowered for token in TEST_FRAMEWORK_TOKENS):
            found["test_framework"] = True
        if any(token in lowered for token in HEALTH_CHECK_TOKENS):
            found["health_check"] = True
        if any(token in lowered for token in LOGGING_TOKENS):
            found["logging"] = True
        if any(term in lowered for term in FINANCE_TERMS):
            found["finance_terms"] = True
        if any(token in lowered for token in ["semver", "version:", "__version__", "release version"]):
            found["versioning"] = True
    return found


def analyze(context: AnalyzerContext) -> dict:
    rel_paths = {item["path"] for item in context.inventory.get("files", [])}
    lower_paths = {path.lower() for path in rel_paths}
    file_names = {Path(path).name.lower() for path in rel_paths}
    indicators = _text_indicators(context)

    docs = {name: _marker_present(lower_paths, markers) for name, markers in DOC_MARKERS.items()}
    ci_cd_present = _has_ci(rel_paths)
    test_directory_present = any(path.split("/", 1)[0].lower() in TEST_MARKERS for path in lower_paths)
    test_file_present = any("test" in path or "spec" in path for path in lower_paths)
    test_evidence_present = test_directory_present or test_file_present or indicators["test_framework"]
    deploy_script_present = bool(file_names & DEPLOY_SCRIPT_NAMES)
    rollback_script_present = bool(file_names & ROLLBACK_SCRIPT_NAMES)
    health_script_present = any(any(token in Path(path).name.lower() for token in HEALTH_CHECK_TOKENS) for path in lower_paths)
    environment_template_present = any(Path(path).name.lower() in {".env.example", ".env.template"} for path in lower_paths)
    release_workflow_present = ci_cd_present or docs["changelog"] or any("release" in Path(path).name.lower() for path in lower_paths)
    monitoring_evidence_present = docs["monitoring"] or indicators["health_check"] or health_script_present
    logging_evidence_present = docs["audit_logging"] or indicators["logging"]
    finance_terms_present = indicators["finance_terms"]

    findings = []
    strict = context.profile in STRICT_PROFILES

    def require(condition: bool, rule_id: str, title: str, description: str, evidence_value: str, remediation: list[str], *, severity: str = "High", decision: str = "Conditional", owner: str = "DevOps", approvers: list[str] | None = None):
        if condition:
            return
        findings.append(_finding(
            rule_id,
            _severity(context.profile, severity),
            title,
            description,
            evidence_value=evidence_value,
            decision_impact=decision,
            remediation=remediation,
            owner_role=owner,
            requires_approval_from=approvers,
        ))

    if strict:
        require(
            docs["deployment"] or deploy_script_present,
            "DEL-001",
            "Missing deployment guide",
            "No deployment guide or deployment script was detected for a strict assurance profile.",
            "deployment guide or deploy script",
            ["Add deployment instructions", "Document target environments and deployment commands"],
            approvers=["DevOps", "Enterprise Architecture"],
        )
        require(
            docs["runbook"],
            "DEL-003",
            "Missing runbook",
            "No runbook was detected for operational handoff and incident response.",
            "runbook",
            ["Add a runbook with support, escalation, and recovery procedures"],
            approvers=["Operations"],
        )
        require(
            docs["architecture"],
            "DEL-004",
            "Missing architecture overview",
            "No architecture overview was detected for technical review.",
            "architecture overview",
            ["Add architecture overview with components, dependencies, and trust boundaries"],
            owner="Architecture",
            approvers=["Enterprise Architecture"],
        )
        require(
            docs["support"] or docs["operational_ownership"],
            "DEL-005",
            "Missing support model",
            "No support model or operational ownership artifact was detected.",
            "support model or owner metadata",
            ["Add support model and operational owner evidence"],
            owner="Business Owner",
            approvers=["ITGC", "Operations"],
        )
        require(
            docs["changelog"] or release_workflow_present,
            "DEL-006",
            "Missing changelog or release notes",
            "No changelog, release notes, or release workflow evidence was detected.",
            "changelog or release notes",
            ["Add changelog, release notes, or documented release workflow"],
            owner="Engineering",
        )
        require(
            test_evidence_present,
            "DEL-008",
            "Missing test evidence",
            "No test directory, test files, or test framework indicators were detected.",
            "test evidence",
            ["Add automated tests or documented test execution evidence"],
            owner="Engineering",
            approvers=["Engineering Lead"],
        )
        require(
            docs["configuration_management"] or docs["environment_separation"] or environment_template_present,
            "DEL-012",
            "Missing configuration management notes",
            "No configuration management, environment separation notes, or environment template was detected.",
            "configuration management notes or environment template",
            ["Document configuration management and environment separation", "Add a sanitized environment template"],
            approvers=["DevOps", "Security Architecture"],
        )
        if not ci_cd_present and not release_workflow_present:
            findings.append(_finding(
                "DEL-006",
                "High" if context.profile in {"finance-sox", "production-critical"} else "Medium",
                "Missing CI/CD or release procedure",
                "No CI/CD configuration or release procedure was detected.",
                evidence_value="CI/CD or release procedure",
                decision_impact="Conditional",
                remediation=["Add CI/CD configuration or a documented release procedure", "Include deterministic build and test steps"],
                owner_role="DevOps",
                requires_approval_from=["DevOps", "ITGC"],
            ))

    if context.profile in FINANCE_PROFILES:
        require(
            docs["data_flow"],
            "DEL-007",
            "Missing data flow documentation",
            "Finance/SOX profile requires data flow documentation.",
            "data flow documentation",
            ["Add data flow documentation covering source, transformation, storage, and outputs"],
            severity="High",
            decision="Mandatory Review" if finance_terms_present else "Conditional",
            owner="SOX",
            approvers=["SOX", "Data Governance"],
        )
        for doc_name, title, evidence in [
            ("change_management", "Missing change management evidence", "change management evidence"),
            ("access_control", "Missing access/control documentation", "access/control documentation"),
            ("approval_workflow", "Missing approval workflow documentation", "approval workflow documentation"),
            ("audit_logging", "Missing audit logging evidence", "audit logging evidence"),
        ]:
            require(
                docs[doc_name],
                "DEL-012",
                title,
                f"Finance/SOX profile requires {evidence}.",
                evidence,
                [f"Add {evidence}", "Attach control owner review evidence where required"],
                severity="High",
                decision="Mandatory Review",
                owner="SOX",
                approvers=["SOX", "ITGC"],
            )
        if finance_terms_present:
            require(
                docs["sox_impact"],
                "DEL-007",
                "Missing SOX impact note for finance indicators",
                "Finance indicators were detected but no SOX/control impact note was found.",
                "SOX/control impact note",
                ["Add SOX/control impact assessment", "Obtain SOX owner review"],
                severity="High",
                decision="Mandatory Review",
                owner="SOX",
                approvers=["SOX"],
            )

    if context.profile in PRODUCTION_PROFILES:
        require(
            docs["rollback"] or rollback_script_present,
            "DEL-002",
            "Missing rollback procedure",
            "Production-critical profile requires rollback procedure or rollback automation evidence.",
            "rollback procedure",
            ["Add rollback procedure and validate rollback ownership"],
            severity="Critical",
            decision="Block",
            approvers=["Operations", "Enterprise Architecture"],
        )
        require(
            monitoring_evidence_present,
            "DEL-009",
            "Missing monitoring or health check evidence",
            "Production-critical profile requires monitoring or health check evidence.",
            "monitoring or health check evidence",
            ["Add monitoring documentation or health check endpoint/script evidence"],
            severity="High",
            decision="Conditional",
            approvers=["Operations"],
        )
        require(
            docs["backup_restore"],
            "DEL-010",
            "Missing backup/restore documentation",
            "Production-critical profile requires backup and restore documentation.",
            "backup/restore documentation",
            ["Add backup and restore procedures", "Document recovery ownership and validation"],
            severity="High",
            decision="Conditional",
            approvers=["Operations", "ITGC"],
        )
        require(
            docs["incident_response"],
            "DEL-011",
            "Missing incident response notes",
            "Production-critical profile requires incident response notes.",
            "incident response notes",
            ["Add incident response notes, escalation paths, and owner contacts"],
            severity="High",
            decision="Conditional",
            approvers=["Operations", "Security"],
        )
        require(
            logging_evidence_present,
            "DEL-012",
            "Missing logging or audit evidence",
            "Production-critical profile requires logging or audit evidence.",
            "logging or audit evidence",
            ["Add logging configuration or audit logging documentation"],
            severity="High",
            decision="Conditional",
            approvers=["Operations", "Security"],
        )

    required_signals = [
        docs["readme"],
        docs["installation"],
        docs["deployment"] or deploy_script_present,
        docs["rollback"] or rollback_script_present,
        docs["runbook"],
        docs["architecture"],
        docs["data_flow"],
        docs["security_notes"],
        docs["support"],
        docs["changelog"] or release_workflow_present,
        docs["incident_response"],
        docs["backup_restore"],
        monitoring_evidence_present,
        docs["configuration_management"] or docs["environment_separation"] or environment_template_present,
        docs["operational_ownership"],
        ci_cd_present,
        test_evidence_present,
    ]
    score = round(sum(1 for value in required_signals if value) / len(required_signals) * 100) if required_signals else 100
    metrics = {
        "readme_present": docs["readme"],
        "installation_guide_present": docs["installation"],
        "deployment_guide_present": docs["deployment"],
        "rollback_guide_present": docs["rollback"],
        "runbook_present": docs["runbook"],
        "architecture_overview_present": docs["architecture"],
        "data_flow_documentation_present": docs["data_flow"],
        "security_notes_present": docs["security_notes"],
        "support_model_present": docs["support"],
        "changelog_present": docs["changelog"],
        "ci_cd_present": ci_cd_present,
        "test_evidence_present": test_evidence_present,
        "monitoring_evidence_present": monitoring_evidence_present,
        "backup_restore_documentation_present": docs["backup_restore"],
        "incident_response_notes_present": docs["incident_response"],
        "configuration_management_notes_present": docs["configuration_management"],
        "environment_template_present": environment_template_present,
        "deployment_script_present": deploy_script_present,
        "rollback_script_present": rollback_script_present,
        "health_check_script_or_endpoint_indicator_present": health_script_present or indicators["health_check"],
        "logging_evidence_present": logging_evidence_present,
        "finance_terms_detected": finance_terms_present,
        "delivery_readiness_score": score,
    }
    return {"metrics": metrics, "findings": findings}
