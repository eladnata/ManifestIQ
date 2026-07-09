from __future__ import annotations

import re

from scanner.analyzers.base import AnalyzerContext, iter_text_files, make_finding

SOX_TERMS = [
    "journal", "gl", "ledger", "reconciliation", "revenue", "billing", "invoice", "payment", "vendor",
    "customer balance", "trial balance", "financial close", "posting", "approval", "control", "sap", "sox",
    "segregation of duties"
]


def analyze(context: AnalyzerContext) -> dict:
    pattern = re.compile(r"\b(" + "|".join(re.escape(t) for t in SOX_TERMS) + r")\b", re.IGNORECASE)
    matched_terms = set()
    evidence = []
    findings = []
    for path, text in iter_text_files(context.root):
        rel = path.relative_to(context.root).as_posix()
        for line_no, line in enumerate(text.splitlines(), start=1):
            match = pattern.search(line)
            if match:
                term = match.group(1).lower()
                matched_terms.add(term)
                if len(evidence) < 20:
                    evidence.append({"file_path": rel, "line": line_no, "term": term})
    if matched_terms:
        findings.append(make_finding(
            rule_id="SOX-001",
            category="SOX",
            severity="High",
            title="Potential SOX/Finance impact detected",
            description="Finance or control-related terms were detected. Human SOX/control review may be required before production use.",
            evidence_type="keyword_match",
            confidence="medium",
            remediation=["Complete SOX impact assessment", "Identify impacted processes and controls", "Attach approval before production use"],
            owner_role="SOX Owner",
        ))
    return {"metrics": {"sox_finance_impact": "potential" if matched_terms else "none", "matched_terms": sorted(matched_terms), "evidence": evidence}, "findings": findings}
