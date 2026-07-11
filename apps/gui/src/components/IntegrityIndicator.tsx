import type { ReactElement } from "react";
import type { EvidenceIntegrityState } from "../data/boardVerdictSchema";
import { IconFrame } from "../design-system/primitives/IconFrame";
import { SealIcon, EmptySlotIcon } from "../design-system/icons";
import "./IntegrityIndicator.css";

interface IntegrityIndicatorProps {
  integrity: EvidenceIntegrityState | null;
}

/**
 * Per docs/design/COMPONENT_RULES.md §8 (Evidence Seal): signals verified
 * artifact integrity — a fact, never a judgment. This is the ONE place in
 * the workbench where the integrity-green tone may appear, and only when the
 * state is genuinely Verified. Partial/Missing use amber/unknown-gray, never
 * green. `integrity === null` means no sealed run exists yet (pre-scan
 * stations) — rendered as a quiet, honest "no run yet" state, never a
 * fabricated pass.
 */
export function IntegrityIndicator({ integrity }: IntegrityIndicatorProps): ReactElement {
  if (integrity === null) {
    return (
      <span className="integrity-indicator integrity-indicator--unknown" title="No sealed run yet">
        <IconFrame size="sm" tone="unknown">
          <EmptySlotIcon size={14} />
        </IconFrame>
        <span className="type-mono integrity-indicator__label">No sealed run yet</span>
      </span>
    );
  }

  const { state, verified_count, total_count } = integrity;

  const tone = state === "Verified" ? "integrity" : state === "Partial" ? "caution" : "unknown";
  const label =
    state === "Verified"
      ? `Integrity verified · ${verified_count}/${total_count} artifacts`
      : state === "Partial"
        ? `Integrity partial · ${verified_count}/${total_count} verified`
        : "Integrity unknown · manifest missing";

  return (
    <span className={`integrity-indicator integrity-indicator--${tone}`} title={label}>
      <IconFrame size="sm" tone={tone}>
        <SealIcon size={14} />
      </IconFrame>
      <span className="type-mono integrity-indicator__label">{label}</span>
    </span>
  );
}
