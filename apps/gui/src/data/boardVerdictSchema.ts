/**
 * TypeScript mirror of the Board Verdict Room data contract produced by
 * scanner/ui/executive_gui_renderer.py (build_board_verdict_data_contract).
 *
 * This file defines shape only. It performs no computation, inference, or
 * mutation of any decision, score, or status. All values are read verbatim
 * from the JSON exported by `python -m scanner render-gui-data`.
 *
 * Do not change scanner logic, scoring, or trust/fail-closed behavior to
 * satisfy this shape — if the Python contract changes, update this file to
 * match it, never the reverse.
 */

export interface DecisionLayer {
  display: string;
  confirmed: boolean;
  limitations?: string[];
  source_value?: string;
  empty?: boolean;
}

export interface DecisionLayers {
  raw_scanner_decision: DecisionLayer;
  review_readiness: DecisionLayer;
  risk_acceptance_coverage: DecisionLayer;
  release_readiness: DecisionLayer;
  human_approval: DecisionLayer;
}

export interface EvidenceIntegrityState {
  state: "Verified" | "Partial" | "Missing";
  verified_count: number;
  total_count: number;
  failed: string[];
}

export type BlockerSummary = string;
export type Limitation = string;
export type ReviewerRole = string;

export interface BoardVerdictData {
  schema: string;
  schema_version: string;
  visible_decision: string;
  executive_decision_label: string;
  one_line_reason: string;
  score: number | null;
  top_blockers: BlockerSummary[];
  next_action: string;
  required_reviewers: ReviewerRole[];
  layers: DecisionLayers;
  integrity: EvidenceIntegrityState;
  limitations: Limitation[];
  non_claims: string[];
  evidence_package: string;
  manifest_hash: string | null;
}

export const EXPECTED_SCHEMA = "manifestiq-board-verdict-data";

export function isBoardVerdictData(value: unknown): value is BoardVerdictData {
  if (typeof value !== "object" || value === null) return false;
  const v = value as Record<string, unknown>;
  return (
    v.schema === EXPECTED_SCHEMA &&
    typeof v.visible_decision === "string" &&
    typeof v.layers === "object" &&
    v.layers !== null
  );
}
