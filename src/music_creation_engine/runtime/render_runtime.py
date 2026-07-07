from __future__ import annotations

import logging
import shutil
import subprocess
import sys
from pathlib import Path

from music_creation_engine.models import ErrorCode, EngineError, RenderRequest

logger = logging.getLogger(__name__)

DEFAULT_SOUNDFONTS_LINUX = (
    "/usr/share/sounds/sf2/FluidR3_GM.sf2",
    "/usr/share/sounds/sf2/fluid-soundfont.sf2",
    "/usr/share/sounds/sf3/default.sf3",
)

DEFAULT_SOUNDFONTS_WINDOWS = (
    "C:\\Windows\\System32\\drivers\\gm.dls",
)


def _find_soundfont(explicit: str | None) -> str | None:
    if explicit and Path(explicit).exists():
        return explicit
    defaults = DEFAULT_SOUNDFONTS_WINDOWS if sys.platform == "win32" else DEFAULT_SOUNDFONTS_LINUX
    for path in defaults:
        if Path(path).exists():
            return path
    return None


def render_demo_artifacts(request: RenderRequest) -> dict[str, object]:
    midi_path = Path(request.midi_path)
    if not midi_path.exists():
        raise EngineError(
            code=ErrorCode.FILE_NOT_FOUND,
            message=f"MIDI file not found: {midi_path}",
            detail=str(midi_path),
        )

    fluidsynth = shutil.which("fluidsynth")
    ffmpeg = shutil.which("ffmpeg")
    soundfont = _find_soundfont(request.soundfont_path)
    if not fluidsynth:
        raise EngineError(code=ErrorCode.MISSING_DEPENDENCY, message="fluidsynth is not installed.")
    if not ffmpeg:
        raise EngineError(code=ErrorCode.MISSING_DEPENDENCY, message="ffmpeg is not installed.")
    if not soundfont:
        raise EngineError(code=ErrorCode.MISSING_DEPENDENCY, message="No SoundFont file found.")

    logger.info("render: start midi=%s output=%s format=%s", midi_path, request.output_base, request.format)

    output_base = Path(request.output_base)
    output_base.parent.mkdir(parents=True, exist_ok=True)
    wav_path = output_base.with_suffix(".wav")
    mp3_path = output_base.with_suffix(".mp3")

    fluidsynth_result = subprocess.run(
        [fluidsynth, "-ni", "-F", str(wav_path), soundfont, str(midi_path)],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if not wav_path.exists():
        logger.error("FluidSynth failed: %s", fluidsynth_result.stderr.strip())
        raise EngineError(code=ErrorCode.RUNTIME_FAILURE, message="FluidSynth did not create a WAV file.")

    logger.info("render: wav created %s", wav_path)

    if request.format in {"mp3", "all"}:
        ffmpeg_result = subprocess.run(
            [ffmpeg, "-y", "-i", str(wav_path), "-codec:a", "libmp3lame", "-qscale:a", "2", str(mp3_path)],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        if not mp3_path.exists():
            logger.error("FFmpeg failed: %s", ffmpeg_result.stderr.strip())
            raise EngineError(code=ErrorCode.RUNTIME_FAILURE, message="FFmpeg did not create an MP3 file.")

        logger.info("render: mp3 created %s", mp3_path)

    result: dict[str, object] = {"status": "ok", "wav": str(wav_path)}
    if mp3_path.exists():
        result["mp3"] = str(mp3_path)
    return result
