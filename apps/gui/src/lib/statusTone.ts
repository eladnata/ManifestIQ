import type { PillTone } from "../design-system/primitives/StatusPill";

const MISSING_LABELS = new Set(["Missing Evidence", "Unknown", "Insufficient Evidence"]);

/**
 * Classify a decision-layer display string into a visual tone. Mirrors
 * scanner/ui/executive_gui_renderer.py:_status_class exactly so the React
 * shell and the Phase 16A static HTML renderer agree on meaning.
 *
 * This function never returns "integrity" — that tone is reserved
 * exclusively for the evidence-integrity indicator (docs/design/
 * DESIGN_TOKENS.md: "Green may represent only evidence integrity facts").
 */
export function statusTone(display: string, confirmed: boolean): PillTone {
  if (!confirmed || MISSING_LABELS.has(display)) {
    return "unknown";
  }
  const lowered = display.toLowerCase();
  if (["not approved", "not ready", "rejected", "critical", "failed"].some((k) => lowered.includes(k))) {
    return "critical";
  }
  if (["mandatory review", "conditional", "caution", "warning", "partial"].some((k) => lowered.includes(k))) {
    return "caution";
  }
  return "review";
}
