---
name: music-creation
description: 全流程AI音乐创作引擎 — 作词/作曲/总谱分谱/Demo音频/质量评估/发布的一站式聊天式创作体验
version: 1.0.0
tags: [music, composition, lyrics, sheet-music, audio, production]
load_condition: "识别到用户有音乐相关的创作意图时主动询问是否启动。包括但不限于：想写歌、有段旋律/歌词灵感、需要谱曲、想要乐谱、想编曲、需要Demo、想发布音乐作品等场景"
---

# 🎵 音乐创作引擎 (Music Creation Engine)

## 总览

通过聊天对话方式，引导用户完成音乐创作全流程：

```
用户灵感 → 多Agent作词 → 用户确认 → 作曲规划 → 总谱分谱PDF → Demo MP3 → 质量评估 → 发布
```

## 核心管线

### 阶段 1: 灵感勘探与需求采集

检测到用户有音乐创作意图并确认后，通过对话了解：

- **主题/灵感** — 什么故事？什么情绪？
- **风格偏好** — 流行/摇滚/Ballad/Jazz/Folk 等
- **演出形式** — 独唱/乐队/合唱/器乐
- **演出场合** — 演出/直播/个人欣赏
- **乐器配置** — 钢琴/吉他/贝斯/鼓/弦乐/管乐
- **歌手/乐手风格** — 参考歌手或乐队

### 阶段 2: 多Agent 作词协作

使用 `delegate_task` 并行启动以下角色进行作词协作：

| Agent | 职责 |
|-------|------|
| 🎤 **词作家 / Lyricist** | 创作歌词，注意押韵/节奏/段落结构 / Creates lyrics with rhyme, rhythm, structure |
| 🎸 **曲作者 / Composer** | 从旋律角度评估歌词的可唱性和音乐流畅度 / Evaluates singability & melodic flow |
| 🎛️ **音乐制作人 / Producer** | 整体结构评估（Intro/Verse/Chorus/Bridge/Outro）/ Assesses arrangement & structure |

**工作流 / Workflow**：
1. **识别意图 / Detect intent** — 用户聊到音乐相关话题时，主动问「需要帮你写成歌吗？」/ Ask "Want me to write a song?"
2. **需求采集 / Gather requirements** — 如果用户确认，了解灵感/风格/乐器/场合等 / Confirm idea, style, instruments, occasion
3. 并行启动 3 个 Agent 各自创作歌词/评估 / Spawn 3 parallel agents for lyrics
4. 汇总展示给用户 / Show merged results to user
5. 用户提出修改意见 / User gives feedback
6. 重新 spawn Agent 修改 / Re-spawn agents with revisions
7. 用户确认最终版 / User confirms final version

### 阶段 3: 作曲规划

用户确认歌词后，根据聊天的需求决定音乐参数：

- **调性**: 根据情绪决定（欢快=C/G/D，悲伤=Am/Em/Dm）
- **BPM**: 根据风格决定（Ballad=60-80, Pop=100-130, Rock=120-160）
- **拍号**: 默认 4/4
- **和弦进行**: 根据风格自动选择模板
- **编曲复杂度**: minimal / balanced / rich

### 阶段 4: 总谱与分谱生成

调用 `scripts/sheet_music_generator.py`：

```bash
python3 ~/.your-agent/skills/music-creation/scripts/sheet_music_generator.py \
  --lyrics "歌词内容" \
  --key C --bpm 120 \
  --time-signature 4/4 \
  --instruments piano,vocals,guitar,bass,drums \
  --style pop \
  --output /tmp/music_output/song_name \
  --mode all --json
```

**输出文件**：
- `output.mid` — MIDI 试听文件
- `output.pdf` — 总谱 PDF（LilyPond 排版）
- `output.musicxml` — MusicXML 乐谱数据
- `output.ly` — LilyPond 源码

**分谱说明**：总谱 PDF 中包含所有声部。如需单独分谱，使用 music21 提取单一 Part 后再输出。

### 阶段 5: Demo 音频渲染

**MP3 是核心交付格式**。用户试听只发 MP3（体积小、手机直接播放），WAV 做备份留存。

调用 `scripts/demo_renderer.py`：

```bash
python3 ~/.your-agent/skills/music-creation/scripts/demo_renderer.py \
  --midi /tmp/music_output/song_name.mid \
  --output /tmp/music_output/song_name_demo \
  --format mp3 --json
```

**输出文件**：
- `demo.mp3` — **🎧 主交付件，直接发送给用户**（~400KB/分钟，Telegram 直接播放）
- `demo.wav` — 原始无损（保留以供后续处理）

**发送方式**：在回复中包含 `MEDIA:/tmp/music_output/song_name_demo.mp3`，Telegram 会自动以内联音频形式播放。

**音色说明**：
- 使用 FluidSynth + FluidR3_GM SoundFont（GM 标准音色库）
- 音色质量相当于 2000 年代合成器，适合 Demo 试听
- 如需更高质量，后续可接入 REAPER + VST 音源

### 阶段 6: 质量评估

使用 `delegate_task` 启动多个评估 Agent 对生成的音乐进行评估：

