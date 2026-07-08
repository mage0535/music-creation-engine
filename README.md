# 🎵 Music Creation Engine

[English](README.en.md) | [中文版](README.md)

**AI Agent 原生音乐创作执行引擎 — 将 LLM 作曲决策转化为出版级乐谱 + 音频成品**

> **两层关系**
>
> | 项目 | 定位 | 功能 |
> |------|------|------|
> | **Hermes / Codex / OpenClaw** | Agent 底座 | 对话管理、意图识别、LLM 推理 |
> | **music-creation-engine** | 能力扩展层 | 将 Agent 结构化参数 → MIDI/PDF/MP3 成品 |
>
> **Agent 负责"想"（LLM 作曲决策），Engine 负责"做"（确定性的乐谱生成 + 音频渲染）。**

---

## 适用场景

- ✅ 你想让 Agent 不仅"聊出"一首歌，而是**真实生成 MIDI、PDF 乐谱、MP3 试听**
- ✅ 你希望 Agent 能用**和弦走向、段落结构、音名旋律**等结构化参数精确控制作曲结果
- ✅ 你需要在 Agent 工作流中跟踪每次生成的历史、**修订迭代、重试、清理**
- ✅ 你希望一套 API + CLI 统一对接 Hermes / Codex / OpenClaw 三种 Agent

---

## 项目概览

| 特性 | 说明 |
|------|------|
| 🎼 **结构化作曲** | 和弦走向、段落结构、音名旋律、乐器分工 — Agent 的 LLM 怎么想，Engine 怎么做 |
| 🎹 **音名输入** | `["A4","B4","C5"]` 或 `[69,71,72]` 双格式 |
| 📄 **多格式输出** | MIDI / MusicXML / LilyPond 源码 / 出版级 PDF |
| 🔊 **音频渲染** | FluidSynth → WAV → FFmpeg → MP3 |
| 🔄 **异步工作流** | `?async=true` → 立即返回，后台生成，轮询状态 |
| 📦 **产物管理** | 自动 manifest + checkpoints + file inventory |
| 🎯 **MIDI 工具** | diff / inspect / query / transform |
| 🖖 **可演奏性检查** | 多乐器音域校验 + 跨度/密度/手位分析 |
| 🔍 **参考搜索** | Meting-Agent → MCP stdio → iTunes HTTP 三级回退 |
| 🐳 **容器化** | Dockerfile + docker-compose.yml |

---

## 快速开始

### Docker（推荐）

```bash
git clone https://github.com/mage0535/music-creation-engine.git
cd music-creation-engine
docker compose up
# 服务启动在 http://localhost:8000
```

### 手动安装

```bash
# 1. 克隆
git clone https://github.com/YOUR_REPO/music-creation-engine.git && cd music-creation-engine

# 2. 安装 Python 包
python3 -m pip install -e .

# 3. 安装系统依赖
sudo apt-get install -y lilypond fluidsynth fluid-soundfont-gm ffmpeg

# 4.（可选）安装参考搜索
npm install -g @eldment/meting-agent

# 5. 启动服务
uvicorn music_creation_engine.api.app:create_app --factory --host 0.0.0.0 --port 8000
```

### 验证

```bash
curl http://localhost:8000/health
# {"status":"ok"}

curl -X POST http://localhost:8000/v1/score \
  -H "Content-Type: application/json" \
  -d '{"lyrics":"Hello","output_base":"/tmp/song","key":"Am","bpm":72,"instruments":"piano,vocals","chord_progression":["Am","F","C","G"],"melody":{"vocals":["A4","B4","C5","A4"]}}'
```

---

## 目录

