from __future__ import annotations

import re

from scanner.analyzers.base import AnalyzerContext, iter_text_files, make_finding

SECRET_PATTERNS = [
    ("AWS Access Key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("Private Key", re.compile(r"-----BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("GitHub Token", re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}")),
    ("Generic API Key", re.compile(r"(?i)(api[_-]?key|token|secret)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}")),
    ("Password Assignment", re.compile(r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"]?[^'\"\s]{6,}")),
    ("Connection String", re.compile(r"(?i)(server=.*;.*(user id|uid)=.*;.*(password|pwd)=)")),
]


def analyze(context: AnalyzerContext) -> dict:
    findings = []
    confirmed = 0
    potential = 0
    for path, text in iter_text_files(context.root):
        rel = path.relative_to(context.root).as_posix()
        if rel.endswith(".env.example"):
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            for label, pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    confirmed += 1 if label in {"AWS Access Key", "Private Key", "GitHub Token", "Connection String"} else 0
                    potential += 1
                    findings.append(make_finding(
                        rule_id="SEC-001",
                        category="Security",
                        severity="Critical" if label in {"AWS Access Key", "Private Key", "GitHub Token", "Connection String"} else "High",
                        title=f"Potential hardcoded secret detected: {label}",
                        description="A credential-like value was found in source files.",
                        file_path=rel,
                        line_start=line_no,
                        line_end=line_no,
                        confidence="high" if label in {"AWS Access Key", "Private Key", "GitHub Token", "Connection String"} else "medium",
                        remediation=[
                            "Remove the secret from source code",
                            "Rotate the credential if it was real",
                            "Move secrets to approved secret storage",
                            "Re-run the scanner",
                        ],
                    ))
    return {"metrics": {"confirmed_secret_count": confirmed, "potential_secret_count": potential}, "findings": findings}
