import type { ReactElement } from "react";
import "./NextActionBar.css";

interface NextActionBarProps {
  nextAction: string;
}

/**
 * One next action for the room's one question. Per docs/design/
 * COMPONENT_RULES.md §17: verb-first, honest, never an approval affordance.
 * Presented as a labelled statement rather than a button — the described
 * action happens outside this read-only viewer, so there is nothing to
 * submit. Lives in the hero's assurance rail as part of the Hero Decision
 * Area's required content (COMPONENT_RULES.md §3).
 */
export function NextActionBar({ nextAction }: NextActionBarProps): ReactElement {
  return (
    <div className="next-action">
      <span className="type-eyebrow next-action__label">Next action</span>
      <p className="next-action__text">
        <span className="next-action__marker" aria-hidden="true" />
        {nextAction}
      </p>
    </div>
  );
}
