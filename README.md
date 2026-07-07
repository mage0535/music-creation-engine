# Music Creation Engine

`music-creation-engine` is a deployable music workflow project for AI agents.

It now supports:

- standalone CLI commands
- FastAPI HTTP service
- Hermes, Codex, and OpenClaw adapter assets
- default public integration with `Meting-Agent`
- optional advanced integrations for memory and research tooling

## Project Layout

```text
config/                      Runtime defaults
src/music_creation_engine/   Package source
scripts/                     Backward-compatible script entrypoints
adapters/                    Hermes / Codex / OpenClaw adapter assets
examples/                    Example agent workflows
references/                  Deployment and handoff docs
tests/                       Verification coverage
```

## Runtime Modes

### CLI

```bash
music-creation-engine health
music-creation-engine capabilities
music-creation-engine references search --keyword "Jay Chou"
```

### HTTP API

```bash
uvicorn music_creation_engine.api.app:create_app --factory --host 0.0.0.0 --port 8000
```

Available endpoints:

- `GET /health`
- `GET /capabilities`
- `POST /v1/score`
- `POST /v1/workflows/full`
- `POST /v1/references/search`

## Installation

### Fast path

```bash
chmod +x install.sh
./install.sh
```

What `install.sh` does:

- installs the Python package in editable mode when possible
- installs public dependencies and public integration tooling when possible
- copies the project bundle into detected agent directories

### Manual setup

```bash
python3 -m pip install -e .
sudo apt-get install -y lilypond fluidsynth fluid-soundfont-gm ffmpeg
npm install -g @eldment/meting-agent
```

## Public vs Advanced Integrations

### Default-enabled public integration

- `Meting-Agent`
  Used for reference song and lyric search.

### Optional advanced integrations

- memory integration
- embedding-backed recall
- browser/research integration

These advanced integrations are intentionally disabled by default and should only be enabled by deployment-specific configuration.

## Agent Adapters

- Hermes: [adapters/hermes/SKILL.md](adapters/hermes/SKILL.md)
- Codex: [adapters/codex/AGENTS.md](adapters/codex/AGENTS.md)
- OpenClaw: [adapters/openclaw/README.md](adapters/openclaw/README.md)

## Example Workflows

- [examples/hermes-workflow.md](examples/hermes-workflow.md)
- [examples/codex-workflow.md](examples/codex-workflow.md)
- [examples/openclaw-workflow.md](examples/openclaw-workflow.md)

## Verification

```bash
python -m pytest -q
```

The test suite validates:

- config loading
- capability detection
- service orchestration
- CLI behavior
- API routes
- adapter target resolution
- expected project layout

## Notes

- The old `scripts/` commands still exist, but they now act as compatibility entrypoints into the package.
- Do not hardcode server paths, secrets, or local machine paths into this repository.
