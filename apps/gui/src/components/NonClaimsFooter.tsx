import type { ReactElement } from "react";
import "./NonClaimsFooter.css";

interface NonClaimsFooterProps {
  nonClaims: string[];
}

/**
 * Per docs/design/COMPONENT_RULES.md §2 (Footer Non-Claims Strip): fixed,
 * non-collapsible, always visible. Never dismissible, never scrolled away.
 * Quiet in visual weight but permanently present — this is the room's
 * standing denial of certification/compliance/approval/safety claims.
 */
export function NonClaimsFooter({ nonClaims }: NonClaimsFooterProps): ReactElement {
  return (
    <footer className="nonclaims" aria-label="Standing non-claims">
      <div className="wrap nonclaims__row">
        <span className="nonclaims__label">Non-claims</span>
        {nonClaims.map((item) => (
          <span key={item} className="nonclaims__item">
            {item}
          </span>
        ))}
      </div>
    </footer>
  );
}
