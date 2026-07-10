from __future__ import annotations

import hashlib
import shutil
import subprocess
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class Workspace:
    source_type: str
    source_path: Path
    working_path: Path
    output_dir: Path
    evidence_dir: Path
    source_metadata: dict


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_tree(path: Path) -> str:
    h = hashlib.sha256()
    for file_path in sorted(p for p in path.rglob("*") if p.is_file()):
        rel = file_path.relative_to(path).as_posix().encode("utf-8")
        h.update(rel)
        h.update(b"\0")
        with file_path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        h.update(b"\0")
    return h.hexdigest()


def _reset_output(output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    workspace_dir = output_dir / "workspace"
    evidence_dir = output_dir / "evidence-package"
    if workspace_dir.exists():
        shutil.rmtree(workspace_dir)
    if evidence_dir.exists():
        shutil.rmtree(evidence_dir)
    workspace_dir.mkdir(parents=True)
    evidence_dir.mkdir(parents=True)
    return workspace_dir, evidence_dir


def _safe_copytree(src: Path, dst: Path) -> None:
    ignore = shutil.ignore_patterns(
        ".git",
        "node_modules",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
        "output",
        "outputs",
        "governance-output",
        "release-output",
        "validation-output",
        "goldset-output",
        "portfolio-output",
        "trend-output",
        "self-assurance-output",
        "release-candidate-output",
        "scanner-output",
        "evidence-package",
    )
    shutil.copytree(src, dst, dirs_exist_ok=True, ignore=ignore)


def prepare_folder_workspace(source_path: Path, output_dir: Path) -> Workspace:
    workspace_dir, evidence_dir = _reset_output(output_dir)
    normalized = workspace_dir / "source"
    _safe_copytree(source_path.resolve(), normalized)
    metadata = {
        "source_type": "folder",
        "source_path": str(source_path.resolve()),
        "scan_timestamp": now_iso(),
        "input_sha256": sha256_tree(normalized),
    }
    return Workspace("folder", source_path.resolve(), normalized, output_dir.resolve(), evidence_dir, metadata)


def prepare_zip_workspace(zip_path: Path, output_dir: Path) -> Workspace:
    workspace_dir, evidence_dir = _reset_output(output_dir)
    normalized = workspace_dir / "source"
    normalized.mkdir()
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            target = (normalized / member.filename).resolve()
            if not str(target).startswith(str(normalized.resolve())):
                raise ValueError(f"Unsafe ZIP path detected: {member.filename}")
        zf.extractall(normalized)
    metadata = {
        "source_type": "zip",
        "source_path": str(zip_path.resolve()),
        "scan_timestamp": now_iso(),
        "input_sha256": sha256_file(zip_path),
        "workspace_sha256": sha256_tree(normalized),
    }
    return Workspace("zip", zip_path.resolve(), normalized, output_dir.resolve(), evidence_dir, metadata)


def prepare_git_workspace(repo_url: str, output_dir: Path, branch: Optional[str] = None, commit: Optional[str] = None) -> Workspace:
    workspace_dir, evidence_dir = _reset_output(output_dir)
    normalized = workspace_dir / "source"
    clone_cmd = ["git", "clone", "--depth", "1"]
    if branch:
        clone_cmd += ["--branch", branch]
    clone_cmd += [repo_url, str(normalized)]
    subprocess.run(clone_cmd, check=True, text=True)
    if commit:
        subprocess.run(["git", "checkout", commit], cwd=normalized, check=True, text=True)
    commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=normalized, text=True).strip()
    metadata = {
        "source_type": "git",
        "repo_url": repo_url,
        "branch": branch,
        "commit_hash": commit_hash,
        "scan_timestamp": now_iso(),
        "input_sha256": sha256_tree(normalized),
    }
    return Workspace("git", Path(repo_url), normalized, output_dir.resolve(), evidence_dir, metadata)
