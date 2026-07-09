from __future__ import annotations

from scanner.analyzers.base import AnalyzerContext, make_finding, read_text_safely


def analyze(context: AnalyzerContext) -> dict:
    findings = []
    large_files = []
    long_files = []
    test_files = []
    logging_indicators = 0

    for file_info in context.inventory["files"]:
        rel = file_info["path"]
        size = file_info["size_bytes"]
        if size > 500_000:
            large_files.append(rel)
            findings.append(make_finding(
                rule_id="MAINT-001",
                category="Maintainability",
                severity="Medium",
                title="Large source file detected",
                description="Large files are harder to review and maintain.",
                file_path=rel,
                evidence_type="file_metric",
                remediation=["Split large files into smaller modules"],
            ))
        if "test" in rel.lower() or rel.lower().startswith("tests/"):
            test_files.append(rel)
        path = context.root / rel
        if path.suffix.lower() in {".py", ".js", ".ts", ".java", ".cs", ".go"}:
            text = read_text_safely(path)
            if text:
                line_count = len(text.splitlines())
                if line_count > 500:
                    long_files.append(rel)
                    findings.append(make_finding(
                        rule_id="MAINT-002",
                        category="Maintainability",
                        severity="Medium",
                        title="Long source file detected",
                        description=f"File has {line_count} lines.",
                        file_path=rel,
                        evidence_type="file_metric",
                        remediation=["Refactor long files into smaller modules"],
                    ))
                if any(token in text for token in ["logging.", "logger.", "console.log", "print("]):
                    logging_indicators += 1

    if not test_files and context.profile in {"enterprise", "finance-sox", "production-critical"}:
        findings.append(make_finding(
            rule_id="MAINT-003",
            category="Maintainability",
            severity="High",
            title="No test files detected",
            description="No test files or test folders were detected.",
            evidence_type="missing_file",
            remediation=["Add automated tests or document test approach"],
        ))

    if logging_indicators == 0 and context.profile in {"enterprise", "finance-sox", "production-critical"}:
        findings.append(make_finding(
            rule_id="OPS-001",
            category="Operations",
            severity="High",
            title="No logging indicators detected",
            description="No logging-related code patterns were detected.",
            evidence_type="code_metric",
            remediation=["Add application logging for operational support"],
        ))

    return {"metrics": {"large_files": large_files, "long_files": long_files, "test_file_count": len(test_files), "logging_indicator_count": logging_indicators}, "findings": findings}
