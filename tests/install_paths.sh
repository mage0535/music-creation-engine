#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

make_stub_bin() {
  local bin_dir="$1"
  mkdir -p "$bin_dir"

  cat >"$bin_dir/python3" <<'EOF'
#!/usr/bin/env bash
exit 0
EOF

  cat >"$bin_dir/npm" <<'EOF'
#!/usr/bin/env bash
exit 0
EOF

  cat >"$bin_dir/lilypond" <<'EOF'
#!/usr/bin/env bash
echo "GNU LilyPond 2.24.3"
EOF

  cat >"$bin_dir/fluidsynth" <<'EOF'
#!/usr/bin/env bash
echo "FluidSynth runtime version 2.3.4"
EOF

  cat >"$bin_dir/ffmpeg" <<'EOF'
#!/usr/bin/env bash
echo "ffmpeg version 6.1.1"
EOF

  cat >"$bin_dir/apt-get" <<'EOF'
#!/usr/bin/env bash
exit 0
EOF

  cat >"$bin_dir/sudo" <<'EOF'
#!/usr/bin/env bash
"$@"
EOF

  chmod +x "$bin_dir/"*
}

assert_exists() {
  local path="$1"
  if [[ ! -e "$path" ]]; then
    echo "missing: $path" >&2
    return 1
  fi
}

test_codex_install_path() {
  local sandbox
  sandbox="$(mktemp -d)"
  trap 'rm -rf "$sandbox"' RETURN

  make_stub_bin "$sandbox/bin"
  export PATH="$sandbox/bin:$PATH"
  export HOME="$sandbox/home"
  export CODEX_HOME="$sandbox/codex"
  mkdir -p "$HOME" "$CODEX_HOME/skills"

  bash "$ROOT_DIR/install.sh" >/dev/null

  assert_exists "$CODEX_HOME/skills/music-creation-engine/SKILL.md"
  assert_exists "$CODEX_HOME/skills/music-creation-engine/scripts/sheet_music_generator.py"
}

test_hermes_install_path() {
  local sandbox
  sandbox="$(mktemp -d)"
  trap 'rm -rf "$sandbox"' RETURN

  make_stub_bin "$sandbox/bin"
  export PATH="$sandbox/bin:$PATH"
  export HOME="$sandbox/home"
  unset CODEX_HOME
  mkdir -p "$HOME/.hermes"

  bash "$ROOT_DIR/install.sh" >/dev/null

  assert_exists "$HOME/.hermes/skills/creative/music-creation-engine/SKILL.md"
  assert_exists "$HOME/.hermes/skills/creative/music-creation-engine/references/install-guide.md"
}

test_codex_install_path
test_hermes_install_path
