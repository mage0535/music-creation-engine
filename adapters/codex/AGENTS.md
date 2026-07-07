# Music Creation Engine Adapter For Codex

## Purpose

This adapter tells Codex-based agents to treat the repository as a real application, not just a skill bundle.

## Preferred entrypoints

- CLI for shell-friendly execution
- HTTP API for integration and service deployment

## Commands

- `music-creation-engine health`
- `music-creation-engine capabilities`
- `music-creation-engine score --lyrics "..."`
- `music-creation-engine render --midi path.mid --output path`
- `music-creation-engine references search --keyword "..." --platform netease`

## Rules

- Prefer package entrypoints over directly re-implementing workflow logic.
- Keep optional integrations behind configuration flags.
- Do not hardcode machine-local absolute paths into docs or adapters.
