// GENERATED FILE — produced by apps/gui/scripts/embed-data.mjs from
// ../../gui-output/board-verdict-data.json
// Do not hand-edit. Re-run the embed step to refresh.
import type { BoardVerdictData } from "../data/boardVerdictSchema";

export const boardVerdictData: BoardVerdictData = {
  "evidence_package": "output\\evidence-package",
  "executive_decision_label": "Not Ready — Return for Remediation",
  "integrity": {
    "failed": [],
    "state": "Verified",
    "total_count": 34,
    "verified_count": 34
  },
  "layers": {
    "human_approval": {
      "confirmed": false,
      "display": "Human approval is not inferred",
      "empty": true
    },
    "raw_scanner_decision": {
      "confirmed": false,
      "display": "Not Approved",
      "limitations": [
        "Raw decision provenance incomplete"
      ]
    },
    "release_readiness": {
      "confirmed": false,
      "display": "Missing Evidence"
    },
    "review_readiness": {
      "confirmed": true,
      "display": "Mandatory Review",
      "source_value": "Not Approved"
    },
    "risk_acceptance_coverage": {
      "confirmed": false,
      "display": "Missing Evidence"
    }
  },
  "limitations": [
    "Raw decision provenance incomplete",
    "release-candidate-summary.json is missing; release readiness cannot be established.",
    "trust-safety-review.json is missing; internal trust-safety posture is unverified for this run."
  ],
  "manifest_hash": "8e2840229a3de6cac1e30cf147232c108224c3515ba25515c9194a6039bf91f5",
  "next_action": "Add ACCESS_CONTROL documentation artifact",
  "non_claims": [
    "Not certified",
    "No SOX / privacy / legal approval",
    "Not a release approval",
    "No safety claim",
    "Human approval is not inferred"
  ],
  "one_line_reason": "Blocked by: ARCH-011: Missing owner metadata",
  "required_reviewers": [
    "AppSec",
    "CISO",
    "CTO / Enterprise Architecture",
    "Data Governance",
    "DevOps / SRE",
    "ITGC / SOX Reviewer",
    "Legal / Open Source Review",
    "Release Manager / Control Owner",
    "Security Architecture"
  ],
  "schema": "manifestiq-board-verdict-data",
  "schema_version": "0.1",
  "score": 41,
  "top_blockers": [
    "ARCH-011: Missing owner metadata",
    "GOV-001: Missing required documentation: OWNER",
    "OPS-002: No audit logging evidence detected"
  ],
  "visible_decision": "Not Ready"
};
