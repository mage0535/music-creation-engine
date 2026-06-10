<p align="center">
  <h1 align="center">🎵 Music Creation Engine / 音乐创作引擎</h1>
  <p align="center">
    <em>AI-Powered Full-Pipeline Music Composition — from Lyrics to MP3</em>
    <br>
    <em>AI 驱动的全链路音乐创作 — 从灵感作词到 Demo 试听</em>
  </p>
  <p align="center">
    <a href="#-features--功能特色"><img src="https://img.shields.io/badge/功能-8%E9%98%B6%E6%AE%B5-green" alt="Features"></a>
    <a href="#-quick-start--快速开始"><img src="https://img.shields.io/badge/安装-5%E5%88%86%E9%92%9F-blue" alt="Setup Time"></a>
    <a href="#-license--许可证"><img src="https://img.shields.io/badge/许可-MIT-purple" alt="License"></a>
    <a href="#-acknowledgments--致谢"><img src="https://img.shields.io/badge/致谢-10项目-orange" alt="References"></a>
  </p>
</p>

---

## 📖 Overview / 概述

**EN:** Music Creation Engine is a zero-GPU, full-pipeline music composition system for AI coding agents. It takes natural language ideas through collaborative multi-agent lyric writing, sheet music generation (PDF/MIDI/MusicXML/LilyPond), demo audio rendering (MP3), quality evaluation, and platform publishing. Designed as a drop-in skill for Claude Code, Hermes Agent, Codex, Cursor, and any other AI coding assistant.

**CN:** 音乐创作引擎是一个零 GPU 的全链路音乐创作系统，专为 AI 编码智能体设计。通过自然语言接收创作灵感，经过多 Agent 协作作词、乐谱生成、Demo 音频渲染、质量评估和多平台发布，一站式完成从灵感到歌曲的全流程。即插即用的 skill 设计，兼容所有主流 AI 编码助手。

**Why / 为什么做这个:** Most AI coding agents can write code but cannot compose music. Existing music AI tools either require expensive GPUs, lack AI-agent-native interfaces (JSON output, MCP protocol), or require deep musical expertise to use. This engine bridges the gap — any AI agent can now walk a user through composition in natural conversation, producing real sheet music and playable audio. / 大多数 AI 编码助手能写代码但不会创作音乐。现有的音乐 AI 工具要么需要 GPU、要么不支持智能体原生调用（JSON 输出、MCP 协议）、要么需要深厚的乐理知识。本引擎填补了这个空白——任何 AI 助手都可以通过自然对话引导用户创作，输出真实的乐谱和可播放的音频。

---

## ✨ Features / 功能特色

### 🎤 Multi-Agent Lyric Writing / 多智能体协作作词

**EN:** 3 parallel agents work together via `delegate_task`:
- **Lyricist** — Creates lyrics with rhyme, rhythm, and structure
- **Composer** — Evaluates singability and melodic flow from music perspective
- **Producer** — Assesses overall arrangement (Intro/Verse/Chorus/Bridge/Outro)

User reviews, gives feedback, and agents iterate until confirmed.

**CN:** 通过 `delegate_task` 并行启动 3 个 Agent 协同创作：
- **词作家** — 创作歌词，注意押韵、节奏和段落结构
- **曲作者** — 从旋律角度评估歌词的可唱性和音乐流畅度
- **音乐制作人** — 从整体结构角度评估（主歌/副歌/桥段编排）

用户审阅反馈，Agent 反复修改，直到确认最终版本。

### 🎼 Sheet Music Generation / 乐谱生成

**EN:** Professional-grade score output in multiple formats:
- **PDF** — LilyPond engraving, publication-quality full score (~229KB)
- **MIDI** — Playback file for any MIDI player (~1.8KB)
- **MusicXML** — Universal format for Sibelius, Finale, Dorico, etc. (~80KB)
- **LilyPond** — Editable `.ly` source for custom engraving

Supports per-instrument part extraction (piano, vocals, guitar, bass, drums, strings, flute, sax, trumpet, synth). Chord progressions adapt to style (pop, rock, ballad, jazz, folk).

