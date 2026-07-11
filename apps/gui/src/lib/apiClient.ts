/**
 * Local-only API client for the ManifestIQ assessment workbench.
 *
 * Every function here calls a same-origin relative path ("/api/...") via
 * fetch(). There is no absolute URL, no external host, no WebSocket, no
 * browser storage, and no polling interval shorter than what a human is
 * already waiting on. This is the ONLY network activity the frontend
 * performs, and it never leaves 127.0.0.1 (the server that serves this
 * bundle is the same server that answers these requests).
 */

export type SourceType = "folder" | "zip" | "git";

export interface HealthPayload {
  schema: string;
  schema_version: string;
  status: string;
  mode: string;
  network: string;
  telemetry: string;
  cloud: string;
  ai: string;
  version: string;
  profiles: string[];
  source_types: string[];
}

export interface PreflightCheck {
  id: string;
  label: string;
  status: "pass" | "fail" | "warning";
  detail: string;
}

export interface PreflightResult {
  schema: string;
  schema_version: string;
  state: "ready" | "needs_attention" | "cannot_run";
  checks: PreflightCheck[];
  blockers: string[];
  expected_artifacts: string[];
  non_claims: string[];
}

export interface StageStatus {
  id: string;
  label: string;
  state: "pending" | "running" | "complete" | "warning" | "failed_closed";
  explanation: string;
  artifacts_expected: string[];
  artifacts_produced: string[];
}

export interface IntegritySummary {
  state: "Verified" | "Partial" | "Missing";
  verified_count: number;
  total_count: number;
  failed: string[];
}

export interface RunStatus {
  schema: string;
  schema_version: string;
  run_id: string;
  status: "running" | "sealed" | "failed";
  source_type: SourceType;
  profile: string;
  run_dir: string;
  evidence_dir: string;
  started_at: string;
  finished_at: string | null;
  error: string | null;
  stages: StageStatus[];
  integrity: IntegritySummary | null;
  manifest_hash: string | null;
  non_claims: string[];
}

export interface RunRequestPayload {
  source_type: SourceType;
  source_value: string;
  profile: string;
}

async function postJson<T>(path: string, payload: unknown): Promise<T> {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = (await response.json()) as T;
  if (!response.ok) {
    throw new ApiError(response.status, data);
  }
  return data;
}

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(path);
  const data = (await response.json()) as T;
  if (!response.ok) {
    throw new ApiError(response.status, data);
  }
  return data;
}

export class ApiError extends Error {
  status: number;
  body: unknown;
  constructor(status: number, body: unknown) {
    super(`API error ${status}`);
    this.status = status;
    this.body = body;
  }
}

export function getHealth(): Promise<HealthPayload> {
  return getJson<HealthPayload>("/api/health");
}

export function postPreflight(payload: RunRequestPayload): Promise<PreflightResult> {
  return postJson<PreflightResult>("/api/preflight", payload);
}

export function postRun(payload: RunRequestPayload): Promise<RunStatus> {
  return postJson<RunStatus>("/api/runs", payload);
}

export function getRun(runId: string): Promise<RunStatus> {
  return getJson<RunStatus>(`/api/runs/${encodeURIComponent(runId)}`);
}

export function getBoardVerdictData<T>(runId: string): Promise<T> {
  return getJson<T>(`/api/runs/${encodeURIComponent(runId)}/board-verdict-data`);
}