- [快速开始](#快速开始)
- [架构](#架构)
- [功能模块](#功能模块)
- [API 参考](#api-参考)
- [CLI 参考](#cli-参考)
- [参数说明](#参数说明)
- [配置](#配置)
- [项目结构](#项目结构)
- [Agent 适配器](#agent-适配器)
- [资源占用](#资源占用-预估)
- [致谢](#致谢)
- [许可证](#许可证)

---

## 架构

```
用户 → Agent (Hermes / Codex / OpenClaw)       ← 决策层
         │ LLM 规划: key, bpm, chords, sections, melody, roles
         ▼
music-creation-engine                            ← 执行层
  │
  ├── 校验层   (bpm 20-300 / key 白名单 / inst 白名单 / chord 正则)
  ├── music21  → MIDI / MusicXML / LilyPond / PDF
  ├── fluidsynth → WAV → ffmpeg → MP3
  ├── ArtifactService → manifest + checkpoints + file inventory
  ├── FileResponse    → 文件下载 (mid/pdf/mp3/wav/xml/ly)
  ├── Workflow        → async / status / revise / retry / cancel / delete / cleanup
  ├── MIDI tools      → diff / diff-files / inspect / query / transform
  └── Reference       → Meting CLI → MCP stdio → iTunes HTTP
```

**边界原则：** Engine 不调用 LLM。所有 LLM 推理在 Agent 层完成。这使得 Engine 可以通过 65 个确定性测试覆盖。

---

## 功能模块

### 1. 乐谱生成 (`runtime/score_runtime.py`)

music21 引擎驱动，接受结构化作曲参数：

```python
# 支持音名输入（LLM 友好）
melody = {"vocals": ["A4", "B4", "C5", "A4"]}
# 也支持 MIDI 数字（向后兼容）
melody = {"vocals": [69, 71, 72, 69]}
```

每个段落可独立设置调性、乐器、小节数：
```json
"sections": [
  {"name": "intro",  "bars": 4, "key": "Am"},
  {"name": "verse",  "bars": 8, "key": "Am"},
  {"name": "chorus", "bars": 8, "key": "C"},
  {"name": "bridge", "bars": 4, "key": "F"},
  {"name": "outro",  "bars": 4, "key": "Am"}
]
```

### 2. 音频渲染 (`runtime/render_runtime.py`)

FluidSynth + FFmpeg 流水线：MIDI → WAV（SoundFont 渲染）→ MP3 编码。跨平台 SoundFont 检测（Linux `/usr/share/sounds/sf2/`，Windows `C:\Windows\System32\drivers\gm.dls`）。

### 3. 工作流与产物管理

```text
build/workflows/{workflow_id}/
├── artifacts/
│   ├── composition.mid        (MIDI 文件)
│   ├── composition.musicxml   (可导入 DAW)
│   ├── composition.ly         (LilyPond 源码)
│   ├── composition.pdf        (出版级乐谱)
│   ├── composition.wav        (无损音频)
│   └── composition.mp3        (试听)
├── manifest.json              (请求 + 产物清单)
├── checkpoints.json           (各阶段记录)
└── status.json                (异步状态)
```

生命周期：
```
queued → processing → completed
                  → failed → retry → processing → completed
                  → cancelled
```

### 4. MIDI 工具 (`services/midi_service.py`)

| 工具 | 功能 |
|------|------|
| `diff` | 两组音符差分对比（added/removed） |
| `diff-files` | 两个 `.mid` 文件差分 |
| `inspect` | 分析 count / min / max / unique |
| `query` | 按 min_pitch / max_pitch 过滤 |
| `transform` | transpose / replace\_phrase / reverse / invert |

### 5. 可演奏性检查 (`services/playability_service.py`)

- 钢琴：音域 21-108、手跨 ≤24 半音、每手 ≤1 八度、≤10 同时音符
- 人声：音域 55-84（C4~C6）
- 吉他/贝斯：音域 + 位置移位警告
- 小提琴/长笛/萨克斯/小号/大提琴：各自标准音域

### 6. 参考搜索 (`integrations/meting.py`)

三级回退：Meting-Agent 直接调用 → MCP stdio 协议 → iTunes HTTP API。结果归一化为 `title` / `artist` / `album` / `preview_url` / `song_id`。

---

## API 参考

### 健康 & 能力
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/capabilities` | 工具/集成可用性 |

### 作曲
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/v1/score` | 结构化参数 → MIDI/PDF/XML |
| POST | `/v1/render` | MIDI → WAV/MP3 |
| POST | `/v1/workflows/full` | 同步执行（完整流水线） |
| POST | `/v1/workflows/full?async=true` | 异步执行（轮询状态） |
| GET | `/v1/workflows/{id}/status` | 异步状态查询 |
| POST | `/v1/workflows/{id}/revise` | 修订迭代 |
| POST | `/v1/workflows/{id}/retry` | 重试 |
| POST | `/v1/workflows/{id}/cancel` | 取消 |
| DELETE | `/v1/workflows/{id}` | 删除 |
| GET | `/v1/workflows` | 列表 |
| POST | `/v1/workflows/cleanup` | 定时清理 |
| GET | `/v1/workflows/{id}/checkpoints` | 检查点 |

### MIDI
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/v1/midi/diff` | 音符列表对比 |
| POST | `/v1/midi/diff-files` | .mid 文件对比 |
| POST | `/v1/midi/inspect` | 音符分析 |
| POST | `/v1/midi/query` | 过滤查询 |
| POST | `/v1/midi/transform` | 移调/替换/反转/倒影 |

### 校验 & 搜索
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/v1/playability` | 可演奏性检查 |
| POST | `/v1/references/search` | 参考歌曲线索 |

### 产物
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/v1/artifacts/{id}` | Manifest + file inventory |
| GET | `/v1/artifacts/{id}/files/{name}` | 文件下载 |

---

## CLI 参考

```bash
# 作曲
music-creation-engine score \
  --lyrics "歌词" --output /tmp/song \
  --key Am --bpm 72 \
  --instruments piano,vocals,bass \
  --chord-progression "Am,F,C,G" \
  --sections '[{"name":"intro","bars":4}]' \
  --melody '{"vocals":["A4","B4","C5"]}' \
  --instrument-roles '{"piano":"chord","bass":"bass"}'

# 工作流
music-creation-engine workflow full --lyrics "..." --output /tmp/song
music-creation-engine workflow status --workflow-id abc123
music-creation-engine workflow revise --workflow-id abc123
music-creation-engine workflow retry --workflow-id abc123
music-creation-engine workflow list

# MIDI
music-creation-engine midi diff --left-notes "60,62" --right-notes "60,64"
music-creation-engine midi transform --notes "60,62,64" --operation reverse

# 校验
music-creation-engine playability --instrument piano --notes "48,60,72,84"
```

---

## 参数说明

| 参数 | 类型 | 必填 | 默认 | 示例 |
|------|------|------|------|------|
| `lyrics` | `str` | ✅ | — | `"Verse text"` |
| `output_base` | `str` | ✅ | — | `"/tmp/song"` |
| `key` | `str` | 否 | `C` | `"Am"` |
| `bpm` | `int` | 否 | `120` | `72` |
| `instruments` | `str` | 否 | `"piano,vocals"` | `"piano,bass,drums"` |
| `chord_progression` | `list[str]` | 否 | 模板 | `["Am","F","C","G"]` |
| `sections` | `list[object]` | 否 | 歌词行数 | `[{name:"verse",bars:8}]` |
| `melody` | `dict[str,list]` | 否 | 模板 | `{"vocals":["A4","B4","C5"]}` |
| `instrument_roles` | `dict[str,str]` | 否 | 自动 | `{"piano":"chord","bass":"bass"}` |

**有效值：** 乐器 `piano vocals guitar bass drums strings flute sax trumpet synth` | 角色 `chord melody bass pad rhythm` | BPM 20–300 | 段落 ≤50/总小节 ≤2000

---

## 配置

`config/defaults.yaml`：

```yaml
project:
  output_dir: build/output
  workflow_dir: build/workflows
integrations:
  meting_enabled: true
  midi_composer_enabled: false
  reaper_enabled: false
tools:
  ffmpeg_command: ffmpeg
  lilypond_command: lilypond
  fluidsynth_command: fluidsynth
  meting_command: npx
```

环境变量 `MCE_OUTPUT_DIR` / `MCE_WORKFLOW_DIR` 可覆盖。

---

## 项目结构

```
├── install.sh                  ← 安装入口
├── Dockerfile / compose.yml    ← 容器部署
├── pyproject.toml              ← 包元数据
├── SKILL.md                    ← Agent skill 声明
├── README.md / .en.md          ← 双语文档
├── config/defaults.yaml        ← 配置
├── src/music_creation_engine/
│   ├── api/app.py              ← 20 路由
│   ├── cli.py                  ← 22 命令
│   ├── models.py               ← 数据模型
│   ├── services/               ← 6 服务
│   ├── runtime/                ← 执行引擎
│   └── integrations/           ← 集成（meting/MCP/reaper）
├── adapters/hermes/ codex/ openclaw/
├── references/                 ← 设计文档 + 开发日志
└── tests/                      ← 65+30 测试
```

---

## Agent 适配器

| Agent | 文件 | 安装路径 |
|-------|------|---------|
| Hermes | `adapters/hermes/SKILL.md` | `~/.hermes/skills/creative/music-creation-engine/` |
| Codex | `adapters/codex/AGENTS.md` | `$CODEX_HOME/skills/music-creation-engine/` |
| OpenClaw | `adapters/openclaw/README.md` | `~/.openclaw/skills/music-creation-engine/` |

---

## 资源占用（预估）

| 组件 | 大小 |
|------|------|
| music21 | ~50 MB |
| LilyPond | ~200 MB |
| FluidSynth + FluidR3_GM.sf2 | ~146 MB |
| FFmpeg | ~10 MB |
| Meting-Agent (可选) | ~15 MB |
| **运行时内存** | ~100 MB |
| **每次生成产物** | ~1-5 MB |

---

## 致谢

- [music21](https://github.com/cuthbertLab/music21) — MIT 乐理引擎 | [LilyPond](https://lilypond.org) — 乐谱排版 | [FluidSynth](https://github.com/FluidSynth/fluidsynth) — MIDI 合成
- [Meting-Agent](https://github.com/ELDment/Meting-Agent) — 音乐搜索 MCP | [midi-composer-mcp](https://github.com/voho/midi-composer-mcp) — 40+ 乐理 MCP 工具 | [reaper-mcp](https://github.com/bonfire-audio/reaper-mcp) — DAW 控制

---

## 变更日志

详见 [CHANGELOG.md](CHANGELOG.md) | 详见 [references/release-notes-v0.4.0.md](references/release-notes-v0.4.0.md)

## 许可证

待定
