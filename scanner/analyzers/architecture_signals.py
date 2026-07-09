from __future__ import annotations

from scanner.analyzers.base import AnalyzerContext


def analyze(_context: AnalyzerContext) -> dict:
    return {
        "status": "skipped",
        "metrics": {"implementation_status": "TODO: implement deterministic architecture signal checks"},
        "findings": [],
        "errors": [],
    }
