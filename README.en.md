# 🎵 Music Creation Engine

[中文版](README.md) | [English](README.en.md)

**An AI Agent-native music composition execution engine — converts LLM composition decisions into publication-quality sheet music + audio artifacts**

> **Two-Layer Relationship**
>
> | Project | Role | Responsibility |
> |---------|------|---------------|
> | **Hermes / Codex / OpenClaw** | Agent base | Conversation, intent parsing, LLM reasoning |
> | **music-creation-engine** | Execution layer | Converts structured parameters → MIDI/PDF/MP3 artifacts |
>
> **Agent handles "thinking" (LLM composition decisions). Engine handles "doing" (deterministic score generation + audio rendering).**

---

## Use Cases

- ✅ You want your Agent to **actually generate MIDI, PDF sheet music, and MP3 audio** — not just describe them
- ✅ You want **structured control** over composition results: chord progressions, section structure, note-name melody, instrument roles
- ✅ You need **workflow tracking** with history, revision iteration, retry, and cleanup
- ✅ You want a single API + CLI surface that works across Hermes / Codex / OpenClaw

---

## Feature Overview

| Feature | Description |
|---------|-------------|
| 🎼 **Structured Composition** | Chord progressions, sections, note-name melody, instrument roles |
| 🎹 **Note Name Input** | `["A4","B4","C5"]` or `[69,71,72]` — both accepted |
| 📄 **Multi-Format Output** | MIDI / MusicXML / LilyPond source / PDF sheet music |
| 🔊 **Audio Rendering** | FluidSynth → WAV → FFmpeg → MP3 |
| 🔄 **Async Workflow** | `?async=true` → immediate return, background generation, poll status |
| 📦 **Artifact Management** | Auto manifest + checkpoints + file inventory per workflow |
| 🎯 **MIDI Tools** | diff / inspect / query / transform (transpose/replace/reverse/invert) |
| 🖖 **Playability Check** | Multi-instrument range validation, span, density, hand-crossing |
| 🔍 **Reference Search** | Meting-Agent → MCP stdio → iTunes HTTP three-tier fallback |
| 🐳 **Dockerized** | Dockerfile + docker-compose.yml |

---

## Quick Start

### Docker (Recommended)

```bash
git clone https://github.com/YOUR_REPO/music-creation-engine.git
cd music-creation-engine
docker compose up
# Server at http://localhost:8000
```

### Manual Install

```bash
# 1. Clone
git clone https://github.com/YOUR_REPO/music-creation-engine.git && cd music-creation-engine

# 2. Install Python package
python3 -m pip install -e .

# 3. Install system dependencies
sudo apt-get install -y lilypond fluidsynth fluid-soundfont-gm ffmpeg

# 4. (Optional) Install reference search
npm install -g @eldment/meting-agent

# 5. Start server
uvicorn music_creation_engine.api.app:create_app --factory --host 0.0.0.0 --port 8000
```

### Verify

```bash
curl http://localhost:8000/health
# {"status":"ok"}

curl -X POST http://localhost:8000/v1/score \
  -H "Content-Type: application/json" \
  -d '{"lyrics":"Hello","output_base":"/tmp/song","key":"Am","bpm":72,"instruments":"piano,vocals","chord_progression":["Am","F","C","G"],"melody":{"vocals":["A4","B4","C5","A4"]}}'
```

---

## Table of Contents

- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Functional Modules](#functional-modules)
- [API Reference](#api-reference)
- [CLI Reference](#cli-reference)
- [Parameters](#parameters)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Agent Adapters](#agent-adapters)
- [Resource Usage](#resource-usage-estimated)
- [Acknowledgments](#acknowledgments)
- [License](#license)

---

## Architecture

```
User → Agent (Hermes / Codex / OpenClaw)       ← Decision layer
         │ LLM plans: key, bpm, chords, sections, melody, roles
         ▼
music-creation-engine                            ← Execution layer
  │
  ├── Validation  (bpm 20-300 / key whitelist / inst whitelist / chord regex)
  ├── music21     → MIDI / MusicXML / LilyPond / PDF
  ├── fluidsynth  → WAV → ffmpeg → MP3
  ├── ArtifactService → manifest + checkpoints + file inventory
  ├── FileResponse    → file download (mid/pdf/mp3/wav/xml/ly)
  ├── Workflow        → async / status / revise / retry / cancel / delete / cleanup
  ├── MIDI tools      → diff / diff-files / inspect / query / transform
  └── Reference       → Meting CLI → MCP stdio → iTunes HTTP
```

**Architectural boundary:** The Engine does NOT call LLMs. All LLM reasoning stays in the Agent layer, enabling 65 deterministic unit tests.

---

## Functional Modules

### 1. Score Generation (`runtime/score_runtime.py`)

Powered by music21. Accepts structured composition parameters:

```python
# LLM-friendly note names
melody = {"vocals": ["A4", "B4", "C5", "A4"]}
# Backward-compatible MIDI numbers
melody = {"vocals": [69, 71, 72, 69]}
```

Per-section key/instrument overrides:
```json
"sections": [
  {"name": "intro",  "bars": 4, "key": "Am"},
  {"name": "verse",  "bars": 8, "key": "Am"},
  {"name": "chorus", "bars": 8, "key": "C"},
  {"name": "bridge", "bars": 4, "key": "F"},
  {"name": "outro",  "bars": 4, "key": "Am"}
]
```

### 2. Audio Rendering (`runtime/render_runtime.py`)

FluidSynth → WAV → FFmpeg → MP3 pipeline. Cross-platform SoundFont detection.

### 3. Workflow & Artifact Management

```text
build/workflows/{workflow_id}/
├── artifacts/
│   ├── composition.mid        (MIDI)
│   ├── composition.musicxml   (DAW-importable)
│   ├── composition.ly         (LilyPond source)
│   ├── composition.pdf        (sheet music)
│   ├── composition.wav        (lossless audio)
│   └── composition.mp3        (preview audio)
├── manifest.json
├── checkpoints.json
└── status.json
```

States: `queued → processing → completed → failed → cancelled`

### 4. MIDI Tools (`services/midi_service.py`)

| Tool | Description |
|------|-------------|
| `diff` | Compare note lists (added/removed) |
| `diff-files` | Compare two `.mid` files via music21 |
| `inspect` | Analyze count/min/max/unique pitches |
| `query` | Filter by min_pitch / max_pitch |
| `transform` | transpose / replace\_phrase / reverse / invert |

### 5. Playability Check (`services/playability_service.py`)

Instrument-specific range tables: piano (21-108), vocals (55-84), guitar (40-84), bass (28-60), violin, flute, sax, trumpet, cello. Per-hand span analysis, density warnings.

### 6. Reference Search (`integrations/meting.py`)

Three-tier: Meting-Agent direct → MCP stdio → iTunes HTTP. Normalized schema.

---

## API Reference

### Health & Capabilities
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/capabilities` | Tool/integration availability |

### Composition
| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/score` | Structured params → MIDI/PDF/XML |
| POST | `/v1/render` | MIDI → WAV/MP3 |
| POST | `/v1/workflows/full` | Sync pipeline |
| POST | `/v1/workflows/full?async=true` | Async pipeline (poll status) |
| GET | `/v1/workflows/{id}/status` | Async status |
| POST | `/v1/workflows/{id}/revise` | Revision iteration |
| POST | `/v1/workflows/{id}/retry` | Retry |
| POST | `/v1/workflows/{id}/cancel` | Cancel |
| DELETE | `/v1/workflows/{id}` | Delete |
| GET | `/v1/workflows` | List all |
| POST | `/v1/workflows/cleanup` | Scheduled cleanup |
| GET | `/v1/workflows/{id}/checkpoints` | View checkpoints |

### MIDI
| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/midi/diff` | Compare note lists |
| POST | `/v1/midi/diff-files` | Compare .mid files |
| POST | `/v1/midi/inspect` | Analyze notes |
| POST | `/v1/midi/query` | Filter by pitch |
| POST | `/v1/midi/transform` | Transpose/replace/reverse/invert |

### Validation & Search
| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/playability` | Playability check |
| POST | `/v1/references/search` | Reference song lookup |

### Artifacts
| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/artifacts/{id}` | Manifest + file inventory |
| GET | `/v1/artifacts/{id}/files/{name}` | File download |

---

## CLI Reference

```bash
# Composition
music-creation-engine score \
  --lyrics "Verse text" --output /tmp/song \
  --key Am --bpm 72 \
  --instruments piano,vocals,bass \
  --chord-progression "Am,F,C,G" \
  --sections '[{"name":"intro","bars":4}]' \
  --melody '{"vocals":["A4","B4","C5"]}' \
  --instrument-roles '{"piano":"chord","bass":"bass"}'

# Workflow
music-creation-engine workflow full --lyrics "..." --output /tmp/song
music-creation-engine workflow status --workflow-id abc123
music-creation-engine workflow revise --workflow-id abc123
music-creation-engine workflow retry --workflow-id abc123
music-creation-engine workflow list

# MIDI
music-creation-engine midi diff --left-notes "60,62" --right-notes "60,64"
music-creation-engine midi transform --notes "60,62,64" --operation reverse

# Validation
music-creation-engine playability --instrument piano --notes "48,60,72,84"
```

---

## Parameters

| Parameter | Type | Required | Default | Example |
|-----------|------|----------|---------|---------|
| `lyrics` | `str` | ✅ | — | `"Verse text"` |
| `output_base` | `str` | ✅ | — | `"/tmp/song"` |
| `key` | `str` | no | `C` | `"Am"` |
| `bpm` | `int` | no | `120` | `72` |
| `instruments` | `str` | no | `"piano,vocals"` | `"piano,bass,drums"` |
| `chord_progression` | `list[str]` | no | template | `["Am","F","C","G"]` |
| `sections` | `list[object]` | no | lyric lines | `[{name:"verse",bars:8}]` |
| `melody` | `dict[str,list]` | no | template | `{"vocals":["A4","B4","C5"]}` |
| `instrument_roles` | `dict[str,str]` | no | auto | `{"piano":"chord","bass":"bass"}` |

**Valid values:** Instruments `piano vocals guitar bass drums strings flute sax trumpet synth` | Roles `chord melody bass pad rhythm` | BPM 20–300 | Sections ≤50/total bars ≤2000

---

## Configuration

`config/defaults.yaml`:

```yaml
project:
  output_dir: build/output
  workflow_dir: build/workflows
integrations:
  meting_enabled: true
  midi_composer_enabled: false
  reaper_enabled: false
tools:
  ffmpeg_command: ffmpeg
  lilypond_command: lilypond
  fluidsynth_command: fluidsynth
  meting_command: npx
```

Env overrides: `MCE_OUTPUT_DIR` / `MCE_WORKFLOW_DIR`

---

## Project Structure

```
├── install.sh                  ← Install entry
├── Dockerfile / compose.yml    ← Container deploy
├── pyproject.toml              ← Package metadata
├── SKILL.md                    ← Agent skill declaration
├── README.md / .en.md          ← Bilingual docs
├── config/defaults.yaml        ← Configuration
├── src/music_creation_engine/
│   ├── api/app.py              ← 20 routes
│   ├── cli.py                  ← 22 commands
│   ├── models.py               ← Data models
│   ├── services/               ← 6 services
│   ├── runtime/                ← Execution engines
│   └── integrations/           ← meting/MCP/reaper
├── adapters/hermes/ codex/ openclaw/
├── references/                 ← Design docs + dev log
└── tests/                      ← 65+30 tests
```

---

## Agent Adapters

| Agent | File | Install Path |
|-------|------|-------------|
| Hermes | `adapters/hermes/SKILL.md` | `~/.hermes/skills/creative/music-creation-engine/` |
| Codex | `adapters/codex/AGENTS.md` | `$CODEX_HOME/skills/music-creation-engine/` |
| OpenClaw | `adapters/openclaw/README.md` | `~/.openclaw/skills/music-creation-engine/` |

---

## Resource Usage (Estimated)

| Component | Size |
|-----------|------|
| music21 | ~50 MB |
| LilyPond | ~200 MB |
| FluidSynth + FluidR3_GM.sf2 | ~146 MB |
| FFmpeg | ~10 MB |
| Meting-Agent (optional) | ~15 MB |
| **Runtime memory** | ~100 MB |
| **Per-generation artifacts** | ~1-5 MB |

---

## Acknowledgments

- [music21](https://github.com/cuthbertLab/music21) — MIT music theory engine | [LilyPond](https://lilypond.org) — Music engraving | [FluidSynth](https://github.com/FluidSynth/fluidsynth) — MIDI synthesis
- [Meting-Agent](https://github.com/ELDment/Meting-Agent) — Music search MCP | [midi-composer-mcp](https://github.com/voho/midi-composer-mcp) — 40+ music theory tools | [reaper-mcp](https://github.com/bonfire-audio/reaper-mcp) — DAW control

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) | See [references/release-notes-v0.4.0.md](references/release-notes-v0.4.0.md)

## License

TBD
