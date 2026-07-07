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

## Integration policy

- Enable `meting` by default.
- Keep advanced memory and research integrations disabled unless explicitly requested.
- Prefer structured score input (`chord_progression`, `sections`, `melody`, `instrument_roles`) when the prompt already contains a concrete composition plan.
