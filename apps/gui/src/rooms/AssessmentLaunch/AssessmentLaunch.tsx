import { useState, type ReactElement } from "react";
import { Surface } from "../../design-system/primitives/Surface";
import { Button } from "../../design-system/primitives/Button";
import type { SourceType } from "../../lib/apiClient";
import "./AssessmentLaunch.css";

const SOURCE_LABELS: Record<SourceType, string> = {
  folder: "Folder path",
  zip: "ZIP file path",
  git: "Git repository URL",
};

const SOURCE_PLACEHOLDERS: Record<SourceType, string> = {
  folder: "tests/sample_projects/insecure-python",
  zip: "/path/to/project.zip",
  // Deliberately scheme-less: an inert placeholder string that reads as a
  // literal https:// URL would (correctly) trip the build's static-output
  // safety check, which flags any hardcoded network URL literal.
  git: "example.com/org/repo.git",
};

const PROFILES = ["enterprise", "finance-sox", "production-critical"] as const;

const EXPECTED_OUTPUTS = [
  "Findings and evidence, preserved verbatim",
  "A decision packet with a conservative visible decision",
  "A sealed, hash-verified evidence manifest",
  "A Board Verdict Room for this run",
];

interface AssessmentLaunchProps {
  onLaunch: (sourceType: SourceType, sourceValue: string, profile: string) => void;
  submitting: boolean;
}

/**
 * Per docs/design/GUI_PRODUCT_WORKFLOW.md Step 1: configure what will be
 * assessed, locally and deterministically. One job — no cloud/account
 * affordance, no AI toggle, no rule builder. Folder/ZIP are the default
 * local/offline path; Git is explicitly called out as requiring an outbound
 * fetch by user choice, deferred to the Preflight Gate's explicit notice.
 */
export function AssessmentLaunch({ onLaunch, submitting }: AssessmentLaunchProps): ReactElement {
  const [sourceType, setSourceType] = useState<SourceType>("folder");
  const [sourceValue, setSourceValue] = useState("");
  const [profile, setProfile] = useState<string>("finance-sox");

  const canSubmit = sourceValue.trim().length > 0 && !submitting;

  return (
    <div className="assessment-launch">
      <div className="type-eyebrow">Assessment Launch</div>
      <h1 className="assessment-launch__headline">What will be assessed?</h1>
      <p className="assessment-launch__sub">
        Local and deterministic. Nothing here is transmitted anywhere.
      </p>

      <Surface variant="raised" className="assessment-launch__hero-card">
        <div className="assessment-launch__hero-band">
          <div>
            <span className="type-eyebrow">Local assurance chamber</span>
            <p className="assessment-launch__hero-copy">
              Select the source, set the doctrine profile, and stage the assessment without handing custody to
              any cloud service.
            </p>
          </div>
          <div className="assessment-launch__hero-metrics" aria-label="Assessment launch cues">
            <div className="assessment-launch__metric">
              <span className="type-eyebrow">Mode</span>
              <strong>Read-only</strong>
            </div>
            <div className="assessment-launch__metric">
              <span className="type-eyebrow">Trust</span>
              <strong>Deterministic</strong>
            </div>
            <div className="assessment-launch__metric">
              <span className="type-eyebrow">Network</span>
              <strong>{sourceType === "git" ? "User-invoked clone" : "Offline"}</strong>
            </div>
          </div>
        </div>

        <div className="assessment-launch__intake-grid">
          <div className="assessment-launch__intake-panel">
            <div className="assessment-launch__section">
              <span className="type-eyebrow">Source type</span>
              <div className="assessment-launch__segmented" role="radiogroup" aria-label="Source type">
                {(["folder", "zip", "git"] as SourceType[]).map((type) => (
                  <button
                    key={type}
                    type="button"
                    role="radio"
                    aria-checked={sourceType === type}
                    className={`assessment-launch__segment ${sourceType === type ? "assessment-launch__segment--active" : ""}`}
                    onClick={() => setSourceType(type)}
                  >
                    {type === "folder" ? "Folder" : type === "zip" ? "ZIP" : "Git URL"}
                  </button>
                ))}
              </div>
            </div>

            <div className="assessment-launch__section">
              <label className="type-eyebrow" htmlFor="source-value">
                {SOURCE_LABELS[sourceType]}
              </label>
              <input
                id="source-value"
                className="assessment-launch__input type-mono"
                type="text"
                value={sourceValue}
                placeholder={SOURCE_PLACEHOLDERS[sourceType]}
                onChange={(e) => setSourceValue(e.target.value)}
              />
              {sourceType === "git" && (
                <p className="assessment-launch__note">
                  Starting a scan from a Git URL performs an explicit outbound <code className="type-mono">git clone</code> —
                  the only network action ManifestIQ ever takes, and only because you chose it.
                </p>
              )}
            </div>

            <div className="assessment-launch__section">
              <span className="type-eyebrow">Profile</span>
              <div className="assessment-launch__segmented" role="radiogroup" aria-label="Assessment profile">
                {PROFILES.map((p) => (
                  <button
                    key={p}
                    type="button"
                    role="radio"
                    aria-checked={profile === p}
                    className={`assessment-launch__segment ${profile === p ? "assessment-launch__segment--active" : ""}`}
                    onClick={() => setProfile(p)}
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <Surface variant="inset" className="assessment-launch__outputs">
            <span className="type-eyebrow">Expected outputs</span>
            <ul className="assessment-launch__output-list">
              {EXPECTED_OUTPUTS.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </Surface>
        </div>
      </Surface>

      <div className="assessment-launch__guarantees">
        <Surface variant="inset" className="assessment-launch__guarantee-card">
          <span className="type-eyebrow">Local-only guarantee</span>
          <p className="assessment-launch__guarantee-text">
            No cloud upload, no telemetry, no AI/LLM, no external enrichment. Folder and ZIP sources
            require no network access at all.
          </p>
        </Surface>
        <Surface variant="inset" className="assessment-launch__guarantee-card">
          <span className="type-eyebrow">Read-only analysis</span>
          <p className="assessment-launch__guarantee-text">
            The scan reads your source; it never edits, formats, or mutates it.
          </p>
        </Surface>
      </div>

      <div className="assessment-launch__actions">
        <Button
          variant="primary"
          disabled={!canSubmit}
          onClick={() => onLaunch(sourceType, sourceValue.trim(), profile)}
        >
          {submitting ? "Checking…" : "Run Preflight"}
        </Button>
      </div>
    </div>
  );
}
