# Continuous Development Log

## 2026-07-07

### What changed

- Converted the repository from a skill bundle into a standalone project layout.
- Added Python package source under `src/music_creation_engine/`.
- Added shared config, capability detection, services, runtime backends, CLI, and FastAPI app.
- Kept `scripts/` as compatibility entrypoints that now call the package.
- Added agent adapters for Hermes, Codex, and OpenClaw.
- Added example workflows for all three agent targets.
- Rewrote installation flow around the new package structure.
- Classified integrations into:
  - public default: `Meting-Agent`
  - advanced optional: memory, embedding, browser/research

### Why

The old repository could be copied as a skill bundle, but it was not a real deployable project. The new structure makes it runnable, testable, and easier for multiple contributors and multiple agents to extend safely.

### Verification status

- Config tests: passed
- Capability tests: passed
- Service tests: passed
- CLI tests: passed
- API tests: passed
- Adapter target tests: passed
- Layout tests: passed

### Follow-up candidates

- Add true `POST /v1/render` HTTP route.
- Add persistent job and artifact tracking.
- Add deployment examples for Docker and systemd.
- Replace dry-run fallback with richer dependency diagnostics and example remediation.
