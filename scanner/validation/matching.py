from __future__ import annotations

import re
from typing import Any


STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "before", "by", "for", "from", "has", "in", "is",
    "of", "or", "the", "to", "with", "without",
}


DOMAIN_ALIASES = {
    "application security": "security",
    "security": "security",
    "sox / finance": "sox",
    "sox": "sox",
    "license": "license risk",
    "license risk": "license risk",
    "ai / model risk": "ai model risk",
    "ai model risk": "ai model risk",
}


def normalize_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def normalize_domain(value: Any) -> str:
    normalized = normalize_text(value)
    return DOMAIN_ALIASES.get(normalized, normalized)


def title_tokens(value: Any) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", normalize_text(value))
        if token and token not in STOPWORDS
    }


def title_overlap(left: Any, right: Any) -> float:
    left_tokens = title_tokens(left)
    right_tokens = title_tokens(right)
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def file_path_matches(left: Any, right: Any) -> bool:
    if not left or not right:
        return False
    left_text = str(left).replace("\\", "/").lower()
    right_text = str(right).replace("\\", "/").lower()
    return left_text == right_text or left_text.endswith("/" + right_text) or right_text.endswith("/" + left_text)


def score_match(human_finding: dict[str, Any], scanner_finding: dict[str, Any]) -> dict[str, Any]:
    score = 0
    reasons: list[str] = []

    human_rule = human_finding.get("rule_id")
    if human_rule and human_rule == scanner_finding.get("rule_id"):
        score += 4
        reasons.append("rule_id matched")

    if human_finding.get("severity") == scanner_finding.get("severity"):
        score += 1
        reasons.append("severity matched")

    if normalize_domain(human_finding.get("domain")) == normalize_domain(scanner_finding.get("category")):
        score += 1
        reasons.append("domain matched")

    if file_path_matches(human_finding.get("file_path"), scanner_finding.get("file_path")):
        score += 2
        reasons.append("file_path matched")

    overlap = title_overlap(human_finding.get("title"), scanner_finding.get("title"))
    if overlap >= 0.5:
        score += 2
        reasons.append(f"title token overlap high ({overlap:.2f})")
    elif overlap >= 0.25:
        score += 1
        reasons.append(f"title token overlap partial ({overlap:.2f})")

    if human_finding.get("decision_impact") == scanner_finding.get("decision_impact"):
        score += 1
        reasons.append("decision_impact matched")

    if score >= 7 or ("rule_id matched" in reasons and "severity matched" in reasons):
        confidence = "High"
    elif score >= 5:
        confidence = "Medium"
    elif score >= 3:
        confidence = "Low"
    else:
        confidence = "None"

    return {"score": score, "match_confidence": confidence, "match_reasons": reasons}


def match_findings(human_findings: list[dict[str, Any]], scanner_findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    matches = []
    used_scanner_ids: set[str] = set()

    for human in sorted(human_findings, key=lambda item: item.get("human_finding_id", "")):
        candidates = []
        for scanner in scanner_findings:
            scanner_id = scanner.get("finding_id")
            if scanner_id in used_scanner_ids:
                continue
            scored = score_match(human, scanner)
            if scored["match_confidence"] == "None":
                continue
            candidates.append((scored["score"], scanner_id or "", scanner, scored))

        if not candidates:
            continue
        _score, _scanner_id, scanner, scored = sorted(candidates, key=lambda item: (-item[0], item[1]))[0]
        scanner_id = scanner.get("finding_id")
        if scanner_id:
            used_scanner_ids.add(scanner_id)
        matches.append({
            "human_finding_id": human.get("human_finding_id"),
            "scanner_finding_id": scanner_id,
            "human_rule_id": human.get("rule_id"),
            "scanner_rule_id": scanner.get("rule_id"),
            "human_domain": human.get("domain"),
            "human_severity": human.get("severity"),
            "human_decision_impact": human.get("decision_impact"),
            "human_materiality": human.get("materiality"),
            "match_confidence": scored["match_confidence"],
            "match_reasons": scored["match_reasons"],
        })

    return matches


def scanner_blocking_findings(scanner_findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        finding
        for finding in scanner_findings
        if finding.get("severity") in {"Critical", "High"}
        and finding.get("decision_impact") in {"Block", "Mandatory Review"}
    ]
