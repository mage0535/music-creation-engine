#!/usr/bin/env python3
"""
Demo 音频渲染器 — MIDI → FluidSynth → FFmpeg MP3/OGG

Usage:
  python3 demo_renderer.py --midi ./score.mid --soundfont /usr/share/sounds/sf2/FluidR3_GM.sf2 --output ./demo

输出:
  demo.mp3   - 压缩试听版 (192kbps)
  demo.wav   - 原始无损版
  demo.ogg   - OGG 格式 (可选)
"""
import os, sys, json, argparse, subprocess, shutil


DEFAULT_SF = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
ALTERNATE_SFS = [
    "/usr/share/sounds/sf2/FluidR3_GM.sf2",
    "/usr/share/sounds/sf2/FluidR3_GS.sf2",
    "/usr/share/sounds/sf2/fluid-soundfont.sf2",
    "/usr/share/sounds/sf3/default.sf3",
    "/usr/share/sounds/sf2/default.sf2",
]


def parse_args():
    p = argparse.ArgumentParser(description="Demo 音频渲染器")
    p.add_argument("--midi", "-m", required=True, help="输入 MIDI 文件")
    p.add_argument("--soundfont", "-s", help=f"SoundFont 文件 (默认自动查找)")
    p.add_argument("--output", "-o", default="./demo", help="输出文件基础名")
    p.add_argument("--gain", type=float, default=0.5, help="音量增益 (0.0-1.0)")
    p.add_argument("--sample-rate", type=int, default=44100, help="采样率")
    p.add_argument("--format", default="mp3", help="输出格式: mp3, wav, ogg, all")
    p.add_argument("--json", action="store_true", help="JSON 输出")
    return p.parse_args()


def find_soundfont(path=None):
    if path and os.path.exists(path):
        return path
    for sf in ALTERNATE_SFS:
        if os.path.exists(sf):
            return sf
    # dpkg 查找
    try:
        result = subprocess.run(
            ["dpkg", "-L", "fluid-soundfont-gm"], capture_output=True, text=True, timeout=10)
        for line in result.stdout.splitlines():
            if line.endswith(".sf2"):
                return line.strip()
    except Exception:
        pass
    # find 命令兜底
    try:
        result = subprocess.run(
            ["find", "/usr/share/sounds", "-name", "*.sf2", "-type", "f"],
            capture_output=True, text=True, timeout=10)
        lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
        if lines:
            return lines[0]
    except Exception:
        pass
    return None


def render_wav(midi_path, sf_path, output_wav, sample_rate=44100, gain=0.5):
    """使用 FluidSynth 将 MIDI 渲染为 WAV"""
    if not shutil.which("fluidsynth"):
        raise RuntimeError("fluidsynth 未安装，请 apt install fluidsynth")

    cmd = [
        "fluidsynth", "-ni",
        "-F", output_wav,
        "-g", str(gain),
        "-r", str(sample_rate),
        sf_path,
        midi_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"fluidsynth 失败: {result.stderr[:200]}")
    return output_wav


def convert_to_mp3(wav_path, output_mp3):
    """WAV → MP3"""
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg 未安装")
    cmd = [
        "ffmpeg", "-y", "-i", wav_path,
        "-codec:a", "libmp3lame",
        "-qscale:a", "2",  # ~192kbps, 高音质
        "-ar", "44100",
        output_mp3
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg MP3 转换失败: {result.stderr[:200]}")
    return output_mp3


def convert_to_ogg(wav_path, output_ogg):
    """WAV → OGG"""
    cmd = [
        "ffmpeg", "-y", "-i", wav_path,
        "-codec:a", "libvorbis",
        "-qscale:a", "5",
        output_ogg
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg OGG 转换失败: {result.stderr[:200]}")
    return output_ogg


def main():
    args = parse_args()
    results = {"midi_source": os.path.abspath(args.midi)}

    if not os.path.exists(args.midi):
        print(json.dumps({"error": f"MIDI 文件不存在: {args.midi}"}), ensure_ascii=False)
        sys.exit(1)

    sf_path = find_soundfont(args.soundfont)
    if not sf_path:
        print(json.dumps({"error": "未找到 SoundFont 文件，请安装 fluid-soundfont-gm"}),
              ensure_ascii=False)
        sys.exit(1)
    results["soundfont"] = sf_path

    output_dir = os.path.dirname(args.output) or "."
    os.makedirs(output_dir, exist_ok=True)

    # Stage 1: WAV
    wav_path = args.output + ".wav"
    print(f"🎵 FluidSynth 渲染: {args.midi} → WAV...", file=sys.stderr)
    render_wav(args.midi, sf_path, wav_path, args.sample_rate, args.gain)
    wav_size = os.path.getsize(wav_path)
    results["wav"] = wav_path
    results["wav_size_kb"] = round(wav_size / 1024, 1)

    # Stage 2: MP3
    if args.format in ("mp3", "all"):
        mp3_path = args.output + ".mp3"
        print(f"🎵 FFmpeg 编码: WAV → MP3...", file=sys.stderr)
        convert_to_mp3(wav_path, mp3_path)
        mp3_size = os.path.getsize(mp3_path)
        results["mp3"] = mp3_path
        results["mp3_size_kb"] = round(mp3_size / 1024, 1)
        print(f"   ✅ MP3: {mp3_path} ({results['mp3_size_kb']}KB)", file=sys.stderr)

    # Stage 3: OGG (optional)
    if args.format in ("ogg", "all"):
        ogg_path = args.output + ".ogg"
        print(f"🎵 FFmpeg 编码: WAV → OGG...", file=sys.stderr)
        convert_to_ogg(wav_path, ogg_path)
        ogg_size = os.path.getsize(ogg_path)
        results["ogg"] = ogg_path
        results["ogg_size_kb"] = round(ogg_size / 1024, 1)

    results["status"] = "ok"

    if args.json:
        print(json.dumps(results, ensure_ascii=False))
    else:
        print(f"\n✅ Demo 渲染完成!", file=sys.stderr)
        for k, v in results.items():
            if not k.endswith("_kb") and k != "status":
                print(f"   {k}: {v}", file=sys.stderr)

    if not args.json:
        print(json.dumps(results, ensure_ascii=False))


if __name__ == "__main__":
    main()
