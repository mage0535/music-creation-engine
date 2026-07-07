from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

from music_creation_engine.models import ErrorCode, EngineError, ScoreRequest

logger = logging.getLogger(__name__)


def _load_music21():
    try:
        from music21 import chord, instrument, key, meter, metadata, midi, note, stream, tempo
    except ModuleNotFoundError as exc:
        raise EngineError(
            code=ErrorCode.MISSING_DEPENDENCY,
            message="music21 is not installed. Install the music extra or run install.sh first.",
        ) from exc
    return chord, instrument, key, meter, metadata, midi, note, stream, tempo


INSTRUMENT_FACTORY = {
    "piano": "Piano",
    "vocals": "Vocalist",
    "guitar": "AcousticGuitar",
    "bass": "ElectricBass",
    "drums": "Woodblock",
    "strings": "Violin",
    "flute": "Flute",
    "sax": "AltoSaxophone",
    "trumpet": "Trumpet",
    "synth": "Vibraphone",
}


CHORD_PROGRESSIONS = {
    "pop": ["C", "G", "Am", "F"],
    "rock": ["C", "G", "F", "C"],
    "ballad": ["C", "Am", "F", "G"],
    "jazz": ["Cmaj7", "Dm7", "G7", "Cmaj7"],
    "folk": ["C", "F", "C", "G"],
}


def _chord_root_midi(chord_name: str) -> int:
    base = chord_name.split("/")[0]
    mapping = {
        "C": 60, "Cm": 60, "Cmaj7": 60,
        "D": 62, "Dm": 62, "Dm7": 62,
        "E": 64, "Em": 64,
        "F": 65,
        "G": 67, "G7": 67,
        "A": 69, "Am": 69,
        "B": 71, "Bm": 71,
    }
    return mapping.get(base, 60)


def _section_measure_count(request: ScoreRequest) -> int:
    if request.sections:
        return sum(int(section.get("bars", 0)) for section in request.sections) or 4
    return max(4, len([line for line in request.lyrics.splitlines() if line.strip()]) or 4)


def _build_part(stream_mod, note_mod, chord_mod, instrument_mod, name: str, measures: int, request: ScoreRequest):
    part = stream_mod.Part()
    instrument_name = INSTRUMENT_FACTORY.get(name, "Piano")
    part.insert(0, getattr(instrument_mod, instrument_name)())
    role = request.instrument_roles.get(name, "chord" if name == "piano" else "melody")
    progression = request.chord_progression or CHORD_PROGRESSIONS.get(request.style, CHORD_PROGRESSIONS["pop"])
    melody = request.melody.get(name, [])

    if name == "drums":
        for _ in range(measures):
            for midi_pitch in (36, 42, 38, 42):
                drum = note_mod.Unpitched(midi_pitch)
                drum.quarterLength = 1
                part.append(drum)
        return part

    base_map = {
        "piano": [60, 64, 67, 72],
        "vocals": [67, 69, 71, 72],
        "guitar": [55, 59, 62, 67],
        "bass": [36, 36, 43, 43],
        "strings": [64, 67, 71, 76],
        "flute": [72, 74, 76, 79],
        "sax": [65, 67, 69, 72],
        "trumpet": [67, 69, 71, 74],
        "synth": [68, 72, 75, 79],
    }
    pitches = base_map.get(name, base_map["piano"])
    for index in range(measures):
        if role == "bass":
            pitch = _chord_root_midi(progression[index % len(progression)]) - 24
            item = note_mod.Note(pitch)
            item.quarterLength = 4
            part.append(item)
            continue
        if role == "pad":
            root = _chord_root_midi(progression[index % len(progression)])
            chord_note = chord_mod.Chord([root, root + 4, root + 7])
            chord_note.quarterLength = 4
            part.append(chord_note)
            continue
        if role == "chord" or name == "piano":
            root = _chord_root_midi(progression[index % len(progression)])
            chord_note = chord_mod.Chord([root, root + 4, root + 7])
            chord_note.quarterLength = 4
            part.append(chord_note)
            continue
        if melody:
            pitch = melody[index % len(melody)]
            item = note_mod.Note(pitch)
            item.quarterLength = 1
            part.append(item)
            continue
        for pitch in pitches:
            item = note_mod.Note(pitch)
            item.quarterLength = 1
            part.append(item)
    return part


def generate_score_artifacts(request: ScoreRequest) -> dict[str, object]:
    chord_mod, instrument_mod, key_mod, meter_mod, metadata_mod, midi_mod, note_mod, stream_mod, tempo_mod = _load_music21()

    output_base = Path(request.output_base)
    output_base.parent.mkdir(parents=True, exist_ok=True)
    instruments = [item.strip() for item in request.instruments.split(",") if item.strip()]
    measures = _section_measure_count(request)

    logger.info(
        "score: start key=%s bpm=%d instruments=%s measures=%d output=%s",
        request.key, request.bpm, instruments, measures, output_base,
    )

    score = stream_mod.Score()
    score.insert(0, metadata_mod.Metadata(title=output_base.stem.replace("_", " ").title()))
    score.insert(0, tempo_mod.MetronomeMark(number=request.bpm))
    score.insert(0, key_mod.Key(request.key))
    score.insert(0, meter_mod.TimeSignature(request.time_signature))

    if request.sections:
        score.metadata.movementName = ",".join(
            f"{section.get('name','section')}:{section.get('bars',0)}" for section in request.sections
        )

    for instrument_name in instruments:
        part = _build_part(stream_mod, note_mod, chord_mod, instrument_mod, instrument_name, measures, request)
        part.partName = instrument_name
        score.append(part)

    lyric_words = [word for line in request.lyrics.splitlines() for word in line.split()]
    for part in score.parts:
        if "vocal" in (part.partName or "").lower():
            notes = list(part.flatten().notes)
            for index, word in enumerate(lyric_words):
                if index < len(notes):
                    notes[index].addLyric(word)

    results: dict[str, object] = {
        "status": "ok",
        "parts": instruments,
        "request_echo": {
            "chord_progression": request.chord_progression,
            "sections": request.sections,
            "melody": request.melody,
            "instrument_roles": request.instrument_roles,
        },
    }
    midi_path = output_base.with_suffix(".mid")
    mf = midi_mod.translate.music21ObjectToMidiFile(score)
    mf.open(str(midi_path), "wb")
    mf.write()
    mf.close()
    results["midi"] = str(midi_path)
    logger.info("score: midi written %s", midi_path)

    xml_path = output_base.with_suffix(".musicxml")
    score.write("musicxml", fp=str(xml_path))
    results["musicxml"] = str(xml_path)
    logger.info("score: musicxml written %s", xml_path)

    ly_path = output_base.with_suffix(".ly")
    try:
        score.write("lilypond", fp=str(ly_path))
        results["lilypond"] = str(ly_path)
        logger.info("score: lilypond written %s", ly_path)
        lilypond = shutil.which("lilypond")
        if lilypond:
            subprocess.run(
                [lilypond, f"--output={output_base}", str(ly_path)],
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
            )
            pdf_path = output_base.with_suffix(".pdf")
            if pdf_path.exists():
                results["pdf"] = str(pdf_path)
                logger.info("score: pdf rendered %s", pdf_path)
            else:
                logger.warning("score: lilypond ran but no pdf at %s", pdf_path)
    except Exception as exc:
        logger.warning("score: lilypond error: %s", exc)
        results["lilypond_error"] = str(exc)

    return results
