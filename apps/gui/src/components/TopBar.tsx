import type { ReactElement } from "react";
import type { EvidenceIntegrityState } from "../data/boardVerdictSchema";
import { IntegrityIndicator } from "./IntegrityIndicator";
import "./TopBar.css";

interface TopBarProps {
  roomName: string;
  integrity: EvidenceIntegrityState | null;
  manifestHash: string | null;
}

/**
 * Per docs/design/COMPONENT_RULES.md §1 (Top Bar) and §9 (Manifest
 * Fingerprint): orients the user to the current room and anchors it to its
 * evidence. The monospace manifest fingerprint is the run's provenance made
 * legible — the evidence-vault "jewelry" of VISUAL_TASTE_DOCTRINE §4. No
 * approval status here; the only green is delegated to IntegrityIndicator.
 */
export function TopBar({ roomName, integrity, manifestHash }: TopBarProps): ReactElement {
  const fingerprint = manifestHash ? `⌗ ${manifestHash.slice(0, 12)}…${manifestHash.slice(-4)}` : null;

  return (
    <header className="topbar">
      <div className="topbar__row">
        <div className="topbar__identity">
          <span className="topbar__brand">ManifestIQ</span>
          <span className="topbar__divider" aria-hidden="true" />
          <span className="topbar__room">{roomName}</span>
        </div>
        <div className="topbar__evidence">
          {fingerprint && (
            <span className="topbar__fingerprint type-mono" title="Run manifest fingerprint">
              {fingerprint}
            </span>
          )}
          <IntegrityIndicator integrity={integrity} />
        </div>
      </div>
    </header>
  );
}
