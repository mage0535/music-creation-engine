<p align="center">
  <h1 align="center">🎵 Music Creation Engine</h1>
  <p align="center">
    <em>AI-Powered Full-Pipeline Music Composition — from Lyrics to MP3</em>
    <br>
    <em>AI 驱动的全链路音乐创作引擎 — 从作词到试听 Demo</em>
  </p>
  <p align="center">
    <a href="#features"><img src="https://img.shields.io/badge/features-8_stages-green" alt="Features"></a>
    <a href="#quick-start"><img src="https://img.shields.io/badge/setup-5_min-blue" alt="Setup Time"></a>
    <a href="#license"><img src="https://img.shields.io/badge/license-MIT-purple" alt="License"></a>
    <a href="#acknowledgments"><img src="https://img.shields.io/badge/references-7_projects-orange" alt="References"></a>
    <a href="https://github.com/mage0535/music-creation-engine"><img src="https://img.shields.io/github/stars/mage0535/music-creation-engine?style=flat" alt="Stars"></a>
  </p>
</p>

---

## 📖 Overview / 概述

**EN:** Music Creation Engine is a zero-GPU, full-pipeline music composition system for AI coding agents. It takes natural language ideas through collaborative multi-agent lyric writing, sheet music generation (PDF/MIDI/MusicXML/LilyPond), demo audio rendering (MP3), quality evaluation, and platform publishing. Designed as a drop-in skill for Claude Code, Hermes Agent, Codex, Cursor, and any other AI coding assistant.

**CN:** 音乐创作引擎是一个零 GPU 的全链路音乐创作系统，专为 AI 编码智能体设计。它通过自然语言接收创作灵感，经过多 Agent 协作作词、乐谱生成（PDF/MIDI/MusicXML）、Demo 音频渲染（MP3）、质量评估和多平台发布，一站式完成从灵感成歌的全流程。即插即用的 skill 设计，兼容 Claude Code、Hermes Agent、Codex、Cursor 等任何 AI 编码助手。

---

## ✨ Features / 功能特色

### Core Capabilities / 核心能力

| Feature / 功能 | Description / 描述 |
|----------------|-------------------|
| 🎤 **Multi-Agent Lyric Writing** | 3 parallel agents (Lyricist, Composer, Producer) collaborate on lyrics via `delegate_task`, iterating with user feedback |
| 🎼 **Sheet Music Generation** | Full score PDF (LilyPond), MIDI playback, MusicXML export for DAW import, per-instrument part sheets |
| 🎧 **Demo Audio Rendering** | MIDI → FluidSynth GM → FFmpeg MP3. Ready to play on any device in under 30 seconds |
| 📊 **Quality Evaluation** | 4 expert agents evaluate melody, rhythm, emotion, and structure with scores and commentary |
| 🌐 **Platform Publishing** | Via AiToEarn MCP: TikTok, YouTube, Twitter, NetEase Cloud, QQ Music, and more |
| 🔍 **Reference Search** | Meting-Agent MCP searches NetEase/QQ/Kugou/Kuwo for reference songs and lyrics |

### What Makes It Unique / 独到之处

1. **Zero GPU Required** — All computation runs on CPU. Music theory (music21), score engraving (LilyPond), and audio synthesis (FluidSynth) are all CPU-native
2. **AI-Agent Native** — Scripts output JSON, designed for tool-calling LLMs. SKILL.md follows standard AI agent skill conventions. install.sh auto-detects your agent environment
3. **Conversational Workflow** — The agent asks "want me to write a song?" when it detects music-related intent, then guides you through the entire pipeline in natural dialogue
4. **Export-Anywhere** — Score PDF (publication-quality), MIDI, MusicXML, LilyPond source, WAV, and MP3 — use any or all
5. **Production-Quality Scores** — LilyPond engraving produces scores that meet professional publishing standards, with proper beaming, slurs, dynamics, and articulation
6. **Reference-Driven Creation** — Meting-Agent MCP fetches real songs from Chinese music platforms for style/lyric reference during composition

### Compatibility / 兼容性

| Environment | Support |
|------------|---------|
| **Hermes Agent** | ✅ skill_view('music-creation') |
| **Claude Code** | ✅ Copy SKILL.md to ~/.claude/skills/ |
| **Cursor / Codex** | ✅ Reference README in project docs |
| **Any LLM chat** | ✅ Paste README.md into system prompt |
| **Platform** | Linux ✅ (Ubuntu/Debian), macOS ⚠️ (brew, some tools may differ) |
| **GPU** | ❌ Not required |
| **RAM** | ~200MB minimum |
| **Disk** | ~425MB for all dependencies |

---

## 🚀 Quick Start / 快速开始