**CN:** 出版级乐谱多格式输出：
- **PDF** — LilyPond排版，出版级质量总谱
- **MIDI** — 任何 MIDI 播放器可播
- **MusicXML** — 通用格式，可导入打谱软件
- **LilyPond** — 可编辑的排版源码

支持逐乐器分谱提取（钢琴、人声、吉他、贝斯、鼓、弦乐、长笛、萨克斯、小号、合成器）。和弦进行根据风格自动适配（流行、摇滚、抒情、爵士、民谣）。

### 🎧 Demo Audio Rendering / Demo 音频渲染

**EN:** Pipeline: MIDI → FluidSynth GM SoundFont → WAV → FFmpeg MP3. Ready to listen on any device in under 30 seconds.

**CN:** 管线：MIDI → FluidSynth GM标准音色库 → WAV 无损 → FFmpeg MP3 压缩。30 秒内可在任何设备上试听。

### 📊 Quality Evaluation / 质量评估

**EN:** 4 expert agents evaluate the output across dimensions with scores and commentary:
- Melody fluency and memorability
- Rhythm groove and variation
- Emotion conveyance and mood matching
- Structure coherence and arrangement logic

**CN:** 4 个评估 Agent 从多维度打分并给出文字评价：
- 旋律流畅度与记忆点
- 节奏律动与变化
- 情感传达与氛围匹配
- 结构合理性与编排逻辑

### 🌐 Platform Publishing / 多平台发布

**EN:** Via AiToEarn MCP to TikTok, YouTube, Twitter, NetEase Cloud Music, QQ Music, Bilibili, Xiaohongshu, Kuaishou. Auto-generates cover, title, tags.

**CN:** 通过 AiToEarn MCP 发布到抖音、YouTube、Twitter、网易云音乐、QQ 音乐、B站、小红书、快手。自动生成封面、标题、标签。

### 🔍 Reference Search / 参考搜索

**EN:** Meting-Agent MCP searches songs, lyrics, and albums from NetEase, QQ Music, Kugou, and Kuwo for style reference during composition.

**CN:** 通过 Meting-Agent MCP 从网易云、QQ 音乐、酷狗、酷我搜索参考歌曲、歌词和专辑信息，辅助创作。

---

## 🎯 What Makes It Unique / 独到之处

| # | English | 中文 |
|---|---------|------|
| 1 | **Zero GPU** — All computation is CPU-native (music21, LilyPond, FluidSynth, FFmpeg). Runs on any $5 VPS. | **零 GPU** — 所有运算纯 CPU 运行（music21、LilyPond、FluidSynth、FFmpeg），任何低配服务器都行 |
| 2 | **AI-Agent Native** — Scripts output JSON, designed for tool-calling LLMs. SKILL.md follows standard AI agent conventions. install.sh auto-detects your agent environment. | **智能体原生** — 脚本输出 JSON，专为调用工具的 LLM 设计。SKILL.md 遵循标准 AI 智能体规范，install.sh 自动检测你的智能体环境 |
| 3 | **Conversational Workflow** — Agent detects music intent naturally, asks "want me to write a song?", then guides through the full pipeline in dialogue. No hardcoded keywords. | **对话式工作流** — 智能体自然识别音乐意图，主动询问「需要帮你写成歌吗？」，全程对话引导，不绑死关键词 |
| 4 | **Export-Anywhere** — Score PDF, MIDI, MusicXML, LilyPond source, WAV, and MP3 — use any or all. | **随处导出** — PDF 乐谱、MIDI、MusicXML、LilyPond 源码、WAV 无损、MP3 压缩，随你便 |
| 5 | **Production-Quality Scores** — LilyPond engraving meets professional publishing standards with proper beaming, slurs, dynamics. | **出版级乐谱** — LilyPond 排版达到专业出版标准，连音线、力度记号一应俱全 |
| 6 | **Reference-Driven Creation** — Fetches real songs from Chinese music platforms for style/lyric reference. | **参考驱动创作** — 从中国音乐平台搜索真实歌曲作为风格/歌词参考 |
| 7 | **Bilingual Documentation** — Full EN+CN README, inline code comments in Chinese. English-first code, Chinese-first user interaction. | **双语文档** — 完整中英文 README，代码注释中文，用户交互中文优先 |

