#!/usr/bin/env bash
# ============================================================================
# Music Creation Engine — One-Click Install Script
# AI-Agent Friendly Installer
# ============================================================================
# After running this, tell your AI agent: "I have the music-creation-engine
# installed. Load the skill from ~/.your-agent/skills/music-creation-engine/SKILL.md"
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  🎵 Music Creation Engine — Installer v1.0      ║${NC}"
echo -e "${CYAN}║  音乐创作引擎 — 一键安装脚本                        ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""

# ── Detect OS ────────────────────────────────────────────────────────
OS="$(uname -s)"
ARCH="$(uname -m)"
echo -e "${YELLOW}[DETECT]${NC} OS: $OS, Arch: $ARCH"

# ── Step 1: Install Python packages ──────────────────────────────────
echo ""
echo -e "${CYAN}[1/5]${NC} Installing Python packages (music21, abjad)..."

install_pip_pkg() {
    if python3 -c "import $1" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} $1 already installed ($(python3 -c "import $1; print(getattr($1, '__version__', 'ok'))"))"
    else
        echo -e "  Installing $1..."
        pip install $1 2>/dev/null || pip install --break-system-packages $1 2>/dev/null || {
            echo -e "  ${YELLOW}⚠ pip failed, trying uv...${NC}"
            uv pip install $1 2>/dev/null || {
                echo -e "  ${RED}✗ Failed to install $1. Try: pip install $1${NC}"
                return 1
            }
        }
        echo -e "  ${GREEN}✓${NC} $1 installed"
    fi
}

install_pip_pkg music21
install_pip_pkg abjad

# ── Step 2: Install system tools ─────────────────────────────────────
echo ""
echo -e "${CYAN}[2/5]${NC} Installing system tools..."

if [[ "$OS" == "Linux" ]]; then
    if command -v apt &>/dev/null; then
        echo -e "  ${YELLOW}apt${NC} detected. Installing lilypond, fluidsynth, fluid-soundfont-gm..."
        apt-get install -y lilypond fluidsynth fluid-soundfont-gm 2>/dev/null && \
            echo -e "  ${GREEN}✓${NC} System tools installed" || \
            echo -e "  ${YELLOW}⚠ Some system packages failed. Try: apt install lilypond fluidsynth fluid-soundfont-gm${NC}"
    elif command -v brew &>/dev/null; then
        echo -e "  ${YELLOW}brew${NC} detected. Installing lilypond, fluidsynth..."
        brew install lilypond fluidsynth fluid-soundfont-gm 2>/dev/null || \
            echo -e "  ${YELLOW}⚠ brew install failed. Try: brew install lilypond fluidsynth${NC}"
    else
        echo -e "  ${YELLOW}⚠ No package manager found. Install manually:${NC}"
        echo -e "     - lilypond (https://lilypond.org)"
        echo -e "     - fluidsynth (https://www.fluidsynth.org)"
    fi
elif [[ "$OS" == "Darwin" ]]; then
    if command -v brew &>/dev/null; then
        echo -e "  ${YELLOW}brew${NC} detected. Installing lilypond, fluidsynth..."
        brew install lilypond fluidsynth fluid-soundfont-gm 2>/dev/null || \
            echo -e "  ${YELLOW}⚠ brew install failed. Try: brew install lilypond fluidsynth${NC}"
    fi
fi

# ── Step 3: Install Meting-Agent MCP (optional) ──────────────────────
echo ""
echo -e "${CYAN}[3/5]${NC} Installing Meting-Agent MCP (music search, optional)..."
if command -v npm &>/dev/null; then
    if npm list -g @eldment/meting-agent &>/dev/null; then
        echo -e "  ${GREEN}✓${NC} @eldment/meting-agent already installed"
    else
        npm install -g @eldment/meting-agent 2>/dev/null && \
            echo -e "  ${GREEN}✓${NC} @eldment/meting-agent installed" || \
            echo -e "  ${YELLOW}⚠ npm install failed. Skip or try: npm install -g @eldment/meting-agent${NC}"
    fi
else
    echo -e "  ${YELLOW}⚠ npm not found. Skip Meting-Agent (music search won't work)${NC}"
fi

# ── Step 4: Install Skill files ──────────────────────────────────────
echo ""
echo -e "${CYAN}[4/5]${NC} Installing skill files..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Try common agent skill directories
SKILL_DIRS=()
if [[ -n "$HERMES_HOME" ]]; then
    SKILL_DIRS+=("$HERMES_HOME/skills/creative/music-creation-engine")
