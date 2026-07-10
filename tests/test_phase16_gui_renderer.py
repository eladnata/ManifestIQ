import json
import re
from pathlib import Path

from typer.testing import CliRunner

from scanner.app.cli import app
from scanner.core.evidence import write_json
from scanner.ui.executive_gui_renderer import (
    MISSING_EVIDENCE_LABEL,
    RAW_PROVENANCE_LIMITATION,
    build_board_verdict_view,
    render_executive_cockpit_html,
)

runner = CliRunner()

FORBIDDEN_CLAIM_TERMS = [
    "Approved",
    "Certified",
    "Compliant",
    "Safe",
    "Production Ready",
    "SOX Approved",
    "Privacy Approved",
    "Legally Approved",
    "Fully Secure",
]

FORBIDDEN_RUNTIME_PATTERNS = [
    r"<script[^>]*\ssrc=",
    r"<link[^>]*\shref=",
    r"fetch\(",
    r"XMLHttpRequest",
    r"WebSocket",
    r"localStorage",
    r"sessionStorage",
    r"@import",
    r"url\(\s*['\"]?https?:",
]


def _write_manifest(package_dir: Path) -> None:
    files = []
    for path in sorted(p for p in package_dir.rglob("*") if p.is_file() and p.name != "manifest.json"):
        import hashlib

        h = hashlib.sha256(path.read_bytes()).hexdigest()
        files.append({"path": path.relative_to(package_dir).as_posix(), "sha256": h})
    write_json(package_dir / "manifest.json", {"files": files, "package_sha256": "test"})


def _full_evidence_package(tmp_path: Path) -> Path:
    """A package with every optional artifact present and raw provenance complete."""
    package = tmp_path / "evidence-package"
    package.mkdir()

    write_json(
        package / "decision-packet.json",
        {
            "raw_decision": "Not Approved",
            "raw_score": 41,
            "decision": {
                "value": "Not Approved",
                "score": 41,
                "rationale": "Blocked by a hardcoded secret and missing owner metadata.",
                "blocking_reasons": [
                    "SEC-001: Hardcoded secret detected",
                    "ARCH-011: Missing owner metadata",
                    "GOV-001: Missing required documentation: OWNER",
                ],
            },
            "required_actions": ["Remove hardcoded secret and rotate credential."],
            "required_reviewers": ["CISO", "AppSec", "Security Architecture"],
        },
    )
    write_json(package / "scan-summary.json", {"decision": "Not Approved"})
    write_json(package / "system-dossier.json", {"system_identity": {"name": "sample-system"}})
    write_json(
        package / "risk-acceptance-review.json",
        {"raw_decision": "Not Approved", "raw_score": 41, "review_status": "Partially Covered"},
    )
    write_json(package / "release-candidate-summary.json", {"status": "Not Ready"})
    write_json(package / "trust-safety-review.json", {"review_status": "Passed"})
    write_json(package / "findings.json", {"findings": []})

    _write_manifest(package)
    return package


def _empty_evidence_package(tmp_path: Path) -> Path:
    """A package with no artifacts at all — the maximal missing-evidence case."""
    package = tmp_path / "evidence-package-empty"
    package.mkdir()
    return package


def _incomplete_provenance_package(tmp_path: Path) -> Path:
    """decision-packet.json present but missing raw_decision / raw_score."""
    package = tmp_path / "evidence-package-incomplete"
    package.mkdir()
    write_json(
        package / "decision-packet.json",
        {
            "decision": {
                "value": "Not Approved",
                "score": 41,
                "rationale": "Blocked by missing owner metadata.",
                "blocking_reasons": ["ARCH-011: Missing owner metadata"],
            },
        },
    )
    write_json(package / "scan-summary.json", {"decision": "Not Approved"})
    _write_manifest(package)
    return package


# ---------------------------------------------------------------------------
# 1 & 2. CLI command exists and generates an HTML file.
# ---------------------------------------------------------------------------


def test_render_gui_cli_generates_html_file(tmp_path):
    package = _full_evidence_package(tmp_path)
    output = tmp_path / "gui-output"

    result = runner.invoke(
        app,
        ["render-gui", "--evidence-package", str(package), "--output", str(output)],
    )

    assert result.exit_code == 0, result.output
    out_file = output / "manifestiq-executive-cockpit.html"
    assert out_file.is_file()
    assert out_file.stat().st_size > 0


# ---------------------------------------------------------------------------
# 3 & 4. Output is self-contained: no external runtime dependencies.
# ---------------------------------------------------------------------------


