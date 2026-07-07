#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

prompt_yes_no() {
  local prompt="$1"
  local default_answer="${2:-yes}"
  local suffix="[Y/n]"
  local answer

  if [[ "${MCE_NONINTERACTIVE:-0}" == "1" || ! -t 0 ]]; then
    [[ "$default_answer" == "yes" ]]
    return
  fi

  if [[ "$default_answer" == "no" ]]; then
    suffix="[y/N]"
  fi

  while true; do
    read -r -p "$prompt $suffix " answer || answer=""
    answer="${answer:-$default_answer}"
    case "$answer" in
      y|Y|yes|YES) return 0 ;;
      n|N|no|NO) return 1 ;;
    esac
  done
}

copy_bundle() {
  local target="$1"
  mkdir -p "$target"
  cp "$ROOT_DIR/README.md" "$target/"
  if [[ -f "$ROOT_DIR/README.en.md" ]]; then
    cp "$ROOT_DIR/README.en.md" "$target/"
  fi
  if [[ -f "$ROOT_DIR/CHANGELOG.md" ]]; then
    cp "$ROOT_DIR/CHANGELOG.md" "$target/"
  fi
  cp "$ROOT_DIR/SKILL.md" "$target/"
  cp "$ROOT_DIR/pyproject.toml" "$target/"

  mkdir -p "$target/scripts" "$target/references" "$target/config" "$target/adapters" "$target/examples" "$target/src"
  cp "$ROOT_DIR/scripts/"*.py "$target/scripts/"
  cp "$ROOT_DIR/references/"*.md "$target/references/"
  cp "$ROOT_DIR/config/"*.yaml "$target/config/"
  cp -r "$ROOT_DIR/adapters/." "$target/adapters/"
  cp -r "$ROOT_DIR/examples/." "$target/examples/"
  cp -r "$ROOT_DIR/src/." "$target/src/"
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
  if prompt_yes_no "Install the editable Python package and CLI entrypoint?" "yes"; then
    install_python_deps
  fi

  if prompt_yes_no "Install local rendering tools (lilypond, fluidsynth, ffmpeg) when available?" "yes"; then
    install_system_tools
  fi

  if prompt_yes_no "Install the public reference integration (@eldment/meting-agent) globally when available?" "yes"; then
    install_public_integrations
  fi

  local installed=0
  if prompt_yes_no "Copy the bundle into detected agent skill directories?" "yes"; then
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
  fi

  if [[ "$installed" -eq 0 ]]; then
    if prompt_yes_no "No agent skill directory was detected. Copy the bundle to a fallback directory under your home folder?" "yes"; then
      local fallback="${HOME}/music-creation-engine"
      copy_bundle "$fallback"
    fi
  fi
}

main "$@"
