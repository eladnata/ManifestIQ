#!/usr/bin/env node
// Fails the build if the static output contains any external-dependency or
// forbidden-approval-language signal. Run after `vite build`, before the
// output is considered ready to ship as `gui-output/manifestiq-gui/` or
// served by `python -m scanner gui`.
//
// Phase 17A rule change: fetch() itself is now ALLOWED, because the
// assessment workbench legitimately calls its own same-origin local API
// (fetch("/api/health"), fetch("/api/runs"), ...). What remains forbidden is
// any external network target — enforced below by findNetworkUrlViolations,
// which flags every literal http(s):// URL anywhere in the bundle (including
// one used as a fetch() argument). XMLHttpRequest, WebSocket, and browser
// storage remain fully forbidden; this app uses none of them.
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";

const distDir = process.argv[2] ? join(process.cwd(), process.argv[2]) : join(process.cwd(), "dist");

const FORBIDDEN_RUNTIME_PATTERNS = [
  [/<script[^>]*\ssrc=["']https?:/i, '<script src="http'],
  [/<link[^>]*\shref=["']https?:/i, '<link href="http'],
  [/@import\s+url\(["']?https?:/i, "@import (external)"],
  [/XMLHttpRequest/, "XMLHttpRequest"],
  [/\bWebSocket\b/, "WebSocket"],
  [/\blocalStorage\b/, "localStorage"],
  [/\bsessionStorage\b/, "sessionStorage"],
];

// react-dom embeds these as inert string constants: XML namespace URIs used
// only for attribute/property equality checks (never fetched), and a
// dev-mode error-decoder link that is only ever interpolated into a thrown
// Error's message text for a developer to read, never requested by the app.
// Any other http(s):// literal is still a hard failure.
const KNOWN_INERT_URL_SUBSTRINGS = [
  "http://www.w3.org/1999/xhtml",
  "http://www.w3.org/2000/svg",
  "http://www.w3.org/1999/xlink",
  "http://www.w3.org/XML/1998/namespace",
  "http://www.w3.org/1998/Math/MathML",
  "https://reactjs.org/docs/error-decoder.html",
];

function findNetworkUrlViolations(text, file, failures) {
  const re = /https?:\/\/[^\s"'`)]*/g;
  let match;
  while ((match = re.exec(text)) !== null) {
    const url = match[0];
    if (KNOWN_INERT_URL_SUBSTRINGS.some((known) => url.startsWith(known))) continue;
    failures.push(`${file}: unexpected network URL literal found: ${url.slice(0, 80)}`);
  }
}

// Defense in depth: every literal fetch("...") string argument must be a
// same-origin relative path. A protocol-relative target ("//host/...") would
// resolve to an external host despite containing no "http" substring, so it
// is checked for explicitly rather than relying only on findNetworkUrlViolations.
function findNonLocalFetchTargets(text, file, failures) {
  const re = /fetch\(\s*["'`](\/[^"'`]*)["'`]/g;
  let match;
  while ((match = re.exec(text)) !== null) {
    const target = match[1];
    if (target.startsWith("//")) {
      failures.push(`${file}: fetch() target is protocol-relative (external): ${target}`);
    }
  }
}

const FORBIDDEN_CLAIM_TERMS = [
  "Approved",
  "Certified",
  "Compliant",
  "Safe",
  "Production Ready",
  "SOX Approved",
  "Privacy Approved",
  "Legally Approved",
  "Fully Secure",
];

function listFiles(dir) {
  const out = [];
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) {
      out.push(...listFiles(full));
    } else if (/\.(html|js|css|mjs)$/.test(entry)) {
      out.push(full);
    }
  }
  return out;
}

function checkForbiddenClaims(text, file, failures) {
  const footerStart = text.indexOf('aria-label="Standing non-claims"');
  // Anything before a non-claims footer marker is checked; the footer itself
  // legitimately contains denied forms ("Not certified", "No ... approval").
  const body = footerStart !== -1 ? text.slice(0, footerStart) : text;

  for (const term of FORBIDDEN_CLAIM_TERMS) {
    const re = new RegExp(term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "gi");
    let match;
    while ((match = re.exec(body)) !== null) {
      const start = Math.max(0, match.index - 12);
      const preceding = body.slice(start, match.index).toLowerCase();
      if (!preceding.includes("not ") && !preceding.includes("no ")) {
        failures.push(
          `${file}: forbidden claim term "${term}" appears without a preceding negation near: ...${body.slice(start, match.index + term.length + 12)}...`,
        );
      }
    }
  }
}

let files;
try {
  files = listFiles(distDir);
} catch (err) {
  console.error(`Could not read build output directory: ${distDir}`);
  console.error(String(err));
  process.exit(1);
}

if (files.length === 0) {
  console.error(`No built files found under ${distDir}. Did the build run?`);
  process.exit(1);
}

const failures = [];

for (const file of files) {
  const text = readFileSync(file, "utf-8");

  for (const [pattern, label] of FORBIDDEN_RUNTIME_PATTERNS) {
    if (pattern.test(text)) {
      failures.push(`${file}: forbidden runtime pattern found: ${label}`);
    }
  }

  findNetworkUrlViolations(text, file, failures);
  findNonLocalFetchTargets(text, file, failures);

  if (file.endsWith(".html")) {
    checkForbiddenClaims(text, file, failures);
  }
}

if (failures.length > 0) {
  console.error("Static output safety check FAILED:\n");
  for (const f of failures) console.error(` - ${f}`);
  process.exit(1);
}

console.log(`Static output safety check PASSED (${files.length} files scanned in ${distDir}).`);
