import { useState, type ReactElement } from "react";
import { parseBlocker, MISSING_EVIDENCE_LABEL } from "../lib/blockerModel";
import "./BlockerCard.css";

interface BlockerCardProps {
  statement: string;
}

/**
 * Per docs/design/COMPONENT_RULES.md §5 (Blocker Card): one blocker presented
 * as an executive decision-driver — severity lane, domain/rule family, title,
 * disposition, and an evidence route. A card, never a table row or accordion.
 * Fields the evidence does not provide (business impact) render as an explicit
 * "Missing Evidence" fact rather than being fabricated. Click the evidence
 * reference to reveal the raw finding verbatim; nothing is editable.
 */
export function BlockerCard({ statement }: BlockerCardProps): ReactElement {
  const [open, setOpen] = useState(false);
  const { ruleId, title, domainFamily, hasRuleId } = parseBlocker(statement);

  return (
    <article className="blocker-card">
      <header className="blocker-card__head">
        <span className="blocker-card__severity">
          <span className="blocker-card__severity-dot" aria-hidden="true" />
          Blocking
        </span>
        <span className="blocker-card__domain">{domainFamily}</span>
      </header>

      <h3 className="blocker-card__title">{title}</h3>

      <dl className="blocker-card__meta">
        <div className="blocker-card__meta-row">
          <dt>Rule</dt>
          <dd className="type-mono blocker-card__rule">{ruleId}</dd>
        </div>
        <div className="blocker-card__meta-row">
          <dt>Disposition</dt>
          <dd>
            <span className="blocker-card__disposition">Mandatory Review</span>
          </dd>
        </div>
        <div className="blocker-card__meta-row">
          <dt>Business impact</dt>
          <dd>
            <span className="blocker-card__missing">{MISSING_EVIDENCE_LABEL}</span>
          </dd>
        </div>
      </dl>

      <footer className="blocker-card__foot">
        <button
          type="button"
          className="blocker-card__evidence"
          aria-expanded={open}
          disabled={!hasRuleId}
          onClick={() => setOpen((v) => !v)}
        >
          <span className="blocker-card__evidence-mark" aria-hidden="true">
            ⌗
          </span>
          Evidence reference
        </button>
        {open && (
          <p className="blocker-card__evidence-detail type-mono">
            {ruleId} — {title}
          </p>
        )}
      </footer>
    </article>
  );
}