---

## 🔧 Compatibility / 兼容性

| Environment / 环境 | Status / 状态 | Notes / 说明 |
|-------------------|---------------|-------------|
| **Hermes Agent** | ✅ 原生支持 | `skill_view('music-creation')` 自动加载 |
| **Claude Code** | ✅ 直接复制 | 复制 SKILL.md 到 `~/.claude/skills/` |
| **Cursor / Codex** | ✅ 项目引用 | 在项目文档中引用 README 即可 |
| **纯 LLM 聊天** | ✅ 粘贴可用 | 把 README 丢进系统提示词，大模型就能理解 |
| **Linux** | ✅ 完整支持 | Ubuntu/Debian 全量测试通过 |
| **macOS** | ⚠️ 部分支持 | brew 安装，部分系统工具可能有差异 |
| **GPU** | ❌ 不需要 | 纯 CPU 运行 |
| **内存** | ~200MB | 运行时内存占用 |
| **磁盘** | ~425MB | 全部依赖安装后总大小 |

---

## 🚀 Quick Start / 快速开始

### One-Click Install / 一键安装

```bash
git clone https://github.com/mage0535/music-creation-engine.git
cd music-creation-engine
chmod +x install.sh
./install.sh
```

**What install.sh does / install.sh 做的事情:**
1. Detect OS and architecture / 检测操作系统和架构
2. Install Python packages (music21, abjad) / 安装 Python 依赖
3. Install system tools (lilypond, fluidsynth, fluid-soundfont-gm) / 安装系统工具
4. Install Meting-Agent MCP (optional, for music search) / 安装音乐搜索 MCP（可选）
5. Install SKILL.md to agent skill directory (auto-detects Hermes/Claude) / 安装技能文件到智能体技能目录
6. Verify all components / 验证所有组件
7. Show quick test command / 显示快速测试命令

### Manual Install / 手动安装

**EN:**
```bash
# Python packages
pip install music21 abjad

# System tools
sudo apt install lilypond fluidsynth fluid-soundfont-gm

# Optional: music search MCP
npm install -g @eldment/meting-agent
```

**CN:**
```bash
# Python 包
pip install music21 abjad

# 系统工具
sudo apt install lilypond fluidsynth fluid-soundfont-gm

# 可选：音乐搜索 MCP
npm install -g @eldment/meting-agent
```

### Verify Installation / 验证安装

```bash
python3 -c "import music21; print(f'music21 {music21.__version__}')"
python3 -c "import abjad; print(f'abjad {abjad.__version__}')"
lilypond --version | head -1
fluidsynth --version | head -1
ffmpeg -version | head -1
```

**Expected output / 期望输出:**
```
music21 10.3.0
abjad 3.31
GNU LilyPond 2.24.3
FluidSynth runtime version 2.3.4
ffmpeg version 6.1.1
```

---

## 🎮 Usage / 使用方法

### For AI Coding Agents / 给 AI 编码助手

**EN:** Tell your AI assistant:
> "I have the music-creation-engine installed. Load the SKILL.md from `~/.your-agent/skills/music-creation/SKILL.md`"

The agent will then detect music-related intents in your conversation and proactively offer: "Want me to help turn this into a song?"

**CN:** 告诉你的 AI 助手：
> "我已经安装了 music-creation-engine，从 `~/.your-agent/skills/music-creation/SKILL.md` 加载 skill"

AI 助手之后会自动识别你聊天中的音乐创作意图，主动问：「需要帮你写成歌吗？」

### Direct Script Usage / 直接脚本调用

**Generate Sheet Music / 生成乐谱:**

```bash
python3 scripts/sheet_music_generator.py \
  --lyrics "清晨的阳光洒落窗台\n微风带走了昨夜的尘埃" \
  --key C --bpm 120 \
  --instruments piano,vocals,guitar,bass \
  --style pop \
  --output /tmp/my_song \
  --mode all --json
```

**Arguments / 参数说明:**

