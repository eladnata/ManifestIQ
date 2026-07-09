from __future__ import annotations

import re

from scanner.analyzers.base import AnalyzerContext, iter_text_files, make_finding

SAST_PATTERNS = [
    ("SEC-002", "Unsafe dynamic execution", "Critical", re.compile(r"\b(eval|exec)\s*\("), "Avoid eval/exec or strictly validate input"),
    ("SEC-003", "Potential command injection", "Critical", re.compile(r"(subprocess\.(run|call|Popen)|os\.system)\s*\(.*shell\s*=\s*True"), "Avoid shell=True and pass command arguments safely"),
    ("SEC-004", "Potential SQL injection via string formatting", "High", re.compile(r"(?i)(select|insert|update|delete).*(\+|%\s|\.format\(|f['\"])", re.IGNORECASE), "Use parameterized queries"),
    ("SEC-005", "Insecure pickle deserialization", "Critical", re.compile(r"pickle\.loads?\s*\("), "Avoid unsafe deserialization of untrusted input"),
    ("SEC-006", "Weak hash algorithm", "High", re.compile(r"hashlib\.(md5|sha1)\s*\("), "Use SHA-256 or approved algorithms unless explicitly non-security use"),
]


def analyze(context: AnalyzerContext) -> dict:
    findings = []
    for path, text in iter_text_files(context.root):
        rel = path.relative_to(context.root).as_posix()
        if path.suffix.lower() not in {".py", ".js", ".ts", ".java", ".cs", ".go", ".ps1", ".php", ".rb"}:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            for rule_id, title, severity, pattern, remediation in SAST_PATTERNS:
                if pattern.search(line):
                    findings.append(make_finding(
                        rule_id=rule_id,
                        category="Security",
                        severity=severity,
                        title=title,
                        description="Static code pattern indicates a potential security weakness.",
                        file_path=rel,
                        line_start=line_no,
                        line_end=line_no,
                        confidence="medium",
                        remediation=[remediation],
                    ))
    return {"metrics": {"sast_finding_count": len(findings)}, "findings": findings}
