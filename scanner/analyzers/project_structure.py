from __future__ import annotations

from pathlib import Path

from scanner.analyzers.base import AnalyzerContext, make_finding

STRICT_PROFILES = {"enterprise", "finance-sox", "production-critical", "ai-enabled"}
PRODUCTION_PROFILES = {"production-critical"}
SOURCE_DIR_NAMES = {"src", "app", "apps", "lib", "libs", "scanner", "package", "packages", "services"}
TEST_DIR_NAMES = {"test", "tests", "__tests__", "spec", "specs"}
CI_PATH_PREFIXES = {".github/workflows", ".gitlab-ci.yml", "azure-pipelines.yml", "Jenkinsfile", ".circleci", "bitbucket-pipelines.yml"}
ENTRY_POINT_NAMES = {
    "main.py", "app.py", "__main__.py", "server.py", "manage.py", "index.js", "server.js", "app.js",
    "main.go", "Program.cs", "pom.xml", "build.gradle", "package.json", "pyproject.toml",
}
BUILD_FILES = {
    "pyproject.toml", "setup.py", "requirements.txt", "package.json", "pom.xml", "build.gradle", "go.mod",
    "Cargo.toml", ".csproj", "composer.json",
}
PACKAGE_MANIFESTS = {"package.json", "requirements.txt", "pyproject.toml", "Pipfile", "poetry.lock", "pom.xml", "build.gradle", "go.mod"}
LOCK_FILES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "Pipfile.lock", "requirements.lock", "go.sum"}
OWNER_FILES = {"codeowners", "owners.md", "owner.md", "maintainers.md", "maintainers", ".github/codeowners"}
CONFIG_TEMPLATE_NAMES = {".env.example", ".env.template", "config.example.yml", "config.example.yaml", "settings.example.toml"}
GENERATED_DIR_NAMES = {"dist", "build", "target", "coverage", "vendor", "generated"}
TEMP_CACHE_DIR_NAMES = {"tmp", "temp", ".cache", ".pytest_cache", "__pycache__"}
KNOWN_HIDDEN_DIRS = {".github", ".gitlab", ".vscode", ".idea"}
BINARY_EXTENSIONS = {".exe", ".dll", ".so", ".dylib", ".bin", ".class", ".jar", ".war", ".ear"}
ARCHIVE_EXTENSIONS = {".zip", ".tar", ".gz", ".tgz", ".rar", ".7z"}
DATABASE_EXTENSIONS = {".sqlite", ".db", ".sqlite3", ".mdb"}
LOG_EXTENSIONS = {".log"}
SCRIPT_EXTENSIONS = {".sh", ".ps1", ".bat", ".cmd"}
SOURCE_EXTENSIONS = {".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".cs", ".go", ".rb", ".php"}
TEST_FRAMEWORK_TOKENS = {"pytest", "unittest", "jest", "mocha", "vitest", "junit", "xunit", "nunit", "go test"}


def _rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _all_dirs(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_dir())


def _first_part(path: str) -> str:
    return path.split("/", 1)[0]


def _has_ci(rel_paths: set[str]) -> bool:
    return any(
        rel in CI_PATH_PREFIXES or any(rel.startswith(prefix + "/") for prefix in CI_PATH_PREFIXES)
        for rel in rel_paths
    )


def _finding(
    rule_id: str,
    severity: str,
    title: str,
    description: str,
    *,
    file_path: str | None = None,
    evidence_type: str = "metadata",
    evidence_value: str,
    decision_impact: str = "Conditional",
    remediation: list[str],
    owner_role: str = "Architecture",
    requires_approval_from: list[str] | None = None,
) -> dict:
    finding = make_finding(
        rule_id=rule_id,
        category="Architecture",
        severity=severity,
        title=title,
        description=description,
        file_path=file_path,
        evidence_type=evidence_type,
        confidence="High",
        remediation=remediation,
        owner_role=owner_role,
    )
    finding.update({
        "decision_impact": decision_impact,
        "requires_approval_from": requires_approval_from or ["Enterprise Architecture"],
        "evidence_value": evidence_value,
        "evidence_snippet": evidence_value,
    })
    return finding


def analyze(context: AnalyzerContext) -> dict:
    files = sorted(context.inventory.get("files", []), key=lambda item: item["path"])
    rel_paths = {item["path"] for item in files}
    lower_paths = {path.lower() for path in rel_paths}
    root_files = [path for path in rel_paths if "/" not in path]
    source_files = [item for item in files if item["extension"] in SOURCE_EXTENSIONS]
    source_roots = sorted({_first_part(item["path"]) for item in source_files if "/" in item["path"]})
    source_directory_detected = bool({root.lower() for root in source_roots} & SOURCE_DIR_NAMES)
    test_dirs = sorted(dir_path.name for dir_path in _all_dirs(context.root) if dir_path.name.lower() in TEST_DIR_NAMES)
    test_files = [path for path in rel_paths if "test" in path.lower() or "spec" in path.lower()]
    unit_test_indicators = [path for path in test_files if "unit" in path.lower()]
    integration_test_indicators = [path for path in test_files if "integration" in path.lower() or "e2e" in path.lower()]
    ci_cd_detected = _has_ci(rel_paths)
    entry_points = sorted(path for path in rel_paths if Path(path).name in ENTRY_POINT_NAMES)
    binary_files = sorted(item["path"] for item in files if item["extension"] in BINARY_EXTENSIONS)
    archive_files = sorted(item["path"] for item in files if item["extension"] in ARCHIVE_EXTENSIONS)
    database_files = sorted(item["path"] for item in files if item["extension"] in DATABASE_EXTENSIONS)
    log_files = sorted(item["path"] for item in files if item["extension"] in LOG_EXTENSIONS)
    script_files = sorted(item["path"] for item in files if item["extension"] in SCRIPT_EXTENSIONS)
    hidden_dirs = sorted(_rel(path, context.root) for path in _all_dirs(context.root) if path.name.startswith(".") and path.name not in {".git"})
    suspicious_hidden_dirs = [path for path in hidden_dirs if Path(path).name not in KNOWN_HIDDEN_DIRS]
    owner_files = sorted(path for path in rel_paths if path.lower() in OWNER_FILES or path.lower().endswith("/codeowners"))
    build_files = sorted(path for path in rel_paths if Path(path).name in BUILD_FILES or Path(path).suffix == ".csproj")
    manifests = sorted(path for path in rel_paths if Path(path).name in PACKAGE_MANIFESTS)
    lock_files = sorted(path for path in rel_paths if Path(path).name in LOCK_FILES)
    config_templates = sorted(path for path in rel_paths if Path(path).name in CONFIG_TEMPLATE_NAMES)
    generated_files = sorted(path for path in rel_paths if any(part.lower() in GENERATED_DIR_NAMES for part in path.split("/")))
    temp_cache_files = sorted(path for path in rel_paths if any(part.lower() in TEMP_CACHE_DIR_NAMES for part in path.split("/")))
    max_depth = max((path.count("/") + 1 for path in rel_paths), default=0)
    app_roots = sorted({_first_part(path) for path in manifests if "/" in path})

    text_for_framework_detection = " ".join(lower_paths)
    test_framework_detected = any(token in text_for_framework_detection for token in TEST_FRAMEWORK_TOKENS)

    findings = []
    strict = context.profile in STRICT_PROFILES
    production = context.profile in PRODUCTION_PROFILES

    if not entry_points and source_files:
        findings.append(_finding(
            "ARCH-001",
            "High",
            "No clear entry point detected",
            "Source files are present, but no common application entry point or build descriptor was detected.",
            evidence_value="entry_points_detected=[]",
            decision_impact="Block" if production else "Conditional",
            remediation=["Add a documented entry point or build descriptor", "Document startup commands in README or deployment documentation"],
        ))

    if source_files and not source_directory_detected and len(source_files) > 1:
        findings.append(_finding(
            "ARCH-002",
            "High" if strict else "Medium",
            "Missing recognizable source directory",
            "Source code exists but no conventional source directory such as src, app, lib, package, or services was detected.",
            evidence_value=f"source_roots={source_roots or ['repository root']}",
            remediation=["Move source code into a recognizable source directory", "Document module boundaries"],
        ))

    language_count = len(context.inventory.get("languages", {}))
    if language_count >= 4 and len(manifests) >= 2:
        findings.append(_finding(
            "ARCH-003",
            "High",
            "Mixed unrelated technology stacks detected",
            "Multiple language ecosystems and dependency manifests were detected. This may indicate unrelated applications in one repository.",
            evidence_value=f"languages={sorted(context.inventory.get('languages', {}).keys())}; manifests={manifests}",
            decision_impact="Mandatory Review",
            remediation=["Split unrelated applications or document repository boundaries", "Identify owning teams and release units"],
        ))

    if len(app_roots) > 1:
        findings.append(_finding(
            "ARCH-003",
            "High",
            "Multiple application roots detected",
            "Dependency manifests exist under multiple top-level directories, which may indicate multiple applications in one repository.",
            evidence_value=f"application_roots={app_roots}",
            decision_impact="Mandatory Review",
            remediation=["Document repository application boundaries", "Split unrelated applications where appropriate"],
        ))

    if len(root_files) > 20:
        findings.append(_finding(
            "ARCH-004",
            "Medium" if context.profile == "sandbox" else "High",
            "Excessive root-level files",
            "The repository root contains many files, which makes ownership, packaging, and review boundaries harder to verify.",
            evidence_value=f"root_file_count={len(root_files)}",
            remediation=["Move source, docs, scripts, and configuration into clear directories", "Keep root-level files limited to package metadata and key documentation"],
        ))

    if max_depth > 8:
        findings.append(_finding(
            "ARCH-004",
            "Medium",
            "Excessive nested folder depth",
            "Repository folder nesting is unusually deep and may obscure module boundaries.",
            evidence_value=f"max_depth={max_depth}",
            remediation=["Flatten unnecessarily deep folder structures", "Document module boundaries"],
        ))

    for hidden_dir in suspicious_hidden_dirs:
        findings.append(_finding(
            "ARCH-005",
            "Medium",
            "Suspicious hidden directory committed",
            "A hidden directory outside common repository metadata locations was detected.",
            file_path=hidden_dir,
            evidence_type="file_presence",
            evidence_value=hidden_dir,
            remediation=["Remove local hidden directories from source control", "Document any intentional hidden directory"],
        ))

    for file_path in binary_files:
        findings.append(_finding(
            "ARCH-006",
            "High",
            "Committed binary artifact detected",
            "A binary artifact is committed to the repository and requires provenance review.",
            file_path=file_path,
            evidence_type="file_presence",
            evidence_value=file_path,
            decision_impact="Mandatory Review",
            remediation=["Remove generated binary artifacts or document approved provenance", "Store build outputs outside source control"],
        ))

    for file_path in archive_files:
        findings.append(_finding(
            "ARCH-007",
            "High" if strict else "Medium",
            "Committed archive artifact detected",
            "An archive artifact is committed to the repository and may hide unreviewed source or binaries.",
            file_path=file_path,
            evidence_type="file_presence",
            evidence_value=file_path,
            remediation=["Remove archive artifacts from source control", "Document any approved packaged evidence separately"],
        ))

    for file_path in database_files:
        findings.append(_finding(
            "ARCH-008",
            "Critical" if context.profile in {"finance-sox", "production-critical"} else "High",
            "Committed local database file detected",
            "A local database file is committed to the repository and may contain sensitive or operational data.",
            file_path=file_path,
            evidence_type="file_presence",
            evidence_value=file_path,
            decision_impact="Mandatory Review",
            remediation=["Remove local database files from source control", "Replace with sanitized fixtures where required", "Document data classification"],
            requires_approval_from=["Data Governance", "Security Architecture"],
        ))

    if strict and not test_dirs and not test_files:
        findings.append(_finding(
            "ARCH-009",
            "High",
            "Missing test structure",
            "No tests directory or test file indicators were detected for a strict assurance profile.",
            evidence_type="missing_file",
            evidence_value="tests directory or test files",
            remediation=["Add automated tests under a recognizable tests directory", "Document test execution evidence"],
            owner_role="Engineering",
            requires_approval_from=["Engineering Lead"],
        ))
    elif test_files and not test_framework_detected:
        findings.append(_finding(
            "ARCH-009",
            "Medium",
            "Test files present but no test framework detected",
            "Test-like files were detected, but no common test framework indicator was found in manifests or file names.",
            evidence_value=f"test_files={sorted(test_files)[:10]}",
            remediation=["Add or document the test framework", "Ensure tests can be executed deterministically"],
            owner_role="Engineering",
        ))

    if strict and not ci_cd_detected:
        findings.append(_finding(
            "ARCH-010",
            "High" if context.profile in {"finance-sox", "production-critical"} else "Medium",
            "Missing CI/CD definition",
            "No common CI/CD configuration was detected for a strict assurance profile.",
            evidence_type="missing_file",
            evidence_value="CI/CD configuration",
            remediation=["Add CI/CD workflow configuration or documented release procedure", "Include deterministic test/build steps"],
            owner_role="DevOps",
            requires_approval_from=["DevOps", "ITGC"],
        ))

    if source_files and not build_files and strict:
        findings.append(_finding(
            "ARCH-010",
            "Medium",
            "Missing build or package manager file",
            "Source code exists but no common build or package manager descriptor was detected.",
            evidence_type="missing_file",
            evidence_value="build/package descriptor",
            remediation=["Add a build descriptor or package manager file", "Document build commands"],
            owner_role="Engineering",
        ))

    if manifests and not lock_files and strict:
        findings.append(_finding(
            "ARCH-010",
            "Medium",
            "Missing dependency lock file",
            "Dependency manifests exist but no lock file was detected in project structure review.",
            evidence_type="missing_file",
            evidence_value=f"manifests={manifests}",
            remediation=["Generate and commit lock files for reproducible builds"],
            owner_role="Engineering",
        ))

    if strict and not config_templates:
        findings.append(_finding(
            "ARCH-010",
            "Medium",
            "Missing environment configuration template",
            "No .env.example or equivalent configuration template was detected.",
            evidence_type="missing_file",
            evidence_value="environment template",
            remediation=["Add a sanitized environment template", "Document required configuration variables"],
            owner_role="DevOps",
        ))

    if strict and not owner_files:
        findings.append(_finding(
            "ARCH-011",
            "High",
            "Missing owner metadata",
            "No CODEOWNERS, OWNERS.md, or maintainers file was detected.",
            evidence_type="missing_file",
            evidence_value="CODEOWNERS/OWNERS/MAINTAINERS",
            decision_impact="Block" if context.profile in {"finance-sox", "production-critical"} else "Conditional",
            remediation=["Add CODEOWNERS or OWNERS.md", "Identify technical and operational owners"],
            owner_role="Business Owner",
            requires_approval_from=["ITGC", "Engineering Lead"],
        ))

    unmanaged_scripts = [path for path in script_files if not (path.startswith("scripts/") or path.startswith("tools/"))]
    if len(unmanaged_scripts) >= 3 or len(script_files) > 8:
        findings.append(_finding(
            "ARCH-012",
            "High" if strict else "Medium",
            "Excessive unmanaged scripts detected",
            "Shell or PowerShell scripts were found outside a managed scripts/tools structure or exceed expected volume.",
            evidence_value=f"script_files={script_files}",
            remediation=["Move scripts under a managed scripts or tools directory", "Document script purpose, ownership, and execution controls"],
            owner_role="DevOps",
        ))

    for file_path in log_files:
        findings.append(_finding(
            "ARCH-012",
            "Medium",
            "Committed log file detected",
            "A log file is committed to the repository and may contain sensitive or environment-specific data.",
            file_path=file_path,
            evidence_type="file_presence",
            evidence_value=file_path,
            remediation=["Remove committed log files", "Add log patterns to .gitignore"],
            owner_role="Engineering",
        ))

    if generated_files:
        findings.append(_finding(
            "ARCH-012",
            "Medium",
            "Generated or vendor code committed",
            "Generated, build, target, vendor, or coverage files were detected in source control.",
            file_path=generated_files[0],
            evidence_type="file_presence",
            evidence_value=f"generated_file_count={len(generated_files)}",
            remediation=["Remove generated or vendor artifacts unless explicitly approved", "Document provenance when vendored code is required"],
            owner_role="Engineering",
        ))

    if temp_cache_files:
        findings.append(_finding(
            "ARCH-012",
            "Medium",
            "Temporary or cache files committed",
            "Temporary or cache directories appear to be committed.",
            file_path=temp_cache_files[0],
            evidence_type="file_presence",
            evidence_value=f"temp_cache_file_count={len(temp_cache_files)}",
            remediation=["Remove temporary/cache artifacts", "Update .gitignore"],
            owner_role="Engineering",
        ))

    metrics = {
        "root_file_count": len(root_files),
        "source_directory_detected": source_directory_detected,
        "test_directory_detected": bool(test_dirs),
        "unit_test_indicator_detected": bool(unit_test_indicators),
        "integration_test_indicator_detected": bool(integration_test_indicators),
        "ci_cd_detected": ci_cd_detected,
        "entry_points_detected": entry_points,
        "binary_file_count": len(binary_files),
        "archive_file_count": len(archive_files),
        "database_file_count": len(database_files),
        "log_file_count": len(log_files),
        "script_file_count": len(script_files),
        "hidden_directory_count": len(hidden_dirs),
        "owner_files_detected": owner_files,
        "source_roots": source_roots,
        "build_files_detected": build_files,
        "lock_files_detected": lock_files,
        "environment_templates_detected": config_templates,
        "max_folder_depth": max_depth,
    }
    return {"metrics": metrics, "findings": findings}