### One-Click Install / 一键安装

```bash
git clone https://github.com/mage0535/music-creation-engine.git
cd music-creation-engine
chmod +x install.sh
./install.sh
```

### Manual Install / 手动安装

```bash
# Python packages
pip install music21 abjad

# System tools
sudo apt install lilypond fluidsynth fluid-soundfont-gm

# Optional: music search MCP
npm install -g @eldment/meting-agent
```

### Verify / 验证

```bash
python3 -c "import music21; print(f'music21 {music21.__version__}')"
python3 -c "import abjad; print(f'abjad {abjad.__version__}')"
lilypond --version | head -1
fluidsynth --version | head -1
```

---

## 🎮 Usage / 使用方法

### For AI Coding Agents / 给 AI 编码助手

Tell your AI assistant:

> "I have the music-creation-engine installed. Load the SKILL.md from `~/.your-agent/skills/music-creation/SKILL.md`"

This triggers the **conversation-driven workflow**: the agent detects when you're talking about music ideas and offers to compose.

### Direct Script Usage / 脚本直接调用

**Generate Sheet Music / 生成乐谱:**
```bash
python3 scripts/sheet_music_generator.py \
  --lyrics "Morning light fills the window\nGentle breeze takes the dust away" \
  --key C --bpm 120 \
  --instruments piano,vocals,guitar,bass,drums \
  --style pop \
  --output /tmp/my_song \
  --mode all --json
```

**Render Demo / 渲染试听:**
```bash
python3 scripts/demo_renderer.py \
  --midi /tmp/my_song.mid \
  --output /tmp/my_song_demo \
  --format mp3 --json
```

### Output Files / 输出文件

```
/tmp/my_song/
├── score.pdf        (229KB) — Full score, publication-quality
├── score.mid        (1.8KB) — MIDI playback
├── score.musicxml   (80KB)  — Universal format
├── demo.mp3         (462KB) — 🎧 Listen on any device
└── demo.wav         (4.6MB) — Uncompressed original
```

---

## 🏗 Architecture / 架构

```
User Idea (chat)
    │
    ├── Intent Detection (natural language, no hardcoded keywords)
    │
    ├── Phase 1: Multi-Agent Lyric Writing
    │   ├── Lyricist Agent ──── writes lyrics with rhyme & structure
    │   ├── Composer Agent ──── evaluates singability & melody
    │   └── Producer Agent ──── assesses arrangement & structure
    │   └── ← User iterates until satisfied
    │
    ├── Phase 2: Sheet Music Generation
    │   ├── music21 (music theory engine)
    │   ├── Abjad → LilyPond → PDF score
    │   └── MIDI + MusicXML export
    │
    ├── Phase 3: Demo Audio
    │   ├── FluidSynth (MIDI→WAV via GM soundfont)
    │   └── FFmpeg (WAV→MP3 for listening)
    │
    ├── Phase 4: Quality Evaluation
    │   ├── 4 parallel eval agents (melody/rhythm/emotion/structure)
    │   └── Detailed scoring report
    │
    └── Phase 5: Publishing (optional)
        └── AiToEarn MCP → TikTok/YouTube/Twitter/Music platforms
```

### Tool Chain Diagram / 工具链联动

```
┌───────────────────────────────────────────────────────────┐
│              Music Creation Engine Tool Chain               │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  SKILL.md ─── orchestrates the multi-agent pipeline       │
│    │                                                      │
│    ├── script: sheet_music_generator.py                   │
│    │   ├── music21 (theory, chord analysis, transposition)│
│    │   └── abjad → lilypond (score engraving → PDF)      │
│    │                                                      │
│    ├── script: demo_renderer.py                           │
│    │   ├── fluidsynth (MIDI→WAV audio rendering)         │
│    │   └── ffmpeg (WAV→MP3 encoding)                     │
│    │                                                      │
│    ├── MCP: meting-agent (reference song search/lyrics)  │
│    ├── MCP: aitoearn (publish to music platforms)        │
│    └── tool: delegate_task (parallel multi-agent lyrics)  │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

---

## 📦 Dependencies / 依赖清单

| Package | Version | Size | Purpose |
|---------|---------|------|---------|
| music21 | 10.3.0+ | ~50MB | Music theory, analysis, notation I/O |
| abjad | 3.31+ | ~5MB | Python API for LilyPond scores |
| lilypond | 2.24+ | ~200MB | Professional music engraving |
| fluidsynth | 2.3+ | ~5MB | MIDI→WAV audio rendering |
| fluid-soundfont-gm | — | ~140MB | General MIDI soundfont |
| ffmpeg | 6.x+ | ~10MB | WAV→MP3/OGG encoding |
| @eldment/meting-agent | latest | ~15MB | MCP: music platform search (optional) |

---

## 🔧 Configuration for AI Agents / 智能体配置

### Hermes Agent

Skill auto-detects music intent. Alternatively, install scripts as tools:

```yaml
# ~/.hermes/tool_manifest.yaml
music_creation:
  status: active
  skill: music-creation
  scripts:
    - scripts/sheet_music_generator.py
    - scripts/demo_renderer.py
