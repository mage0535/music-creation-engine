# 🎵 AI 音乐创作引擎 — 可行性报告与架构方案

## 一、环境约束

| 资源 | 限制 |
|------|------|
| GPU | ❌ 无 (纯 CPU) |
| RAM | 7.8GB (可用 ~3.6GB) |
| 磁盘 | 88GB 总 / 22GB 可用 |
| Python | 3.12.3 |
| OS | Ubuntu Linux x86_64 |

**核心策略**：所有 AI 推理走 API（LLM 作曲决策），本地只做 MIDI/乐谱生成和音频渲染（CPU 可承受）。

---

## 二、你给的 20 个项目的评估结果

### ✅ 可直接集成的（无需 GPU，零摩擦）

| 项目 | ⭐ | 核心价值 |
|------|---|---------|
| **ELDment/Meting-Agent** | 88 | **MCP 音乐平台代理** — 8 个一致接口覆盖网易云/QQ/酷狗/酷我。搜索歌曲、获取歌词、播放链接、专辑/歌手信息。**直接作为 MCP server 注册 config.yaml 即可用** |
| **jnMetaCode/agency-agents-zh** | 13.4k | **215 个专家角色库** — 含音乐制作人、作词人、作曲、编曲等角色 prompt，可直接用于多 Agent 创作编排 |
| **titanwings/colleague-skill** | 10k | **人格蒸馏工具** — 将任何人（音乐人、歌手）的聊天记录/作品提炼为 AI 人格 |
| **Qing-Iwannago/sound_weaver** | ⭐少 | **文字→MIDI 创作** — Spring Boot + LangChain4j，LLM 生成音乐参数 → Java MIDI API 输出 .mid 文件。**其乐理 RAG 知识库可用** |
| **Muyu1uz/music-master** | ⭐少 | **多 Agent 音乐创作编排**（LangGraph + DeepAgents）— 作词→作曲→编曲→封面→prompt 流水线 |
| **Hang-666-star/melt-agents-to-evaluate-music** | ⭐少 | **多 Agent 音乐质量评估** — 6 个专家 Agent（旋律、节奏、情感、创新等）对作品打分讨论 |
| **DawnnnHuang/Audio-Ops-Agents** | 1 | **音頻运营 Prompt 方法论** — 把感性需求翻译为音乐工程规格的结构化模板 |
| **FF0214/ai-music-studio** | 0 | **多 Agent 音乐工业化**（Suno API）— 热点→歌词→音乐→审核全自动 |
| **Tz-WIND/ATRI_AGENT** | 13 | **本地音乐工作站** — Python + music21 + Rust 音频引擎。支持 MIDI 生成、修改、检查可演奏性、导出。**核心组件：音乐理论库 + 音频引擎** |

### 💡 参考设计可复用（不直接装，但模式可取）

| 项目 | 可取设计 |
|------|---------|
| **yujansen/Music_Agent** | 歌词 → LLM 规划 → 配乐的 Agent 工作流设计；编曲复杂度三档（minimal/balanced/rich）；MusicXML 乐谱输出 |
| **hellen9527/music_agent** | Hermes Agent 上的意图路由设计（music_router 模式）|
| **anbeime/skill** | 182 个官方技能索引，61 个中文技能可直接补充到我们的技能库 |
| **GuJiV/TikTok-Agent-Script-Studio** | 多阶段流水线 + 合规审查设计模式 |
| **XUTENGXIANG/ai-music-creator** | 太少（演示级），不采用 |

### ❌ 不适合集成（需要 GPU 或架构不兼容）

| 项目 | 原因 |
|------|------|
| **mindforge-x/musio** | Java 21 + Spring Boot 运行栈与 Hermes Python 栈不兼容，仅 QQ 音乐源 |
| **hgsanyang/SoulTuner-Agent** | ✅ GPU 必需（M2D-CLAP + OMAR-RQ 模型推理），Docker Compose 需 GPU |
| **shaozheng0503/aimv-studio** | ✅ GPU 必需（ACEStep / Wan2.2 本地模型），CrewAI 编排但依赖本地生成 |
| **treesan/vcutclaw** | ✅ GPU 强烈推荐（torch 视频解码 + ASR）|
| **YoungB1oodXD/music-agent** | 含 torch 依赖（可 CPU 跑但需大量磁盘装 FMA 数据集 106,573 首歌）|
| **elfbobo/yinova** | Hermes 分支，核心能力已被我们覆盖 |

---

## 三、你必须安装的核心工具（不在你给的列表里）