| Flag / 参数 | Default / 默认值 | Description / 说明 |
|-------------|------------------|-------------------|
| `--lyrics` | `""` | 歌词文本（`\n` 换行）|
| `--lyrics-file` | — | 从文件读取歌词 |
| `--key` | `C` | 调性（C, Dm, G, Am 等）|
| `--bpm` | `120` | 速度 |
| `--time-signature` | `4/4` | 拍号 |
| `--instruments` | `piano,vocals` | 乐器列表（逗号分隔）|
| `--style` | `pop` | 风格（pop/rock/ballad/jazz/folk）|
| `--output` | `./output/music_score` | 输出文件基础路径 |
| `--mode` | `all` | 输出模式（all/pdf/midi/xml/ly）|

**Supported Instruments / 支持乐器:**
`piano`, `vocals`, `guitar`, `bass`, `drums`, `strings`, `flute`, `sax`, `trumpet`, `synth`

**Render Demo Audio / 渲染试听音频:**

```bash
python3 scripts/demo_renderer.py \
  --midi /tmp/my_song.mid \
  --output /tmp/my_song_demo \
  --format mp3 --json
```

**Arguments / 参数说明:**

| Flag / 参数 | Default / 默认值 | Description / 说明 |
|-------------|------------------|-------------------|
| `--midi` | 必填 | 输入 MIDI 文件 |
| `--soundfont` | 自动检测 | SoundFont 文件 |
| `--output` | `./demo` | 输出基础路径 |
| `--gain` | `0.5` | 音量（0.0-1.0）|
| `--sample-rate` | `44100` | 采样率 |
| `--format` | `mp3` | 输出格式（mp3/wav/ogg/all）|

**JSON Output / JSON 输出示例:**

```json
{
  "midi": "/tmp/music_test/morning_light.mid",
  "pdf": "/tmp/music_test/morning_light.pdf",
  "musicxml": "/tmp/music_test/morning_light.musicxml",
  "lilypond": "/tmp/music_test/morning_light.ly",
  "parts": [
    {"instrument": "piano", "measures": 16},
    {"instrument": "vocals", "measures": 16}
  ]
}
```

---

## 📦 Dependencies / 依赖清单

| Package / 包 | Version / 版本 | Size / 大小 | Purpose / 用途 |
|-------------|----------------|-------------|----------------|
| music21 | 10.3.0+ | ~50MB | 乐理引擎（分析、调性、和弦、声部）/ Music theory engine |
| abjad | 3.31+ | ~5MB | LilyPond Python API / 乐谱排版接口 |
| lilypond | 2.24+ | ~200MB | 专业乐谱排版系统 / Professional music engraving |
| fluidsynth | 2.3+ | ~5MB | MIDI→WAV 音频渲染 / MIDI audio rendering |
| fluid-soundfont-gm | — | ~140MB | GM 标准音色库 / General MIDI soundfont |
| ffmpeg | 6.x+ | ~10MB | WAV→MP3 编码 / Audio encoding |
| @eldment/meting-agent | latest | ~15MB | 音乐搜索 MCP（可选）/ Music search MCP (optional) |

---

## 🏗 Architecture / 架构

### Full Pipeline / 完整管线

```
EN: Your Idea → Agent asks → Multi-Agent Lyrics → Sheet Music → Demo MP3 → Evaluate → Publish
CN: 你的灵感 → AI主动询问 → 多Agent协作作词 → 乐谱生成 → Demo试听 → 质量评估 → 发布
```

```
User / 用户 (聊天对话)
    │
    ├── 🔍 Intent Detection / 意图识别 (natural language, no keywords)
    │   └── "Want me to write a song? / 需要帮你写成歌吗？"
    │
    ├── 🎤 Phase 1: Multi-Agent Lyrics / 多智能体作词
    │   ├── Lyricist Agent / 词作家
    │   ├── Composer Agent / 曲作者
    │   └── Producer Agent / 音乐制作人
    │   └── ← User iterates / 用户反复修改 → 确认 |
    │
    ├── 🎼 Phase 2: Sheet Music / 乐谱生成
    │   ├── music21 → chord/key/voice analysis / 和弦/调性/声部分析
    │   └── Abjad → LilyPond → PDF/MIDI/XML
    │
    ├── 🎧 Phase 3: Demo Audio / Demo 音频
    │   ├── FluidSynth: MIDI→WAV (GM soundfont / 标准音色库)
    │   └── FFmpeg: WAV→MP3 (ready to play / 直接试听)
    │
    ├── 📊 Phase 4: Quality Eval / 质量评估
    │   └── 4 parallel agents / 4个并行Agent（旋律/节奏/情感/结构）
    │
    └── 🌐 Phase 5: Publish / 发布（optional / 可选）
        └── AiToEarn MCP → TikTok/YouTube/Twitter/网易云等
```

