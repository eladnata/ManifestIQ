#!/usr/bin/env node
// Embeds a Board Verdict data JSON file (produced by
// `python -m scanner render-gui-data`) into a generated, build-time TypeScript
// module. This is a local file-to-file copy step only: no network access, no
// server, no fetch. The resulting module is statically imported by the React
// app, so the built output never performs a runtime request for this data.
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { resolve } from "node:path";

const inputArg = process.argv[2];
if (!inputArg) {
  console.error("Usage: node scripts/embed-data.mjs <path-to-board-verdict-data.json>");
  process.exit(1);
}

const inputPath = resolve(inputArg);
if (!existsSync(inputPath)) {
  console.error(`Data file not found: ${inputPath}`);
  process.exit(1);
}

const raw = readFileSync(inputPath, "utf-8");
const parsed = JSON.parse(raw); // validates it is well-formed JSON before embedding

if (parsed.schema !== "manifestiq-board-verdict-data") {
  console.error(`Unexpected schema in ${inputPath}: ${parsed.schema}`);
  process.exit(1);
}

const outPath = resolve(new URL("../src/generated/boardVerdictData.ts", import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1"));

const contents = `// GENERATED FILE — produced by apps/gui/scripts/embed-data.mjs from
// ${inputArg.replace(/\\/g, "/")}
// Do not hand-edit. Re-run the embed step to refresh.
import type { BoardVerdictData } from "../data/boardVerdictSchema";

export const boardVerdictData: BoardVerdictData = ${JSON.stringify(parsed, null, 2)};
`;

writeFileSync(outPath, contents, "utf-8");
console.log(`Embedded ${inputPath} -> ${outPath}`);
