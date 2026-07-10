from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

NON_CLAIMS = [
    "Not certified",
    "No SOX / privacy / legal approval",
    "Not a release approval",
    "No safety claim",
    "Human approval is not inferred",
]

REQUIRED_REVIEWER_FALLBACK = ["CISO", "CTO", "AppSec"]

MISSING_EVIDENCE_LABEL = "Missing Evidence"
RAW_PROVENANCE_LIMITATION = "Raw decision provenance incomplete"


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _verify_manifest(evidence_package: Path, manifest: dict[str, Any] | None) -> dict[str, Any]:
    """Fail-closed integrity check: every manifest entry must exist on disk with a hash recorded."""
    if manifest is None:
        return {"state": "Missing", "verified_count": 0, "total_count": 0, "failed": []}

    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        return {"state": "Missing", "verified_count": 0, "total_count": 0, "failed": []}

    failed: list[str] = []
    verified = 0
    for item in files:
        if not isinstance(item, dict):
            continue
        rel_path = str(item.get("path", ""))
        has_hash = bool(item.get("sha256"))
        target = evidence_package / rel_path if rel_path else None
        if not rel_path or not has_hash or target is None or not target.is_file():
            failed.append(rel_path or "(unnamed artifact)")
            continue
        verified += 1

    total = len([i for i in files if isinstance(i, dict)])
    if not failed and total > 0:
        state = "Verified"
    elif verified > 0:
        state = "Partial"
    else:
        state = "Missing"
    return {"state": state, "verified_count": verified, "total_count": total, "failed": failed}


def _raw_decision_layer(decision_packet: dict[str, Any] | None, scan_summary: dict[str, Any] | None) -> dict[str, Any]:
    """
    Raw scanner decision layer.

    decision-packet.json is not permitted to silently promote a derived decision into a
    raw decision. raw_decision / raw_score must be explicit provenance fields; their absence
    is a visible limitation, not an inferred pass. See docs/internal/EVIDENCE_INTEGRITY_STANDARD.md.
    """
    limitations: list[str] = []

    raw_decision = None
    raw_score = None
    if isinstance(decision_packet, dict):
        raw_decision = decision_packet.get("raw_decision")
        raw_score = decision_packet.get("raw_score")

    if raw_decision is None or raw_score is None:
        limitations.append(RAW_PROVENANCE_LIMITATION)
        # Conservative fallback: surface the scan-level decision label, if any, but never as
        # confirmed raw provenance, and never more favorable than the derived decision.
        fallback_decision = None
        if isinstance(scan_summary, dict):
            fallback_decision = scan_summary.get("decision")
        if isinstance(fallback_decision, str) and fallback_decision:
            display = fallback_decision
            confirmed = False
        else:
            display = MISSING_EVIDENCE_LABEL
            confirmed = False
        return {
            "display": display,
            "confirmed": confirmed,
            "limitations": limitations,
        }

    return {
        "display": str(raw_decision),
        "confirmed": True,
        "limitations": limitations,
    }