### Tool Chain / 工具链联动

```
┌───────────────────────────────────────────────────────────────┐
│                    Music Creation Engine                       │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  SKILL.md ─── orchestrator / 主编排层                          │
│    │                                                          │
│    ├── delegate_task (multi-agent lyrics / 多Agent作词)        │
│    ├── sheet_music_generator.py                               │
│    │   ├── music21 (theory/乐理, chords/和弦, key/调式)       │
│    │   └── abjad → lilypond (PDF engraving / PDF排版)         │
│    ├── demo_renderer.py                                       │
│    │   ├── fluidsynth (MIDI→WAV)                              │
│    │   └── ffmpeg (WAV→MP3)                                   │
│    ├── meting-agent MCP (reference songs / 参考歌曲搜索)       │
│    └── aitoearn MCP (publish / 多平台发布)                     │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## 🔬 Test / 测试验证

**EN:** Run the full pipeline with a test song to verify everything works.

**CN:** 用一首测试歌曲跑通全链路，验证所有组件正常。

```bash
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

**Expected Output / 期望输出:**

| File / 文件 | Size / 大小 | Description / 说明 |
|------------|------------|-------------------|
| test_song.pdf | ~229KB | 总谱 PDF / Full score PDF |
| test_song.mid | ~1.8KB | MIDI 播放文件 / MIDI playback |
| test_song.musicxml | ~80KB | 通用乐谱格式 / Universal score format |
| test_song.ly | ~4.4KB | LilyPond 源码 / LilyPond source |
| test_demo.mp3 | ~462KB | 🎧 试听 MP3 / Listen on any device |

---

## 📋 Project Structure / 项目结构

```
music-creation-engine/
├── README.md                     # 中英双语说明文档 / Bilingual documentation
├── SKILL.md                      # AI 智能体技能定义 / AI agent skill definition
├── install.sh                    # 一键安装脚本 / One-click installer
├── .gitignore
├── scripts/
│   ├── sheet_music_generator.py  # 歌词→乐谱 / Lyrics → Score (MIDI/PDF/XML)
│   └── demo_renderer.py          # MIDI→FluidSynth→MP3 / Audio rendering
└── references/
    └── install-guide.md          # 详细安装指南 / Detailed install guide
```

---

## 🔧 Configuration for AI Agents / 智能体配置

### Hermes Agent

**EN:** Skill auto-detects music intent in conversation. Alternatively register scripts in tool manifest:

**CN:** 技能自动识别对话中的音乐意图。也可在工具清单中注册脚本：

```yaml
# ~/.hermes/tool_manifest.yaml
music_creation:
  status: active
  skill: music-creation
  scripts:
    - scripts/sheet_music_generator.py
    - scripts/demo_renderer.py
```

**MCP Registration / MCP 注册:**

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

### Claude Code / Cursor / Codex

```bash
# Copy to skills directory / 复制到技能目录
cp SKILL.md ~/.claude/skills/music-creation/
cp -r scripts/ ~/.claude/skills/music-creation/scripts/
```

### Any LLM Chat / 任何 LLM 聊天

**EN:** Copy the contents of this README and SKILL.md into the system prompt. The LLM will understand the full pipeline.

**CN:** 把 README 和 SKILL.md 的内容复制到系统提示词中，大模型就能理解完整管线。

---

## 🐛 Troubleshooting / 故障排查

