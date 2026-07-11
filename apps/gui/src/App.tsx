import { useEffect, useRef, useState, type ReactElement } from "react";
import { AppShell } from "./components/AppShell";
import { WorkflowRail, type Station } from "./components/WorkflowRail";
import { AssessmentLaunch } from "./rooms/AssessmentLaunch/AssessmentLaunch";
import { PreflightGate } from "./rooms/PreflightGate/PreflightGate";
import { ScanRunProgress } from "./rooms/ScanRunProgress/ScanRunProgress";
import { EvidenceSealed } from "./rooms/EvidenceSealed/EvidenceSealed";
import { BoardVerdictRoom } from "./rooms/BoardVerdictRoom/BoardVerdictRoom";
import type { BoardVerdictData } from "./data/boardVerdictSchema";
import {
  getBoardVerdictData,
  getRun,
  postPreflight,
  postRun,
  type PreflightResult,
  type RunStatus,
  type SourceType,
} from "./lib/apiClient";
import { deriveJourneyState, shouldAdvanceFromScan } from "./lib/runJourney";

const ROOM_NAMES: Record<Station, string> = {
  launch: "Assessment Launch",
  preflight: "Preflight Gate",
  scan: "Scan Run Progress",
  sealed: "Evidence Sealed",
  verdict: "Board Verdict Room",
};

const DEFAULT_NON_CLAIMS = [
  "Not certified",
  "No SOX / privacy / legal approval",
  "Not a release approval",
  "No safety claim",
  "Human approval is not inferred",
];

const POLL_INTERVAL_MS = 900;

function readUrlState(): { station: Station | null; runId: string | null } {
  const params = new URLSearchParams(window.location.search);
  const runId = params.get("run");
  const station = params.get("station") as Station | null;
  return { station, runId };
}

function writeUrlState(station: Station, runId: string | null): void {
  const params = new URLSearchParams();
  if (runId) params.set("run", runId);
  params.set("station", station);
  window.history.replaceState(null, "", `?${params.toString()}`);
}

/**
 * The Assessment Workbench: a guided, linear journey through five stations —
 * Assessment Launch, Preflight Gate, Scan Run Progress, Evidence Sealed,
 * Board Verdict Room (docs/design/GUI_PRODUCT_WORKFLOW.md). All API calls
 * are same-origin relative fetch() to this same server; there is no
 * localStorage/sessionStorage — only the URL's own query string carries
 * enough state (run id + station) to survive a page reload.
 *
 * The Board Verdict Room only ever renders fetched, run-specific data. It
 * never falls back to the static sample/generated fixture once a run is in
 * play — a loading state is shown instead until the real data arrives.
 */
