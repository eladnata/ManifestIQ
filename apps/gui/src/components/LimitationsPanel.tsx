import type { ReactElement } from "react";
import { Surface } from "../design-system/primitives/Surface";
import "./LimitationsPanel.css";

interface LimitationsPanelProps {
  limitations: string[];
}

/**
 * Renders every run-specific limitation as a calm trust boundary — visible
 * but secondary to the verdict (docs/design/UI_FOUNDATIONS.md §10: missing
 * evidence is always visible, never hidden; VISUAL_TASTE_DOCTRINE.md §12: the
 * product is honest about what it does not know). Reads as a quiet rail, not
 * an error report. The phrase "Raw decision provenance incomplete" is shown
 * verbatim when present, exactly as the data contract states it.
 */
export function LimitationsPanel({ limitations }: LimitationsPanelProps): ReactElement {
  return (
    <Surface variant="inset" ariaLabel="Limitations">
      <div className="limitations-panel">
        <span className="type-eyebrow limitations-panel__label">Limitations</span>
        <span className="limitations-panel__note">What this run could not establish</span>
        {limitations.length === 0 ? (
          <p className="limitations-panel__empty">No material limitations recorded for this run.</p>
        ) : (
          <ul className="limitations-panel__list">
            {limitations.map((item) => (
              <li key={item} className="limitations-panel__item">
                {item}
              </li>
            ))}
          </ul>
        )}
      </div>
    </Surface>
  );
}
