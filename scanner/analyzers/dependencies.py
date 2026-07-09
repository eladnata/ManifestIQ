from __future__ import annotations

import json
import re

from scanner.analyzers.base import AnalyzerContext, make_finding, read_text_safely


def _parse_requirements(text: str) -> list[dict]:
    deps = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        pinned = "==" in stripped
        name = re.split(r"[=<>!~]", stripped)[0].strip()
        deps.append({"name": name, "raw": stripped, "pinned": pinned})
    return deps


def _parse_package_json(text: str) -> list[dict]:
    deps = []
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        return deps
    for section in ["dependencies", "devDependencies"]:
        for name, version in obj.get(section, {}).items():
            deps.append({"name": name, "raw": version, "pinned": not any(ch in version for ch in ["^", "~", "*", "x"]) and version != "latest", "section": section})
    return deps


def analyze(context: AnalyzerContext) -> dict:
    deps = []
    findings = []
    files = {f["path"]: f for f in context.inventory["files"]}

    for rel_path in list(files):
        path = context.root / rel_path
        if path.name == "requirements.txt":
            text = read_text_safely(path) or ""
            for dep in _parse_requirements(text):
                dep["ecosystem"] = "python"
                dep["source_file"] = rel_path
                deps.append(dep)
        elif path.name == "package.json":
            text = read_text_safely(path) or ""
            for dep in _parse_package_json(text):
                dep["ecosystem"] = "npm"
                dep["source_file"] = rel_path
                deps.append(dep)

    lock_files = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "Pipfile.lock", "requirements.lock"}
    has_lock = any(path.split("/")[-1] in lock_files for path in files)

    for dep in deps:
        if dep.get("raw") == "latest" or dep.get("raw") == "*":
            findings.append(make_finding(
                rule_id="DEP-002",
                category="Supply Chain",
                severity="High",
                title=f"Unbounded dependency version: {dep['name']}",
                description="A dependency uses latest, wildcard, or unbounded version syntax.",
                file_path=dep["source_file"],
                confidence="high",
                remediation=["Pin dependency versions and commit lock files"],
            ))
        elif not dep.get("pinned", False) and dep["ecosystem"] in {"python", "npm"}:
            findings.append(make_finding(
                rule_id="DEP-003",
                category="Supply Chain",
                severity="Medium",
                title=f"Dependency is not strictly pinned: {dep['name']}",
                description="Dependency version is not pinned to an exact version.",
                file_path=dep["source_file"],
                confidence="medium",
                remediation=["Pin dependency versions for reproducible builds"],
            ))

    if deps and not has_lock and context.profile in {"enterprise", "finance-sox", "production-critical"}:
        findings.append(make_finding(
            rule_id="DEP-001",
            category="Supply Chain",
            severity="High",
            title="Dependencies found without a lock file",
            description="Dependency manifests exist but no lock file was detected.",
            evidence_type="missing_file",
            confidence="medium",
            remediation=["Generate and commit an approved lock file"],
        ))

    return {"metrics": {"dependency_count": len(deps), "lock_file_detected": has_lock, "dependencies": deps}, "findings": findings}
