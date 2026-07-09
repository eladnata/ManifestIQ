from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_reviewer_worksheet(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def worksheet_false_positive_ids(worksheet: dict[str, Any] | None) -> set[str]:
    if not worksheet:
        return set()
    ids = set()
    for item in worksheet.get("false_positive_findings", []):
        if isinstance(item, str):
            ids.add(item)
        elif isinstance(item, dict) and item.get("finding_id"):
            ids.add(item["finding_id"])
    return ids


def worksheet_valid_scanner_only_ids(worksheet: dict[str, Any] | None) -> set[str]:
    if not worksheet:
        return set()
    ids = set()
    for item in worksheet.get("scanner_only_valid_findings", []):
        if isinstance(item, str):
            ids.add(item)
        elif isinstance(item, dict) and item.get("finding_id"):
            ids.add(item["finding_id"])
    return ids


def confidence_calibration(worksheet: dict[str, Any] | None) -> dict[str, Any]:
    if not worksheet:
        return {"status": "Not Evaluated", "method": "reviewer worksheet not provided"}
    score = worksheet.get("evidence_quality_score")
    return {
        "status": "Worksheet Provided",
        "evidence_quality_score": score,
        "calibrated": score is not None and int(score) >= 4,
    }


def review_preparation_acceleration(goldset: dict[str, Any], worksheet: dict[str, Any] | None) -> dict[str, Any]:
    manual_minutes = float(goldset.get("manual_review_time_minutes") or 0)
    if not worksheet:
        return {
            "status": "Not Evaluated",
            "manual_review_time_minutes": manual_minutes,
            "estimated_time_saved_minutes": 0,
            "acceleration": 0.0,
        }
    saved = float(worksheet.get("estimated_time_saved_minutes") or 0)
    acceleration = round(saved / manual_minutes, 4) if manual_minutes > 0 else 0.0
    return {
        "status": "Worksheet Provided",
        "manual_review_time_minutes": manual_minutes,
        "estimated_time_saved_minutes": saved,
        "acceleration": acceleration,
    }


def worksheet_top_blocker_agreement(worksheet: dict[str, Any] | None) -> float | None:
    if not worksheet:
        return None
    value = worksheet.get("top_blocker_agreement")
    if value == "Agree":
        return 1.0
    if value == "Partially Agree":
        return 0.5
    if value == "Disagree":
        return 0.0
    return None
