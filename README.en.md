# Music Creation Engine

English | [中文](README.md)

`music-creation-engine` is a deployable music execution engine for AI agents. It does not replace the agent's reasoning layer. Instead, it turns an already-decided structured music plan into deterministic, verifiable deliverables.

Current version: `v0.4.0`

## What This Project Solves

The project is not trying to generate music "by prompt alone". It makes the full path from user intent to final deliverables executable as an engineering workflow.

It addresses these problems:

- agents can reason, but they often cannot reliably produce MIDI, PDF, WAV, or MP3 artifacts;
- generation results lack workflow checkpoints, revision, retry, and cleanup controls;
- reference lookup, MIDI editing, and playability checks are often split across unrelated tools;
- Hermes, Codex, and OpenClaw need one reusable execution surface.

## Direction

The architecture follows a simple split:

- the Agent decides;
- the Engine executes;
- the workflow records checkpoints and artifacts;
- optional sidecars extend capability without becoming core dependencies.

### Goals

- accept structured composition plans and generate verifiable artifacts;
- expose CLI, HTTP API, and workflow lifecycle controls;
- serve Hermes, Codex, and OpenClaw from the same implementation surface;
- support public release and GitHub Releases automation;
- keep advanced integrations optional.

## Workflow

Recommended order:

1. `health` and `capabilities` to confirm the service is alive.
2. The Agent produces structured inputs: `key`, `bpm`, `style`, `chord_progression`, `sections`, `melody`, `instrument_roles`.
3. `score` generates the core notation artifacts.
4. `render` produces WAV / MP3 / PDF outputs.
5. `workflow full` runs the end-to-end path in one call.
6. `workflow status`, `workflow revise`, `workflow retry`, `workflow cancel`, `workflow delete`, and `workflow cleanup` manage lifecycle.
7. `midi inspect`, `midi diff`, `midi query`, and `midi transform` support iteration.
8. `playability` checks whether the result is actually playable.
9. `references search` provides public reference lookup.

## Integrated Tools

- `music21`
- `LilyPond`
- `FluidSynth`
- `ffmpeg`
- `PyYAML`
- `@eldment/meting-agent`
- optional `midi-composer-mcp`
- optional `reaper-mcp`

## How To Use It

### Health and capabilities

```bash
music-creation-engine health
music-creation-engine capabilities
```

### Generate a structured score

```bash
music-creation-engine score \
  --lyrics "Verse text" \
  --output build/output/song \
  --key Am \
  --bpm 72 \
  --instruments piano,vocals,bass,drums \
  --style pop \
  --chord-progression "Am,F,C,G" \
  --sections '[{"name":"intro","bars":4},{"name":"verse","bars":8},{"name":"chorus","bars":8},{"name":"outro","bars":4}]' \
  --melody '{"vocals":["A4","B4","C5","A4"]}' \
  --instrument-roles '{"piano":"chord","bass":"bass","vocals":"melody","drums":"rhythm"}'
```

### Run the full workflow

```bash
music-creation-engine workflow full \
  --lyrics "..." \
  --output build/output/song \
  --no-render-demo
```

### Inspect and download artifacts

- `GET /v1/artifacts/{workflow_id}`
- `GET /v1/artifacts/{workflow_id}/files/{filename}`
- `GET /v1/workflows/{workflow_id}/checkpoints`

### MIDI-level validation

```bash
music-creation-engine midi inspect --midi-path build/output/song.mid
music-creation-engine midi diff-files --left-path a.mid --right-path b.mid
music-creation-engine midi transform --midi-path a.mid --operation transpose --semitones 2
```

### Playability check

```bash
music-creation-engine playability --instrument piano --notes "48,60,72,84"
```

### Reference search

```bash
music-creation-engine references search --keyword "Jay Chou" --platform netease
```

## Outputs

A full workflow can produce:

- `composition.mid`
- `composition.musicxml`
- `composition.ly`
- `composition.pdf`
- `composition.wav`
- `composition.mp3`
- workflow manifest
- workflow checkpoints

## Installation

### Recommended: Docker

```bash
docker compose up
```

### Local install

```bash
python3 -m pip install -e .
```

Install system rendering dependencies if you want the full output chain:

```bash
sudo apt-get install -y lilypond fluidsynth fluid-soundfont-gm ffmpeg
```

### Installer

```bash
./install.sh
```

The installer asks for:

- Python editable package and CLI entrypoint
- local rendering tools (`lilypond`, `fluidsynth`, `ffmpeg`)
- public reference integration (`@eldment/meting-agent`)
- copying the bundle into detected agent skill directories
- fallback bundle copy under the home directory if no skill directory exists

Default answers are `yes`. In non-interactive environments, the script proceeds with the defaults.

## Release

The repository is prepared for public release:

- `.github/workflows/release.yml`
- release tags follow `v0.4.0`
- pushing a `v*` tag will build and publish a GitHub Release

## Next Options

1. Stronger Meting normalization and provider-specific adapters.
2. More robust async orchestration.
3. Deeper native MIDI editing primitives.
4. More precise playability heuristics.
5. Optional deep integration with `midi-composer-mcp` or `reaper-mcp`.

## Acknowledgements

This project's direction and integration strategy were informed by:

- `midi-composer-mcp`
- `mcp-score`
- `Midra`
- `reaper-mcp`
- `ATRI_AGENT`
- `music.build`
- `OpenClaw`
- `Hermes`

It also borrows ideas from public music-agent workflows, workflow orchestration systems, and release automation patterns.
