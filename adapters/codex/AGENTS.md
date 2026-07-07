# Music Creation Engine Adapter For Codex

## Purpose

This adapter tells Codex-based agents to treat the repository as a real application, not just a skill bundle.

## Preferred entrypoints

- CLI for shell-friendly execution
- HTTP API for integration and service deployment

## Commands

### Health & Capabilities
- `music-creation-engine health`
- `music-creation-engine capabilities`

### Full Pipeline (recommended for one-shot)
```bash
music-creation-engine workflow full \
  --lyrics "Verse text here" \
  --key Am \
  --bpm 72 \
  --instruments piano,vocals,bass,drums \
  --style pop \
  --chord-progression "Am,F,C,G" \
  --sections '[{"name":"intro","bars":4},{"name":"verse","bars":8},{"name":"chorus","bars":8},{"name":"outro","bars":4}]' \
  --melody '{"vocals":[69,71,72,69,71,72,76,74]}' \
  --instrument-roles '{"piano":"chord","bass":"bass","vocals":"melody","drums":"rhythm"}' \
  --output build/output/song
```

### Score Only (for review checkpoints)
```bash
music-creation-engine score \
  --lyrics "..." \
  --output build/output/song \
  --key C --bpm 120 \
  --instruments piano,vocals \
  --chord-progression "Am,F,C,G" \
  --sections '[{"name":"verse","bars":8}]' \
  --melody '{"vocals":[60,62,64,65,67]}' \
  --instrument-roles '{"piano":"chord","vocals":"melody"}'
```

### Render Audio
```bash
music-creation-engine render --midi path.mid --output path
```

### Reference Search
```bash
music-creation-engine references search --keyword "Jay Chou" --platform netease
```

### MIDI Tools
```bash
music-creation-engine midi diff --left-notes "60,62,64" --right-notes "60,64,65"
music-creation-engine midi inspect --notes "60,62,64,65,67,69,71,72"
music-creation-engine midi query --notes "60,62,64,65,67,69,71,72" --min-pitch 64 --max-pitch 72
```

### Playability Check
```bash
music-creation-engine playability --instrument piano --notes "48,60,72,84"
```

## HTTP API Reference

### POST /v1/score
```json
{
  "lyrics": "Verse text",
  "output_base": "build/output/song",
  "key": "Am",
  "bpm": 72,
  "time_signature": "4/4",
  "instruments": "piano,vocals,bass,drums",
  "style": "pop",
  "chord_progression": ["Am", "F", "C", "G"],
  "sections": [
    {"name": "intro", "bars": 4},
    {"name": "verse", "bars": 8},
    {"name": "chorus", "bars": 8}
  ],
  "melody": {"vocals": [69, 71, 72, 69, 71, 72, 76, 74]},
  "instrument_roles": {"piano": "chord", "bass": "bass", "vocals": "melody"}
}
```

### POST /v1/workflows/full
Same body as /v1/score, plus `"render_demo": true`.

Response includes `workflow_id`.

### GET /v1/artifacts/{workflow_id}
Returns manifest with all artifact paths and checkpoints.

### GET /v1/artifacts/{workflow_id}/files/{filename}
Downloads a specific file (MIDI, PDF, MP3, WAV, MusicXML, LilyPond).

## Valid Values

| Parameter | Valid Values |
|-----------|-------------|
| **instruments** | piano, vocals, guitar, bass, drums, strings, flute, sax, trumpet, synth |
| **instrument_roles** | chord, melody, bass, pad, rhythm |
| **key** | C, C#, Db, D, D#, Eb, E, F, F#, Gb, G, G#, Ab, A, A#, Bb, B, Cm, Dm, Em, Fm, Gm, Am, Bm |
| **bpm** | 40–240 |
| **style** | pop, rock, ballad, jazz, folk |
| **time_signature** | 4/4, 3/4, 6/8 |
| **chord_progression** | Array of chord names: C, Dm, Em, F, G, Am, Bdim, Cmaj7, Dm7, G7, etc. |
| **mode** | all (default) |

## Error Codes

| Code | Meaning | Agent Response |
|------|---------|---------------|
| MISSING_DEPENDENCY | music21/lilypond/fluidsynth/ffmpeg not installed | Tell user to run install.sh |
| MISSING_TOOL | Optional tool not found | Degrade gracefully, skip optional feature |
| FILE_NOT_FOUND | Requested MIDI/file not on disk | Report path, ask user to regenerate |
| RUNTIME_FAILURE | Unexpected internal error | Retry once, then escalate |
| INVALID_INPUT | Malformed parameters | Show user valid format and retry |
| INTEGRATION_UNAVAILABLE | Meting-Agent or sidecar unreachable | Degrade, skip reference data |

## Rules

- Prefer package entrypoints over directly re-implementing workflow logic.
- Always pass structured parameters (chord_progression, sections, melody, instrument_roles) when the Agent has composition knowledge from LLM reasoning. Style-only calls produce template-quality output.
- Keep optional integrations behind configuration flags.
- Do not hardcode machine-local absolute paths into docs or adapters.
- Set `render_demo: false` when user only wants score artifacts, not audio.
