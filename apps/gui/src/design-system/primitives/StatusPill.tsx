import type { ReactElement } from "react";
import "./StatusPill.css";

export type PillTone = "critical" | "caution" | "review" | "unknown" | "integrity";

interface StatusPillProps {
  label: string;
  tone: PillTone;
}

/**
 * Per docs/design/COMPONENT_RULES.md §15: labels a single state from the
 * sanctioned status vocabulary. One meaning — never color alone. The
 * "integrity" tone is the only sanctioned green and is reserved for
 * evidence-integrity facts; it must never be used for a decision, layer,
 * or readiness state.
 */
export function StatusPill({ label, tone }: StatusPillProps): ReactElement {
  return <span className={`status-pill status-pill--${tone}`}>{label}</span>;
}