| Problem / 问题 | Cause / 原因 | Solution / 解决 |
|---------------|-------------|----------------|
| `ModuleNotFoundError: No module named 'music21'` | Python 包未安装 | `pip install music21` |
| `lilypond: command not found` | 系统工具缺失 | `apt install lilypond`（或 brew）|
| `fluidsynth: command not found` | FluidSynth 缺失 | `apt install fluidsynth fluid-soundfont-gm` |
| 鼓声部报错 | music21 API 兼容性 | 确保使用 `note.Unpitched(pitch_number)` |
| PDF 输出为空 | LilyPond 排版问题 | 检查 `lilypond --version` ≥ 2.24 |
| MP3 文件生成为 0KB | FFmpeg 编码问题 | 确认 `ffmpeg -version` 正常 |
| Meting-Agent 不响应 | MCP 未连接 | 确认 `npm list -g @eldment/meting-agent` |

---

## 🤝 Acknowledgments / 致谢

**EN:** This project builds upon the following open-source projects and communities. We are deeply grateful for their work.

**CN:** 本项目基于以下开源项目和社区构建。衷心感谢他们的贡献。

| Project / 项目 | License / 许可 | Role in Engine / 在本引擎中的角色 |
|----------------|---------------|-----------------------------------|
| **[music21](https://github.com/cuthbertLab/music21)** | MIT | **乐理核心引擎** — 和弦分析、调性检测、声部操作、多种格式读写。MIT 出品。_The core engine for chord analysis, key detection, and score manipulation._ |
| **[Abjad](https://github.com/Abjad/abjad)** | MIT | **LilyPond 排版接口** — 用 Python 构建出版级乐谱文件。_Python API for building LilyPond score files._ |
| **[LilyPond](https://lilypond.org)** | GPL | **乐谱排版系统** — 世界顶级的音乐排版引擎，渲染专业 PDF 乐谱。_The world's finest music engraving system._ |
| **[FluidSynth](https://github.com/FluidSynth/fluidsynth)** | LGPL | **音频合成器** — 将 MIDI 通过 GM 标准音色库渲染为 WAV 音频。_Real-time software synthesizer for MIDI rendering._ |
| **[Meting-Agent](https://github.com/ELDment/Meting-Agent)** | MIT | **音乐搜索 MCP** — 搜索网易云/QQ/酷狗/酷我的歌曲和歌词。_MCP server for Chinese music platforms._ |
| **[agency-agents-zh](https://github.com/jnMetaCode/agency-agents-zh)** | MIT | **多角色灵感** — 215 个中文 AI 专家角色定义，启发了我们的多 Agent 作词协作设计。_Inspired multi-agent lyric workflow pattern._ |
| **[ATRI_AGENT](https://github.com/Tz-WIND/ATRI_AGENT)** | MIT | **音乐工作站参考** — music21+DAW 集成模式的参考项目。_Demonstrated music21+DAW integration._ |
| **[FFmpeg](https://ffmpeg.org)** | LGPL | **音频编码层** — WAV 到 MP3/OGG 的格式转换。_Audio encoding and format conversion._ |
| **[music-master](https://github.com/Muyu1uz/music-master)** | — | **多Agent编排参考** — LangGraph 多智能体音乐创作流水线设计。_Multi-agent music creation pipeline design._ |
| **[Hermes Agent](https://github.com/NousResearch/hermes-agent)** | Apache 2.0 | **运行框架** — 多 Agent 协作和 skill 编排的基础框架。_The agent framework powering multi-agent orchestration._ |

---

## 📄 License / 许可证

**EN:** MIT © 2026 — Free to use, modify, share, and deploy with any AI agent, commercial or personal.

**CN:** MIT 许可 — 可自由使用、修改、分享和部署于任何 AI 智能体，商用或个人用途均可。

---

## 🔗 Links / 链接

- **GitHub**: https://github.com/mage0535/music-creation-engine
- **Report Issues / 反馈问题**: https://github.com/mage0535/music-creation-engine/issues
- **Release / 发行版**: https://github.com/mage0535/music-creation-engine/releases/tag/v1.0.0

**Topics / 标签:** `music-creation` `ai-composer` `sheet-music` `lilypond` `music21` `midi` `audio-demo` `fluidsynth` `hermes-agent` `claude-code` `ai-agent` `music-ai` `multilingual` `mcp-server` `zero-gpu` `open-source`
