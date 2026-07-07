# Install Guide

## Goal

Install `music-creation-engine` as a standalone project and optionally expose it to supported agents.

## Core setup

```bash
python3 -m pip install -e .
sudo apt-get install -y lilypond fluidsynth fluid-soundfont-gm ffmpeg
```

## Public integration

```bash
npm install -g @eldment/meting-agent
```

This is the only integration expected to be enabled by default.

## Optional sidecar integrations

```bash
npm install -g midi-composer-mcp
```

`reaper-mcp` remains optional and should only be configured on machines that actually have REAPER available.

## Agent bundle install

```bash
chmod +x install.sh
./install.sh
```

Detected targets:

- `CODEX_HOME/skills/music-creation-engine`
- `~/.codex/skills/music-creation-engine`
- `~/.hermes/skills/creative/music-creation-engine`
- `~/.claude/skills/music-creation-engine`
- `~/.openclaw/skills/music-creation-engine`

## API launch

```bash
uvicorn music_creation_engine.api.app:create_app --factory --host 0.0.0.0 --port 8000
```

## CLI examples

```bash
music-creation-engine health
music-creation-engine capabilities
music-creation-engine references search --keyword "Lo-fi"
music-creation-engine score --lyrics "hello world" --output build/output/song --chord-progression "Am,F,C,G"
music-creation-engine workflow full --lyrics "hello world" --output build/output/song
music-creation-engine midi diff --left-notes "60,62" --right-notes "60,64"
```

## Advanced integrations

Advanced integrations should be configured manually per deployment. They are not installed or enabled by default:

- memory integration
- embedding integration
- browser/research integration
- REAPER-backed advanced rendering
