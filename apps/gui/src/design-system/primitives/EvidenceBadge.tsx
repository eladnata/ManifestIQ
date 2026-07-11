import { useState, type ReactElement } from "react";
import "./EvidenceBadge.css";

interface EvidenceBadgeProps {
  reference: string;
  detail?: string;
}

/**
 * Per docs/design/COMPONENT_RULES.md §16: attaches a traceable evidence
 * reference to a claim and routes to it. A claim with no evidence badge
 * must not be styled as confirmed. Click reveals a compact inline detail —
 * no navigation, no editing, no external link.
 */
export function EvidenceBadge({ reference, detail }: EvidenceBadgeProps): ReactElement {
  const [open, setOpen] = useState(false);

  return (
    <span className="evidence-badge-wrap">
      <button
        type="button"
        className="evidence-badge"
        aria-expanded={open}
        onClick={() => setOpen((v) => !v)}
      >
        <span className="type-mono">{reference}</span>
      </button>
      {open && detail ? <span className="evidence-badge-detail type-mono">{detail}</span> : null}
    </span>
  );
}
