# 架构摘要

本文件是 `architecture-report.md` 的精简公开版，用于仓库内协作，不依赖任何私有笔记路径或服务器环境。

## 核心结论

1. 项目应保持为 Skill-first 形态，而不是单独拆成 MCP 服务。
2. 生成链路应继续采用 `music21 -> LilyPond/FluidSynth/FFmpeg` 的纯 CPU 方案。
3. LLM 负责创作决策与交互，确定性工具负责乐理、排版与音频渲染。

## 为什么优先 Skill

- 更适合多轮对话式创作。
- 更适合多 Agent 协作作词、评审和修改。
- 更容易直接复用现有脚本输出。
- 安装和迁移成本低，适合 Hermes、Claude、Codex 一类智能体环境。

## 当前推荐链路

```text
用户意图
-> 多 Agent 作词与确认
-> 作曲规划
-> music21 生成乐谱结构
-> LilyPond 输出 PDF
-> FluidSynth 渲染 WAV
-> FFmpeg 转码 MP3
-> 质量评估
-> 发布
```

## 约束

- 默认目标环境为无 GPU 的 Linux 主机。
- 依赖尽量控制在系统包与 Python 包范围内。
- 运行结果应可导出为 PDF、MIDI、MusicXML、WAV、MP3。

## 后续扩展方向

- 可选接入 REAPER MCP 以提升渲染与混音质量。
- 可选接入外部音乐生成 API 负责完整人声歌曲生成。
- 可选接入参考歌曲检索 MCP，辅助风格分析与歌词参考。
