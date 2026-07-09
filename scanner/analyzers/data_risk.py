from __future__ import annotations

import re

from scanner.analyzers.base import AnalyzerContext, iter_text_files, make_finding

SENSITIVE_TERMS = [
    "customer", "client", "email", "phone", "passport", "id_number", "bank", "iban", "credit", "salary",
    "invoice", "payment", "vendor", "employee", "payroll", "address"
]
SENSITIVE_EXTENSIONS = {".csv", ".xlsx", ".xls", ".sqlite", ".db", ".bak", ".dump", ".sql", ".log"}


def analyze(context: AnalyzerContext) -> dict:
    findings = []
    term_hits = []
    for file_info in context.inventory["files"]:
        path = file_info["path"]
        ext = file_info["extension"]
        if ext in SENSITIVE_EXTENSIONS:
            severity = "High" if ext in {".sqlite", ".db", ".dump", ".bak", ".sql"} else "Medium"
            findings.append(make_finding(
                rule_id="DATA-001",
                category="Data Protection",
                severity=severity,
                title=f"Potential sensitive data file committed: {path}",
                description="A data-like file exists in the source package and may contain sensitive or business data.",
                file_path=path,
                evidence_type="file_extension",
                confidence="medium",
                remediation=["Remove sample or real data from source package", "Add data classification note", "Use sanitized test data only"],
                owner_role="System Owner",
            ))

    term_pattern = re.compile(r"\b(" + "|".join(map(re.escape, SENSITIVE_TERMS)) + r")\b", re.IGNORECASE)
    for path, text in iter_text_files(context.root):
        rel = path.relative_to(context.root).as_posix()
        for line_no, line in enumerate(text.splitlines(), start=1):
            match = term_pattern.search(line)
            if match:
                term_hits.append(match.group(1).lower())
                if len(term_hits) <= 25:
                    findings.append(make_finding(
                        rule_id="DATA-002",
                        category="Data Protection",
                        severity="Medium",
                        title="Sensitive data indicator detected",
                        description=f"Sensitive data keyword detected: {match.group(1)}",
                        file_path=rel,
                        line_start=line_no,
                        line_end=line_no,
                        confidence="low",
                        remediation=["Confirm data classification", "Document whether real or sanitized data is used"],
                        owner_role="System Owner",
                    ))
    return {"metrics": {"sensitive_keyword_hits": len(term_hits), "unique_terms": sorted(set(term_hits))}, "findings": findings}
