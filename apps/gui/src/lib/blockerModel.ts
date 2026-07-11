/**
 * Presentation-only derivation of blocker display fields from the raw blocker
 * string already present in the data contract (e.g. "ARCH-011: Missing owner
 * metadata"). This performs NO scoring, NO evidence parsing, and adds NO data
 * — it only splits a string the contract already provides and maps a rule-ID
 * prefix to a human domain-family label. The underlying finding is never
 * mutated, downgraded, or hidden (COMPONENT_RULES.md §5).
 */

const DOMAIN_FAMILIES: Record<string, string> = {
  ARCH: "Architecture",
  GOV: "Governance",
  OPS: "Operations",
  SEC: "Security",
  DP: "Data Protection",
  DATA: "Data Protection",
  SC: "Supply Chain",
  SUP: "Supply Chain",
  LIC: "License",
  SOX: "SOX / Finance",
  FIN: "SOX / Finance",
  AI: "AI / Model Risk",
  DEL: "Delivery",
  MNT: "Maintainability",
  PLT: "Platform",
};

export interface BlockerModel {
  raw: string;
  ruleId: string;
  title: string;
  domainFamily: string;
  hasRuleId: boolean;
}

const MISSING_EVIDENCE = "Missing Evidence";

export function parseBlocker(raw: string): BlockerModel {
  const colonIndex = raw.indexOf(":");
  if (colonIndex === -1) {
    return {
      raw,
      ruleId: MISSING_EVIDENCE,
      title: raw.trim() || MISSING_EVIDENCE,
      domainFamily: MISSING_EVIDENCE,
      hasRuleId: false,
    };
  }

  const ruleId = raw.slice(0, colonIndex).trim();
  const title = raw.slice(colonIndex + 1).trim() || MISSING_EVIDENCE;
  const prefix = ruleId.split(/[-_]/)[0]?.toUpperCase() ?? "";
  const domainFamily = DOMAIN_FAMILIES[prefix] ?? "Assurance";

  return { raw, ruleId, title, domainFamily, hasRuleId: Boolean(ruleId) };
}

export const MISSING_EVIDENCE_LABEL = MISSING_EVIDENCE;
