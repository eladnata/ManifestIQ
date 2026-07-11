import type { BoardVerdictData } from "../data/boardVerdictSchema";
import type { RunStatus } from "./apiClient";

export type JourneyState =
  | "preflight_ready"
  | "scan_running"
  | "scan_failed_closed"
  | "scan_complete_unsealed"
  | "evidence_sealed"
  | "verdict_ready";

export function deriveJourneyState(run: RunStatus | null, boardVerdict: BoardVerdictData | null): JourneyState {
  if (run == null) {
    return "scan_running";
  }
  if (run.status === "failed") {
    return "scan_failed_closed";
  }
  if (boardVerdict != null && run.board_verdict_ready) {
    return "verdict_ready";
  }
  return run.journey_state;
}

export function stationForJourneyState(state: JourneyState): "launch" | "preflight" | "scan" | "sealed" | "verdict" {
  switch (state) {
    case "preflight_ready":
      return "preflight";
    case "evidence_sealed":
      return "sealed";
    case "verdict_ready":
      return "verdict";
    case "scan_running":
    case "scan_failed_closed":
    case "scan_complete_unsealed":
    default:
      return "scan";
  }
}

export function shouldAdvanceFromScan(state: JourneyState): boolean {
  return state === "evidence_sealed" || state === "verdict_ready";
}
