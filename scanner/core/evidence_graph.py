from __future__ import annotations

import hashlib


def _node_id(node_type: str, name: str) -> str:
    return f"{node_type}-" + hashlib.sha256(name.encode("utf-8")).hexdigest()[:12]


def _add_node(nodes: dict[str, dict], node_type: str, name: str, **attrs) -> str:
    node_id = _node_id(node_type, name)
    nodes[node_id] = {"id": node_id, "type": node_type, "name": name, **attrs}
    return node_id


def _edge(edges: list[dict], source: str, target: str, relationship: str) -> None:
    edges.append({"source": source, "target": target, "relationship": relationship})


def build_evidence_graph(inventory: dict, signals: list[dict], findings: list[dict], claims: list[dict], gaps: list[dict], rulebook: dict, scoring: dict) -> dict:
    nodes: dict[str, dict] = {}
    edges: list[dict] = []

    decision_id = _add_node(nodes, "decision", scoring.get("decision", "unknown"), score=scoring.get("score"))

    file_nodes = {}
    for file_info in sorted(inventory.get("files", []), key=lambda item: item["path"]):
        file_nodes[file_info["path"]] = _add_node(nodes, "file", file_info["path"], extension=file_info.get("extension"), size_bytes=file_info.get("size_bytes"))

    signal_nodes = {}
    for signal in signals:
        node_type = "technology"
        if signal["domain"] == "data":
            node_type = "data_indicator"
        elif signal["domain"] == "egress":
            node_type = "egress"
        elif signal["domain"] == "license":
            node_type = "component"
        signal_nodes[signal["signal_id"]] = _add_node(nodes, node_type, signal["signal_id"], confidence=signal.get("confidence"))

    rule_nodes = {}
    for rule_id, rule in sorted(rulebook["rules"].items()):
        rule_nodes[rule_id] = _add_node(nodes, "rule", rule_id, category=rule.get("category"), severity=rule.get("severity"))

    finding_nodes = {}
    for finding in findings:
        finding_nodes[finding["finding_id"]] = _add_node(nodes, "finding", finding["finding_id"], rule_id=finding.get("rule_id"), severity=finding.get("severity"), decision_impact=finding.get("decision_impact"))
        if finding.get("rule_id") in rule_nodes:
            _edge(edges, finding_nodes[finding["finding_id"]], rule_nodes[finding["rule_id"]], "triggers")
        if finding.get("file_path") in file_nodes:
            _edge(edges, file_nodes[finding["file_path"]], finding_nodes[finding["finding_id"]], "evidences")
        if finding.get("decision_impact") == "Block" or finding.get("severity") == "Critical":
            _edge(edges, finding_nodes[finding["finding_id"]], decision_id, "blocks")
        elif finding.get("decision_impact") in {"Mandatory Review", "Conditional"}:
            _edge(edges, finding_nodes[finding["finding_id"]], decision_id, "conditions")

    claim_nodes = {}
    for claim in claims:
        claim_nodes[claim["claim_id"]] = _add_node(nodes, "claim", claim["claim_id"], confidence=claim.get("confidence"), statement=claim.get("statement"))
        for signal_id in claim.get("related_signals", []):
            if signal_id in signal_nodes:
                _edge(edges, signal_nodes[signal_id], claim_nodes[claim["claim_id"]], "supports")
        for finding_id in claim.get("related_findings", []):
            if finding_id in finding_nodes:
                _edge(edges, finding_nodes[finding_id], claim_nodes[claim["claim_id"]], "supports")

    for gap in gaps:
        gap_id = _add_node(nodes, "gap", gap["gap_id"], domain=gap.get("domain"), severity=gap.get("severity"))
        for finding_id in gap.get("related_findings", []):
            if finding_id in finding_nodes:
                _edge(edges, finding_nodes[finding_id], gap_id, "lacks")
        for rule_id in gap.get("related_rules", []):
            if rule_id in rule_nodes:
                _edge(edges, rule_nodes[rule_id], gap_id, "requires")
        if gap.get("decision_impact") == "Block":
            _edge(edges, gap_id, decision_id, "blocks")
        else:
            _edge(edges, gap_id, decision_id, "conditions")

    return {
        "schema": "enterprise-whitebox-evidence-graph",
        "schema_version": "0.1",
        "nodes": [nodes[key] for key in sorted(nodes)],
        "edges": sorted(edges, key=lambda item: (item["source"], item["relationship"], item["target"])),
    }