| 工具 | 类型 | 作用 | 安装 |
|------|------|------|------|
| **music21** | Python 库 | ⭐ **音乐理论引擎** — 读/写/操作乐谱（MusicXML/MIDI/LilyPond）、和弦分析、调性检测、转调、声部编排。MIT 协议，MIT 出品 | `pip install music21` |
| **Abjad** | Python 库 | **乐谱生成引擎** — Python API 构建 LilyPond 文件，从音符到总谱 | `pip install abjad` |
| **LilyPond** | 系统工具 | **专业乐谱排版** — 出版级简谱/五线谱 PDF 输出 | `apt install lilypond` |
| **REAPER MCP** | MCP 服务 | **58 个 DAW 控制工具** — 项目管理、MIDI 作曲、FX 混音、母带处理 | 需安装 REAPER + [bonfire-audio/reaper-mcp](https://github.com/bonfire-audio/reaper-mcp) |
| **ACESStep** (可选) | API | AI 音乐生成 API（歌词→歌曲），有免费额度 | 注册 API |
| **kokoro** | Python 库 | **TTS 人声 Demo** — 82 种语言，CPU 可跑，用于 demo 人声合成 | `pip install kokoro` ✅ 已装 |
| **Suno API** (可选) | API | 歌词→完整歌曲（带人声）的外部生成服务 | 注册账号 |
| **AiToEarn MCP** | ✅ 已装 | 发布到各大音乐/视频平台 | ✅ 已配置 |

---

## 四、完整工作流架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                         🎵 音乐创作引擎                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  用户聊天输入（灵感/想法/意图）                                       │
│       │                                                              │
│       ▼                                                              │
│  ┌─────────────┐                                                     │
│  │  1. 灵感勘探  │ ◄── agency-agents-zh 音乐角色 × colleague-skill   │
│  │   (多Agent)  │     蒸馏的音乐人人格                                │
│  └──────┬──────┘                                                     │
│         │ 歌词想法                                                    │
│         ▼                                                            │
│  ┌─────────────┐                                                     │
│  │  2. 作词     │ ◄── 多 Agent 协作（作词人/诗人/音乐制作人）         │
│  │   (迭代)     │     用户审核调整 → 确认最终歌词                     │
│  └──────┬──────┘                                                     │
│         │ 确认歌词                                                    │
│         ▼                                                            │
│  ┌─────────────┐                                                     │
│  │  3. 作曲规划  │ ◄── LLM (用户指定风格/乐器/演出形式/场合)          │
│  │             │     music21 乐理分析（调性/和声/节奏）              │
│  └──────┬──────┘                                                     │
│         │ 音乐参数 (BPM/调式/和弦走向/配器)                           │
│         ▼                                                            │
│  ┌──────────────────────────────────────────────┐                    │
│  │  4. 乐谱生成（核心环节）                       │                    │
│  │                                              │                    │
│  │  a) 总谱生成 ← Abjad + music21               │                    │
│  │     - 按乐器/声部分配声部                      │                    │
│  │     - music21 做声部叠加/移调/和声检查          │                    │
│  │     - Abjad 构建 LilyPond 源码                 │                    │
│  │                                              │                    │
│  │  b) 分乐器谱 ← Abjad 逐声部导出               │                    │
│  │     - 钢琴谱/吉他谱/贝斯谱/鼓谱/主旋律谱        │                    │
│  │     - 支持简谱和五线谱两种格式                  │                    │
│  │                                              │                    │
│  │  c) 用户确认 ← 输出 PDF/MusicXML/简谱图片       │                    │
│  │     - 用户可逐页审阅，沟通修改                  │                    │
│  └──────────────────────────────────────────────┘                    │
│         │ 确认乐谱                                                    │
│         ▼                                                            │
│  ┌──────────────────────────────────────────────┐                    │
│  │  5. Demo 音频渲染                              │                    │
│  │                                              │                    │
│  │  方案A: MIDI → 软件音源渲染（via REAPER MCP） │                    │
│  │   - MIDI 文件导入 REAPER                      │                    │
│  │   - reaper-mcp 调用 VST 音源                   │                    │
│  │   - 混音/母带处理                              │                    │
│  │                                              │                    │
│  │  方案B: MIDI → FluidSynth 软件合成（无 REAPER）│                    │
│  │   - timidity++ / fluidsynth 直接渲染 MIDI     │                    │
│  │   - 选择 SoundFont 音色库                     │                    │
│  │                                              │                    │
│  │  方案C: API 生成（有歌词时）                    │                    │
│  │   - Suno API / ACEStep API 傳歌词+参数生成      │                    │
│  │   - 人声+伴奏完整歌曲                          │                    │
│  │                                              │                    │
│  │  人声 Demo: kokoro TTS 合成歌词朗读/哼唱        │                    │
│  └──────────────────────────────────────────────┘                    │
│         │ Demo 音频文件                                              │
│         ▼                                                            │
│  ┌─────────────┐                                                     │
│  │  6. 质量评估  │ ◄── melt-agents-to-evaluate-music 6 专家 Agent   │
│  │             │     旋律/节奏/结构/情感/创新/可解释性评分            │
│  └──────┬──────┘                                                     │
│         │ 评估报告                                                    │
│         ▼                                                            │
│  ┌─────────────┐                                                     │
│  │  7. 发布     │ ◄── AiToEarn MCP（已配）                          │
│  │             │     网易云音乐/QQ音乐/抖音/YouTube/B站/TikTok等     │
│  └─────────────┘                                                     │
│                                                                      │
│  ┌─────────────────────┐                                            │
│  │  8. 录播分析        │ ← 用户录制音频文件 (.wav/.mp3)              │
│  │                     │    music21 音符识别/调性/节奏分析            │
│  │                     │    多 Agent 给出优化建议                     │
│  │                     │    自动混音/母带处理 (via reaper-mcp)       │
│  └─────────────────────┘                                            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 五、工具间的调用联动图