def test_output_is_self_contained(tmp_path):
    package = _full_evidence_package(tmp_path)
    output = tmp_path / "gui-output"
    runner.invoke(app, ["render-gui", "--evidence-package", str(package), "--output", str(output)])

    text = (output / "manifestiq-executive-cockpit.html").read_text(encoding="utf-8")

    for pattern in FORBIDDEN_RUNTIME_PATTERNS:
        assert not re.search(pattern, text, re.IGNORECASE), f"forbidden pattern found: {pattern}"

    # No <img>/<script src> external assets at all, and no network scheme anywhere.
    assert "<img" not in text.lower()
    assert "http://" not in text
    assert "https://" not in text


# ---------------------------------------------------------------------------
# 5. Human approval slot is present and empty / not inferred.
# ---------------------------------------------------------------------------


def test_human_approval_slot_present_and_empty(tmp_path):
    package = _full_evidence_package(tmp_path)
    view = build_board_verdict_view(package)
    human = view["layers"]["human_approval"]

    assert human["display"] == "Human approval is not inferred"
    assert human["confirmed"] is False
    assert human.get("empty") is True

    document = render_executive_cockpit_html(view)
    assert "Human approval is not inferred" in document
    assert "empty-tag" in document


# ---------------------------------------------------------------------------
# 6. Five decision layers are rendered separately (never merged).
# ---------------------------------------------------------------------------


def test_five_decision_layers_rendered_separately(tmp_path):
    package = _full_evidence_package(tmp_path)
    view = build_board_verdict_view(package)
    layers = view["layers"]

    expected_keys = {
        "raw_scanner_decision",
        "review_readiness",
        "risk_acceptance_coverage",
        "release_readiness",
        "human_approval",
    }
    assert set(layers.keys()) == expected_keys
    for key in expected_keys:
        assert "display" in layers[key]

    document = render_executive_cockpit_html(view)
    assert document.count('class="slot ') + document.count('class="slot state-') >= 5 or document.count("slot-name") == 5
    assert "1 · Raw Scanner Decision" in document
    assert "2 · Review Readiness" in document
    assert "3 · Risk Acceptance Coverage" in document
    assert "4 · Release Readiness" in document
    assert "5 · Human Approval" in document


# ---------------------------------------------------------------------------
# 7. Missing evidence is rendered visibly (fail closed, not hidden).
# ---------------------------------------------------------------------------


def test_missing_evidence_rendered_visibly_for_empty_package(tmp_path):
    package = _empty_evidence_package(tmp_path)
    view = build_board_verdict_view(package)

    assert view["visible_decision"] == "Not Ready"
    assert view["layers"]["raw_scanner_decision"]["display"] == MISSING_EVIDENCE_LABEL
    assert view["layers"]["raw_scanner_decision"]["confirmed"] is False
    assert view["layers"]["release_readiness"]["display"] == MISSING_EVIDENCE_LABEL
    assert view["layers"]["risk_acceptance_coverage"]["display"] == MISSING_EVIDENCE_LABEL
    assert len(view["limitations"]) > 0

    document = render_executive_cockpit_html(view)
    assert MISSING_EVIDENCE_LABEL in document


def test_incomplete_raw_provenance_is_a_visible_limitation_not_a_promotion(tmp_path):
    """
    decision-packet.json exists and has a derived decision, but no raw_decision / raw_score.
    The renderer must not silently promote the derived decision into a confirmed raw decision.
    """
    package = _incomplete_provenance_package(tmp_path)
    view = build_board_verdict_view(package)

    raw_layer = view["layers"]["raw_scanner_decision"]
    assert raw_layer["confirmed"] is False
    assert RAW_PROVENANCE_LIMITATION in raw_layer["limitations"]
    assert RAW_PROVENANCE_LIMITATION in view["limitations"]

    # Visible decision stays conservative — it is not promoted from the derived decision.value.
    assert view["visible_decision"] == "Not Ready"

    document = render_executive_cockpit_html(view)
    assert RAW_PROVENANCE_LIMITATION in document


def test_release_readiness_is_missing_evidence_when_artifact_absent(tmp_path):
    """
    Release readiness must never be inferred from the raw decision or any other layer —
    without release-candidate-summary.json it must render as Missing Evidence.
    """
    package = _incomplete_provenance_package(tmp_path)
    view = build_board_verdict_view(package)
    assert view["layers"]["release_readiness"]["display"] == MISSING_EVIDENCE_LABEL
    assert view["layers"]["release_readiness"]["confirmed"] is False


# ---------------------------------------------------------------------------
# 8. Forbidden approval language never rendered as a product claim.
# ---------------------------------------------------------------------------


