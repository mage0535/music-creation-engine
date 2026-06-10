#!/usr/bin/env python3
"""
音乐乐谱生成器 — 歌词→乐谱（总谱/分谱）的完整管线
使用 music21 + Abjad + LilyPond 生成出版级乐谱 PDF 和 MIDI 试听文件
输出: .pdf, .mid, .musicxml, .ly

Usage:
  python3 sheet_music_generator.py --lyrics "歌词内容" --key C --bpm 120 \
    --instruments piano,guitar,bass,drums --output ./my_song
"""
import os, sys, json, argparse, tempfile, subprocess
from pathlib import Path

from music21 import *
from music21 import stream, note, chord, meter, key, tempo, instrument, midi

# ── 命令行参数 ──────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="音乐乐谱生成器")
    p.add_argument("--lyrics", "-l", help="歌词文本（按行=按句）", default="")
    p.add_argument("--lyrics-file", "-f", help="歌词文件路径")
    p.add_argument("--key", "-k", default="C", help="调性 (C, Dm, G, Am 等)")
    p.add_argument("--bpm", type=int, default=120, help="速度 BPM")
    p.add_argument("--time-signature", default="4/4", help="拍号 (4/4, 3/4, 6/8)")
    p.add_argument("--instruments", "-i", default="piano,vocals",
                    help="乐器列表 (逗号分隔): piano,vocals,guitar,bass,drums,strings")
    p.add_argument("--style", default="pop", help="风格: pop, rock, ballad, jazz, folk")
    p.add_argument("--output", "-o", default="./output/music_score",
                    help="输出文件基础路径（不含扩展名）")
    p.add_argument("--mode", default="all",
                    help="输出模式: all=PDF+MIDI+XML, pdf, midi, xml, ly")
    p.add_argument("--json", action="store_true", help="JSON 模式输出")
    return p.parse_args()

# ── 和弦进行模板 ──────────────────────────────────────────

CHORD_PROGRESSIONS = {
    "pop":    ["C", "G", "Am", "F"],
    "rock":   ["C", "G", "F", "C"],
    "ballad": ["C", "G/B", "Am", "F", "C", "G", "F", "C"],
    "jazz":   ["Cmaj7", "Dm7", "G7", "Cmaj7"],
    "folk":   ["C", "F", "C", "G"],
}

# ── 乐器配置 ──────────────────────────────────────────────

INSTRUMENT_MAP = {
    "piano":   instrument.Piano(),
    "vocals":  instrument.Vocalist(),
    "guitar":  instrument.AcousticGuitar(),
    "bass":    instrument.ElectricBass(),
    "drums":   instrument.HiHatCymbal(),
    "strings": instrument.Violin(),
    "flute":   instrument.Flute(),
    "sax":     instrument.AltoSaxophone(),
    "trumpet": instrument.Trumpet(),
    "synth":   instrument.Vibraphone(),
}

OCTAVE_OFFSET = {
    "piano": 0, "vocals": 0, "guitar": -1, "bass": -2,
    "drums": 0, "strings": 0, "flute": 1, "sax": 0,
    "trumpet": 0, "synth": 0
}

# ── 核心生成逻辑 ──────────────────────────────────────────

def generate_score(args):
    """生成完整总谱"""
    lyrics_lines = _load_lyrics(args)
    num_phrases = max(len(lyrics_lines) if lyrics_lines else 8, 4)
    instruments = args.instruments.split(",")
    key_sig = key.Key(args.key)
    time_sig = meter.TimeSignature(args.time_signature)
    prog = CHORD_PROGRESSIONS.get(args.style, CHORD_PROGRESSIONS["pop"])

    score = stream.Score()
    score.insert(0, tempo.MetronomeMark(number=args.bpm))
    score.insert(0, key_sig)
    score.insert(0, time_sig)
    score.insert(0, metadata.Metadata())
    score.metadata.title = args.output.split("/")[-1].replace("_", " ").title()
    score.metadata.composer = "AI Music Engine"

    parts_info = []
    for inst_name in instruments:
        inst_name = inst_name.strip()
        p = _build_part(inst_name, num_phrases, prog, key_sig, args.bpm, time_sig)
        p.partName = inst_name.capitalize()
        score.append(p)
        parts_info.append({"instrument": inst_name, "measures": num_phrases * 4})

    _add_lyrics(score, lyrics_lines, instruments)
    return score, parts_info, lyrics_lines


