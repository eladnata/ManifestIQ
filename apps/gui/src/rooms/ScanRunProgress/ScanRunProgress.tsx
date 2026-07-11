import { Button } from "../../design-system/primitives/Button";
import type { ReactElement } from "react";
import { Surface } from "../../design-system/primitives/Surface";
import type { RunStatus, StageStatus } from "../../lib/apiClient";
import "./ScanRunProgress.css";

interface ScanRunProgressProps {
  run: RunStatus | null;
  onContinueToSeal: (() => void) | null;
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
export function ScanRunProgress({ run, onContinueToSeal }: ScanRunProgressProps): ReactElement {
  if (!run) {
    return (
      <div className="scan-run-progress">
        <div className="type-eyebrow">Scan Run Progress</div>
        <h1 className="scan-run-progress__headline">Starting the scan…</h1>
      </div>
    );
  }

  const allArtifacts = run.stages.flatMap((stage) => stage.artifacts_produced);
  const integrityLabel =
    run.integrity == null
      ? "Waiting for seal"
      : run.integrity.state === "Verified"
        ? `Integrity verified · ${run.integrity.verified_count}/${run.integrity.total_count}`
        : run.integrity.state === "Partial"
          ? `Integrity partial · ${run.integrity.verified_count}/${run.integrity.total_count}`
          : "Integrity unknown";
  const journeyLabel = run.journey_state.replace(/_/g, " ");
  const nextAction =
    run.status === "failed"
      ? "Run failed closed"
      : onContinueToSeal
        ? "Continue to Evidence Seal"
        : "Waiting for evidence seal";

  return (
    <div className="scan-run-progress">
      <div className="type-eyebrow">Scan Run Progress</div>
      <h1 className="scan-run-progress__headline">What is the scan doing right now?</h1>
      <div className="scan-run-progress__sub">
        <span className="type-mono">{run.run_id}</span>
      </div>

      <Surface variant="raised" className="scan-run-progress__hero">
        <div className="scan-run-progress__hero-main">
          <div className="scan-run-progress__hero-copy">
            <span className="type-eyebrow">Assessment run</span>
            <p className="scan-run-progress__hero-line">
              Profile <strong>{run.profile}</strong> · source <strong>{run.source_type}</strong> · elapsed{" "}
              <strong>{elapsed(run.started_at, run.finished_at)}</strong>
            </p>
            <p className="scan-run-progress__hero-note">
              Scan completes only when the evidence package is sealed and ready for review.
            </p>
          </div>
          <div className="scan-run-progress__hero-status">
            <div className="scan-run-progress__status-card">
              <span className="type-eyebrow">Current state</span>
              <strong>{journeyLabel}</strong>
            </div>
            <div className="scan-run-progress__status-card">
              <span className="type-eyebrow">Next action</span>
              <strong>{nextAction}</strong>
            </div>
          </div>
        </div>
      </Surface>

      <div className="scan-run-progress__grid">
        <Surface variant="flush" className="scan-run-progress__stages">
          <div className="scan-run-progress__section-head">
            <span className="type-eyebrow">Stage instrument</span>
          </div>
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

        <div className="scan-run-progress__side">
          <Surface variant="inset" className="scan-run-progress__evidence-rail">
            <span className="type-eyebrow">Evidence production</span>
            <div className="scan-run-progress__evidence-metrics">
              <div>
                <span className="type-eyebrow">Manifest</span>
                <strong className="type-mono">
                  {run.manifest_hash ? `${run.manifest_hash.slice(0, 12)}…${run.manifest_hash.slice(-4)}` : "Pending"}
                </strong>
              </div>
              <div>
                <span className="type-eyebrow">Integrity</span>
                <strong>{integrityLabel}</strong>
              </div>
            </div>
            <div className="scan-run-progress__artifact-list">
              {allArtifacts.length === 0 ? (
                <span className="scan-run-progress__artifact-empty">Artifacts will appear here as each stage completes.</span>
              ) : (
                allArtifacts.map((artifact) => (
                  <span key={`${run.run_id}-${artifact}`} className="type-mono scan-run-progress__artifact-chip">
                    {artifact}
                  </span>
                ))
              )}
            </div>
          </Surface>

          {run.status !== "failed" && (
            <Surface variant="inset" className="scan-run-progress__next-zone">
              <span className="type-eyebrow">Next station</span>
              <p className="scan-run-progress__next-copy">
                {onContinueToSeal
                  ? "Evidence is ready to be sealed into the review packet."
                  : "Waiting for the sealed evidence package before the Board Verdict can open."}
              </p>
              {onContinueToSeal && (
                <div className="scan-run-progress__actions">
                  <Button variant="primary" onClick={onContinueToSeal}>
                    Continue to Evidence Seal
                  </Button>
                </div>
              )}
            </Surface>
          )}
        </div>
      </div>

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
