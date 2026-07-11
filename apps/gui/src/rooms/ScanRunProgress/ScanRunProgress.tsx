import type { ReactElement } from "react";
import { Surface } from "../../design-system/primitives/Surface";
import type { RunStatus, StageStatus } from "../../lib/apiClient";
import "./ScanRunProgress.css";

interface ScanRunProgressProps {
  run: RunStatus | null;
}

const STAGE_STATE_LABEL: Record<StageStatus["state"], string> = {
  pending: "Pending",
  running: "Running",
  complete: "Complete",
  warning: "Warning",
  failed_closed: "Failed closed",
};

function elapsed(startedAt: string, finishedAt: string | null): string {
  const start = new Date(startedAt).getTime();
  const end = finishedAt ? new Date(finishedAt).getTime() : Date.now();
  const seconds = Math.max(0, Math.round((end - start) / 1000));
  return `${seconds}s`;
}

/**
 * Per docs/design/SCAN_RUN_EXPERIENCE.md: a preflight-instrument progression,
 * not a spinner or a build log. Stage "complete" is never green — green is
 * reserved for evidence-integrity facts at sealing, never for stage success.
 * A failed stage fails closed and is stated plainly, never hidden.
 */
export function ScanRunProgress({ run }: ScanRunProgressProps): ReactElement {
  if (!run) {
    return (
      <div className="scan-run-progress">
        <div className="type-eyebrow">Scan Run Progress</div>
        <h1 className="scan-run-progress__headline">Starting the scan…</h1>
      </div>
    );
  }

  return (
    <div className="scan-run-progress">
      <div className="type-eyebrow">Scan Run Progress</div>
      <h1 className="scan-run-progress__headline">What is the scan doing right now?</h1>
      <p className="scan-run-progress__sub">
        <span className="type-mono">{run.run_id}</span> · {run.profile} · elapsed {elapsed(run.started_at, run.finished_at)}
      </p>

      <Surface variant="flush" className="scan-run-progress__stages">
        {run.stages.map((stage) => (
          <div key={stage.id} className={`scan-stage scan-stage--${stage.state}`}>
            <span className="scan-stage__marker" aria-hidden="true" />
            <div className="scan-stage__body">
              <div className="scan-stage__head">
                <span className="scan-stage__label">{stage.label}</span>
                <span className="scan-stage__state">{STAGE_STATE_LABEL[stage.state]}</span>
              </div>
              <p className="scan-stage__explanation">{stage.explanation}</p>
              {stage.artifacts_produced.length > 0 && (
                <p className="scan-stage__artifacts type-mono">{stage.artifacts_produced.join(" · ")}</p>
              )}
            </div>
          </div>
        ))}
      </Surface>

      {run.status === "failed" && (
        <Surface variant="inset" className="scan-run-progress__error" tone="critical">
          <span className="type-eyebrow">Run failed closed</span>
          <p className="scan-run-progress__error-text">
            {run.error ?? "The run stopped before producing a sealed evidence package."} Any evidence
            already produced remains visible and unaltered.
          </p>
        </Surface>
      )}
    </div>
  );
}