def _review_readiness_layer(decision_packet: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(decision_packet, dict):
        return {"display": MISSING_EVIDENCE_LABEL, "confirmed": False}
    decision = decision_packet.get("decision")
    value = decision.get("value") if isinstance(decision, dict) else None
    if not value:
        return {"display": MISSING_EVIDENCE_LABEL, "confirmed": False}
    # Review readiness is never rendered as approval; it is a bounded label describing
    # whether the packet is assembled and coherent enough for human review.
    return {"display": "Mandatory Review", "confirmed": True, "source_value": str(value)}


def _risk_acceptance_layer(risk_review: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(risk_review, dict):
        return {"display": MISSING_EVIDENCE_LABEL, "confirmed": False}
    status = risk_review.get("review_status")
    if not status:
        return {"display": MISSING_EVIDENCE_LABEL, "confirmed": False}
    return {"display": str(status), "confirmed": True}


def _release_readiness_layer(release_candidate: dict[str, Any] | None) -> dict[str, Any]:
    """
    Release readiness is its own evidence layer and must never be inferred from the raw
    scanner decision or any other layer. Without release-candidate-summary.json, this
    layer is Missing Evidence, not a derived guess.
    """
    if isinstance(release_candidate, dict):
        status = release_candidate.get("status") or release_candidate.get("release_readiness")
        if status:
            return {"display": str(status), "confirmed": True}
    return {"display": MISSING_EVIDENCE_LABEL, "confirmed": False}


def _top_blockers(decision_packet: dict[str, Any] | None, limit: int = 3) -> list[str]:
    if not isinstance(decision_packet, dict):
        return []
    decision = decision_packet.get("decision")
    reasons = decision.get("blocking_reasons") if isinstance(decision, dict) else None
    if not isinstance(reasons, list):
        return []
    return [str(r) for r in reasons[:limit]]


def _required_reviewers(decision_packet: dict[str, Any] | None) -> list[str]:
    if isinstance(decision_packet, dict):
        reviewers = decision_packet.get("required_reviewers")
        if isinstance(reviewers, list) and reviewers:
            return [str(r) for r in reviewers]
    return list(REQUIRED_REVIEWER_FALLBACK)


def _one_line_reason(decision_packet: dict[str, Any] | None) -> str:
    if not isinstance(decision_packet, dict):
        return "Decision packet is missing; conclusions cannot be traced to evidence."
    decision = decision_packet.get("decision")
    rationale = decision.get("rationale") if isinstance(decision, dict) else None
    if isinstance(rationale, str) and rationale.strip():
        return rationale.strip()
    blockers = _top_blockers(decision_packet, limit=1)
    if blockers:
        return f"Blocked by: {blockers[0]}"
    return MISSING_EVIDENCE_LABEL


def _score(decision_packet: dict[str, Any] | None) -> Any:
    if not isinstance(decision_packet, dict):
        return None
    decision = decision_packet.get("decision")
    return decision.get("score") if isinstance(decision, dict) else None


def _next_action(decision_packet: dict[str, Any] | None) -> str:
    if isinstance(decision_packet, dict):
        actions = decision_packet.get("required_actions")
        if isinstance(actions, list) and actions:
            return str(actions[0])
    return "Resolve outstanding blockers and re-run the assessment to regenerate evidence."


def build_board_verdict_view(evidence_package: Path | str) -> dict[str, Any]:
    """
    Build a plain-data view model for the Board Verdict Room from an evidence package.

    Read-only: never mutates the evidence package. Fails closed on every missing or
    incomplete artifact rather than inferring a favorable state.
    """
    package = Path(evidence_package)

    manifest = _read_json(package / "manifest.json")
    decision_packet = _read_json(package / "decision-packet.json")
    scan_summary = _read_json(package / "scan-summary.json")
    system_dossier = _read_json(package / "system-dossier.json")
    risk_review = _read_json(package / "risk-acceptance-review.json")
    release_candidate = _read_json(package / "release-candidate-summary.json")
    trust_safety_review = _read_json(package / "trust-safety-review.json")
    findings = _read_json(package / "findings.json")
    _ = findings  # read for completeness; not directly rendered on this room

    integrity = _verify_manifest(package, manifest)

    raw_layer = _raw_decision_layer(decision_packet, scan_summary)
    review_layer = _review_readiness_layer(decision_packet)
    risk_layer = _risk_acceptance_layer(risk_review)
    release_layer = _release_readiness_layer(release_candidate)
    human_layer = {"display": "Human approval is not inferred", "confirmed": False, "empty": True}

    limitations: list[str] = list(raw_layer.get("limitations", []))
    if manifest is None:
        limitations.append("manifest.json is missing; evidence integrity cannot be verified.")
    elif integrity["state"] != "Verified":
        limitations.append(f"{len(integrity['failed'])} artifact(s) referenced by the manifest could not be verified.")
    if decision_packet is None:
        limitations.append("decision-packet.json is missing; the visible decision is conservative.")
    if release_candidate is None:
        limitations.append("release-candidate-summary.json is missing; release readiness cannot be established.")
    if trust_safety_review is None:
        limitations.append("trust-safety-review.json is missing; internal trust-safety posture is unverified for this run.")
    if system_dossier is None:
        limitations.append("system-dossier.json is missing; system composition and scope are unverified.")

    # Visible decision is never more favorable than the raw layer allows, and is capped to
    # a conservative label whenever any material evidence is missing.
    if decision_packet is not None and raw_layer["confirmed"]:
        decision = decision_packet.get("decision") or {}
        visible_decision = str(decision.get("value") or MISSING_EVIDENCE_LABEL)
    else:
        visible_decision = "Not Ready"

    return {
        "visible_decision": visible_decision,
        "one_line_reason": _one_line_reason(decision_packet),
        "score": _score(decision_packet),
        "top_blockers": _top_blockers(decision_packet),
        "next_action": _next_action(decision_packet),
        "required_reviewers": _required_reviewers(decision_packet),
        "layers": {
            "raw_scanner_decision": raw_layer,
            "review_readiness": review_layer,
            "risk_acceptance_coverage": risk_layer,
            "release_readiness": release_layer,
            "human_approval": human_layer,
        },
        "integrity": integrity,
        "limitations": sorted(set(limitations)),
        "non_claims": list(NON_CLAIMS),
        "evidence_package": str(package),
        "manifest_hash": (manifest or {}).get("package_sha256"),
    }


def _e(value: Any) -> str:
    """HTML-escape any renderable value; never trust evidence-package content as markup."""
    return html.escape(str(value), quote=True)


def _status_class(display: str, confirmed: bool) -> str:
    if not confirmed or display in (MISSING_EVIDENCE_LABEL, "Unknown", "Insufficient Evidence"):
        return "state-unknown"
    lowered = display.lower()
    if any(k in lowered for k in ("not approved", "not ready", "rejected", "critical", "failed")):
        return "state-critical"
    if any(k in lowered for k in ("mandatory review", "conditional", "caution", "warning", "partial")):
        return "state-caution"
    if any(k in lowered for k in ("ready for review", "review", "covered", "not ready")):
        return "state-review"
    return "state-review"


def _layer_slot_html(name: str, layer: dict[str, Any], *, empty_slot: bool = False) -> str:
    display = layer.get("display", MISSING_EVIDENCE_LABEL)
    confirmed = bool(layer.get("confirmed"))
    css_state = "state-empty" if empty_slot else _status_class(display, confirmed)
    empty_tag = (
        '<span class="empty-tag">Human approval is not inferred</span>' if empty_slot else ""
    )
    return f"""
      <div class="slot {css_state}">
        <div class="slot-name">{_e(name)}</div>
        <div class="slot-state">{_e(display)}</div>
        {empty_tag}
      </div>"""


def _blockers_html(blockers: list[str]) -> str:
    if not blockers:
        return '<li class="blocker-item unknown">Missing Evidence — no blocking reasons could be read from the decision packet.</li>'
    return "\n".join(f'<li class="blocker-item">{_e(b)}</li>' for b in blockers)


def _reviewers_html(reviewers: list[str]) -> str:
    return "\n".join(f'<span class="role-chip">{_e(r)}</span>' for r in reviewers)


def _limitations_html(limitations: list[str]) -> str:
    if not limitations:
        return '<li class="limitation-item">No material limitations recorded for this run.</li>'
    return "\n".join(f'<li class="limitation-item">{_e(item)}</li>' for item in limitations)


def _non_claims_html(non_claims: list[str]) -> str:
    return "\n".join(f'<span class="nc-item">{_e(item)}</span>' for item in non_claims)


def _integrity_badge(integrity: dict[str, Any]) -> str:
    state = integrity.get("state", "Missing")
    if state == "Verified":
        css = "integrity-verified"
        label = f"Integrity verified · {integrity['verified_count']}/{integrity['total_count']} artifacts"
    elif state == "Partial":
        css = "integrity-partial"
        label = f"Integrity partial · {integrity['verified_count']}/{integrity['total_count']} artifacts verified"
    else:
        css = "integrity-missing"
        label = "Integrity unknown · manifest missing or unreadable"
    return f'<span class="integrity-badge {css}">{_e(label)}</span>'


_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>ManifestIQ — Board Verdict Room</title>
<style>
{css}
</style>
</head>
<body>
<header class="topbar">
  <div class="wrap topbar-row">
    <div class="brand">ManifestIQ <span>· Executive Assurance Cockpit</span></div>
    <div class="chip-scope">{integrity_badge}</div>
  </div>
</header>

<main class="wrap">
  <section class="decision-card" aria-label="Visible decision">
    <div class="eyebrow">Visible decision</div>
    <div class="verdict">{visible_decision}
      <small>Deterministic outcome. This is not an approval and confers no approval.</small>
    </div>
    <div class="rationale-line"><b>Why:</b> {one_line_reason}</div>

    <ul class="blocker-list">
      {blockers_html}
    </ul>

    <div class="nextaction">
      <span class="lab">Next action</span>
      <span>{next_action}</span>
    </div>

    <div class="roles">
      {reviewers_html}
    </div>
  </section>

  <section class="layers" aria-label="Decision layers — kept separate">
    <h2>Decision layers — never merged</h2>
    <div class="slots">
      {layer_raw}
      {layer_review}
      {layer_risk}
      {layer_release}
      {layer_human}
    </div>
  </section>

  <section class="panel" aria-label="Missing evidence and limitations">
    <div class="hd">Limitations</div>
    <ul class="limitation-list">
      {limitations_html}
    </ul>
  </section>
</main>

<footer class="nonclaims" aria-label="Standing non-claims">
  <div class="inner">
    <span class="lab">Non-claims</span>
    {non_claims_html}
  </div>
</footer>
</body>
</html>
"""

_CSS = """
:root{
  --paper:#eef1f4; --panel:#ffffff; --panel-2:#f7f9fb;
  --ink:#16202b; --muted:#5b6b7a; --faint:#8a98a6;
  --line:#d7dee5; --line-strong:#c2ccd6;
  --red:#9c2027; --red-bg:#f7e9ea;
  --amber:#8a5d00; --amber-bg:#f7efdd;
  --slate:#2f5b8a; --slate-bg:#e7eff7;
  --verify:#1f7a5a; --verify-bg:#e4f1eb;
  --unknown:#6a7885;
  --mono: ui-monospace, "Cascadia Mono", Consolas, "Liberation Mono", Menlo, monospace;
  --sans: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --radius:4px;
}
@media (prefers-color-scheme: dark){
  :root{
    --paper:#0f151b; --panel:#151d25; --panel-2:#111820;
    --ink:#e7edf3; --muted:#9fb0bf; --faint:#6f8091;
    --line:#25313c; --line-strong:#324150;
    --red:#e07b82; --red-bg:#2a171a;
    --amber:#d7a94b; --amber-bg:#241d10;
    --slate:#8fb4dc; --slate-bg:#14202c;
    --verify:#6fc4a0; --verify-bg:#122019;
    --unknown:#8496a4;
  }
}
*{box-sizing:border-box}
html,body{margin:0}
body{font-family:var(--sans); color:var(--ink); background:var(--paper); line-height:1.5; padding-bottom:70px;}
.wrap{max-width:1180px; margin:0 auto; padding:0 20px}
.eyebrow{font-size:11px; letter-spacing:.14em; text-transform:uppercase; color:var(--muted); font-weight:600}
.topbar{background:var(--panel); border-bottom:1px solid var(--line)}
.topbar-row{display:flex; align-items:center; gap:16px; padding:14px 0; flex-wrap:wrap}
.brand{font-weight:700; font-size:15px}
.brand span{color:var(--muted); font-weight:500}
.chip-scope{margin-left:auto}
.integrity-badge{font-family:var(--mono); font-size:12px; border-radius:100px; padding:4px 12px; border:1px solid var(--line-strong)}
.integrity-verified{color:var(--verify); background:var(--verify-bg); border-color:var(--verify)}
.integrity-partial{color:var(--amber); background:var(--amber-bg); border-color:var(--amber)}
.integrity-missing{color:var(--unknown); background:var(--panel-2)}
main{padding:24px 0 8px}
.decision-card{background:var(--panel); border:1px solid var(--line-strong); border-left:6px solid var(--red); border-radius:var(--radius); padding:22px 24px;}
.verdict{font-size:26px; font-weight:750; margin:4px 0 2px}
.verdict small{display:block; font-size:13px; font-weight:600; color:var(--red); margin-top:6px}
.rationale-line{margin-top:16px; padding-top:14px; border-top:1px solid var(--line); font-size:14px}
.blocker-list{list-style:none; margin:14px 0 0; padding:0}
.blocker-item{font-size:13.5px; padding:6px 0; border-top:1px solid var(--line)}
.blocker-item:first-child{border-top:none}
.blocker-item.unknown{color:var(--unknown); font-style:italic}
.nextaction{margin-top:14px; display:flex; gap:12px; flex-wrap:wrap; align-items:baseline}
.nextaction .lab{font-size:11px; letter-spacing:.12em; text-transform:uppercase; color:var(--muted); font-weight:600; min-width:96px}
.roles{margin-top:14px; display:flex; gap:8px; flex-wrap:wrap}
.role-chip{font-size:12.5px; font-weight:600; border:1px solid var(--line-strong); border-radius:100px; padding:6px 12px; background:var(--panel-2)}
.layers{margin-top:18px}
.layers h2{font-size:12px; letter-spacing:.12em; text-transform:uppercase; color:var(--muted); font-weight:600; margin:0 0 8px}
.slots{display:grid; grid-template-columns:repeat(5,1fr); gap:10px}
.slot{background:var(--panel); border:1px solid var(--line); border-radius:var(--radius); padding:12px}
.slot-name{font-size:10.5px; letter-spacing:.08em; text-transform:uppercase; color:var(--faint); font-weight:600}
.slot-state{font-weight:700; font-size:14px; margin-top:6px}
.state-critical .slot-state{color:var(--red)}
.state-caution .slot-state{color:var(--amber)}
.state-review .slot-state{color:var(--slate)}
.state-unknown .slot-state{color:var(--unknown)}
.state-empty{border-style:dashed; border-color:var(--line-strong); background:repeating-linear-gradient(45deg, transparent 0 8px, rgba(120,135,150,.10) 8px 9px)}
.state-empty .slot-state{color:var(--unknown); font-style:italic; font-weight:600}
.empty-tag{display:inline-block; margin-top:6px; font-size:10.5px; color:var(--unknown); border:1px dashed var(--line-strong); border-radius:3px; padding:2px 7px}
.panel{margin-top:18px; background:var(--panel); border:1px solid var(--line); border-radius:var(--radius)}
.panel .hd{padding:12px 16px; border-bottom:1px solid var(--line); font-size:13px; letter-spacing:.06em; text-transform:uppercase; font-weight:700}
.limitation-list{list-style:none; margin:0; padding:10px 16px 14px}
.limitation-item{font-size:13px; color:var(--muted); padding:6px 0; border-top:1px solid var(--line)}
.limitation-item:first-child{border-top:none}
.nonclaims{position:fixed; left:0; right:0; bottom:0; background:var(--panel); border-top:2px solid var(--line-strong)}
.nonclaims .inner{display:flex; align-items:center; gap:10px 18px; padding:10px 20px; flex-wrap:wrap; max-width:1180px; margin:0 auto}
.nonclaims .lab{font-size:10px; letter-spacing:.14em; text-transform:uppercase; color:var(--red); font-weight:700}
.nc-item{font-size:11.5px; color:var(--muted)}
@media (max-width:900px){.slots{grid-template-columns:repeat(2,1fr)}}
@media (prefers-reduced-motion:reduce){*{transition:none!important; animation:none!important}}
"""


def render_executive_cockpit_html(view: dict[str, Any]) -> str:
    layers = view["layers"]
    return _TEMPLATE.format(
        css=_CSS,
        integrity_badge=_integrity_badge(view["integrity"]),
        visible_decision=_e(view["visible_decision"]),
        one_line_reason=_e(view["one_line_reason"]),
        blockers_html=_blockers_html(view["top_blockers"]),
        next_action=_e(view["next_action"]),
        reviewers_html=_reviewers_html(view["required_reviewers"]),
        layer_raw=_layer_slot_html("1 · Raw Scanner Decision", layers["raw_scanner_decision"]),
        layer_review=_layer_slot_html("2 · Review Readiness", layers["review_readiness"]),
        layer_risk=_layer_slot_html("3 · Risk Acceptance Coverage", layers["risk_acceptance_coverage"]),
        layer_release=_layer_slot_html("4 · Release Readiness", layers["release_readiness"]),
        layer_human=_layer_slot_html("5 · Human Approval", layers["human_approval"], empty_slot=True),
        limitations_html=_limitations_html(view["limitations"]),
        non_claims_html=_non_claims_html(view["non_claims"]),
    )


def collect_executive_gui(evidence_package: Path | str, output_dir: Path | str) -> Path:
    """
    Read an existing evidence package and render the Board Verdict Room to a single
    self-contained HTML file. Read-only: never writes into the evidence package.
    """
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    view = build_board_verdict_view(evidence_package)
    document = render_executive_cockpit_html(view)
    out_path = output / "manifestiq-executive-cockpit.html"
    out_path.write_text(document, encoding="utf-8")
    return out_path
