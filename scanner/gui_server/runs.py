from __future__ import annotations

import json
import threading
import uuid
from pathlib import Path
from typing import Any

from scanner import __version__
from scanner.core.capabilities import STRICT_PROFILES, capability_registry
from scanner.core.evidence import write_json
from scanner.core.orchestrator import ANALYZERS, run_scan
from scanner.core.workspace import now_iso, prepare_folder_workspace, prepare_git_workspace, prepare_zip_workspace
from scanner.ui.executive_gui_renderer import NON_CLAIMS, build_board_verdict_data_contract

SOURCE_TYPES = ("folder", "zip", "git")

EXPECTED_ARTIFACTS = [
    "scan-summary.json",
    "decision-packet.json",
    "findings.json",
    "system-dossier.json",
    "manifest.json",
    "sha256.txt",
    "board-verdict-data.json",
]

JourneyState = str

# Stage -> real evidence-artifact markers, in the order those artifacts are
# actually written by scanner.core.orchestrator.run_scan. This module never
# modifies run_scan; stage progress is derived purely by observing which
# artifacts already exist in the run's evidence directory, so the progression
# reflects genuine scanner output rather than a simulated timeline.
STAGE_DEFINITIONS: list[dict[str, Any]] = [
    {
        "id": "source_intake",
        "label": "Source Intake",
        "markers": ["source-metadata.json"],
        "explanation": "Reading the local source into a deterministic workspace.",
    },
    {
        "id": "project_inventory",
        "label": "Project Inventory",
        "markers": ["file-inventory.json"],
        "explanation": "Building the file, language, and package-manager inventory.",
    },
    {
        "id": "static_analysis",
        "label": "Static Analysis",
        "markers": ["sast-results.json", "secrets-results.json"],
        "explanation": "Running static analysis, secrets, and data-risk detectors.",
    },
    {
        "id": "control_mapping",
        "label": "Control Mapping",
        "markers": ["control-context.json", "enterprise-acceptance-matrix.json"],
        "explanation": "Mapping findings to SOX / ITGC control context.",
    },
    {
        "id": "risk_evaluation",
        "label": "Risk Evaluation",
        "markers": ["scoring-results.json", "findings.json", "gaps.json"],
        "explanation": "Scoring findings and evaluating material gaps.",
    },
    {
        "id": "evidence_package_build",
        "label": "Evidence Package Build",
        "markers": ["system-dossier.json", "evidence-graph.json", "decision-packet.json"],
        "explanation": "Assembling the evidence graph, system dossier, and decision packet.",
    },
    {
        "id": "manifest_sealing",
        "label": "Manifest Sealing",
        "markers": ["manifest.json", "sha256.txt"],
        "explanation": "Computing content hashes and sealing the run manifest.",
        "requires_finished": True,
    },
]


def _check(check_id: str, label: str, status: str, detail: str) -> dict[str, Any]:
    return {"id": check_id, "label": label, "status": status, "detail": detail}


def validate_preflight(source_type: str, source_value: str, profile: str) -> dict[str, Any]:
    """
    Deterministic, read-only preflight validation. Performs no network access
    and starts no scan. Fails closed: any unresolved blocker forces state
    "cannot_run" rather than a favorable default.
    """
    checks: list[dict[str, Any]] = []
    blockers: list[str] = []
    source_value = (source_value or "").strip()

    if source_type not in SOURCE_TYPES:
        checks.append(_check("source_type_valid", "Source type valid", "fail", f"Unknown source type: {source_type!r}"))
        blockers.append(f"Unknown source type: {source_type!r}")
    else:
        checks.append(_check("source_type_valid", "Source type valid", "pass", f"Source type: {source_type}"))

    if not source_value:
        checks.append(_check("source_resolved", "Source resolved", "fail", "No source value provided."))
        blockers.append("Source value is required.")
    elif source_type == "folder":
        path = Path(source_value)
        if path.is_dir():
            checks.append(_check("source_resolved", "Source resolved", "pass", f"Folder found: {path.resolve()}"))
        else:
            checks.append(_check("source_resolved", "Source resolved", "fail", f"Folder not found: {source_value}"))
            blockers.append(f"Folder not found: {source_value}")
    elif source_type == "zip":
        path = Path(source_value)
        if path.is_file():
            checks.append(_check("source_resolved", "Source resolved", "pass", f"ZIP file found: {path.resolve()}"))
        else:
            checks.append(_check("source_resolved", "Source resolved", "fail", f"ZIP file not found: {source_value}"))
            blockers.append(f"ZIP file not found: {source_value}")
    elif source_type == "git":
        checks.append(_check("source_resolved", "Source resolved", "pass", f"Git URL provided: {source_value}"))
        checks.append(
            _check(
                "git_outbound_fetch",
                "Outbound git fetch required",
                "warning",
                "Starting this scan performs an explicit local `git clone` of the URL above. "
                "This is the only network action ManifestIQ ever performs, and only on explicit user choice.",
            )
        )

    if profile not in STRICT_PROFILES:
        checks.append(_check("profile_valid", "Profile valid", "fail", f"Unknown profile: {profile!r}"))
        blockers.append(f"Unknown profile: {profile!r}")
    else:
        checks.append(_check("profile_valid", "Profile valid", "pass", f"Profile: {profile}"))

    capabilities = capability_registry()
    checks.append(
        _check(
            "scanner_available",
            "Scanner engine available",
            "pass",
            f"{len(ANALYZERS)} analyzers ready · {len(capabilities)} capability contracts loaded.",
        )
    )

    local_only_detail = (
        "No cloud upload, no telemetry, no AI/LLM, no external enrichment. "
        + ("Folder/ZIP sources require no network access." if source_type in ("folder", "zip") else "Git source requires an explicit local `git clone` only.")
    )
    checks.append(_check("local_only", "Local-only constraints", "pass", local_only_detail))

    checks.append(
        _check(
            "output_directory_planned",
            "Output directory planned",
            "pass",
            "A new local run directory will be created under gui-runs/ and sealed on completion.",
        )
    )

    if blockers:
        state = "cannot_run"
    elif any(c["status"] == "warning" for c in checks):
        state = "needs_attention"
    else:
        state = "ready"

    return {
        "schema": "manifestiq-preflight",
        "schema_version": "0.1",
        "state": state,
        "checks": checks,
        "blockers": blockers,
        "expected_artifacts": list(EXPECTED_ARTIFACTS),
        "non_claims": list(NON_CLAIMS),
    }


