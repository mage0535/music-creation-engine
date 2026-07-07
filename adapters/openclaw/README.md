# OpenClaw Adapter

This directory contains the OpenClaw-facing integration notes for `music-creation-engine`.

## Recommended usage

- Install the project package.
- Expose the CLI commands as callable tools.
- Optionally expose the HTTP API to OpenClaw workflows that expect network-callable services.

## Minimum tool surface

- health
- capabilities
- score
- render
- workflow full
- references search
- midi diff / inspect / query
- playability

## Structured Parameters

When calling score or workflow, use structured parameters for musically meaningful output:

```json
{
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

Valid instruments: piano, vocals, guitar, bass, drums, strings, flute, sax, trumpet, synth
Valid roles: chord, melody, bass, pad, rhythm

## Artifact Access

- `GET /v1/artifacts/{workflow_id}` — retrieve manifest JSON
- `GET /v1/artifacts/{workflow_id}/files/{filename}` — download generated files

## Integration policy

- Enable `meting` by default.
- Keep advanced memory and research integrations disabled unless explicitly requested.
- midi-composer-mcp and reaper-mcp are optional sidecars.
