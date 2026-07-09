from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


def load_calibration_log(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def summarize_calibration_logs(logs: list[dict[str, Any] | None]) -> dict[str, Any]:
    present = [log for log in logs if log]
    change_counts = Counter(log.get("decision", {}).get("change_type", "unknown") for log in present)
    return {
        "calibration_log_count": len(present),
        "change_type_counts": dict(sorted(change_counts.items())),
        "calibration_ids": sorted(log.get("calibration_id") for log in present if log.get("calibration_id")),
    }
