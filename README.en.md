# Music Creation Engine

English | [中文](README.md)

`music-creation-engine` is a music execution engine for agents such as Hermes, Codex, and OpenClaw. It turns an agent's structured composition plan into verifiable deliverables instead of acting like a chat-only music assistant.

## One-line Positioning

The Agent decides. The Engine executes.

- Agent: understands the user's request and plans style, sections, melody, harmony, and instrument roles
- Engine: produces MIDI, MusicXML, LilyPond, PDF, WAV, MP3, and workflow artifacts

## Current Version

- Current release: `v0.4.0`
- Current development focus: `v0.5.0` hardening
- Source-of-truth summary: `references/project-status.md`

## Typical Use Cases

- You want real music files, not only prompt output
- You want composition, rendering, revision, retry, and artifact management in one workflow
- You want Hermes, Codex, and OpenClaw to share the same execution surface
- You want deterministic, testable boundaries between LLM reasoning and runtime execution

## Core Capabilities

- Structured composition: `key`, `bpm`, `chord_progression`, `sections`, `melody`, `instrument_roles`
- Score outputs: MIDI, MusicXML, LilyPond, PDF
- Audio outputs: WAV, MP3
- Workflow lifecycle: `status`, `revise`, `retry`, `cancel`, `delete`, `cleanup`
- MIDI tools: `diff`, `diff-files`, `inspect`, `query`, `transform`
- Playability checks for piano, vocals, guitar, bass, and more
- Reference search with Meting primary path and HTTP fallback

## Quick Start

### Docker

```bash
git clone https://github.com/mage0535/music-creation-engine.git
cd music-creation-engine
docker compose up
```

### Manual Install

```bash
python3 -m pip install -e .
sudo apt-get install -y lilypond fluidsynth fluid-soundfont-gm ffmpeg
npm install -g @eldment/meting-agent
uvicorn music_creation_engine.api.app:create_app --factory --host 0.0.0.0 --port 8000
```

## Minimal Workflow

1. Call `GET /health` and `GET /capabilities`
2. Use `POST /v1/score` to generate notation and MIDI
3. Use `POST /v1/render` or `POST /v1/workflows/full` for audio and full artifacts
4. Use `POST /v1/workflows/{id}/revise` for iterative changes
5. Use `GET /v1/artifacts/{id}` and `GET /v1/artifacts/{id}/files/{name}` to retrieve outputs

## Auth And Rate Limiting

The `v0.5.0` hardening path now includes basic auth and rate limiting:

- `MCE_API_KEYS`: comma-separated API keys
- `MCE_RATE_LIMIT_PER_MINUTE`: per-minute request cap
- `MCE_AUTH_HEADER_NAME`: custom auth header, default `x-api-key`

If `MCE_API_KEYS` is empty, local development stays open by default.  
If `MCE_API_KEYS` is configured, all `/v1/*` routes require a valid API key.

## Example Request

```json
{
  "lyrics": "Verse text",
  "output_base": "build/output/song",
  "key": "Am",
  "bpm": 72,
  "instruments": "piano,vocals,bass,drums",
  "style": "pop",
  "chord_progression": ["Am", "F", "C", "G"],
  "sections": [
    {"name": "intro", "bars": 4},
    {"name": "verse", "bars": 8},
    {"name": "chorus", "bars": 8}
  ],
  "melody": {"vocals": ["A4", "B4", "C5", "A4"]},
  "instrument_roles": {"piano": "chord", "bass": "bass", "vocals": "melody", "drums": "rhythm"}
}
```

## Main Routes

- `GET /health`
- `GET /capabilities`
- `POST /v1/score`
- `POST /v1/render`
- `POST /v1/workflows/full`
- `GET /v1/workflows/{workflow_id}/status`
- `POST /v1/workflows/{workflow_id}/revise`
- `POST /v1/references/search`
- `POST /v1/midi/inspect`
- `POST /v1/playability`

## Documentation Entry Points

- Source of truth: `references/project-status.md`
- Current state: `references/current-state.md`
- Continuous development log: `references/continuous-development.md`
- Release notes: `references/release-notes-v0.4.0.md`
- Changelog: `CHANGELOG.md`

## Testing

```bash
python -m pytest -q tests --ignore=tests/live_service_test.py
python tests/e2e_http_workflow.py
```

## Project Layout

```text
config/                         default configuration
src/music_creation_engine/      package source
adapters/                       Hermes / Codex / OpenClaw adapters
references/                     status, roadmap, and development docs
tests/                          unit, integration, and E2E tests
Dockerfile
docker-compose.yml
install.sh
```

## Next

Recommended order:

1. Keep the documentation source of truth and engineering boundary stable
2. Finish `v0.5.0` hardening: auth, CI, smart revision, real integration test
3. Only then expand into `midi-composer-mcp`, SSE, and deeper Reaper integration
