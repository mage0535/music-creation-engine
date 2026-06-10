# Music Creation Engine — 安装配置指南

## 快速安装

### 1. Python 依赖

```bash
pip install music21 abjad
```

**验证:**
```bash
python3 -c "import music21; print(f'music21 {music21.__version__}')"
python3 -c "import abjad; print(f'abjad {abjad.__version__}')"
```

### 2. 系统工具

```bash
apt install lilypond fluidsynth fluid-soundfont-gm
```

**验证:**
```bash
lilypond --version
fluidsynth --version
```

### 3. Meting-Agent MCP（可选，用于搜索参考歌曲）

```bash
npm install -g @eldment/meting-agent
```

**MCP 注册 (config.yaml):**
```yaml
mcp_servers:
  meting-agent:
    command: npx
    args: ["@eldment/meting-agent"]
    connect_timeout: 15
    startup: lazy
    timeout: 60
```

**验证:**
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | npx @eldment/meting-agent | python3 -m json.tool | head -10
```

### 4. Skill 安装

```bash
# 复制到你的 Agent 的 skills 目录
cp SKILL.md ~/.your-agent/skills/music-creation/SKILL.md
mkdir -p ~/.your-agent/skills/music-creation/scripts/
cp scripts/* ~/.your-agent/skills/music-creation/scripts/
```

### 5. 工具清单注册

对于 Hermes Agent，追加到 `tool_manifest.yaml`：

```yaml
music_creation:
  status: active
  version: 1.0.0
  skill: music-creation
  scripts:
  - sheet_music_generator.py
  - demo_renderer.py
```

## 完整测试

```bash
# 测试乐谱生成
mkdir -p /tmp/music_test

python3 scripts/sheet_music_generator.py \
  --lyrics "清晨的阳光洒落窗台\n微风带走了昨夜的尘埃" \
  --key C --bpm 120 \
  --instruments piano,vocals,guitar,bass \
  --style pop \
  --output /tmp/music_test/test_song \
  --mode all --json

# 检查输出
ls -lh /tmp/music_test/test_song.*

# 测试 MP3 渲染
python3 scripts/demo_renderer.py \
  --midi /tmp/music_test/test_song.mid \
  --output /tmp/music_test/test_demo \
  --format mp3

# 确认 MP3 存在且可播放
ls -lh /tmp/music_test/test_demo.mp3
```

## 故障排查

| 问题 | 原因 | 解决 |
|------|------|------|
| `ModuleNotFoundError: No module named 'music21'` | 包未安装 | `pip install music21` |
| `lilypond: command not found` | 系统工具缺失 | `apt install lilypond` |
| `fluidsynth: command not found` | FluidSynth 缺失 | `apt install fluidsynth fluid-soundfont-gm` |
| PDF 输出为空 | LilyPond 排版问题 | 检查 `lilypond --version` 是否 ≥ 2.24 |
| 鼓声部 AttributeError | music21 API 变更 | 确保用 `note.Unpitched(pitch_number)` 而非 percussion.Percussion() |
| Meting-Agent 不响应 | MCP server 未启动 | 检查 config.yaml 中 meting-agent 配置，确认 npx 可访问 |

## 对接其他智能体

本套件被设计为**即插即用**：

- **使用 Hermes Agent**: 直接 skill_view('music-creation') 加载
- **使用 Claude Code**: 复制 SKILL.md 到 `~/.claude/skills/`
- **使用 Cursor**: 复制 README.md 到项目文档
- **使用任何 LLM**: 粘贴 README.md 到系统提示词，LLM 即可理解完整管线

---

## 链接 / Links

- **GitHub**: https://github.com/mage0535/music-creation-engine
- **Issues**: https://github.com/mage0535/music-creation-engine/issues
- **Topics**: `music-creation` `ai-composer` `sheet-music` `lilypond` `music21` `midi` `audio-demo` `fluidsynth` `hermes-agent` `claude-code` `ai-agent` `music-ai` `multilingual` `mcp-server` `zero-gpu`
