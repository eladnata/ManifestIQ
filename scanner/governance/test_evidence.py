from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

from scanner.core.evidence import write_json


def _empty_summary(command: str, source_path: str | None, notes: list[str]) -> dict[str, Any]:
    return {
        "schema": "enterprise-whitebox-test-result-summary",
        "schema_version": "0.1",
        "command": command,
        "status": "unknown",
        "tests_passed": 0,
        "tests_failed": 0,
        "tests_skipped": 0,
        "tests_total": 0,
        "duration_seconds": 0,
        "source": "junit_xml" if source_path else "unknown",
        "source_path": source_path,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "notes": notes,
    }


def _int_attr(element: ElementTree.Element, name: str) -> int:
    try:
        return int(float(element.attrib.get(name, "0")))
    except ValueError:
        return 0


def _float_attr(element: ElementTree.Element, name: str) -> float:
    try:
        return float(element.attrib.get(name, "0"))
    except ValueError:
        return 0.0


def _suite_elements(root: ElementTree.Element) -> list[ElementTree.Element]:
    if root.tag == "testsuite":
        return [root]
    return [element for element in root.iter() if element.tag == "testsuite"]


def parse_junit_xml(junit_path: Path | str, command: str) -> dict[str, Any]:
    path = Path(junit_path)
    source_path = str(path)
    if not path.exists():
        return _empty_summary(command, source_path, [f"JUnit XML file is missing: {source_path}"])

    try:
        root = ElementTree.parse(path).getroot()
    except (ElementTree.ParseError, OSError) as exc:
        return _empty_summary(command, source_path, [f"JUnit XML could not be parsed: {exc}"])

    suites = _suite_elements(root)
    if not suites:
        return _empty_summary(command, source_path, ["JUnit XML does not contain a testsuite element."])

    total = sum(_int_attr(suite, "tests") for suite in suites)
    failures = sum(_int_attr(suite, "failures") for suite in suites)
    errors = sum(_int_attr(suite, "errors") for suite in suites)
    skipped = sum(_int_attr(suite, "skipped") for suite in suites)
    duration = round(sum(_float_attr(suite, "time") for suite in suites), 4)
    failed = failures + errors
    passed = max(total - failed - skipped, 0)
    notes = []
    if total == 0:
        status = "unknown"
        notes.append("JUnit XML contains zero tests.")
    elif failed > 0:
        status = "failed"
    else:
        status = "passed"

    return {
        "schema": "enterprise-whitebox-test-result-summary",
        "schema_version": "0.1",
        "command": command,
        "status": status,
        "tests_passed": passed,
        "tests_failed": failed,
        "tests_skipped": skipped,
        "tests_total": total,
        "duration_seconds": duration,
        "source": "junit_xml",
        "source_path": source_path,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "notes": notes,
    }


def collect_test_evidence(junit_path: Path | str, command: str, output_dir: Path | str) -> dict[str, Any]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    summary = parse_junit_xml(junit_path=junit_path, command=command)
    write_json(output / "test_result_summary.json", summary)
    return summary
