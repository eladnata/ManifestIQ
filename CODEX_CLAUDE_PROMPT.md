# Development Agent Instructions

Use this repository as a deterministic local code assurance scanner.

Follow these constraints:

- Do not add AI calls.
- Do not add LLM calls.
- Do not add embeddings, vector search, or model inference.
- Do not add cloud dependencies.
- Do not add telemetry.
- Do not transmit source code externally.
- Keep all user-facing language in English.
- Preserve evidence outputs, manifest generation, and SHA256 hashing.
- Keep analyzer failures visible.
- Keep baseline rules immutable.
- Add tests for meaningful behavior changes.

Primary product direction:

```text
Enterprise White-Box Code Assurance Scanner
```

Primary technical audience:

```text
CISO, CTO, AppSec, Security Engineering, Enterprise Architecture, DevSecOps, ITGC, and code reviewers.
```

When implementation and `MASTER_SPEC.md` conflict, update the implementation to match `MASTER_SPEC.md` unless explicitly instructed to revise the specification.