export function App(): ReactElement {
  const initial = readUrlState();
  const [station, setStation] = useState<Station>(initial.station ?? "launch");
  const [runId, setRunId] = useState<string | null>(initial.runId);

  const [sourceType, setSourceType] = useState<SourceType>("folder");
  const [sourceValue, setSourceValue] = useState("");
  const [profile, setProfile] = useState("finance-sox");

  const [preflight, setPreflight] = useState<PreflightResult | null>(null);
  const [preflightLoading, setPreflightLoading] = useState(false);
  const [starting, setStarting] = useState(false);

  const [run, setRun] = useState<RunStatus | null>(null);
  const [boardVerdict, setBoardVerdict] = useState<BoardVerdictData | null>(null);
  const journeyState = deriveJourneyState(run, boardVerdict);

  const resumedRef = useRef(false);

  // Reflect station/run in the URL (not storage) so a reload can resume.
  useEffect(() => {
    writeUrlState(station, runId);
  }, [station, runId]);

  // On first mount, resume from a run id present in the URL, if any.
  useEffect(() => {
    if (resumedRef.current) return;
    resumedRef.current = true;
    if (!initial.runId) return;

    getRun(initial.runId)
      .then((fetchedRun) => {
        setRun(fetchedRun);
        if (fetchedRun.journey_state === "evidence_sealed" || fetchedRun.journey_state === "verdict_ready") {
          setStation(initial.station === "verdict" ? "verdict" : "sealed");
        } else {
          setStation("scan");
        }
      })
      .catch(() => {
        setStation("launch");
        setRunId(null);
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Poll the run while it is still executing.
  useEffect(() => {
    if (!runId || station !== "scan") return;
    if (run && run.status !== "running") return;

    let cancelled = false;
    const interval = window.setInterval(async () => {
      try {
        const updated = await getRun(runId);
        if (cancelled) return;
        setRun(updated);
        if (shouldAdvanceFromScan(deriveJourneyState(updated, null))) {
          setStation("sealed");
        }
      } catch {
        // Transient poll failure: try again on the next tick rather than
        // fabricating a favorable state.
      }
    }, POLL_INTERVAL_MS);

    return () => {
      cancelled = true;
      window.clearInterval(interval);
    };
  }, [runId, station, run]);

  useEffect(() => {
    if (!runId || !run?.board_verdict_ready || boardVerdict !== null) return;
    let cancelled = false;
    getBoardVerdictData<BoardVerdictData>(runId)
      .then((data) => {
        if (!cancelled) {
          setBoardVerdict(data);
        }
      })
      .catch(() => {
        // Leave the user on the sealed station and try again if they continue
        // navigating; verdict data loading must never block the Scan -> Seal step.
      });
    return () => {
      cancelled = true;
    };
  }, [runId, run?.board_verdict_ready, boardVerdict]);

  useEffect(() => {
    if (station === "scan" && shouldAdvanceFromScan(journeyState)) {
      setStation("sealed");
    }
  }, [journeyState, station]);

  async function handleLaunch(type: SourceType, value: string, chosenProfile: string): Promise<void> {
    setSourceType(type);
    setSourceValue(value);
    setProfile(chosenProfile);
    setPreflightLoading(true);
    try {
      const result = await postPreflight({ source_type: type, source_value: value, profile: chosenProfile });
      setPreflight(result);
      setStation("preflight");
    } finally {
      setPreflightLoading(false);
    }
  }

  async function handleStartScan(): Promise<void> {
    setStarting(true);
    try {
      const started = await postRun({ source_type: sourceType, source_value: sourceValue, profile });
      setRunId(started.run_id);
      setRun(started);
      setStation("scan");
    } finally {
      setStarting(false);
    }
  }

  let content: ReactElement;
  if (station === "launch") {
    content = <AssessmentLaunch onLaunch={handleLaunch} submitting={preflightLoading} />;
  } else if (station === "preflight") {
    content = (
      <PreflightGate
        preflight={preflight}
        loading={preflightLoading}
        onStartScan={handleStartScan}
        onBack={() => setStation("launch")}
        starting={starting}
      />
    );
  } else if (station === "scan") {
    content = <ScanRunProgress run={run} onContinueToSeal={shouldAdvanceFromScan(journeyState) ? () => setStation("sealed") : null} />;
  } else if (station === "sealed") {
    content = run ? (
      <EvidenceSealed run={run} limitations={boardVerdict?.limitations ?? []} onOpenVerdict={() => setStation("verdict")} />
    ) : (
      <p className="type-body">Loading sealed run…</p>
    );
  } else {
    content = boardVerdict ? <BoardVerdictRoom data={boardVerdict} /> : <p className="type-body">Loading verdict…</p>;
  }

  const integrityForShell = run?.integrity ?? null;
  const manifestHashForShell = run?.manifest_hash ?? null;
  const nonClaimsForShell = boardVerdict?.non_claims ?? run?.non_claims ?? DEFAULT_NON_CLAIMS;

  return (
    <AppShell
      roomName={ROOM_NAMES[station]}
      integrity={integrityForShell}
      manifestHash={manifestHashForShell}
      nonClaims={nonClaimsForShell}
      rail={<WorkflowRail current={station} journeyState={journeyState} />}
    >
      {content}
    </AppShell>
  );
}
