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
- `music-creation-engine workflow full --lyrics "..." --output path`
- `music-creation-engine midi diff --left-notes "60,62" --right-notes "60,64"`
- `music-creation-engine playability --instrument piano --notes "48,60,72,84"`

## Rules

- Prefer package entrypoints over directly re-implementing workflow logic.
- Keep optional integrations behind configuration flags.
- Do not hardcode machine-local absolute paths into docs or adapters.
- Prefer structured score parameters over coarse style-only calls whenever harmonic/section detail is already known.