elif [[ -d "$HOME/.hermes" ]]; then
    SKILL_DIRS+=("$HOME/.hermes/skills/creative/music-creation-engine")
fi
if [[ -n "${CODEX_HOME:-}" ]]; then
    SKILL_DIRS+=("$CODEX_HOME/skills/music-creation-engine")
elif [[ -d "$HOME/.codex" ]]; then
    SKILL_DIRS+=("$HOME/.codex/skills/music-creation-engine")
fi
if [[ -d "$HOME/.claude/skills" ]]; then
    SKILL_DIRS+=("$HOME/.claude/skills/music-creation-engine")
fi
if [[ -n "$HOME" ]]; then
    SKILL_DIRS+=("$HOME/music-creation-engine")
fi

INSTALLED=false
for DIR in "${SKILL_DIRS[@]}"; do
    mkdir -p "$DIR/scripts" "$DIR/references" 2>/dev/null
    cp "$SCRIPT_DIR/SKILL.md" "$DIR/" 2>/dev/null && \
    cp "$SCRIPT_DIR/scripts/"*.py "$DIR/scripts/" 2>/dev/null && \
    cp "$SCRIPT_DIR/references/"*.md "$DIR/references/" 2>/dev/null && \
    cp "$SCRIPT_DIR/README.md" "$DIR/" 2>/dev/null && \
    { INSTALLED=true; echo -e "  ${GREEN}✓${NC} Installed to: $DIR"; break; }
done

if ! $INSTALLED; then
    FALLBACK="$HOME/music-creation-engine"
    mkdir -p "$FALLBACK/scripts" "$FALLBACK/references"
    cp "$SCRIPT_DIR/SKILL.md" "$FALLBACK/" 2>/dev/null
    cp "$SCRIPT_DIR/scripts/"*.py "$FALLBACK/scripts/" 2>/dev/null
    cp "$SCRIPT_DIR/references/"*.md "$FALLBACK/references/" 2>/dev/null
    cp "$SCRIPT_DIR/README.md" "$FALLBACK/" 2>/dev/null
    echo -e "  ${GREEN}✓${NC} Installed to: $FALLBACK"
    echo -e "  ${YELLOW}💡${NC} Tell your AI: 'Load the music-creation-engine skill from $FALLBACK/SKILL.md'"
fi

# ── Step 5: Verify installation ──────────────────────────────────────
echo ""
echo -e "${CYAN}[5/5]${NC} Verifying installation..."

PASS=0
FAIL=0

python3 -c "import music21; print(f'  music21 {music21.__version__}')" 2>/dev/null && PASS=$((PASS+1)) || { echo -e "  ${RED}✗ music21 not found${NC}"; FAIL=$((FAIL+1)); }
python3 -c "import abjad; print(f'  abjad {abjad.__version__}')" 2>/dev/null && PASS=$((PASS+1)) || { echo -e "  ${RED}✗ abjad not found${NC}"; FAIL=$((FAIL+1)); }
command -v lilypond &>/dev/null && { lilypond --version 2>&1 | head -1 | sed 's/^/  /'; PASS=$((PASS+1)); } || { echo -e "  ${RED}✗ lilypond not found${NC}"; FAIL=$((FAIL+1)); }
command -v fluidsynth &>/dev/null && { fluidsynth --version 2>&1 | head -1 | sed 's/^/  /'; PASS=$((PASS+1)); } || { echo -e "  ${YELLOW}⚠ fluidsynth not found (MIDI→WAV won't work)${NC}"; }
command -v ffmpeg &>/dev/null && PASS=$((PASS+1)) || { echo -e "  ${YELLOW}⚠ ffmpeg not found (WAV→MP3 won't work)${NC}"; }

echo ""
echo -e "${GREEN}══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ Installation complete!${NC}"
echo -e "${GREEN}  $PASS core components installed, $FAIL missing${NC}"
echo -e "${GREEN}══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}📖${NC} Usage:"
echo -e "  Tell your AI assistant:"
echo -e "  ${CYAN}\"I have the music-creation-engine installed. Load the skill\"${NC}"
echo ""
echo -e "${YELLOW}🔬${NC} Quick test:"
echo -e "  python3 $SCRIPT_DIR/scripts/sheet_music_generator.py \\"
echo -e "    --lyrics \"Hello world test song\\nThis is a quick test\" \\"
echo -e "    --key C --bpm 120 --instruments piano --style pop \\"
echo -e "    --output /tmp/music_test/hello --mode all --json"
echo ""
echo -e "${YELLOW}🔗${NC} GitHub: https://github.com/mage0535/music-creation-engine"
echo ""
