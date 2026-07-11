import type { ReactElement } from "react";
import type { DecisionLayers } from "../data/boardVerdictSchema";
import { DecisionLayerSlot } from "./DecisionLayerSlot";
import "./FiveLayerTrustStrip.css";

interface FiveLayerTrustStripProps {
  layers: DecisionLayers;
}

/**
 * Per docs/design/COMPONENT_RULES.md §4: the five decision layers as five
 * separate, non-promotable gates of one trust instrument. NEVER merged into
 * a single status pill — the strip is deliberately five connected gates, not
 * a summary badge. No green, no gold anywhere in the strip.
 */
export function FiveLayerTrustStrip({ layers }: FiveLayerTrustStripProps): ReactElement {
  return (
    <section className="trust-strip" aria-label="Decision layers — kept separate">
      <div className="trust-strip__header">
        <h2 className="trust-strip__title type-eyebrow">Decision layers</h2>
        <span className="trust-strip__note">Separate and non-promotable — never merged</span>
      </div>
      <div className="trust-strip__instrument">
        <DecisionLayerSlot index={1} name="Raw Scanner Decision" layer={layers.raw_scanner_decision} />
        <DecisionLayerSlot index={2} name="Review Readiness" layer={layers.review_readiness} />
        <DecisionLayerSlot
          index={3}
          name="Risk Acceptance Coverage"
          layer={layers.risk_acceptance_coverage}
        />
        <DecisionLayerSlot index={4} name="Release Readiness" layer={layers.release_readiness} />
        <DecisionLayerSlot
          index={5}
          name="Human Approval"
          layer={layers.human_approval}
          isHumanApprovalSlot
        />
      </div>
    </section>
  );
}
