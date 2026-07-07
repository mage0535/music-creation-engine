# Deployable Music Creation Engine Design

## Goal

Turn the current skill bundle into a deployable, runnable, verifiable standalone project that supports:

- local CLI execution
- HTTP API deployment
- agent integrations for Hermes, Codex, and OpenClaw
- default public integrations
- optional advanced integrations for server-side tools

## Scope

This design keeps the existing score-generation and demo-rendering behavior, but reorganizes it into a real application boundary. It does not attempt to build a full UI, a job queue, or a plugin marketplace in the first pass.

## Recommended Architecture

Use a single repository with clear internal layers:

- `src/music_creation_engine/core`
  Pure project models, configuration loading, workflow orchestration, and capability detection.
- `src/music_creation_engine/services`
  Score generation, demo rendering, reference lookup, and optional memory/research integrations.
- `src/music_creation_engine/cli`
  Command-line entrypoints for health checks, score generation, rendering, and full pipeline workflows.
- `src/music_creation_engine/api`
  FastAPI application exposing health, compose, render, reference-search, and capability endpoints.
- `src/music_creation_engine/adapters`
  Agent-specific prompts, manifests, and installation helpers for Hermes, Codex, and OpenClaw.
- `src/music_creation_engine/integrations`
  Public and advanced integration wrappers with explicit enablement rules.

This keeps the core deterministic and testable while allowing agent and external-tool surfaces to evolve independently.

## Deployment Model

The project must support two first-class runtime modes:

1. CLI mode
   For batch execution, local use, automation, and agent shell calls.
2. HTTP API mode
   For server deployment, workflow reuse, and future integration with external frontends or orchestrators.

Both modes must call the same service layer. CLI commands and API routes are thin wrappers.

## Configuration Model

Use one repository-local configuration format with environment-variable overrides.

- default file: `config/defaults.yaml`
- optional local override: `config/local.yaml`
- environment prefix: `MCE_`

Key settings:

- output directory
- default rendering format
- public integrations enabled by default
- advanced integrations disabled by default
- executable/command paths for `lilypond`, `fluidsynth`, `ffmpeg`, `npx`
- optional endpoints/commands for memory and research tools

## Integration Policy

### Default-enabled public integrations

- `Meting-Agent`
  For reference song, lyric, and metadata lookup.

### Optional advanced integrations

- memory/hindsight integration
  For persistent creative memory and retrieval.
- embedding integration
  For semantic recall and similarity search.
- browser/research integration
  For web reference collection and source gathering.

These advanced integrations must never block the core workflow. If unavailable, the project reports capability status and degrades cleanly.

## Agent Integration Strategy

Agent support is implemented as adapters, not as forks of the core workflow.

- Hermes adapter
  Skill file, install target, and example workflow.
- Codex adapter
  Agent instructions, install target, and example workflow.
- OpenClaw adapter
  Prompt/integration scaffold and example workflow.

Each adapter consumes the same CLI/API contracts.

## Minimal API Surface

- `GET /health`
- `GET /capabilities`
- `POST /v1/score`
- `POST /v1/render`
- `POST /v1/workflows/full`
- `POST /v1/references/search`

## Minimal CLI Surface

- `music-creation-engine health`
- `music-creation-engine capabilities`
- `music-creation-engine score`
- `music-creation-engine render`
- `music-creation-engine workflow full`
- `music-creation-engine references search`
- `music-creation-engine adapters install`

## Error Handling

The project must distinguish:

- invalid user input
- missing optional tools
- missing required rendering dependencies
- external integration unavailable
- runtime generation failure

CLI exits with non-zero status and readable errors. API returns structured JSON errors with stable codes.

## Testing Strategy

The first pass focuses on high-signal tests:

- configuration loading
- capability detection
- CLI command routing
- API health and compose/render routes
- graceful fallback when optional integrations are unavailable
- adapter installation path logic

Score generation and rendering logic should be designed so core tests can mock heavy external dependencies.

## Continuous Development Documentation

The repository should include:

- architecture overview
- deployment instructions
- integration matrix
- agent adapter usage
- continuous-development log for teammate handoff

## Tradeoffs Considered

### Approach A: Monolith script expansion

Fastest, but poor long-term boundaries. Rejected.

### Approach B: Layered single repository

Best balance for current scope. Recommended.

### Approach C: Plugin-first framework

Too heavy for the current maturity of the project. Deferred.