def test_forbidden_claim_language_not_rendered_as_positive_claim(tmp_path):
    package = _full_evidence_package(tmp_path)
    view = build_board_verdict_view(package)
    document = render_executive_cockpit_html(view)

    # Non-claims footer legitimately contains denied forms ("Not certified", "No ... approval").
    # None of the forbidden terms may appear as a bare positive claim outside that footer.
    footer_start = document.find('<footer class="nonclaims"')
    body = document[:footer_start] if footer_start != -1 else document

    for term in FORBIDDEN_CLAIM_TERMS:
        # "Not Approved" / "Not Ready" contain the substrings; only flag a bare, unnegated claim.
        for match in re.finditer(re.escape(term), body, re.IGNORECASE):
            start = max(0, match.start() - 12)
            preceding = body[start:match.start()].lower()
            assert "not " in preceding or "no " in preceding, (
                f"forbidden term '{term}' appears without a preceding negation: "
                f"...{body[start:match.end()+12]}..."
            )


# ---------------------------------------------------------------------------
# 9. Green is used only for evidence integrity.
# ---------------------------------------------------------------------------


def test_green_used_only_for_evidence_integrity(tmp_path):
    package = _full_evidence_package(tmp_path)
    view = build_board_verdict_view(package)
    document = render_executive_cockpit_html(view)

    # The only green token in the design system is --verify / integrity-verified*.
    assert "--verify:" in document
    assert "integrity-verified" in document

    # None of the decision-layer slot CSS classes reference the verify/green token.
    slot_block = document[document.find("class=\"layers\""): document.find("</section>", document.find("class=\"layers\""))]
    assert "state-review" in slot_block or "state-critical" in slot_block or "state-caution" in slot_block or "state-unknown" in slot_block
    assert "verify" not in slot_block.lower()


def test_decision_card_never_uses_integrity_green(tmp_path):
    package = _full_evidence_package(tmp_path)
    view = build_board_verdict_view(package)
    document = render_executive_cockpit_html(view)

    card_start = document.find('class="decision-card"')
    card_end = document.find("</section>", card_start)
    card_block = document[card_start:card_end]
    assert "verify" not in card_block.lower()


# ---------------------------------------------------------------------------
# 10. Existing scanner decisions / scoring are not changed by this phase.
# ---------------------------------------------------------------------------


def test_view_model_does_not_mutate_evidence_package(tmp_path):
    package = _full_evidence_package(tmp_path)
    original = {
        p.relative_to(package).as_posix(): p.read_bytes()
        for p in package.rglob("*")
        if p.is_file()
    }

    build_board_verdict_view(package)

    after = {
        p.relative_to(package).as_posix(): p.read_bytes()
        for p in package.rglob("*")
        if p.is_file()
    }
    assert original == after


def test_view_model_reads_score_and_decision_verbatim_without_recomputation(tmp_path):
    """The renderer must surface the decision packet's existing score/value, never recompute it."""
    package = _full_evidence_package(tmp_path)
    packet = json.loads((package / "decision-packet.json").read_text(encoding="utf-8"))

    view = build_board_verdict_view(package)

    assert view["score"] == packet["decision"]["score"]
    assert view["visible_decision"] == packet["decision"]["value"]


# ---------------------------------------------------------------------------
# Integrity ledger behavior (supports requirement 7 / fail-closed).
# ---------------------------------------------------------------------------


def test_integrity_verified_when_all_manifest_artifacts_present(tmp_path):
    package = _full_evidence_package(tmp_path)
    view = build_board_verdict_view(package)
    assert view["integrity"]["state"] == "Verified"
    assert view["integrity"]["total_count"] > 0
    assert view["integrity"]["failed"] == []


def test_integrity_missing_when_manifest_absent(tmp_path):
    package = _empty_evidence_package(tmp_path)
    view = build_board_verdict_view(package)
    assert view["integrity"]["state"] == "Missing"


def test_integrity_partial_when_manifest_references_missing_file(tmp_path):
    package = _full_evidence_package(tmp_path)
    manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
    manifest["files"].append({"path": "does-not-exist.json", "sha256": "deadbeef"})
    write_json(package / "manifest.json", manifest)

    view = build_board_verdict_view(package)
    assert view["integrity"]["state"] == "Partial"
    assert "does-not-exist.json" in view["integrity"]["failed"]


# ---------------------------------------------------------------------------
# Escaping / injection safety of evidence-package content.
# ---------------------------------------------------------------------------


def test_evidence_content_is_html_escaped(tmp_path):
    package = tmp_path / "evidence-package-escape"
    package.mkdir()
    write_json(
        package / "decision-packet.json",
        {
            "raw_decision": "Not Approved",
            "raw_score": 10,
            "decision": {
                "value": "Not Approved",
                "score": 10,
                "rationale": "<script>alert(1)</script>",
                "blocking_reasons": ["<img src=x onerror=alert(1)>"],
            },
        },
    )
    _write_manifest(package)

    view = build_board_verdict_view(package)
    document = render_executive_cockpit_html(view)

    assert "<script>alert(1)</script>" not in document
    assert "<img src=x" not in document
    assert "&lt;script&gt;" in document
