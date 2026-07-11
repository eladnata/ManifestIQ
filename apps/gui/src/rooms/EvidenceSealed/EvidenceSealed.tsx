import type { ReactElement } from "react";
import { Surface } from "../../design-system/primitives/Surface";
import { Button } from "../../design-system/primitives/Button";
import { StatusPill } from "../../design-system/primitives/StatusPill";
import type { RunStatus } from "../../lib/apiClient";
import "./EvidenceSealed.css";

interface EvidenceSealedProps {
  run: RunStatus;
  limitations: string[];
  onOpenVerdict: () => void;
}

/**
 * Per docs/design/GUI_PRODUCT_WORKFLOW.md Step 4: confirm the run produced a
 * sealed, integrity-verified evidence package. Green is used here ONLY for a
 * genuinely verified integrity state — never for approval, readiness, or a
 * decision. This is the evidence-vault "jewelry" moment.
 */
export function EvidenceSealed({ run, limitations, onOpenVerdict }: EvidenceSealedProps): ReactElement {
  const integrity = run.integrity;
  const tone = integrity?.state === "Verified" ? "integrity" : integrity?.state === "Partial" ? "caution" : "unknown";
  const label =
    integrity == null
      ? "Missing Evidence"
      : integrity.state === "Verified"
        ? `Integrity verified · ${integrity.verified_count}/${integrity.total_count} artifacts`
        : integrity.state === "Partial"
          ? `Integrity partial · ${integrity.verified_count}/${integrity.total_count} verified`
          : "Integrity unknown";

  return (
    <div className="evidence-sealed">
      <div className="type-eyebrow">Evidence Sealed</div>
      <h1 className="evidence-sealed__headline">Is the evidence intact and ready to review?</h1>

      <Surface variant="raised" className="evidence-sealed__card">
        <StatusPill label={label} tone={tone} />
        <div className="evidence-sealed__fingerprint">
          <span className="type-eyebrow">Manifest fingerprint</span>
          <span className="type-mono evidence-sealed__hash">
            {run.manifest_hash ? `⌗ ${run.manifest_hash.slice(0, 16)}…${run.manifest_hash.slice(-6)}` : "Not available"}
          </span>
        </div>
        <div className="evidence-sealed__meta">
          <div>
            <span className="type-eyebrow">Evidence package</span>
            <span className="type-mono evidence-sealed__path">{run.evidence_dir}</span>
          </div>
          <div>
            <span className="type-eyebrow">Artifacts verified</span>
            <span className="evidence-sealed__count">
              {integrity ? `${integrity.verified_count} / ${integrity.total_count}` : "—"}
            </span>
          </div>
        </div>
      </Surface>

      <Surface variant="inset" className="evidence-sealed__limitations">
        <span className="type-eyebrow">Limitations</span>
        {limitations.length === 0 ? (
          <p className="evidence-sealed__limitation-empty">No material limitations recorded for this run.</p>
        ) : (
          <ul className="evidence-sealed__limitation-list">
            {limitations.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        )}
      </Surface>

      <div className="evidence-sealed__actions">
        <Button variant="primary" onClick={onOpenVerdict}>
          Open Board Verdict
        </Button>
      </div>
    </div>
  );
}
