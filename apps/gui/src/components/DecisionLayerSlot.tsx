import type { ReactElement } from "react";
import type { DecisionLayer } from "../data/boardVerdictSchema";
import { statusTone } from "../lib/statusTone";
import "./DecisionLayerSlot.css";

interface DecisionLayerSlotProps {
  index: number;
  name: string;
  layer: DecisionLayer;
  isHumanApprovalSlot?: boolean;
}

/**
 * Per docs/design/COMPONENT_RULES.md §4 (one slot of the Five-Layer Trust
 * Strip): a single decision layer as one gate of a preflight instrument.
 * A thin top accent reads like an annunciator light — calm, never alarmist.
 * The human-approval slot is the only one rendered permanently empty (dashed
 * + hatched), never filled, never colored review/integrity/gold.
 */
export function DecisionLayerSlot({
  index,
  name,
  layer,
  isHumanApprovalSlot = false,
}: DecisionLayerSlotProps): ReactElement {
  const tone = isHumanApprovalSlot ? "unknown" : statusTone(layer.display, layer.confirmed);

  return (
    <div
      className={`layer-slot layer-slot--${tone} ${isHumanApprovalSlot ? "layer-slot--empty" : ""}`}
      aria-label={`${name}: ${layer.display}`}
    >
      <span className="layer-slot__accent" aria-hidden="true" />
      <span className="layer-slot__index type-mono">{String(index).padStart(2, "0")}</span>
      <span className="layer-slot__name">{name}</span>
      <span className="layer-slot__state">{isHumanApprovalSlot ? "Not present" : layer.display}</span>
      {isHumanApprovalSlot && (
        <span className="layer-slot__empty-tag">{layer.display}</span>
      )}
    </div>
  );
}