| Agent | 评估维度 |
|-------|---------|
| 🎼 **旋律评委** | 旋律流畅度、动机发展、记忆点 |
| 🥁 **节奏评委** | 节奏感、律动、节奏变化 |
| 🎭 **情感评委** | 情感传达、氛围匹配度 |
| 📐 **结构评委** | 整体结构合理性、段落衔接 |

**评估输出**：每个维度打分（1-10）+ 文字评价

### 阶段 7: 发布

通过 AiToEarn MCP 发布到音乐/视频平台。发布前提取：

- **封面图**: 使用 Hermes `image_generate` 生成
- **标题/描述**: 根据歌曲信息自动生成
- **标签**: 根据风格/情绪自动生成

### 阶段 8: 录播分析（附加功能）

用户提供录制好的音频文件后：

1. **分析工具**: `music21` 分析乐谱结构、调性、和弦
2. **优化建议**: 多 Agent 从编曲/混音/演奏角度给出建议
3. **自动处理**: 通过 REAPER MCP (如果安装) 或 FFmpeg 进行音频优化

---

## 可用工具/脚本速查

| 工具 | 路径 | 功能 |
|------|------|------|
| 乐谱生成器 | `scripts/sheet_music_generator.py` | 歌词→总谱/分谱 PDF/MIDI/XML |
| Demo 渲染器 | `scripts/demo_renderer.py` | MIDI→FluidSynth→MP3/WAV |
| Meting-Agent MCP | (通过 MCP 调用) | 网易云/QQ/酷狗/酷我音乐搜索参考 |
| AiToEarn MCP | (通过 MCP 调用) | 发布到各音乐/视频平台 |
| agency-agents-zh (可选) | `git clone https://github.com/jnMetaCode/agency-agents-zh.git` | 215 音乐角色 prompt 未安装，需时才装 |
| 架构报告 | `references/architecture-report.md` | 20 项目评估与设计决策 |

---

## 输出文件规范

输出目录: `/tmp/music_output/{歌曲名}/`

```
/tmp/music_output/
├── {song_name}/
│   ├── lyrics.txt              # 歌词最终版
│   ├── song_config.json        # 歌曲配置文件（调性/BPM/乐器/风格）
│   ├── score.pdf               # 总谱 PDF
│   ├── score.mid               # MIDI 文件
│   ├── score.musicxml          # MusicXML 乐谱
│   ├── score.ly                # LilyPond 源文件
│   ├── demo.wav                # 原始无损音频
│   ├── demo.mp3                # MP3 试听文件
│   ├── parts/
│   │   ├── piano.pdf           # 钢琴分谱
│   │   ├── vocals.pdf          # 人声分谱
│   │   ├── guitar.pdf          # 吉他分谱
│   │   └── ...
│   ├── evaluation.json         # 质量评估结果
│   └── cover.png               # 封面图（发布用）
```

---

## 多角色协作（作词阶段具体实现）

识别到用户有音乐创作意图并确认后，按以下流程执行：

### Step 1: 识别意图 + 主动询问
当你在聊天的任何场景（不只是"我想写首歌"）中提到：
- "这段旋律/歌词怎么样"
- "我想写个/首/段歌/曲/音乐"
- "帮我谱个曲"
- "我需要一首X风格的歌曲"
- "有个灵感/想法/主题想写成歌"
- "帮我编个曲"

主动问一句：「需要帮你写成歌吗？我可以从作词到Demo一条龙。」
如果用户确认，进入 Step 2。

### Step 2: 需求采集对话

### Step 3: Spawn 作词 Agent 并行工作
```
delegate_task(tasks=[
  {
    goal: "你是词作家，根据用户灵感创作完整歌词",
    context: "用户灵感: ...\n风格: ...\n创作方向: ..."
  },
  {
    goal: "你是曲作者，从旋律可唱性角度评估歌词方向",
    context: "..."
  },
  {
    goal: "你是音乐制作人，从结构和市场角度评估",
    context: "..."
  }
])
```

### Step 4: 展示结果 → 用户修改 → 重复
收集三个 Agent 输出 → 展示给用户 → 用户提出修改意见 → 重新 spawn → 确认最终版

### Step 5: 确认歌词后执行乐谱生成
调用 sheet_music_generator.py → 展示生成的 PDF/MIDI

### Step 6: 用户确认乐谱后渲染 Demo
调用 demo_renderer.py → 发送 MP3 给用户试听

---

## 当前限制与未来扩展

| 限制 | 说明 | 未来方案 |
|------|------|---------|
| 旋律人工感 | 当前是基于音乐模板的算法生成，非 AI 作曲 | 接入 Suno/ACEStep API 或本地 YuE 模型（需 GPU）|
| 音色一般 | FluidSynth GM 音色库，2000 年代合成质量 | 安装 REAPER + VST 音源 |
| 无歌声音轨 | 仅乐器 Demo，没有人声 | kokoro TTS 哼唱 / Suno API |
| 简谱有限 | 当前主力五线谱 | 增加简谱输出模块（music21 数字→PIL 渲染）|

---

## 链接 / Links

- **GitHub**: https://github.com/mage0535/music-creation-engine
- **Issues**: https://github.com/mage0535/music-creation-engine/issues
- **Install**: `git clone https://github.com/mage0535/music-creation-engine.git && cd music-creation-engine && chmod +x install.sh && ./install.sh`
