# music21 API 备注

## 已知兼容点

- 歌词应优先通过 `note.addLyric()` 挂载。
- 打击乐应优先通过 `note.Unpitched()` 表示。
- 遍历音符时优先使用 `list(part.flatten().notes)`，避免直接依赖旧接口。

## 常用导出

```python
score.write("musicxml", fp="output.musicxml")
score.write("midi", fp="output.mid")
score.write("lilypond", fp="output.ly")
```

## LilyPond 渲染

`.ly` 文件生成后，需要额外调用 `lilypond` 输出 PDF。

## 建议

- 升级 `music21` 前先跑一遍完整链路。
- 新增乐器映射时先确认 MIDI 编号和导出表现一致。
- 涉及歌词、鼓组、分谱时优先补回归测试。