```

For MCP registration:

```yaml
# ~/.hermes/config.yaml
mcp_servers:
  meting-agent:
    command: npx
    args: ["@eldment/meting-agent"]
    connect_timeout: 15
    startup: lazy
    timeout: 60
```

### Claude Code

Copy to skills directory:

```bash
cp SKILL.md ~/.claude/skills/music-creation/
cp -r scripts/ ~/.claude/skills/music-creation/scripts/
```

### Any LLM Chat

Copy the contents of this README and SKILL.md into the system prompt. The LLM will understand the full pipeline.

---

## 🔬 Test / 测试验证

```bash
# Full pipeline test
mkdir -p /tmp/music_test
python3 scripts/sheet_music_generator.py \
  --lyrics "清晨的阳光洒落窗台\n微风带走了昨夜的尘埃" \
  --key C --bpm 120 \
  --instruments piano,vocals,guitar,bass \
  --style pop \
  --output /tmp/music_test/test_song \
  --mode all --json

python3 scripts/demo_renderer.py \
  --midi /tmp/music_test/test_song.mid \
  --output /tmp/music_test/test_demo \
  --format mp3

ls -lh /tmp/music_test/test_*
```

Expected output: `test_song.mid` (~1.8KB), `test_song.pdf` (~229KB), `test_demo.mp3` (~462KB)

---

## 📋 Project Structure / 项目结构

```
music-creation-engine/
├── README.md                          # This file (EN+CN)
├── SKILL.md                           # AI agent skill definition
├── install.sh                         # One-click installer
├── scripts/
│   ├── sheet_music_generator.py       # Lyrics → score (MIDI/PDF/XML)
│   └── demo_renderer.py               # MIDI → FluidSynth → MP3
└── references/
    └── install-guide.md               # Detailed install & troubleshooting
```

---

## 🤝 Acknowledgments / 致谢

This project benefits from the following open-source projects and communities:

- **[music21](https://github.com/cuthbertLab/music21)** (MIT) — MIT's music theory library. The core engine for chord analysis, key detection, and score manipulation. _music21 is the foundation of our sheet music pipeline._
- **[Abjad](https://github.com/Abjad/abjad)** (MIT) — Python API for building LilyPond files. _Powers our publication-quality score generation._
- **[LilyPond](https://lilypond.org)** (GPL) — The world's finest music engraving system. _Renders editor-quality PDF scores from our Abjad output._
- **[FluidSynth](https://github.com/FluidSynth/fluidsynth)** (LGPL) — Real-time software synthesizer. _Renders MIDI files to audio using the FluidR3 GM soundfont._
- **[Meting-Agent](https://github.com/ELDment/Meting-Agent)** (MIT) — MCP server for NetEase/QQ/Kugou/Kuwo music platforms. _Provides reference song search and lyric retrieval during composition._
- **[jnMetaCode/agency-agents-zh](https://github.com/jnMetaCode/agency-agents-zh)** (MIT) — 215 Chinese AI expert agent definitions. _Inspired our multi-agent lyric writing workflow pattern._
- **[Tz-WIND/ATRI_AGENT](https://github.com/Tz-WIND/ATRI_AGENT)** (MIT) — AI Agent music workstation. _Demonstrated the music21+DAW integration pattern we adapted for our pipeline._
- **[FFmpeg](https://ffmpeg.org)** (LGPL) — The complete multimedia framework. _Our audio encoding and format conversion layer._
- **[Muyu1uz/music-master](https://github.com/Muyu1uz/music-master)** — Multi-agent music creation with LangGraph. _Informed our phase orchestration design._
- **[Nous Research / Hermes Agent](https://github.com/NousResearch/hermes-agent)** — The multi-agent framework that powers our lyric collaboration and skill orchestration.

---

## 📄 License

MIT © 2026 — Free to use, modify, share, and deploy with any AI agent.

---

## 🔗 Links / 链接

- **GitHub**: https://github.com/mage0535/music-creation-engine
- **Report Issues**: https://github.com/mage0535/music-creation-engine/issues
- **Topics**: `music-creation` `ai-composer` `sheet-music` `lilypond` `music21` `midi` `audio-demo` `fluidsynth` `hermes-agent` `claude-code` `ai-agent` `music-ai` `multilingual` `mcp-server` `zero-gpu`