```
用户 (Telegram/CLI)
    │
    ▼
Hermes Agent (主编排层)
    │
    ├── 作词阶段
    │   ├──→ agency-agents-zh (加载「作词人」「作曲人」角色)
    │   ├──→ colleague-skill (必要时蒸馏特定风格)
    │   └──→ 用户对话迭代
    │
    ├── 乐理计算/乐谱生成
    │   ├──→ music21 (调性/和弦/声部/分析/移调)
    │   ├──→ Abjad → LilyPond (总谱/分谱 PDF 输出)
    │   └──→ Meting-Agent MCP (搜索参考歌曲的风格/歌词/和弦)
    │
    ├── 音频渲染
    │   ├──→ REAPER MCP (如果安装: MIDI→VST音源→混音→导出)
    │   ├──→ fluidsynth (备选: MIDI→SoundFont→WAV)
    │   └──→ kokoro TTS (人声 Demo)
    │
    ├── 质量评估
    │   └──→ melt-agents-to-evaluate-music (6 Agent 评分)
    │
    ├── 发布
    │   └──→ AiToEarn MCP (抖音/YouTube/网易云/QQ音乐等)
    │
    ├── 录播分析
    │   ├──→ music21 (音符/节奏/结构分析)
    │   └──→ REAPER MCP (混音调整)
    │
    └── 工具链管理
        └──→ anbeime/skill (技能更新源)
```

---

## 六、需要安装的软件包清单

### 第一阶段：核心 — 乐理/乐谱（必须）

```bash
# Python 乐理引擎
pip install music21 abjad

# 乐谱排版
apt install lilypond

# SoundFont 合成器（备选渲染方案）
apt install fluidsynth fluid-soundfont-gm
```

### 第二阶段：音频工作站（推荐，重大能力提升）

```bash
# REAPER DAW — 从官网下载 Linux 版
# https://www.reaper.fm/download.php
# 安装后注册 reaper-mcp MCP server

# 安装 MCP server
npm install -g @twelvetake/reaper-mcp
# 或 clone bonfire-audio/reaper-mcp
```

### 第三阶段：音乐平台数据

```bash
# Meting-Agent MCP server
npm install @eldment/meting-agent
# 注册到 config.yaml
```

### 第四阶段：Agent 角色库

```bash
git clone --depth 1 https://github.com/jnMetaCode/agency-agents-zh.git
# 将音乐相关角色加载到 Hermes
```

---

## 七、多 Agent 角色分工（作词阶段）

来自 agency-agents-zh 的角色调度：

| 角色 | 职责 | 需加载的技能/Agent |
|------|------|-------------------|
| 🎤 **词作家** | 根据用户灵感写出歌词初稿 | agency-agents-zh 作词人 |
| 🎼 **作曲人** | 为歌词设计旋律/和弦走向 | agency-agents-zh 作曲人 |
| 🎛️ **音乐制作人** | 整体编曲规划（乐器/风格/结构） | agency-agents-zh 音乐制作人 |
| 📝 **审词师** | 审阅歌词的节奏感/押韵/可唱性 | melt-agents-to-evaluate-music |
| 👂 **用户本人** | 最终确认方向 | — |
| 🎻 **编曲师** | 分乐器谱编排（钢琴/吉他/鼓/弦乐等）| music21 + Abjad |

```
用户"我想写一首关于夏天的歌"
  ↓
词作家: 创作 3 版歌词方向（青春/离别/欢快）
用户: "选欢快版，但副歌要更抓耳"
  ↓
词作家: 修改副歌 → 确认
  ↓
作曲人: 设计 C大调 120BPM 和弦走向 C-G-Am-F
用 music21 生成旋律草稿（MIDI）
  ↓
用户试听 MIDI → "主歌可以慢点，Bridge 换个调"
  ↓
音乐制作人: 调整结构 Intro(4) → Verse(16) → Chorus(16) → Bridge(8,转Dm) → Chorus(16) → Outro(4)
  ↓
编曲师 (music21 + Abjad):
  - 钢琴谱（左手伴奏+右手旋律）
  - 吉他谱（和弦图+扫弦节奏）
  - 贝斯谱（根音+walking）
  - 鼓谱（basic rock pattern）
  ↓
总谱 + 分谱 PDF → 用户确认 → 渲染 Demo
```

