from scanner.core.acceptance_matrix import build_acceptance_matrix
from scanner.core.capabilities import capability_registry
from scanner.core.claims import build_claims
from scanner.core.rule_contract import validate_rule_contracts


def test_system_dossier_module_exists_with_builder():
    from scanner.core.system_dossier import build_system_dossier

    assert callable(build_system_dossier)


def test_analyzer_capabilities_include_domains_and_limitations():
    capabilities = capability_registry()

    assert capabilities
    for capability in capabilities:
        assert "domains" in capability
        assert isinstance(capability["domains"], list)
        assert capability["domains"]
        assert "limitations" in capability
        assert isinstance(capability["limitations"], list)


def test_acceptance_matrix_matches_phase10_domain_contract():
    matrix = build_acceptance_matrix([], [], {"confidence_counts": {}}, {"decision": "Approved", "score": 100})
    allowed_statuses = {"Accepted", "Conditional", "Mandatory Review", "Blocked", "Insufficient Evidence"}

    assert matrix["schema"] == "enterprise-whitebox-acceptance-matrix"
    for row in matrix["domains"]:
        assert row["status"] in allowed_statuses
        assert {"domain", "status", "confidence", "blocking_findings", "mandatory_review_findings", "gaps", "required_actions"} <= row.keys()


def test_claims_are_not_generated_without_evidence_linkage():
    claims = build_claims(
        [],
        [],
        {"evaluations": []},
        {"production_readiness_required": True, "languages": []},
    )

    assert claims == []


def test_v2_rule_contract_requires_enterprise_metadata():
    rulebook = {
        "rules": {
            "CUSTOM-V2-BAD": {
                "rule_id": "CUSTOM-V2-BAD",
                "severity": "High",
                "decision_impact": "Mandatory Review",
                "required_signals": ["delivery.runbook.detected"],
            }
        }
    }

    validation = validate_rule_contracts(rulebook, capability_registry(), {"delivery.runbook.detected"})

    assert validation["valid"] is False
    messages = [error["error"] for error in validation["errors"]]
    assert "name is required for v2 rule contracts" in messages
    assert "category is required for v2 rule contracts" in messages
