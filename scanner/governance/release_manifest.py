from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_release_manifest(manifest_path: Path | str) -> dict[str, Any]:
    path = Path(manifest_path)
    return read_json(path)


def resolve_manifest_path(manifest_path: Path | str, value: str | None) -> Path | None:
    if value is None:
        return None
    path = Path(value)
    if path.is_absolute():
        return path
    cwd_path = Path.cwd() / path
    if cwd_path.exists():
        return cwd_path
    manifest_relative_path = Path(manifest_path).parent / path
    return manifest_relative_path


def load_optional_json(manifest_path: Path | str, value: str | None) -> tuple[dict[str, Any] | None, str | None, str]:
    resolved = resolve_manifest_path(manifest_path, value)
    if resolved is None:
        return None, None, "not_provided"
    if not resolved.exists():
        return None, str(resolved), "missing"
    return read_json(resolved), str(resolved), "provided"
