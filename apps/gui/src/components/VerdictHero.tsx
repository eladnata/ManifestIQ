import type { ReactElement } from "react";
import { NextActionBar } from "./NextActionBar";
import "./VerdictHero.css";

interface VerdictHeroProps {
  executiveDecisionLabel: string;
  oneLineReason: string;
  score: number | null;
  nextAction: string;
  tone: "critical" | "caution" | "review";
}

/**
 * Per docs/design/COMPONENT_RULES.md §3 (Hero Decision Area): the single
 * focal surface of the room and the one editorial moment on the screen
 * (VISUAL_TASTE_DOCTRINE.md §6). A boardroom decision statement — not a card
 * title. Left region carries the verdict; the right assurance rail carries a
 * bounded score and the one next action. Never green, never a merged status
 * pill, never an "Approved" output.
 */
export function VerdictHero({
  executiveDecisionLabel,
  oneLineReason,
  score,
  nextAction,
  tone,
}: VerdictHeroProps): ReactElement {
  const boundedScore = score === null ? null : Math.max(0, Math.min(100, score));

  return (
    <section className={`verdict-hero verdict-hero--${tone}`} aria-label="Visible executive decision">
      <div className="verdict-hero__statement">
        <div className="verdict-hero__eyebrow type-eyebrow">
          <span className="verdict-hero__eyebrow-dot" aria-hidden="true" />
          Visible decision
        </div>
        <h1 className="verdict-hero__headline">{executiveDecisionLabel}</h1>
        <p className="verdict-hero__disclaimer">
          Deterministic outcome. This is not an approval and confers no approval.
        </p>
        <p className="verdict-hero__reason">
          <span className="verdict-hero__reason-label">Why</span>
          {oneLineReason}
        </p>
      </div>

      <aside className="verdict-hero__rail" aria-label="Assurance summary">
        <div className="verdict-hero__score-block">
          <span className="type-eyebrow">Assurance score</span>
          <div className="verdict-hero__score-value">
            {boundedScore === null ? (
              <span className="verdict-hero__score-missing">Missing Evidence</span>
            ) : (
              <>
                <span className="verdict-hero__score-number type-mono">{boundedScore}</span>
                <span className="verdict-hero__score-scale type-mono">/ 100</span>
              </>
            )}
          </div>
          {boundedScore !== null && (
            <div
              className="verdict-hero__meter"
              role="img"
              aria-label={`Assurance score ${boundedScore} of 100, bounded by missing evidence`}
            >
              <span className="verdict-hero__meter-fill" style={{ width: `${boundedScore}%` }} />
            </div>
          )}
          <span className="verdict-hero__score-caption">
            Deterministic · local evidence only · bounded by missing evidence
          </span>
        </div>

        <div className="verdict-hero__rail-divider" />

        <NextActionBar nextAction={nextAction} />
      </aside>
    </section>
  );
}
