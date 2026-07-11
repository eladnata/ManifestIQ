import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Local-only static build for ManifestIQ's Board Verdict Room.
// - "./" base so the built index.html opens directly from disk (file://) or any local server,
//   with no absolute-path asset references.
// - No proxy, no dev-server API surface, no external asset sources.
export default defineConfig({
  plugins: [react()],
  base: "./",
  build: {
    outDir: "dist",
    assetsDir: "assets",
    sourcemap: false,
    // Disabled: the modulepreload polyfill issues a fetch() for bundled local
    // chunks in browsers without native modulepreload support. This app is a
    // single small bundle opened directly from disk; the polyfill is
    // unnecessary and its presence would otherwise require an allowlist
    // exception in the static-output safety check. Removing it keeps that
    // check a strict, unqualified "no fetch(), ever" rule.
    modulePreload: false,
  },
});
