# Release Notes - v0.4.0

## Summary

`v0.4.0` turns `music-creation-engine` into a documented, publishable, agent-facing execution engine with a stable workflow surface, public release automation, and a stronger reference-search normalization layer.

## Highlights

### Workflow and delivery

- Stable composition -> render -> artifact workflow
- Revision, retry, cancel, delete, cleanup, and status lifecycle controls
- CLI, HTTP API, and agent adapter alignment

### Public packaging

- Chinese-first README with English switch page
- Formal changelog
- GitHub Release automation
- Installer prompts that explain each deployment decision

### Reference search hardening

- Better Meting-first normalization
- More tolerant MCP parsing
- Richer normalized song metadata
- Reduced dependence on HTTP fallback for usable output

## Notable technical changes

- Unified version metadata at `0.4.0`
- Runtime path resolution kept at entrypoints instead of config-load time
- Meting payload normalization expanded beyond a single provider shape
- MCP result parsing now supports text JSON, code-fenced JSON, and structured content

## Output surface

The engine can produce:

- MIDI
- MusicXML
- LilyPond
- PDF
- WAV
- MP3
- workflow manifest
- workflow checkpoints

## Compatibility

- Hermes
- Codex
- OpenClaw

## Verification baseline

- local unit/integration tests
- end-to-end HTTP workflow test
- GitHub Release publishing via `v0.4.0`
