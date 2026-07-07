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
- `music-creation-engine midi diff`
- `music-creation-engine midi inspect`
- `music-creation-engine midi query`
- `music-creation-engine playability`

## Workflow

1. Collect the user's style, lyrics, instrument, and tempo needs.
2. Run `workflow full` when the user wants one-shot output.
3. Run `score` first, then `render`, when the user wants review checkpoints.
4. Use reference search when the user asks for style comparisons or lyric references.

## Structured score parameters

The adapter can now pass:

- `chord_progression`
- `sections`
- `melody`
- `instrument_roles`

Use these whenever the conversation already contains a concrete plan. Do not collapse a rich user request back into a coarse `style` value if you already know the intended harmonic or structural plan.

## Advanced integrations

- Memory integration is optional and should only be used when explicitly enabled.
- Research integration is optional and should only be used for public-source gathering.
