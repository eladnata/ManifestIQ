from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_manifest(evidence_dir: Path) -> dict:
    files = []
    for path in sorted(p for p in evidence_dir.rglob("*") if p.is_file() and p.name not in {"manifest.json", "sha256.txt"}):
        files.append({"path": path.relative_to(evidence_dir).as_posix(), "sha256": sha256_file(path)})
    package_hash = hashlib.sha256()
    for item in files:
        package_hash.update(item["path"].encode("utf-8"))
        package_hash.update(item["sha256"].encode("utf-8"))
    manifest = {"files": files, "package_sha256": package_hash.hexdigest()}
    write_json(evidence_dir / "manifest.json", manifest)
    (evidence_dir / "sha256.txt").write_text(manifest["package_sha256"] + "\n", encoding="utf-8")
    return manifest
