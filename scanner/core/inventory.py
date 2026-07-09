from __future__ import annotations

from collections import Counter
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache"}
EXT_LANGUAGE_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript/React",
    ".jsx": "JavaScript/React",
    ".java": "Java",
    ".cs": "C#",
    ".go": "Go",
    ".ps1": "PowerShell",
    ".sql": "SQL",
    ".html": "HTML",
    ".css": "CSS",
    ".yml": "YAML",
    ".yaml": "YAML",
    ".json": "JSON",
    ".xml": "XML",
    ".sh": "Shell",
}
PACKAGE_FILES = {
    "package.json": "npm",
    "package-lock.json": "npm-lock",
    "requirements.txt": "pip",
    "pyproject.toml": "python-project",
    "Pipfile": "pipenv",
    "Pipfile.lock": "pipenv-lock",
    "poetry.lock": "poetry-lock",
    "pom.xml": "maven",
    "build.gradle": "gradle",
    "go.mod": "go-modules",
    "go.sum": "go-lock",
    "composer.json": "composer",
    "packages.lock.json": "nuget-lock",
}
CONFIG_NAMES = {".env", ".env.example", "docker-compose.yml", "Dockerfile", "appsettings.json", "web.config"}
CI_PATTERNS = {".github/workflows", "azure-pipelines.yml", ".gitlab-ci.yml"}
DATA_EXTENSIONS = {".csv", ".xlsx", ".xls", ".sqlite", ".db", ".bak", ".dump", ".sql", ".log"}


def iter_files(root: Path):
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file():
            yield path


def build_inventory(root: Path) -> dict:
    files = []
    language_counter: Counter[str] = Counter()
    package_managers = set()
    config_files = []
    ci_cd_files = []
    data_files = []
    documentation_files = []
    total_bytes = 0

    for path in iter_files(root):
        rel = path.relative_to(root).as_posix()
        size = path.stat().st_size
        total_bytes += size
        ext = path.suffix.lower()
        language = EXT_LANGUAGE_MAP.get(ext)
        if language:
            language_counter[language] += size
        if path.name in PACKAGE_FILES:
            package_managers.add(PACKAGE_FILES[path.name])
        if path.name in CONFIG_NAMES or ext in {".yml", ".yaml", ".json", ".toml", ".ini"}:
            config_files.append(rel)
        if any(rel.startswith(p) or rel.endswith(p) for p in CI_PATTERNS):
            ci_cd_files.append(rel)
        if ext in DATA_EXTENSIONS:
            data_files.append(rel)
        if path.name.lower() in {"readme.md", "readme.txt", "changelog.md", "owners.md", "codeowners"} or "docs/" in rel.lower():
            documentation_files.append(rel)
        files.append({"path": rel, "size_bytes": size, "extension": ext})

    languages = {}
    if total_bytes:
        for lang, bytes_count in language_counter.items():
            languages[lang] = round(bytes_count / total_bytes * 100, 2)

    return {
        "file_count": len(files),
        "total_bytes": total_bytes,
        "files": files,
        "languages": languages,
        "package_managers": sorted(package_managers),
        "config_files": sorted(set(config_files)),
        "ci_cd_files": sorted(set(ci_cd_files)),
        "data_files": sorted(set(data_files)),
        "documentation_files": sorted(set(documentation_files)),
    }
