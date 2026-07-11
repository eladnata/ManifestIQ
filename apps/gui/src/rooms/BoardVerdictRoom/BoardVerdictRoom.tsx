import type { ReactElement } from "react";
import type { BoardVerdictData } from "../../data/boardVerdictSchema";
import { VerdictHero } from "../../components/VerdictHero";
import { FiveLayerTrustStrip } from "../../components/FiveLayerTrustStrip";
import { BlockerCard } from "../../components/BlockerCard";
import { RequiredReviewers } from "../../components/RequiredReviewers";
import { LimitationsPanel } from "../../components/LimitationsPanel";
import { statusTone } from "../../lib/statusTone";
import "./BoardVerdictRoom.css";

interface BoardVerdictRoomProps {
  data: BoardVerdictData;
}

/**
 * Per docs/design/MANIFESTIQ_DESIGN_SKILL_PACK.md §6 Room 1 and
 * docs/design/SCREEN_PURPOSE_MATRIX.md: one job — "Can this system proceed —
 * if not, why not and what next?" answered in five seconds. Composition:
 * hero (decision + reason + score + next action), the three decision-driver
 * blocker cards, the five-layer trust instrument (with human approval empty),
 * then the secondary reviewer + limitations rails. No table, no domain map,
 * no evidence ledger, no portfolio, no debug JSON — those are other rooms.
 */
export function BoardVerdictRoom({ data }: BoardVerdictRoomProps): ReactElement {
  const heroTone = statusTone(data.visible_decision, true);
  const resolvedHeroTone: "critical" | "caution" | "review" =
    heroTone === "critical" || heroTone === "review" ? heroTone : "caution";

  return (
    <div className="wrap board-verdict-room">
      <VerdictHero
        executiveDecisionLabel={data.executive_decision_label}
        oneLineReason={data.one_line_reason}
        score={data.score}
        nextAction={data.next_action}
        tone={resolvedHeroTone}
      />

      <section className="board-verdict-room__blockers" aria-label="Top blockers">
        <div className="board-verdict-room__section-head">
          <h2 className="type-eyebrow">Top blockers</h2>
          <span className="board-verdict-room__section-note">
            Decision drivers returning this system for remediation
          </span>
        </div>
        {data.top_blockers.length === 0 ? (
          <p className="board-verdict-room__no-blockers">
            Missing Evidence — no blocking reasons could be read from the decision packet.
          </p>
        ) : (
          <div className="board-verdict-room__blocker-grid">
            {data.top_blockers.map((statement) => (
              <BlockerCard key={statement} statement={statement} />
            ))}
          </div>
        )}
      </section>

      <FiveLayerTrustStrip layers={data.layers} />

      <div className="board-verdict-room__support">
        <RequiredReviewers reviewers={data.required_reviewers} />
        <LimitationsPanel limitations={data.limitations} />
      </div>
    </div>
  );
}