def _stage_state(all_present: bool, any_present: bool, finished: bool, requires_finished: bool) -> str:
    complete = all_present and (finished if requires_finished else True)
    if complete:
        return "complete"
    if finished:
        # The run has concluded (successfully or not) but this stage never
        # produced its expected evidence. Fail closed rather than leave an
        # ambiguous "pending" state.
        return "failed_closed"
    if any_present:
        return "running"
    return "pending"


def compute_stages(evidence_dir: Path, *, finished: bool) -> list[dict[str, Any]]:
    """Derive stage progress purely from which real evidence artifacts exist on disk."""
    stages: list[dict[str, Any]] = []
    for stage_def in STAGE_DEFINITIONS:
        markers_present = [(evidence_dir / marker).is_file() for marker in stage_def["markers"]]
        all_present = bool(markers_present) and all(markers_present)
        any_present = any(markers_present)
        state = _stage_state(all_present, any_present, finished, bool(stage_def.get("requires_finished", False)))
        produced = [marker for marker, present in zip(stage_def["markers"], markers_present) if present]
        stages.append(
            {
                "id": stage_def["id"],
                "label": stage_def["label"],
                "state": state,
                "explanation": stage_def["explanation"],
                "artifacts_expected": list(stage_def["markers"]),
                "artifacts_produced": produced,
            }
        )
    return stages


def derive_run_journey_state(
    *,
    status: str,
    stages: list[dict[str, Any]],
    integrity: dict[str, Any] | None,
    manifest_hash: str | None,
    board_verdict_ready: bool,
) -> str:
    """
    Guided GUI lifecycle states for Phase 17A.1.

    These states are intentionally more specific than the low-level run
    status so the frontend can move the user through Scan -> Seal -> Verdict
    without inferring progress from visual stage completion alone.
    """
    if status == "failed":
        return "scan_failed_closed"

    all_complete = all(stage.get("state") == "complete" for stage in stages)
    all_before_seal_complete = all(
        stage.get("state") == "complete" for stage in stages if stage.get("id") != "manifest_sealing"
    )
    seal_complete = any(stage.get("id") == "manifest_sealing" and stage.get("state") == "complete" for stage in stages)
    evidence_verified = integrity is not None and bool(manifest_hash) and integrity.get("state") == "Verified"

    if status == "sealed" and seal_complete and evidence_verified:
        return "verdict_ready" if board_verdict_ready else "evidence_sealed"
    if all_complete or all_before_seal_complete:
        return "scan_complete_unsealed"
    return "scan_running"


