# Music Creation Engine

中文 | [English](README.en.md)

`music-creation-engine` 是一个面向 AI 智能体的可部署音乐执行引擎。它不负责替代智能体做创作判断，而是把智能体已经决定好的结构化音乐方案，稳定地落成可验证、可交付的产物。

当前版本：`v0.4.0`

## 项目思路

这个项目解决的核心问题不是“让模型随便生成一段音乐”，而是把“从用户需求到最终成品”的链路做成真实可执行的工程流程。

它重点解决这些问题：

- 智能体能说清楚，但不能稳定落地成 MIDI、PDF、WAV、MP3。
- 生成结果没有统一工作流、没有清晰检查点、没有回滚和重试机制。
- 参考检索、MIDI 编辑、演奏可行性检查分散在不同工具里，难以形成闭环。
- Hermes、Codex、OpenClaw 等不同智能体需要同一套可复用的入口和协议。

## 目标与方向

项目目标是把音乐创作流程做成“Agent 决策，Engine 执行”的分层系统。

### 目标

- 接收结构化作曲计划并生成可验证产物。
- 提供 CLI、HTTP API、Workflow 三种入口。
- 让 Hermes、Codex、OpenClaw 使用同一套执行面。
- 保留检查点、修订、重试、清理、删除等工作流能力。
- 支持公开发布与 GitHub Releases 自动化。

### 当前方向

1. 稳定的结构化作曲与渲染。
2. 更强的工作流生命周期管理。
3. 更可靠的公共参考检索。
4. 更强的原生 MIDI 编辑与可演奏性校验。
5. 可选的外部 sidecar 集成，而不是把所有能力硬塞进核心。

## 工作流

推荐的真实执行顺序如下：

1. `health` 和 `capabilities` 先确认服务可用。
2. 智能体先输出结构化方案：`key`、`bpm`、`style`、`chord_progression`、`sections`、`melody`、`instrument_roles`。
3. `score` 生成 MIDI、MusicXML、LilyPond 等基础乐谱产物。
4. `render` 生成 WAV / MP3 / PDF。
5. `workflow full` 一次性执行完整闭环。
6. `workflow status`、`workflow revise`、`workflow retry`、`workflow cancel`、`workflow delete`、`workflow cleanup` 管理生命周期。
7. `midi inspect`、`midi diff`、`midi query`、`midi transform` 做二次编辑与验证。
8. `playability` 检查实际可演奏性。
9. `references search` 提供公开参考检索。

## 集成工具

### 核心工具

- `music21`
- `LilyPond`
- `FluidSynth`
- `ffmpeg`
- `PyYAML`

### 参考与扩展

- `@eldment/meting-agent`
- `midi-composer-mcp`
- `reaper-mcp`

### 智能体适配

- Hermes
- Codex
- OpenClaw

## 具体操作方法

### 1. 先看可用能力

```bash
music-creation-engine health
music-creation-engine capabilities
```

### 2. 生成结构化乐谱

```bash
music-creation-engine score \
  --lyrics "Verse text" \
  --output build/output/song \
  --key Am \
  --bpm 72 \
  --instruments piano,vocals,bass,drums \
  --style pop \
  --chord-progression "Am,F,C,G" \
  --sections '[{"name":"intro","bars":4},{"name":"verse","bars":8},{"name":"chorus","bars":8},{"name":"outro","bars":4}]' \
  --melody '{"vocals":["A4","B4","C5","A4"]}' \
  --instrument-roles '{"piano":"chord","bass":"bass","vocals":"melody","drums":"rhythm"}'
```

### 3. 生成完整成品

```bash
music-creation-engine workflow full \
  --lyrics "..." \
  --output build/output/song \
  --no-render-demo
```

### 4. 查看和下载产物

- `GET /v1/artifacts/{workflow_id}`
- `GET /v1/artifacts/{workflow_id}/files/{filename}`
- `GET /v1/workflows/{workflow_id}/checkpoints`

### 5. 做 MIDI 级别验证

```bash
music-creation-engine midi inspect --midi-path build/output/song.mid
music-creation-engine midi diff-files --left-path a.mid --right-path b.mid
music-creation-engine midi transform --midi-path a.mid --operation transpose --semitones 2
```

### 6. 做可演奏性检查

```bash
music-creation-engine playability --instrument piano --notes "48,60,72,84"
```

### 7. 做参考检索

```bash
music-creation-engine references search --keyword "Jay Chou" --platform netease
```

## 生成的产物

一次完整工作流可以产出：

- `composition.mid`
- `composition.musicxml`
- `composition.ly`
- `composition.pdf`
- `composition.wav`
- `composition.mp3`
- workflow manifest
- workflow checkpoints

## 安装步骤

### 推荐方式：Docker

```bash
docker compose up
```

### 本地安装

```bash
python3 -m pip install -e .
```

如果需要完整渲染链路，再安装系统依赖：

```bash
sudo apt-get install -y lilypond fluidsynth fluid-soundfont-gm ffmpeg
```

### 安装脚本

```bash
./install.sh
```

脚本会按顺序询问以下选项：

- 是否安装 Python 可编辑包与 CLI 入口
- 是否安装本地渲染工具 `lilypond` / `fluidsynth` / `ffmpeg`
- 是否安装公共参考集成 `@eldment/meting-agent`
- 是否把 bundle 复制到检测到的智能体技能目录
- 如果没有技能目录，是否复制到 home 目录下的兜底位置

默认行为是“是”。如果在非交互环境运行，脚本会按默认值继续。

## 安装确认说明

- `Python editable package and CLI entrypoint`：安装后可直接使用 `music-creation-engine` 命令。
- `local rendering tools`：用于 PDF、WAV、MP3 等产物生成；没有这些工具也能做部分工作流，但渲染会降级。
- `public reference integration`：用于参考检索层，优先走 public agent / MCP / CLI 兼容路径。
- `copy bundle into detected agent skill directories`：把项目打包到 Hermes、Codex、OpenClaw 等常见技能路径，便于智能体直接调用。
- `fallback directory`：当系统没有检测到任何技能目录时，使用用户主目录下的兜底副本。

## 下一步方向

1. 更强的 Meting 结果规范化和 provider 适配。
2. 更强的异步队列和任务编排。
3. 更深的原生 MIDI 编辑能力。
4. 更细的 playability 规则。
5. 按需接入 `midi-composer-mcp` 或 `reaper-mcp` 作为可选 sidecar。

## 致谢

本项目的思路、实现和集成方向借鉴并参考了以下项目与工具：

- `midi-composer-mcp`
- `mcp-score`
- `Midra`
- `reaper-mcp`
- `ATRI_AGENT`
- `music.build`
- `OpenClaw`
- `Hermes`

同时也参考了多个公开的音乐智能体、工作流编排和发布自动化项目，用于完善本项目的工程边界与可执行性。

## English

If you need the English documentation, switch to [README.en.md](README.en.md).
