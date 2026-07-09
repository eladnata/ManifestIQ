from __future__ import annotations

import re

from scanner.analyzers.base import AnalyzerContext, iter_text_files, make_finding

CONFIG_PATTERNS = [
    ("CFG-001", "Debug mode enabled", "High", re.compile(r"(?i)\bdebug\b\s*[:=]\s*(true|1|yes|on)"), "Disable debug mode outside local development"),
    ("CFG-002", "TLS/SSL verification disabled", "High", re.compile(r"(?i)(verify_ssl|ssl_verify|rejectUnauthorized)\s*[:=]\s*(false|0|no)"), "Enable TLS/SSL certificate verification"),
    ("CFG-003", "Wildcard CORS or public origin allowed", "High", re.compile(r"(?i)(allow_all_origins\s*[:=]\s*true|cors.*\*)"), "Restrict CORS origins"),
    ("CFG-004", "Service binds to all interfaces", "Medium", re.compile(r"0\.0\.0\.0"), "Confirm this exposure is intended and protected"),
    ("CFG-005", "Default admin credential pattern", "High", re.compile(r"(?i)(admin/admin|admin\s*[:=]\s*admin)"), "Remove default credentials"),
]


def analyze(context: AnalyzerContext) -> dict:
    findings = []
    for path, text in iter_text_files(context.root):
        rel = path.relative_to(context.root).as_posix()
        if not any(token in rel.lower() for token in ["config", ".env", "settings", "docker", "compose", "yaml", "yml", "json", "toml", "ini", "py", "js", "ts"]):
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            for rule_id, title, severity, pattern, remediation in CONFIG_PATTERNS:
                if pattern.search(line):
                    findings.append(make_finding(
                        rule_id=rule_id,
                        category="Configuration",
                        severity=severity,
                        title=title,
                        description="Risky configuration value detected.",
                        file_path=rel,
                        line_start=line_no,
                        line_end=line_no,
                        confidence="medium",
                        remediation=[remediation],
                    ))
    return {"metrics": {"config_finding_count": len(findings)}, "findings": findings}
