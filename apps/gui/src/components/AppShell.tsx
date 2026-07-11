import type { ReactElement, ReactNode } from "react";
import type { EvidenceIntegrityState } from "../data/boardVerdictSchema";
import { TopBar } from "./TopBar";
import { NonClaimsFooter } from "./NonClaimsFooter";
import "./AppShell.css";

interface AppShellProps {
  roomName: string;
  integrity: EvidenceIntegrityState | null;
  manifestHash: string | null;
  nonClaims: string[];
  rail?: ReactNode;
  children: ReactNode;
}

/**
 * Per docs/design/MANIFESTIQ_DESIGN_SKILL_PACK.md §5 (Global Product Shell):
 * the persistent frame present on every room — top bar / integrity line,
 * an optional workflow rail, and the non-claims footer — wrapping whichever
 * station/room is active. Integrity/manifestHash are nullable because the
 * pre-scan stations (Launch, Preflight) have no sealed run yet; the top bar
 * renders a quiet "no run yet" state rather than fabricating one.
 */
export function AppShell({
  roomName,
  integrity,
  manifestHash,
  nonClaims,
  rail,
  children,
}: AppShellProps): ReactElement {
  return (
    <div className="app-shell">
      <TopBar roomName={roomName} integrity={integrity} manifestHash={manifestHash} />
      <div className="app-shell__body">
        {rail && <div className="app-shell__rail">{rail}</div>}
        <main className="room app-shell__content">{children}</main>
      </div>
      <NonClaimsFooter nonClaims={nonClaims} />
    </div>
  );
}
