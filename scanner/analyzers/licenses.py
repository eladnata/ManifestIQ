from __future__ import annotations

import configparser
import json
import re
import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path

from scanner.analyzers.base import AnalyzerContext, make_finding, read_text_safely
from scanner.core.evidence import write_json

STRICT_PROFILES = {"enterprise", "finance-sox", "production-critical", "ai-enabled"}
AI_PACKAGE_HINTS = {"openai", "anthropic", "langchain", "llama-index", "llamaindex", "transformers", "torch", "tensorflow", "keras", "chromadb", "faiss", "qdrant", "weaviate", "pinecone", "onnxruntime"}
REPO_LICENSE_FILES = {"license", "license.md", "license.txt", "copying"}
NOTICE_FILES = {"notice", "third_party_notices", "third_party_licenses", "oss_notice", "open-source-notices"}
LOCK_FILES = {"package-lock.json", "npm-shrinkwrap.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "Pipfile.lock", "packages.lock.json", "go.sum", "Cargo.lock", "composer.lock"}
MANIFEST_FILES = {"package.json", "requirements.txt", "pyproject.toml", "Pipfile", "pom.xml", "build.gradle", "build.gradle.kts", "go.mod", "Cargo.toml", "composer.json"}
BINARY_EXTENSIONS = {".jar", ".dll", ".exe", ".whl", ".so", ".dylib", ".bin"}
PERMISSIVE = {"MIT", "APACHE-2.0", "BSD-2-CLAUSE", "BSD-3-CLAUSE", "ISC", "ZLIB", "UNLICENSE", "0BSD"}
WEAK_COPYLEFT = {"LGPL-2.1", "LGPL-3.0", "MPL-2.0", "EPL-1.0", "EPL-2.0", "CDDL"}
STRONG_COPYLEFT = {"GPL-2.0", "GPL-3.0"}
RESTRICTIVE = {"AGPL-3.0", "SSPL"}
UNKNOWN_LICENSES = {"UNKNOWN", "UNLICENSED", "LICENSE MISSING", "CUSTOM", "PROPRIETARY"}


def _component(name: str, version: str | None, ecosystem: str, source_file: str, license_value: str | None, scope: str = "unknown", evidence: str | None = None) -> dict:
    classification, risk = classify_license(license_value)
    return {
        "name": name,
        "version": version,
        "ecosystem": ecosystem,
        "source_file": source_file,
        "declared_license": license_value,
        "license_classification": classification,
        "risk_level": risk,
        "scope": scope,
        "evidence": evidence,
    }


def _split_req(raw: str) -> tuple[str, str | None, bool]:
    stripped = raw.strip()
    pinned = "==" in stripped
    parts = re.split(r"==|>=|<=|~=|>|<|!=", stripped, maxsplit=1)
    name = parts[0].strip()
    version = parts[1].strip() if pinned and len(parts) > 1 else None
    return name, version, pinned


def _license_tokens(value: str) -> set[str]:
    return {token.upper() for token in re.split(r"[^A-Za-z0-9.+-]+", value) if token}


def classify_license(value: str | None) -> tuple[str, str]:
    if value is None or not str(value).strip():
        return "missing", "High"
    raw = str(value).strip()
    upper = raw.upper()
    if " OR " in upper or " AND " in upper or "(" in upper or ")" in upper:
        tokens = _license_tokens(raw)
        if tokens & RESTRICTIVE:
            return "ambiguous", "High"
        if tokens & STRONG_COPYLEFT:
            return "ambiguous", "High"
        return "ambiguous", "Medium"
    if upper.startswith("SEE LICENSE IN") or "LICENSEREF" in upper:
        return "ambiguous", "Medium"
    if upper in UNKNOWN_LICENSES or "CUSTOM" in upper:
        return "custom" if "CUSTOM" in upper else "unknown", "High"
    tokens = _license_tokens(raw)
    if tokens & RESTRICTIVE:
        return "restrictive", "Critical" if tokens & {"AGPL-3.0", "SSPL"} else "High"
    if tokens & STRONG_COPYLEFT:
        return "strong_copyleft", "High"
    if tokens & WEAK_COPYLEFT:
        return "weak_copyleft", "Medium"
    if tokens & PERMISSIVE:
        return "permissive", "Low"
    return "unknown", "High"


def _finding(rule_id: str, severity: str, title: str, description: str, *, evidence_value: str, file_path: str | None = None, decision_impact: str = "Conditional", remediation: list[str], category: str = "License Risk", requires_approval_from: list[str] | None = None) -> dict:
    finding = make_finding(
        rule_id=rule_id,
        category=category,
        severity=severity,
        title=title,
        description=description,
        file_path=file_path,
        evidence_type="dependency" if file_path else "metadata",
        confidence="High",
        remediation=remediation,
        owner_role="Legal",
    )
    finding.update({
        "decision_impact": decision_impact,
        "requires_approval_from": requires_approval_from or ["Legal", "Security"],
        "evidence_value": evidence_value,
        "evidence_snippet": evidence_value,
    })
    return finding


def _parse_package_json(path: Path, rel: str) -> list[dict]:
    text = read_text_safely(path) or ""
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        return []
    components = []
    if obj.get("name") and obj.get("version"):
        components.append(_component(obj["name"], obj.get("version"), "npm", rel, obj.get("license"), "production", "package metadata"))
    for section, scope in [("dependencies", "production"), ("devDependencies", "development"), ("optionalDependencies", "optional"), ("peerDependencies", "peer")]:
        for name, version in obj.get(section, {}).items():
            components.append(_component(name, str(version), "npm", rel, None, scope, section))
    return components


def _parse_package_lock(path: Path, rel: str) -> list[dict]:
    text = read_text_safely(path) or ""
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        return []
    components = []
    packages = obj.get("packages", {})
    for package_path, meta in packages.items():
        if not package_path or not package_path.startswith("node_modules/"):
            continue
        name = package_path.removeprefix("node_modules/")
        components.append(_component(name, meta.get("version"), "npm", rel, meta.get("license"), "unknown", "package-lock packages"))
    return components


def _parse_requirements(path: Path, rel: str) -> list[dict]:
    components = []
    for line in (read_text_safely(path) or "").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("-"):
            continue
        name, version, _pinned = _split_req(stripped)
        components.append(_component(name, version, "python", rel, None, "production", stripped))
    return components


def _parse_pyproject(path: Path, rel: str) -> list[dict]:
    try:
        obj = tomllib.loads(path.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, OSError):
        return []
    project = obj.get("project", {})
    components = []
    if project.get("name"):
        license_value = project.get("license")
        if isinstance(license_value, dict):
            license_value = license_value.get("text") or license_value.get("file")
        components.append(_component(project["name"], project.get("version"), "python", rel, license_value, "production", "pyproject project"))
    for dep in project.get("dependencies", []):
        name, version, _pinned = _split_req(dep)
        components.append(_component(name, version, "python", rel, None, "production", dep))
    return components


def _parse_metadata(path: Path, rel: str) -> list[dict]:
    text = read_text_safely(path) or ""
    name = version = license_value = None
    classifiers = []
    for line in text.splitlines():
        if line.startswith("Name:"):
            name = line.split(":", 1)[1].strip()
        elif line.startswith("Version:"):
            version = line.split(":", 1)[1].strip()
        elif line.startswith("License:"):
            license_value = line.split(":", 1)[1].strip()
        elif line.startswith("Classifier:") and "License" in line:
            classifiers.append(line.split(":", 1)[1].strip())
    if not license_value and classifiers:
        license_value = "; ".join(classifiers)
    return [_component(name, version, "python", rel, license_value, "production", "python metadata")] if name else []


def _parse_pom(path: Path, rel: str) -> list[dict]:
    try:
        root = ET.fromstring(path.read_text(encoding="utf-8"))
    except (ET.ParseError, OSError):
        return []
    ns = {"m": root.tag.split("}")[0].strip("{")} if root.tag.startswith("{") else {}
    def find_text(elem, tag):
        found = elem.find(f"m:{tag}", ns) if ns else elem.find(tag)
        return found.text.strip() if found is not None and found.text else None
    components = []
    group = find_text(root, "groupId")
    artifact = find_text(root, "artifactId")
    version = find_text(root, "version")
    license_nodes = root.findall(".//m:license/m:name", ns) if ns else root.findall(".//license/name")
    license_value = license_nodes[0].text.strip() if license_nodes and license_nodes[0].text else None
    if artifact:
        components.append(_component(f"{group}:{artifact}" if group else artifact, version, "maven", rel, license_value, "production", "pom project"))
    dependency_nodes = root.findall(".//m:dependency", ns) if ns else root.findall(".//dependency")
    for dep in dependency_nodes:
        dep_group = find_text(dep, "groupId")
        dep_artifact = find_text(dep, "artifactId")
        dep_version = find_text(dep, "version")
        if dep_artifact:
            components.append(_component(f"{dep_group}:{dep_artifact}" if dep_group else dep_artifact, dep_version, "maven", rel, None, "production", "pom dependency"))
    return components


def _parse_go_mod(path: Path, rel: str) -> list[dict]:
    components = []
    for line in (read_text_safely(path) or "").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("module") or stripped.startswith("go ") or stripped in {"require (", ")"}:
            continue
        parts = stripped.split()
        if len(parts) >= 2:
            components.append(_component(parts[0], parts[1], "go", rel, None, "production", stripped))
    return components


def _parse_composer_json(path: Path, rel: str) -> list[dict]:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    components = []
    if obj.get("name"):
        license_value = obj.get("license")
        if isinstance(license_value, list):
            license_value = " OR ".join(license_value)
        components.append(_component(obj["name"], obj.get("version"), "php", rel, license_value, "production", "composer package"))
    for section, scope in [("require", "production"), ("require-dev", "development")]:
        for name, version in obj.get(section, {}).items():
            if name == "php":
                continue
            components.append(_component(name, str(version), "php", rel, None, scope, section))
    return components


def _parse_cargo_toml(path: Path, rel: str) -> list[dict]:
    try:
        obj = tomllib.loads(path.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, OSError):
        return []
    package = obj.get("package", {})
    components = []
    if package.get("name"):
        components.append(_component(package["name"], package.get("version"), "rust", rel, package.get("license"), "production", "cargo package"))
    for section in ["dependencies", "dev-dependencies"]:
        for name, value in obj.get(section, {}).items():
            version = value.get("version") if isinstance(value, dict) else str(value)
            components.append(_component(name, version, "rust", rel, None, "development" if section.startswith("dev") else "production", section))
    return components


def _parse_setup_cfg(path: Path, rel: str) -> list[dict]:
    parser = configparser.ConfigParser()
    try:
        parser.read(path, encoding="utf-8")
    except configparser.Error:
        return []
    if not parser.has_section("metadata"):
        return []
    name = parser.get("metadata", "name", fallback=None)
    if not name:
        return []
    return [_component(name, parser.get("metadata", "version", fallback=None), "python", rel, parser.get("metadata", "license", fallback=None), "production", "setup.cfg metadata")]


def _components_from_file(path: Path, rel: str) -> list[dict]:
    name = path.name
    lower = rel.lower()
    if name == "package.json":
        return _parse_package_json(path, rel)
    if name in {"package-lock.json", "npm-shrinkwrap.json"}:
        return _parse_package_lock(path, rel)
    if name.startswith("requirements") and name.endswith(".txt"):
        return _parse_requirements(path, rel)
    if name == "pyproject.toml":
        return _parse_pyproject(path, rel)
    if name in {"METADATA", "PKG-INFO"} or lower.endswith(".dist-info/metadata"):
        return _parse_metadata(path, rel)
    if name == "setup.cfg":
        return _parse_setup_cfg(path, rel)
    if name == "pom.xml":
        return _parse_pom(path, rel)
    if name == "go.mod":
        return _parse_go_mod(path, rel)
    if name == "composer.json":
        return _parse_composer_json(path, rel)
    if name == "Cargo.toml":
        return _parse_cargo_toml(path, rel)
    return []


def _dedupe_components(components: list[dict]) -> list[dict]:
    merged = {}
    for component in components:
        key = (component["ecosystem"], component["name"], component.get("version"), component["source_file"])
        if key not in merged:
            merged[key] = component
            continue
        existing = merged[key]
        if not existing.get("declared_license") and component.get("declared_license"):
            existing.update(component)
    return [merged[key] for key in sorted(merged)]


def analyze(context: AnalyzerContext) -> dict:
    files = sorted(context.inventory.get("files", []), key=lambda item: item["path"])
    rel_paths = {item["path"] for item in files}
    lower_paths = {path.lower() for path in rel_paths}
    file_names = {Path(path).name.lower() for path in rel_paths}
    strict = context.profile in STRICT_PROFILES
    repo_license_present = bool(file_names & REPO_LICENSE_FILES)
    notices_present = bool(file_names & NOTICE_FILES)
    vendored_dirs = sorted({path.split("/", 1)[0] for path in lower_paths if path.startswith("vendor/") or "/vendor/" in path or path.startswith("third_party/")})
    binary_artifacts = sorted(item["path"] for item in files if item["extension"] in BINARY_EXTENSIONS)
    manifests = sorted(path for path in rel_paths if Path(path).name in MANIFEST_FILES or Path(path).name.startswith("requirements"))
    locks = sorted(path for path in rel_paths if Path(path).name in LOCK_FILES)

    components = []
    for item in files:
        rel = item["path"]
        components.extend(_components_from_file(context.root / rel, rel))
    components = _dedupe_components(components)
    sbom = {
        "schema": "enterprise-whitebox-local-sbom",
        "schema_version": "0.1",
        "generated_by": "Enterprise White-Box Code Assurance Scanner",
        "components": components,
    }
    if context.evidence_dir:
        write_json(context.evidence_dir / "local-sbom.json", sbom)
    findings = []

    if not repo_license_present:
        findings.append(_finding("LIC-001", "Medium", "Missing repository license file", "No repository-level LICENSE, COPYING, or equivalent file was detected.", evidence_value="repository license file", remediation=["Add repository license declaration or internal-use license notice"], category="Governance"))
    if components and not notices_present:
        findings.append(_finding("LIC-002", "High" if strict else "Medium", "Missing third-party notices", "Dependencies were detected but no third-party notices or OSS attribution file was found.", evidence_value="third-party notices", remediation=["Add THIRD_PARTY_NOTICES or equivalent attribution file"], category="Governance"))

    for component in components:
        classification = component["license_classification"]
        name = component["name"]
        evidence = f"{name}@{component.get('version') or 'unknown'} license={component.get('declared_license') or 'missing'}"
        if classification == "missing":
            findings.append(_finding("LIC-003", "High" if strict else "Medium", "Dependency missing license", "A dependency component has no locally declared license evidence.", file_path=component["source_file"], evidence_value=evidence, decision_impact="Mandatory Review" if strict else "Conditional", remediation=["Add local package metadata with license evidence", "Review dependency license before approval"]))
        elif classification == "unknown":
            findings.append(_finding("LIC-004", "High", "Dependency has unknown license", "A dependency has an unknown or unrecognized license declaration.", file_path=component["source_file"], evidence_value=evidence, decision_impact="Mandatory Review", remediation=["Review license with Legal", "Replace or document approved use"]))
        elif classification == "restrictive":
            rule_id = "LIC-007" if str(component.get("declared_license", "")).upper() in {"AGPL-3.0", "SSPL"} else "LIC-005"
            findings.append(_finding(rule_id, "Critical" if strict and rule_id == "LIC-007" else "High", "Restrictive license detected", "A restrictive license requires enterprise legal/security review.", file_path=component["source_file"], evidence_value=evidence, decision_impact="Block" if strict and rule_id == "LIC-007" else "Mandatory Review", remediation=["Obtain Legal approval", "Assess replacement dependency options"]))
        elif classification == "strong_copyleft":
            findings.append(_finding("LIC-006", "High", "Strong copyleft license requires review", "A strong copyleft license was detected in local metadata.", file_path=component["source_file"], evidence_value=evidence, decision_impact="Mandatory Review", remediation=["Obtain Legal approval", "Document distribution and linking posture"]))
        elif classification == "ambiguous":
            findings.append(_finding("LIC-008", "High" if strict else "Medium", "Ambiguous license expression", "License expression is ambiguous or references another file.", file_path=component["source_file"], evidence_value=evidence, decision_impact="Mandatory Review" if strict else "Conditional", remediation=["Resolve license expression and record approved interpretation"]))
        elif classification == "custom":
            findings.append(_finding("LIC-015", "High", "Custom license requires review", "Custom or proprietary license text requires Legal review.", file_path=component["source_file"], evidence_value=evidence, decision_impact="Mandatory Review", remediation=["Attach Legal approval for custom license"]))
        if context.profile == "ai-enabled" and name.lower() in AI_PACKAGE_HINTS and classification in {"missing", "unknown", "custom", "ambiguous"}:
            findings.append(_finding("LIC-003", "High", "AI dependency missing license evidence", "AI/model-related dependency requires explicit local license evidence for ai-enabled profile.", file_path=component["source_file"], evidence_value=evidence, decision_impact="Mandatory Review", remediation=["Add license evidence for AI/model dependency", "Review AI dependency license with Legal and Security"]))

    license_evidence_present = repo_license_present or notices_present
    for artifact in binary_artifacts:
        findings.append(_finding("LIC-009", "High", "Binary artifact without license evidence", "A binary artifact is present and requires source/provenance/license evidence.", file_path=artifact, evidence_value=artifact, decision_impact="Mandatory Review", remediation=["Remove binary artifact or attach provenance and license evidence"], category="Supply Chain"))
    if vendored_dirs and not notices_present:
        findings.append(_finding("LIC-010", "High", "Vendored dependency without attribution", "Vendored or third-party directory exists without attribution notices.", file_path=vendored_dirs[0], evidence_value=f"vendored_directories={vendored_dirs}", decision_impact="Mandatory Review", remediation=["Add attribution notices for vendored code", "Document provenance"], category="Supply Chain"))
    if manifests and not locks and strict:
        findings.append(_finding("LIC-011", "High", "Dependency manifest without lock file", "Dependency manifests exist but no lock file was detected for reproducible license inventory.", evidence_value=f"manifests={manifests}", remediation=["Commit lock files for dependency manifests"], category="Supply Chain"))
    if locks and not manifests:
        findings.append(_finding("LIC-012", "Medium", "Lock file without matching manifest", "A lock file exists without a matching dependency manifest.", evidence_value=f"lock_files={locks}", remediation=["Add matching manifest or remove stale lock file"], category="Supply Chain"))
    for component in components:
        version = component.get("version")
        if version and any(token in str(version) for token in ["*", "^", "~", ">=", "<=", ">", "<", "x"]):
            findings.append(_finding("LIC-013", "Medium", "Dependency declared without pinned version", "Dependency version is not pinned, reducing reproducible license evidence.", file_path=component["source_file"], evidence_value=f"{component['name']} version={version}", remediation=["Pin dependency versions and regenerate lock files"], category="Supply Chain"))
    if context.evidence_dir is None:
        findings.append(_finding("LIC-014", "Medium", "Missing local SBOM evidence", "Analyzer did not receive an evidence directory, so local-sbom.json was not written.", evidence_value="local-sbom.json", remediation=["Run through the scanner orchestrator to generate evidence package"], category="Governance"))

    counts = {key: 0 for key in ["missing", "unknown", "restrictive", "weak_copyleft", "permissive", "ambiguous", "custom", "strong_copyleft"]}
    for component in components:
        counts[component["license_classification"]] = counts.get(component["license_classification"], 0) + 1
    penalty = (
        counts.get("missing", 0) * 12 + counts.get("unknown", 0) * 15 + counts.get("ambiguous", 0) * 10
        + counts.get("custom", 0) * 15 + counts.get("strong_copyleft", 0) * 20 + counts.get("restrictive", 0) * 30
        + len(binary_artifacts) * 15 + (10 if components and not notices_present else 0) + (8 if not repo_license_present else 0)
    )
    metrics = {
        "repository_license_present": repo_license_present,
        "third_party_notices_present": notices_present,
        "components_detected": len(components),
        "components_with_declared_license": sum(1 for c in components if c.get("declared_license")),
        "components_missing_license": counts.get("missing", 0),
        "components_unknown_license": counts.get("unknown", 0),
        "components_restrictive_license": counts.get("restrictive", 0) + counts.get("strong_copyleft", 0),
        "components_weak_copyleft_license": counts.get("weak_copyleft", 0),
        "components_permissive_license": counts.get("permissive", 0),
        "ambiguous_license_expressions": counts.get("ambiguous", 0),
        "binary_artifacts_detected": len(binary_artifacts),
        "binary_artifacts_without_license_evidence": len(binary_artifacts) if not license_evidence_present else 0,
        "vendored_directories_detected": len(vendored_dirs),
        "local_sbom_generated": context.evidence_dir is not None,
        "local_sbom_path": "local-sbom.json" if context.evidence_dir is not None else None,
        "license_risk_score": max(0, 100 - penalty),
        "components": components,
    }
    return {"metrics": metrics, "findings": findings}
