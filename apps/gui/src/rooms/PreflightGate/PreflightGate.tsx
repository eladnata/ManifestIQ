import type { ReactElement } from "react";
import { Surface } from "../../design-system/primitives/Surface";
import { Button } from "../../design-system/primitives/Button";
import { StatusPill } from "../../design-system/primitives/StatusPill";
import type { PreflightResult } from "../../lib/apiClient";
import "./PreflightGate.css";

interface PreflightGateProps {
  preflight: PreflightResult | null;
  loading: boolean;
  onStartScan: () => void;
  onBack: () => void;
  starting: boolean;
}

const STATE_LABEL: Record<PreflightResult["state"], string> = {
  ready: "Ready to scan",
  needs_attention: "Needs attention",
  cannot_run: "Cannot run",
};

const STATE_TONE: Record<PreflightResult["state"], "review" | "caution" | "critical"> = {
  ready: "review",
  needs_attention: "caution",
  cannot_run: "critical",
};

const CHECK_TONE: Record<string, "review" | "caution" | "critical"> = {
  pass: "review",
  warning: "caution",
  fail: "critical",
};

/**
 * Per docs/design/GUI_PRODUCT_WORKFLOW.md Step 2: validate the assessment
 * can run safely before committing. Fails closed — an unresolved blocker
 * (state "cannot_run") disables the only forward action. Never claims
 * security approval; "Ready to scan" is a precondition check, not a verdict.
 */
export function PreflightGate({ preflight, loading, onStartScan, onBack, starting }: PreflightGateProps): ReactElement {
  return (
    <div className="preflight-gate">
      <div className="type-eyebrow">Preflight Gate</div>
      <h1 className="preflight-gate__headline">Is this assessment safe to run?</h1>

      {loading || !preflight ? (
        <Surface variant="inset" className="preflight-gate__loading">
          <span className="type-eyebrow">Running preflight checks…</span>
        </Surface>
      ) : (
        <>
          <Surface variant="raised" className="preflight-gate__state-card" tone={STATE_TONE[preflight.state]}>
            <div className="preflight-gate__state-head">
              <div>
                <span className="type-eyebrow">Preflight readiness</span>
                <h2 className="preflight-gate__state-title">{STATE_LABEL[preflight.state]}</h2>
              </div>
              <StatusPill label={STATE_LABEL[preflight.state]} tone={STATE_TONE[preflight.state]} />
            </div>
            <p className="preflight-gate__state-note">
              This confirms the assessment can run deterministically and locally. It is not a security
              approval and confers none.
            </p>
          </Surface>

          <div className="preflight-gate__grid">
            <Surface variant="flush" className="preflight-gate__checks">
              <div className="preflight-gate__section-head">
                <span className="type-eyebrow">Readiness checks</span>
              </div>
              {preflight.checks.map((check) => (
                <div key={check.id} className="preflight-gate__check-row">
                  <StatusPill label={check.status === "pass" ? "Pass" : check.status === "warning" ? "Note" : "Blocked"} tone={CHECK_TONE[check.status]} />
                  <div className="preflight-gate__check-body">
                    <span className="preflight-gate__check-label">{check.label}</span>
                    <span className="preflight-gate__check-detail">{check.detail}</span>
                  </div>
                </div>
              ))}
            </Surface>

            <div className="preflight-gate__side">
              {preflight.blockers.length > 0 && (
                <Surface variant="inset" className="preflight-gate__blockers">
                  <span className="type-eyebrow">Blockers</span>
                  <ul className="preflight-gate__blocker-list">
                    {preflight.blockers.map((b) => (
                      <li key={b}>{b}</li>
                    ))}
                  </ul>
                </Surface>
              )}

              <Surface variant="inset" className="preflight-gate__artifacts">
                <span className="type-eyebrow">Expected artifacts</span>
                <div className="preflight-gate__artifact-chips">
                  {preflight.expected_artifacts.map((artifact) => (
                    <span key={artifact} className="type-mono preflight-gate__artifact-chip">
                      {artifact}
                    </span>
                  ))}
                </div>
              </Surface>
            </div>
          </div>

          <div className="preflight-gate__actions">
            <Button variant="secondary" onClick={onBack}>
              Back to Configure
            </Button>
            <Button
              variant="primary"
              disabled={preflight.state === "cannot_run" || starting}
              onClick={onStartScan}
            >
              {starting ? "Starting…" : "Start Scan"}
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
