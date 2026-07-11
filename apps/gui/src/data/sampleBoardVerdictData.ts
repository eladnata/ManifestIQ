import type { BoardVerdictData } from "./boardVerdictSchema";

/**
 * Committed sample fixture used for local development (`npm run dev`) and as
 * a design reference. This is deliberately conservative: it exercises the
 * missing-evidence and incomplete-raw-provenance paths so the UI never has
 * to be developed against an all-green happy path. This file is NOT the
 * live data path for a production render — see src/generated/ for that.
 */
export const sampleBoardVerdictData: BoardVerdictData = {
  schema: "manifestiq-board-verdict-data",
  schema_version: "0.1",
  visible_decision: "Not Ready",
  executive_decision_label: "Not Ready — Return for Remediation",
  one_line_reason: "Blocked by: SEC-001: Hardcoded secret detected",
  score: 41,
  top_blockers: [
    "SEC-001: Hardcoded secret detected",
    "ARCH-011: Missing owner metadata",
    "GOV-001: Missing required documentation: OWNER",
  ],
  next_action: "Remove hardcoded secret and rotate credential.",
  required_reviewers: ["CISO", "AppSec", "Security Architecture"],
  layers: {
    raw_scanner_decision: {
      display: "Not Approved",
      confirmed: false,
      limitations: ["Raw decision provenance incomplete"],
    },
    review_readiness: { display: "Mandatory Review", confirmed: true, source_value: "Not Approved" },
    risk_acceptance_coverage: { display: "Partially Covered", confirmed: true },
    release_readiness: { display: "Missing Evidence", confirmed: false },
    human_approval: { display: "Human approval is not inferred", confirmed: false, empty: true },
  },
  integrity: { state: "Verified", verified_count: 34, total_count: 34, failed: [] },
  limitations: [
    "Raw decision provenance incomplete",
    "release-candidate-summary.json is missing; release readiness cannot be established.",
    "trust-safety-review.json is missing; internal trust-safety posture is unverified for this run.",
  ],
  non_claims: [
    "Not certified",
    "No SOX / privacy / legal approval",
    "Not a release approval",
    "No safety claim",
    "Human approval is not inferred",
  ],
  evidence_package: "output/evidence-package",
  manifest_hash: "a83badaf980d50ed8097c4ab0c84baebd79905d2bfbad3acd7f2e51b",
};
