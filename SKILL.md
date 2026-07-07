---
name: music-creation-engine
description: Deployable music generation workflow for AI agents, with CLI, API, agent adapters, and configurable integrations.
tags: [music, composition, api, cli, agent, sheet-music, audio]
---

# Music Creation Engine

## Intent

Use this project when the user wants to:

- turn lyrics or an idea into sheet music artifacts
- render demo audio from MIDI
- query reference music metadata
- run music workflows from CLI or HTTP API
- integrate the workflow into Hermes, Codex, or OpenClaw

## Preferred Execution Order

1. `music-creation-engine capabilities`
2. `music-creation-engine score`
3. `music-creation-engine render`
4. `music-creation-engine workflow full`
5. `music-creation-engine references search`

## Rules

- Prefer calling the package entrypoints over re-implementing workflow logic.
- Treat `Meting-Agent` as public-default integration.
- Treat memory and research integrations as advanced opt-in integrations.
- Keep generated artifacts and environment-specific paths out of versioned source.

## HTTP API

- `GET /health`
- `GET /capabilities`
- `POST /v1/score`
- `POST /v1/workflows/full`
- `POST /v1/references/search`

## Adapters

- Hermes adapter: `adapters/hermes/SKILL.md`
- Codex adapter: `adapters/codex/AGENTS.md`
- OpenClaw adapter: `adapters/openclaw/README.md`
