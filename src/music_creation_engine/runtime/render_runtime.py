from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from music_creation_engine.models import RenderRequest


DEFAULT_SOUNDFONTS = (
    "/usr/share/sounds/sf2/FluidR3_GM.sf2",
    "/usr/share/sounds/sf2/fluid-soundfont.sf2",
    "/usr/share/sounds/sf3/default.sf3",
)


def _find_soundfont(explicit: str | None) -> str | None:
    if explicit and Path(explicit).exists():
        return explicit
    for path in DEFAULT_SOUNDFONTS:
        if Path(path).exists():
            return path
    return None


def render_demo_artifacts(request: RenderRequest) -> dict[str, object]:
    midi_path = Path(request.midi_path)
    if not midi_path.exists():
        raise RuntimeError(f"MIDI file not found: {midi_path}")

    fluidsynth = shutil.which("fluidsynth")
    ffmpeg = shutil.which("ffmpeg")
    soundfont = _find_soundfont(request.soundfont_path)
    if not fluidsynth:
        raise RuntimeError("fluidsynth is not installed.")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is not installed.")
    if not soundfont:
        raise RuntimeError("No SoundFont file found.")

    output_base = Path(request.output_base)
    output_base.parent.mkdir(parents=True, exist_ok=True)
    wav_path = output_base.with_suffix(".wav")
    mp3_path = output_base.with_suffix(".mp3")

    subprocess.run(
        [fluidsynth, "-ni", "-F", str(wav_path), soundfont, str(midi_path)],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if not wav_path.exists():
        raise RuntimeError("FluidSynth did not create a WAV file.")

    if request.format in {"mp3", "all"}:
        subprocess.run(
            [ffmpeg, "-y", "-i", str(wav_path), "-codec:a", "libmp3lame", "-qscale:a", "2", str(mp3_path)],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        if not mp3_path.exists():
            raise RuntimeError("FFmpeg did not create an MP3 file.")

    result: dict[str, object] = {"status": "ok", "wav": str(wav_path)}
    if mp3_path.exists():
        result["mp3"] = str(mp3_path)
    return result
