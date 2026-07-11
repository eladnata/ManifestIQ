import type { ReactElement } from "react";
import { Surface } from "../design-system/primitives/Surface";
import "./RequiredReviewers.css";

interface RequiredReviewersProps {
  reviewers: string[];
}

/**
 * Per docs/design/COMPONENT_RULES.md §12 (Reviewer Role Card / Chip):
 * signals required review roles — never a sign-off. Deliberately secondary
 * in visual weight to the verdict hero and blockers (per Phase 16B's "no
 * giant list of reviewers dominating the screen"): shown as quiet chips
 * inside a bounded card, capped visually, never a dashboard of workload.
 */
export function RequiredReviewers({ reviewers }: RequiredReviewersProps): ReactElement {
  return (
    <Surface variant="inset" ariaLabel="Required reviewers">
      <div className="required-reviewers">
        <span className="type-eyebrow required-reviewers__label">Required reviewers</span>
        <span className="required-reviewers__note">
          Review required before any human approval — not a sign-off
        </span>
        <div className="required-reviewers__chips">
          {reviewers.map((role) => (
            <span key={role} className="required-reviewers__chip">
              {role}
            </span>
          ))}
        </div>
      </div>
    </Surface>
  );
}
