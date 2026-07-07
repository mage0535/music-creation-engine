---
name: music-creation-engine
description: Deployable music composition workflow for Hermes Agent. Supports score generation, demo rendering, reference lookup, and optional advanced integrations.
---

# Music Creation Engine for Hermes

Use the project CLI or HTTP API instead of embedding generation logic in the skill.

## Recommended calls

- `music-creation-engine health`
- `music-creation-engine capabilities`
- `music-creation-engine score`
- `music-creation-engine render`
- `music-creation-engine workflow full`
- `music-creation-engine references search`
- `music-creation-engine midi diff|inspect|query`
- `music-creation-engine playability`

## Workflow

1. Collect the user's style, lyrics, instrument, and tempo needs.
2. Use LLM reasoning to plan chord progression, sections structure, melody contour, and per-instrument roles. Convert to structured parameters.
3. Run `workflow full` when the user wants one-shot output with all artifacts.
4. Run `score` first, then `render`, when the user wants review checkpoints.
5. Use `playability` to validate piano/guitar parts before presenting to user.
6. Use `midi inspect` or `midi diff` to compare versions during iteration.
7. Use reference search when the user asks for style comparisons or lyric references.
8. Serve generated files to user via `GET /v1/artifacts/{id}/files/{name}`.

## Structured Parameters (API)

When calling `POST /v1/score` or `POST /v1/workflows/full`, prefer passing structured parameters:

```json
{
  "lyrics": "歌词内容",
  "key": "Am",
  "bpm": 72,
  "instruments": "piano,vocals,bass,drums",
  "style": "pop",
  "chord_progression": ["Am", "F", "C", "G"],
  "sections": [
    {"name": "intro", "bars": 4},
    {"name": "verse", "bars": 8},
    {"name": "chorus", "bars": 8},
    {"name": "outro", "bars": 4}
  ],
  "melody": {"vocals": [69, 71, 72, 69, 71, 72, 76, 74]},
  "instrument_roles": {"piano": "chord", "bass": "bass", "vocals": "melody", "drums": "rhythm"}
}
```

Valid instruments: piano, vocals, guitar, bass, drums, strings, flute, sax, trumpet, synth
Valid roles: chord, melody, bass, pad, rhythm
Valid keys: C, C#, Db, D, Eb, E, F, F#, G, Ab, A, Bb, B (append "m" for minor)
Valid BPM range: 40–240

## Error Response

Error responses have JSON structure: `{"error": {"code": "...", "message": "...", "detail": "..."}}`.

Key codes: MISSING_DEPENDENCY (install needed), FILE_NOT_FOUND (regenerate), RUNTIME_FAILURE (retry), INTEGRATION_UNAVAILABLE (degrade).

## Advanced integrations

- Memory integration is optional and should only be used when explicitly enabled.
- Research integration is optional and should only be used for public-source gathering.
- midi-composer-mcp sidecar is optional; enables richer theory operations.
- reaper-mcp is optional; requires REAPER DAW installed.
