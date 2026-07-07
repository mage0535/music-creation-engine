# Music Creation Engine

`music-creation-engine` is a deployable music composition execution engine for AI agents such as Hermes, Codex, and OpenClaw.

It accepts structured composition plans from an Agent and produces:

- MIDI
- MusicXML
- LilyPond
- PDF sheet music
- WAV
- MP3
- workflow manifests
- workflow checkpoints

## Quick Start

```bash
# Docker (recommended)
docker compose up

# Manual
python3 -m pip install -e .
sudo apt-get install -y lilypond fluidsynth fluid-soundfont-gm ffmpeg
uvicorn music_creation_engine.api.app:create_app --factory --host 0.0.0.0 --port 8000
```

## HTTP API

### Health & Capabilities

- `GET /health`
- `GET /capabilities`

### Composition

- `POST /v1/score`
- `POST /v1/render`
- `POST /v1/workflows/full`
- `POST /v1/workflows/full?async=true`
- `GET /v1/workflows/{workflow_id}/status`
- `POST /v1/workflows/{workflow_id}/revise`
- `POST /v1/workflows/{workflow_id}/retry`
- `POST /v1/workflows/{workflow_id}/cancel`
- `DELETE /v1/workflows/{workflow_id}`
- `POST /v1/workflows/cleanup`
- `GET /v1/workflows`

### References

- `POST /v1/references/search`

### MIDI Tools

- `POST /v1/midi/diff`
- `POST /v1/midi/diff-files`
- `POST /v1/midi/inspect`
- `POST /v1/midi/query`

### Validation

- `POST /v1/playability`

### Artifacts

- `GET /v1/artifacts/{workflow_id}`
- `GET /v1/artifacts/{workflow_id}/files/{filename}`
- `GET /v1/workflows/{workflow_id}/checkpoints`

## CLI

```bash
music-creation-engine health
music-creation-engine capabilities

music-creation-engine score \
  --lyrics "Verse text" \
  --output /tmp/song \
  --key Am \
  --bpm 72 \
  --instruments piano,vocals,bass \
  --chord-progression "Am,F,C,G" \
  --sections '[{"name":"intro","bars":4},{"name":"verse","bars":8}]' \
  --melody '{"vocals":["A4","B4","C5","A4"]}' \
  --instrument-roles '{"piano":"chord","bass":"bass","vocals":"melody"}'

music-creation-engine render --midi /tmp/song.mid --output /tmp/song

music-creation-engine workflow full --lyrics "..." --output /tmp/song --no-render-demo
music-creation-engine workflow list
music-creation-engine workflow status --workflow-id abc123
music-creation-engine workflow revise --workflow-id abc123 --bpm 84
music-creation-engine workflow retry --workflow-id abc123
music-creation-engine workflow cancel --workflow-id abc123
music-creation-engine workflow delete --workflow-id abc123
music-creation-engine workflow cleanup --retention-days 30

music-creation-engine midi diff --left-notes "60,62,64" --right-notes "60,64,65"
music-creation-engine midi diff-files --left-path a.mid --right-path b.mid
music-creation-engine midi inspect --midi-path /tmp/song.mid
music-creation-engine midi query --notes "60,62,64,65,67" --min-pitch 64

music-creation-engine playability --instrument piano --notes "48,60,72,84"
music-creation-engine references search --keyword "Jay Chou" --platform netease
music-creation-engine adapters install
```

## Structured Score Parameters

Recommended fields for high-quality output:

- `chord_progression`
- `sections`
- `melody`
- `instrument_roles`

Examples:

- `melody: {"vocals":["A4","B4","C5"]}`
- `melody: {"vocals":[69,71,72]}`
- `instrument_roles: {"piano":"chord","bass":"bass","vocals":"melody"}`

Valid instruments:

- `piano`
- `vocals`
- `guitar`
- `bass`
- `drums`
- `strings`
- `flute`
- `sax`
- `trumpet`
- `synth`

Valid roles:

- `chord`
- `melody`
- `bass`
- `pad`
- `rhythm`

## Project Layout

```text
config/defaults.yaml             Runtime configuration
src/music_creation_engine/       Package source
scripts/                         Compatibility entrypoints
adapters/                        Hermes / Codex / OpenClaw adapter files
examples/                        Example workflows
references/current-state.md      Short current-state snapshot
references/continuous-development.md
tests/                           Unit, API, and end-to-end tests
Dockerfile
docker-compose.yml
```

## Deployment Notes

- Docker / compose is the preferred deployment path.
- `Meting-Agent` is the default public reference integration, but still needs stronger normalization and MCP-client hardening.
- `midi-composer-mcp` and `reaper-mcp` are optional sidecars, not default runtime dependencies.

## Verification

```bash
python -m pytest -q
python tests/e2e_http_workflow.py
```

## Agent Adapters

- Hermes: [adapters/hermes/SKILL.md](adapters/hermes/SKILL.md)
- Codex: [adapters/codex/AGENTS.md](adapters/codex/AGENTS.md)
- OpenClaw: [adapters/openclaw/README.md](adapters/openclaw/README.md)
