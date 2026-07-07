# 部署验证记录

本文件只记录可公开的安装与验证信息，不包含服务器地址、用户信息或私有路径。

## 已验证依赖

| 组件 | 用途 |
| --- | --- |
| `music21` | 乐理分析、MIDI / MusicXML / LilyPond 导出 |
| `abjad` | 乐谱构建与 LilyPond 生成 |
| `lilypond` | PDF 乐谱排版 |
| `fluidsynth` | MIDI 渲染 WAV |
| `ffmpeg` | WAV 转码 MP3 |

## 最小验证流程

1. 运行 `scripts/sheet_music_generator.py` 生成 `.mid`、`.musicxml`、`.ly`、`.pdf`。
2. 运行 `scripts/demo_renderer.py` 将 `.mid` 渲染为 `.wav` 或 `.mp3`。
3. 确认输出文件存在且非空。

## 兼容性注意

- `music21` 版本变化会影响部分 API。
- `lilypond` 与 `fluidsynth` 必须由系统包提供。
- SoundFont 不存在时，MIDI 渲染会失败。

## 发布前检查

- 仓库内不应保留生成产物。
- 仓库内不应保留私人服务器说明。
- 仓库内不应保留用户数据、cookie、token 或绝对路径。