def _load_lyrics(args):
    if args.lyrics_file:
        with open(args.lyrics_file, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    elif args.lyrics:
        return [line.strip() for line in args.lyrics.split("\\n") if line.strip()]
    return []


def _build_part(inst_name, num_phrases, progression, key_sig, bpm, time_sig):
    """构建单个乐器声部"""
    p = stream.Part()
    p.insert(0, INSTRUMENT_MAP.get(inst_name, instrument.Piano()))
    offset_oct = OCTAVE_OFFSET.get(inst_name, 0)

    base_notes_map = {
        "piano":   [60, 64, 67, 65, 62, 67, 72, 71],
        "vocals":  [67, 69, 71, 72, 74, 72, 71, 69],
        "guitar":  [55, 59, 62, 57, 55, 62, 67, 64],
        "bass":    [36, 40, 43, 41, 36, 43, 48, 45],
        "drums":   [],
        "strings": [64, 67, 71, 69, 64, 71, 76, 74],
        "flute":   [72, 76, 79, 77, 72, 79, 84, 81],
        "sax":     [65, 69, 72, 71, 65, 72, 76, 74],
        "trumpet": [67, 71, 74, 72, 67, 74, 79, 76],
        "synth":   [68, 72, 76, 74, 68, 76, 79, 77],
    }

    if inst_name == "drums":
        return _build_drum_part(num_phrases, bpm)

    notes_arr = base_notes_map.get(inst_name, base_notes_map["piano"])

    for phrase_idx in range(num_phrases):
        chord_root = _chord_to_midi(progression[phrase_idx % len(progression)])
        for i, n_val in enumerate(notes_arr):
            n = note.Note(n_val + offset_oct)
            n.quarterLength = 1.0
            if inst_name == "piano":
                # 钢琴做和弦伴奏
                if i % 2 == 0:
                    n = chord.Chord([
                        n_val + offset_oct,
                        n_val + 4 + offset_oct,
                        n_val + 7 + offset_oct
                    ])
                    n.quarterLength = 2.0
            p.append(n)

    return p


def _build_drum_part(num_phrases, bpm):
    """鼓声部（简单的 basic rock pattern）
    用 note.Unpitched 直接表示鼓音色
    GM MIDI Percussion: 36=Bass Drum, 38=Snare, 42=Hi-Hat Closed, 46=Hi-Hat Open
    """
    p = stream.Part()
    p.insert(0, instrument.HiHatCymbal())
    for phrase_idx in range(num_phrases):
        for beat in range(4):
            if beat == 0 or beat == 2:
                k = note.Unpitched(36)  # Bass Drum
                k.quarterLength = 1.0
                p.append(k)
            else:
                k = note.Unpitched(42)  # Hi-Hat
                k.quarterLength = 0.5
                p.append(k)
                s = note.Unpitched(38)  # Snare on 2 and 4
                s.quarterLength = 0.5
                p.append(s)
    return p


def _add_lyrics(score, lyrics_lines, instruments):
    """为第一声部（通常是 vocals）添加歌词"""
    for part in score.parts:
        if "vocal" in part.partName.lower():
            lyrics = []
            for i, line in enumerate(lyrics_lines):
                words = line.split()
                for word in words:
                    lyrics.append(word)
            if lyrics:
                for i, word in enumerate(lyrics):
                    notes_in_part = list(part.flatten().notes)
                    if i < len(notes_in_part):
                        notes_in_part[i].addLyric(word)


def _chord_to_midi(chord_name):
    """将和弦名称转为 MIDI 根音（简化版）"""
    root_map = {
        "C": 60, "Cm": 60, "Cmaj7": 60, "C7": 60,
        "D": 62, "Dm": 62, "Dm7": 62, "D7": 62,
        "E": 64, "Em": 64, "Em7": 64,
        "F": 65, "Fmaj7": 65,
        "G": 67, "G7": 67, "G/B": 67,
        "A": 69, "Am": 69, "Am7": 69,
        "B": 71, "Bm": 71,
    }
    # 提取根音
    root = chord_name.split("/")[0]
    for k, v in root_map.items():
        if root.startswith(k):
            return v
    return 60


# ── 输出引擎 ──────────────────────────────────────────────

def export_score(score, args, parts_info):
    """输出各种格式"""
    output_base = args.output
    os.makedirs(os.path.dirname(output_base) or ".", exist_ok=True)
    results = {}

    # MIDI
    if args.mode in ("all", "midi"):
        try:
            mf = midi.translate.music21ObjectToMidiFile(score)
            midi_path = output_base + ".mid"
            mf.open(midi_path, "wb")
            mf.write()
            mf.close()
            results["midi"] = midi_path
        except Exception as e:
            results["midi_error"] = str(e)

    # MusicXML
    if args.mode in ("all", "xml"):
        try:
            xml_path = output_base + ".musicxml"
            score.write("musicxml", fp=xml_path)
            results["musicxml"] = xml_path
        except Exception as e:
            results["musicxml_error"] = str(e)

    # LilyPond
    if args.mode in ("all", "ly"):
        try:
            ly_path = output_base + ".ly"
            score.write("lilypond", fp=ly_path)
            results["lilypond"] = ly_path
        except Exception as e:
            results["lilypond_error"] = str(e)

    # PDF via LilyPond
    if args.mode in ("all", "pdf"):
        try:
            ly_path = output_base + ".ly"
            score.write("lilypond", fp=ly_path)
            pdf_path = output_base + ".pdf"
            subprocess.run(["lilypond", "--output=" + output_base, ly_path],
                         capture_output=True, text=True, timeout=60)
            if os.path.exists(pdf_path):
                results["pdf"] = pdf_path
            else:
                # try alternative name
                base_name = os.path.splitext(os.path.basename(ly_path))[0]
                alt_pdf = os.path.join(os.path.dirname(output_base), base_name + ".pdf")
                if os.path.exists(alt_pdf):
                    results["pdf"] = alt_pdf
        except Exception as e:
            results["pdf_error"] = str(e)

    results["parts"] = parts_info
    return results


# ── 主入口 ──────────────────────────────────────────────

def main():
    args = parse_args()

    print(f"🎵 生成乐谱: key={args.key}, bpm={args.bpm}, "
          f"instruments={args.instruments}, style={args.style}", file=sys.stderr)

    score, parts_info, lyrics = generate_score(args)

    if lyrics:
        print(f"📝 歌词: {len(lyrics)} 行", file=sys.stderr)
    print(f"🎻 声部: {len(parts_info)}", file=sys.stderr)

    results = export_score(score, args, parts_info)

    if args.json:
        print(json.dumps(results, ensure_ascii=False))
    else:
        print(f"\n✅ 输出结果:", file=sys.stderr)
        for fmt, path in results.items():
            if not fmt.endswith("_error"):
                size = os.path.getsize(path) if os.path.exists(path) else 0
                print(f"   {fmt.upper()}: {path} ({size/1024:.1f}KB)", file=sys.stderr)
            else:
                print(f"   ⚠️ {fmt}: {path}", file=sys.stderr)

    # JSON 格式供 skill 调用
    print(json.dumps(results, ensure_ascii=False))


if __name__ == "__main__":
    main()
