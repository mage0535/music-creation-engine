#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

copy_bundle() {
  local target="$1"
  mkdir -p "$target"
  cp "$ROOT_DIR/README.md" "$target/"
  cp "$ROOT_DIR/SKILL.md" "$target/"
  cp "$ROOT_DIR/pyproject.toml" "$target/"

  mkdir -p "$target/scripts" "$target/references" "$target/config" "$target/adapters" "$target/examples"
  cp "$ROOT_DIR/scripts/"*.py "$target/scripts/"
  cp "$ROOT_DIR/references/"*.md "$target/references/"
  cp "$ROOT_DIR/config/"*.yaml "$target/config/"
  cp -r "$ROOT_DIR/adapters/." "$target/adapters/"
  cp -r "$ROOT_DIR/examples/." "$target/examples/"
}

install_python_deps() {
  if command -v python3 >/dev/null 2>&1; then
    python3 -m pip install -e "$ROOT_DIR" >/dev/null 2>&1 || true
  fi
}

install_system_tools() {
  if command -v apt-get >/dev/null 2>&1; then
    if command -v sudo >/dev/null 2>&1; then
      sudo apt-get update >/dev/null 2>&1 || true
      sudo apt-get install -y lilypond fluidsynth fluid-soundfont-gm ffmpeg >/dev/null 2>&1 || true
    else
      apt-get update >/dev/null 2>&1 || true
      apt-get install -y lilypond fluidsynth fluid-soundfont-gm ffmpeg >/dev/null 2>&1 || true
    fi
  fi
}

install_public_integrations() {
  if command -v npm >/dev/null 2>&1; then
    npm install -g @eldment/meting-agent >/dev/null 2>&1 || true
  fi
}

main() {
  install_python_deps
  install_system_tools
  install_public_integrations

  local installed=0
  if [[ -n "${CODEX_HOME:-}" ]]; then
    local codex_target="$CODEX_HOME/skills/music-creation-engine"
    copy_bundle "$codex_target"
    installed=1
  elif [[ -d "${HOME:-}/.codex" ]]; then
    local codex_target="${HOME}/.codex/skills/music-creation-engine"
    copy_bundle "$codex_target"
    installed=1
  fi

  if [[ -d "${HOME:-}/.hermes" ]]; then
    local hermes_target="${HOME}/.hermes/skills/creative/music-creation-engine"
    copy_bundle "$hermes_target"
    installed=1
  fi

  if [[ -d "${HOME:-}/.claude/skills" ]]; then
    local claude_target="${HOME}/.claude/skills/music-creation-engine"
    copy_bundle "$claude_target"
    installed=1
  fi

  if [[ -d "${HOME:-}/.openclaw" ]]; then
    local openclaw_target="${HOME}/.openclaw/skills/music-creation-engine"
    copy_bundle "$openclaw_target"
    installed=1
  fi

  if [[ "$installed" -eq 0 ]]; then
    local fallback="${HOME}/music-creation-engine"
    copy_bundle "$fallback"
  fi
}

main "$@"
