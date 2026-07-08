# Music Creation Engine

[English](README.en.md) | 中文

`music-creation-engine` 是一个面向 Hermes、Codex、OpenClaw 等智能体的音乐执行引擎。它负责把智能体已经决定好的结构化音乐方案，落地成可验证、可交付的产物，而不是自己承担对话式创作判断。

## 一句话定位

Agent 负责“想”，Engine 负责“做”。

- Agent：理解用户需求，推理风格、段落、旋律、和声、乐器分工
- Engine：生成 MIDI、MusicXML、LilyPond、PDF、WAV、MP3，并管理工作流产物

## 当前版本

- 当前发布版本：`v0.4.0`
- 当前开发重点：`v0.5.0` 工程硬化
- 项目真相源：`references/project-status.md`

## 适用场景

- 想让智能体真正产出音乐文件，而不是只给一段文本建议
- 想把作曲、渲染、修订、重试、产物管理做成稳定工作流
- 想让 Hermes / Codex / OpenClaw 共用同一套音乐执行层
- 想保留结构化输入和可重复验证的工程边界

## 核心能力

- 结构化作曲：`key`、`bpm`、`chord_progression`、`sections`、`melody`、`instrument_roles`
- 乐谱产物：MIDI、MusicXML、LilyPond、PDF
- 音频产物：WAV、MP3
- 工作流生命周期：`status`、`revise`、`retry`、`cancel`、`delete`、`cleanup`
- MIDI 工具：`diff`、`diff-files`、`inspect`、`query`、`transform`
- 可演奏性检查：钢琴、人声、吉他、贝斯等基础规则
- 参考检索：Meting 主路径，HTTP fallback 兜底

## 快速开始

### Docker

```bash
git clone https://github.com/mage0535/music-creation-engine.git
cd music-creation-engine
docker compose up
```

### 手动安装

```bash
python3 -m pip install -e .
sudo apt-get install -y lilypond fluidsynth fluid-soundfont-gm ffmpeg
npm install -g @eldment/meting-agent
uvicorn music_creation_engine.api.app:create_app --factory --host 0.0.0.0 --port 8000
```

## 最小工作流

1. 调用 `GET /health` 和 `GET /capabilities` 确认服务可用
2. 用 `POST /v1/score` 生成乐谱与 MIDI
3. 用 `POST /v1/render` 或 `POST /v1/workflows/full` 生成音频与完整产物
4. 用 `POST /v1/workflows/{id}/revise` 做修订迭代
5. 用 `GET /v1/artifacts/{id}` 和 `GET /v1/artifacts/{id}/files/{name}` 取回结果

## 认证与限流

`v0.5.0` 工程硬化已经落地基础认证与限流能力：

- `MCE_API_KEYS`：逗号分隔的 API key 列表
- `MCE_RATE_LIMIT_PER_MINUTE`：每分钟限流阈值
- `MCE_AUTH_HEADER_NAME`：自定义鉴权头，默认 `x-api-key`

如果未配置 `MCE_API_KEYS`，本地开发默认不强制鉴权。  
如果配置了 `MCE_API_KEYS`，所有 `/v1/*` 路由都需要携带 API key。

## 示例请求

```json
{
  "lyrics": "Verse text",
  "output_base": "build/output/song",
  "key": "Am",
  "bpm": 72,
  "instruments": "piano,vocals,bass,drums",
  "style": "pop",
  "chord_progression": ["Am", "F", "C", "G"],
  "sections": [
    {"name": "intro", "bars": 4},
    {"name": "verse", "bars": 8},
    {"name": "chorus", "bars": 8}
  ],
  "melody": {"vocals": ["A4", "B4", "C5", "A4"]},
  "instrument_roles": {"piano": "chord", "bass": "bass", "vocals": "melody", "drums": "rhythm"}
}
```

## 主要接口

- `GET /health`
- `GET /capabilities`
- `POST /v1/score`
- `POST /v1/render`
- `POST /v1/workflows/full`
- `GET /v1/workflows/{workflow_id}/status`
- `POST /v1/workflows/{workflow_id}/revise`
- `POST /v1/references/search`
- `POST /v1/midi/inspect`
- `POST /v1/playability`

## 文档入口

- 项目真相源：`references/project-status.md`
- 当前状态：`references/current-state.md`
- 连续开发记录：`references/continuous-development.md`
- 发布说明：`references/release-notes-v0.4.0.md`
- 版本变更：`CHANGELOG.md`

## 测试

```bash
python -m pytest -q tests --ignore=tests/live_service_test.py
python tests/e2e_http_workflow.py
```

## 项目结构

```text
config/                         默认配置
src/music_creation_engine/      主包源码
adapters/                       Hermes / Codex / OpenClaw 适配
references/                     状态、路线图、开发文档
tests/                          单测、集成测试、E2E
Dockerfile
docker-compose.yml
install.sh
```

## 下一步

当前建议顺序：

1. 先稳住文档真相源和工程边界
2. 再推进 `v0.5.0` 的认证、CI、smart revision、真实 integration test
3. 最后再进入 `midi-composer-mcp`、SSE、Reaper 深集成等能力扩展