---

## 八、简谱/五线谱双输出方案

music21 + Abjad + LilyPond 组合可实现：

| 格式 | 方案 | 适用 |
|------|------|------|
| **五线谱 PDF** | Abjad → LilyPond → PDF | 标准乐谱 |
| **简谱图片** | music21 数字表示 → PIL/Matplotlib 渲染 | 民乐/快速谱 |
| **MusicXML** | music21 直接导出 `.mxl` | 导入其他 DAW/打谱软件 |
| **MIDI** | music21 直接导出 `.mid` | 试听/渲染 |
| **吉他谱 (TAB)** | LilyPond 原生支持 fret-diagrams | 吉他分谱 |

```python
# 核心代码模式
from music21 import *
import abjad

# 1. 创建乐谱
s = stream.Score()
p1 = stream.Part()
p1.append(note.Note("C4", type="quarter"))
# ... 添加更多音符

# 2. 做和声分析
analysis = s.analyze('key')  # 调性检测
chords = s.chordify()        # 和弦提取

# 3. 导出多种格式
s.write('musicxml')  # → MusicXML
s.write('midi')      # → MIDI
s.write('lilypond')  # → LilyPond 源码

# 4. Abjad 做排版
staff = abjad.Staff("c'4 d'4 e'4 f'4")
score = abjad.Score([staff])
abjad.persist.as_pdf(score)  # → 出版级 PDF
```

---

## 九、Demo 音频渲染方案对比

| 方案 | 音质 | CPU 开销 | 安装复杂度 | 总评 |
|------|------|---------|-----------|------|
| **REAPER + reaper-mcp** | ⭐⭐⭐⭐⭐ | 中 | 高（需装 REAPER） | 最佳方案 |
| **FluidSynth + SoundFont** | ⭐⭐⭐ | 低 | **极低**（apt 即可） | ✅ **推荐作为默认方案** |
| **Suno API** | ⭐⭐⭐⭐⭐ | 零（云端） | 低（API Key） | ✅ **有歌词时首选** |
| **ACEStep API** | ⭐⭐⭐⭐ | 零（云端） | 低（API Key） | 备选 |
| **kokoro TTS** | ⭐⭐⭐ | 中低 | ✅ 已装 | 仅做歌词人声 Demo |

**推荐默认链路**：音乐参数 → music21 生成 MIDI → fluidsynth 渲染为 WAV → (可选) 叠加 kokoro TTS 人声 → 输出 demo。

---

## 十、后续开发建议优先级

| 优先级 | 任务 | 预估工作量 |
|--------|------|-----------|
| 🥇 P0 | 安装 music21 + abjad + lilypond + fluidsynth（乐理基础） | 15 分钟 |
| 🥇 P0 | 安装 Meting-Agent MCP（音乐数据源） | 10 分钟 |
| 🥇 P0 | 创建 music-creation-skill（整合所有角色和流程） | 2 小时 |
| 🥈 P1 | 配置 agency-agents-zh 音乐相关角色 | 30 分钟 |
| 🥈 P1 | 实现多 Agent 作词协作流程 | 3 小时 |
| 🥈 P1 | 实现总谱/分谱 PDF 输出（abjad+lilypond） | 2 小时 |
| 🥉 P2 | 安装 REAPER + reaper-mcp（专业音频渲染） | 1 小时 |
| 🥉 P2 | 集成 Suno/ACEStep API（AI 歌曲生成） | 1 小时 |
| 🥉 P2 | 实现录播分析流程 | 3 小时 |
| 🥉 P2 | 实现音乐平台发布（AiToEarn 已有） | 1 小时 |

---

## 十一、关于你给的项目的重点推荐

**最值得立即集成的 3 个项目**：

1. **ELDment/Meting-Agent** — 10 分钟装好，MCP 协议接入，立刻获得四平台（网易云/QQ/酷狗/酷我）音乐搜索、歌词、播放链接能力。**对作词参考最有价值**

2. **Tz-WIND/ATRI_AGENT** — music21 + Rust 音频引擎。**最接近你需要的「本地音乐工作站」概念**。Python 运行，不需要 GPU，MIDI 编辑 + 音频导出

3. **Muyu1uz/music-master** — LangGraph + DeepAgents 多 Agent 编排，作词→作曲→编曲流水线设计模式可直接复用

---

*Hermes Agent 音乐创作引擎·可行性报告 v0.1*