class RunManager:
    """
    Manages local assessment runs for the GUI workbench. Never duplicates
    scanner logic: every run invokes the existing prepare_*_workspace + run_scan
    functions unchanged, and reuses build_board_verdict_data_contract for the
    sealed result. All output is written under a local run directory; nothing
    is transmitted externally.
    """

    def __init__(self, runs_dir: Path | str):
        self.runs_dir = Path(runs_dir)
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._records: dict[str, dict[str, Any]] = {}

    def start_run(self, source_type: str, source_value: str, profile: str) -> dict[str, Any]:
        preflight = validate_preflight(source_type, source_value, profile)
        if preflight["state"] == "cannot_run":
            return {"error": "preflight_failed", "preflight": preflight}

        run_id = f"run_{uuid.uuid4().hex[:12]}"
        run_dir = self.runs_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=False)
        evidence_dir = run_dir / "evidence-package"

        write_json(run_dir / "preflight.json", preflight)

        record = {
            "run_id": run_id,
            "status": "running",
            "source_type": source_type,
            "source_value": source_value,
            "profile": profile,
            "run_dir": str(run_dir),
            "evidence_dir": str(evidence_dir),
            "started_at": now_iso(),
            "finished_at": None,
            "error": None,
        }
        with self._lock:
            self._records[run_id] = record

        thread = threading.Thread(target=self._execute, args=(run_id,), daemon=True)
        thread.start()
        return {"run": self._public_run(run_id)}

    def _execute(self, run_id: str) -> None:
        with self._lock:
            record = dict(self._records[run_id])
        run_dir = Path(record["run_dir"])
        try:
            if record["source_type"] == "folder":
                workspace = prepare_folder_workspace(Path(record["source_value"]), run_dir)
            elif record["source_type"] == "zip":
                workspace = prepare_zip_workspace(Path(record["source_value"]), run_dir)
            elif record["source_type"] == "git":
                workspace = prepare_git_workspace(record["source_value"], run_dir)
            else:
                raise ValueError(f"Unknown source type: {record['source_type']}")

            # Convenience top-level copy for the Assessment Launch / Preflight
            # screens; the scanner's own copy inside evidence-package is the
            # canonical evidence artifact and is left untouched.
            write_json(run_dir / "source-metadata.json", workspace.source_metadata)

            run_scan(workspace=workspace, profile=record["profile"], scanner_version=__version__)

            contract = build_board_verdict_data_contract(workspace.evidence_dir)
            write_json(run_dir / "board-verdict-data.json", contract)

            with self._lock:
                self._records[run_id]["status"] = "sealed"
                self._records[run_id]["finished_at"] = now_iso()
        except Exception as exc:  # fail closed: never let a run crash the server
            with self._lock:
                self._records[run_id]["status"] = "failed"
                self._records[run_id]["finished_at"] = now_iso()
                self._records[run_id]["error"] = f"{type(exc).__name__}: {exc}"

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        with self._lock:
            record = self._records.get(run_id)
            if record is None:
                return None
            record = dict(record)
        return self._public_run(run_id, record)

    def _public_run(self, run_id: str, record: dict[str, Any] | None = None) -> dict[str, Any]:
        if record is None:
            with self._lock:
                record = dict(self._records[run_id])

        evidence_dir = Path(record["evidence_dir"])
        finished = record["status"] in ("sealed", "failed")
        stages = compute_stages(evidence_dir, finished=finished)

        integrity = None
        manifest_hash = None
        board_verdict_ready = False
        if record["status"] == "sealed":
            data_path = Path(record["run_dir"]) / "board-verdict-data.json"
            if data_path.is_file():
                contract = json.loads(data_path.read_text(encoding="utf-8"))
                integrity = contract.get("integrity")
                manifest_hash = contract.get("manifest_hash")
                board_verdict_ready = True

        journey_state = derive_run_journey_state(
            status=record["status"],
            stages=stages,
            integrity=integrity,
            manifest_hash=manifest_hash,
            board_verdict_ready=board_verdict_ready,
        )
        next_station = "sealed" if journey_state in {"evidence_sealed", "verdict_ready"} else None

        return {
            "schema": "manifestiq-run-status",
            "schema_version": "0.1",
            "run_id": run_id,
            "status": record["status"],
            "journey_state": journey_state,
            "source_type": record["source_type"],
            "profile": record["profile"],
            "run_dir": record["run_dir"],
            "evidence_dir": record["evidence_dir"],
            "started_at": record["started_at"],
            "finished_at": record["finished_at"],
            "error": record["error"],
            "stages": stages,
            "integrity": integrity,
            "manifest_hash": manifest_hash,
            "board_verdict_ready": board_verdict_ready,
            "next_station": next_station,
            "non_claims": list(NON_CLAIMS),
        }

    def get_board_verdict_data(self, run_id: str) -> dict[str, Any] | None:
        with self._lock:
            record = self._records.get(run_id)
            if record is None:
                return None
            status = record["status"]
            run_dir = Path(record["run_dir"])

        if status != "sealed":
            return None
        data_path = run_dir / "board-verdict-data.json"
        if not data_path.is_file():
            return None
        return json.loads(data_path.read_text(encoding="utf-8"))
