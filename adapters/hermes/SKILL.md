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

## Workflow

1. Collect the user's style, lyrics, instrument, and tempo needs.
2. Run `workflow full` when the user wants one-shot output.
3. Run `score` first, then `render`, when the user wants review checkpoints.
4. Use reference search when the user asks for style comparisons or lyric references.

## Advanced integrations

- Memory integration is optional and should only be used when explicitly enabled.
- Research integration is optional and should only be used for public-source gathering.
