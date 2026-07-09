from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


TRIAGE_LABELS = {
    "valid_material",
    "valid_minor",
    "duplicate",
    "acceptable_noise",
    "false_positive",
    "needs_human_review",
}


def load_triage(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def triage_items_by_finding_id(triage: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not triage:
        return {}
    return {
        item["scanner_finding_id"]: item
        for item in triage.get("triage_items", [])
        if item.get("scanner_finding_id")
    }


def summarize_triage(triages: list[dict[str, Any] | None], scanner_only_count: int) -> dict[str, Any]:
    items = []
    for triage in triages:
        if triage:
            items.extend(triage.get("triage_items", []))
    label_counts = Counter(item.get("label", "unknown") for item in items)
    triaged_count = len(items)
    false_positive_count = label_counts.get("false_positive", 0)
    valid_material_count = label_counts.get("valid_material", 0)
    return {
        "scanner_only_findings_count": scanner_only_count,
        "triaged_scanner_only_findings_count": triaged_count,
        "untriaged_scanner_only_findings_count": max(0, scanner_only_count - triaged_count),
        "triage_rate": round(triaged_count / scanner_only_count, 4) if scanner_only_count else 1.0,
        "valid_material_count": valid_material_count,
        "valid_scanner_only_material_finding_rate": round(valid_material_count / triaged_count, 4) if triaged_count else 0.0,
        "false_positive_count": false_positive_count,
        "false_positive_rate_after_triage": round(false_positive_count / triaged_count, 4) if triaged_count else 0.0,
        "label_counts": dict(sorted(label_counts.items())),
    }


def material_precision_after_triage(matched_material_count: int, triages: list[dict[str, Any] | None]) -> float:
    false_positive_count = 0
    for triage in triages:
        if not triage:
            continue
        false_positive_count += sum(1 for item in triage.get("triage_items", []) if item.get("label") == "false_positive")
    denominator = matched_material_count + false_positive_count
    return round(matched_material_count / denominator, 4) if denominator else 1.0
