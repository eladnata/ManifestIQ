from __future__ import annotations

from scanner.analyzers.base import AnalyzerContext, make_finding

REQUIRED_BY_PROFILE = {
    "sandbox": ["README"],
    "team-use": ["README", "OWNER"],
    "department-use": ["README", "OWNER", "CHANGELOG", "RUNBOOK"],
    "enterprise": ["README", "OWNER", "CODEOWNERS", "CHANGELOG", "RUNBOOK", "ARCHITECTURE", "DEPLOYMENT", "SUPPORT", "SECURITY_NOTES"],
    "finance-sox": [
        "README", "OWNER", "CODEOWNERS", "CHANGELOG", "RUNBOOK", "ARCHITECTURE", "DEPLOYMENT", "SUPPORT",
        "SECURITY_NOTES", "SOX_IMPACT", "DATA_FLOW", "CONTROL_OWNER", "CHANGE_MANAGEMENT", "ACCESS_CONTROL",
        "AUDIT_LOGGING", "APPROVAL_WORKFLOW",
    ],
    "ai-enabled": [
        "README", "OWNER", "CODEOWNERS", "RUNBOOK", "ARCHITECTURE", "DEPLOYMENT", "SUPPORT", "SECURITY_NOTES",
        "AI_USAGE", "AI_ARCHITECTURE", "MODEL_INVENTORY", "DATA_FLOW", "DATA_CLASSIFICATION", "PROVIDER_RISK",
    ],
    "production-critical": [
        "README", "OWNER", "CODEOWNERS", "CHANGELOG", "RUNBOOK", "ARCHITECTURE", "DEPLOYMENT", "SUPPORT",
        "DATA_FLOW", "ROLLBACK", "MONITORING", "BACKUP_RESTORE", "INCIDENT_RESPONSE", "SECURITY_NOTES",
    ],
}

DOC_MARKERS = {
    "README": ["readme.md", "readme.txt"],
    "OWNER": ["owners.md", "owner.md", "codeowners", ".github/codeowners"],
    "CODEOWNERS": ["codeowners", ".github/codeowners"],
    "CHANGELOG": ["changelog.md", "change_log.md"],
    "RUNBOOK": ["runbook.md", "docs/runbook.md", "operations.md"],
    "ARCHITECTURE": ["architecture.md", "docs/architecture.md", "architecture-overview.md"],
    "DEPLOYMENT": ["deployment.md", "deploy.md", "docs/deployment.md", "docs/deploy.md"],
    "SUPPORT": ["support.md", "docs/support.md"],
    "SECURITY_NOTES": ["security.md", "security-notes.md", "docs/security.md", "docs/security-notes.md"],
    "SOX_IMPACT": ["sox.md", "sox-impact.md", "docs/sox-impact.md"],
    "DATA_FLOW": ["data-flow.md", "docs/data-flow.md", "data_classification.md"],
    "DATA_CLASSIFICATION": ["data-classification.md", "data_classification.md", "docs/data-classification.md"],
    "ROLLBACK": ["rollback.md", "docs/rollback.md"],
    "CONTROL_OWNER": ["control-owner.md", "controls.md", "docs/control-owner.md", "docs/controls.md"],
    "CHANGE_MANAGEMENT": ["change-management.md", "docs/change-management.md"],
    "ACCESS_CONTROL": ["access-control.md", "docs/access-control.md"],
    "AUDIT_LOGGING": ["audit-logging.md", "docs/audit-logging.md"],
    "APPROVAL_WORKFLOW": ["approval-workflow.md", "docs/approval-workflow.md"],
    "AI_USAGE": ["ai.md", "ai-usage.md", "docs/ai-usage.md"],
    "AI_ARCHITECTURE": ["ai-architecture.md", "ai_architecture.md", "docs/ai-architecture.md"],
    "MODEL_INVENTORY": ["model-inventory.md", "model_inventory.md", "docs/model-inventory.md"],
    "PROVIDER_RISK": ["provider-risk.md", "ai-provider-risk.md", "docs/provider-risk.md"],
    "MONITORING": ["monitoring.md", "healthcheck.md", "health-check.md", "docs/monitoring.md"],
    "BACKUP_RESTORE": ["backup-restore.md", "backup.md", "restore.md", "docs/backup-restore.md"],
    "INCIDENT_RESPONSE": ["incident-response.md", "docs/incident-response.md"],
}


def analyze(context: AnalyzerContext) -> dict:
    files = {f["path"].lower() for f in context.inventory["files"]}
    required = REQUIRED_BY_PROFILE.get(context.profile, REQUIRED_BY_PROFILE["enterprise"])
    present = []
    missing = []
    for doc_type in required:
        markers = DOC_MARKERS[doc_type]
        if any(marker in files or any(path.endswith(marker) for path in files) for marker in markers):
            present.append(doc_type)
        else:
            missing.append(doc_type)

    findings = []
    for doc_type in missing:
        severity = "High" if doc_type in {
            "OWNER", "CODEOWNERS", "RUNBOOK", "ARCHITECTURE", "DEPLOYMENT", "SOX_IMPACT", "DATA_FLOW",
            "CONTROL_OWNER", "ACCESS_CONTROL", "AUDIT_LOGGING", "APPROVAL_WORKFLOW", "AI_USAGE",
            "AI_ARCHITECTURE", "MODEL_INVENTORY", "DATA_CLASSIFICATION", "ROLLBACK", "MONITORING",
            "BACKUP_RESTORE", "INCIDENT_RESPONSE",
        } else "Medium"
        findings.append(make_finding(
            rule_id="DOC-001" if doc_type != "OWNER" else "GOV-001",
            category="Documentation" if doc_type != "OWNER" else "Governance",
            severity=severity,
            title=f"Missing required documentation: {doc_type}",
            description=f"The {doc_type} documentation artifact is required for profile {context.profile}.",
            evidence_type="missing_file",
            confidence="high",
            remediation=[f"Add {doc_type} documentation artifact"],
            owner_role="System Owner" if doc_type == "OWNER" else "Technical Owner",
        ))

    score = round((len(present) / len(required)) * 100, 2) if required else 100
    return {"metrics": {"documentation_score": score, "required_docs": required, "present_docs": present, "missing_docs": missing}, "findings": findings}
