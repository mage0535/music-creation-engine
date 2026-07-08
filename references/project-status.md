# Project Status

## Role

`music-creation-engine` is the execution layer for agent-native music creation.

- Agent: understands intent and decides composition structure
- Engine: generates notation, audio, workflow artifacts, and validation results

## Current Release

- Stable public release: `v0.4.0`
- Current engineering target: `v0.5.0` hardening

## What Is Already Real

- 20 API routes
- 22 CLI subcommands
- 70 local tests plus end-to-end workflow verification
- workflow lifecycle with `status`, `revise`, `retry`, `cancel`, `delete`, `cleanup`
- MIDI utilities and playability checks
- Meting-backed reference search with fallback
- Docker deployment and GitHub Release automation
- Hermes production verification

## Verification Baseline

- local test suite
- end-to-end HTTP workflow test
- live Hermes verification

## Current Priorities

1. Keep documentation, runtime behavior, and deployment state aligned
2. Harden the service surface with auth, rate limiting, CI, and smarter revision reuse
3. Expand capabilities only after the engineering surface is stable

## v0.5.0 Hardening Scope

- API key authentication for `/v1/*`
- in-memory rate limiting
- CI workflow on push and pull request
- smart revision with score/render reuse when possible
- one real integration test against the actual score runtime

## Later Expansion

- `midi-composer-mcp` deep integration
- SSE workflow progress
- deeper playability heuristics
- Reaper advanced render backend
