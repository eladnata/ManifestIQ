from __future__ import annotations

import json
from pathlib import Path
from typing import Any


EXPECTED_FILE = "expected-findings.json"


def load_expected_findings(fixture_dir: Path) -> dict[str, Any]:
    path = fixture_dir / EXPECTED_FILE
    if not path.exists():
        return {"fixture": fixture_dir.name, "profile": "enterprise", "expected_findings": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("fixture", fixture_dir.name)
    data.setdefault("profile", "enterprise")
    data.setdefault("expected_findings", [])
    return data


def discover_fixtures(suite: str, root: Path | None = None) -> list[Path]:
    root = root or Path("tests/sample_projects")
    if suite in {"adversarial", "adversarial-v0.1"}:
        pattern = "adversarial-*"
    elif suite in {"seeded", "seeded-v0.1"}:
        pattern = "adversarial-*"
    else:
        pattern = f"{suite}-*"
    return sorted(path for path in root.glob(pattern) if path.is_dir() and (path / EXPECTED_FILE).exists())

