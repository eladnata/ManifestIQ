import type { ReactElement } from "react";
import "./WorkflowRail.css";

export type Station = "launch" | "preflight" | "scan" | "sealed" | "verdict";

interface WorkflowRailProps {
  current: Station;
}

const STATIONS: { id: Station; label: string }[] = [
  { id: "launch", label: "Configure" },
  { id: "preflight", label: "Preflight" },
  { id: "scan", label: "Scan" },
  { id: "sealed", label: "Seal" },
  { id: "verdict", label: "Verdict" },
];

function stationState(id: Station, current: Station): "done" | "current" | "pending" {
  if (id === current) return "current";
  const order = STATIONS.map((s) => s.id);
  return order.indexOf(id) < order.indexOf(current) ? "done" : "pending";
}

/**
 * The workflow rail is a journey spine, not a menu (docs/design/
 * GUI_NAVIGATION_MODEL.md §3). It shows five stations — Configure, Preflight,
 * Scan, Seal, Verdict — with state (done / current / pending), reflecting a
 * linear guided journey rather than a free-form nav list.
 */
export function WorkflowRail({ current }: WorkflowRailProps): ReactElement {
  return (
    <nav className="workflow-rail" aria-label="Assessment journey">
      <ol className="workflow-rail__list">
        {STATIONS.map((station, index) => {
          const state = stationState(station.id, current);
          return (
            <li key={station.id} className={`workflow-rail__item workflow-rail__item--${state}`}>
              <span className="workflow-rail__marker" aria-hidden="true">
                {state === "done" ? "✓" : String(index + 1).padStart(2, "0")}
              </span>
              <span className="workflow-rail__label">{station.label}</span>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
