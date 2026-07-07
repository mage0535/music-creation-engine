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
            message="music21 is not installed. Run: pip install music-creation-engine[music]",
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


def _resolve_sections(request: ScoreRequest) -> list[dict[str, object]]:
    if request.sections:
        return request.sections
    lyrics_lines = len([line for line in request.lyrics.splitlines() if line.strip()]) or 4
    return [{"name": "song", "bars": lyrics_lines, "key": request.key}]


def _append_bars_for_section(
    stream_mod, note_mod, chord_mod, part, request: ScoreRequest,
    instrument_name: str, section: dict[str, object], section_start_bar: int,
) -> None:
    bars = int(section.get("bars", 4))
    role = request.instrument_roles.get(instrument_name, "chord" if instrument_name == "piano" else "melody")
    progression = request.chord_progression or CHORD_PROGRESSIONS.get(request.style, CHORD_PROGRESSIONS["pop"])
    melody = request.melody.get(instrument_name, [])

    if instrument_name == "drums":
        for _ in range(bars):
            for midi_pitch in (36, 42, 38, 42):
                drum = note_mod.Unpitched(midi_pitch)
                drum.quarterLength = 1
                part.append(drum)
        return

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
    pitches = base_map.get(instrument_name, base_map["piano"])

    for i in range(bars):
        chord_idx = (section_start_bar + i) % len(progression)
        if role == "bass":
            pitch = _chord_root_midi(progression[chord_idx]) - 24
            item = note_mod.Note(pitch)
            item.quarterLength = 4
            part.append(item)
            continue
        if role == "pad":
            root = _chord_root_midi(progression[chord_idx])
            chord_note = chord_mod.Chord([root, root + 4, root + 7])
            chord_note.quarterLength = 4
            part.append(chord_note)
            continue
        if role == "chord" or instrument_name == "piano":
            root = _chord_root_midi(progression[chord_idx])
            chord_note = chord_mod.Chord([root, root + 4, root + 7])
            chord_note.quarterLength = 4
            part.append(chord_note)
            continue
        if melody:
            note_idx = (section_start_bar + i) % len(melody)
            pitch = melody[note_idx]
            item = note_mod.Note(pitch)
            item.quarterLength = 1
            part.append(item)
            continue
        for pitch in pitches:
            item = note_mod.Note(pitch)
            item.quarterLength = 1
            part.append(item)


def generate_score_artifacts(request: ScoreRequest) -> dict[str, object]:
    chord_mod, instrument_mod, key_mod, meter_mod, metadata_mod, midi_mod, note_mod, stream_mod, tempo_mod = _load_music21()

    output_base = Path(request.output_base)
    output_base.parent.mkdir(parents=True, exist_ok=True)
    instruments = [item.strip() for item in request.instruments.split(",") if item.strip()]
    sections = _resolve_sections(request)
    total_measures = sum(int(s.get("bars", 4)) for s in sections)

    score = stream_mod.Score()
    score.insert(0, metadata_mod.Metadata(title=output_base.stem.replace("_", " ").title()))
    score.insert(0, tempo_mod.MetronomeMark(number=request.bpm))
    score.insert(0, key_mod.Key(request.key))
    score.insert(0, meter_mod.TimeSignature(request.time_signature))

    logger.info(
        "score: start key=%s bpm=%d instruments=%s measures=%d sections=%d output=%s",
        request.key, request.bpm, instruments, total_measures, len(sections), output_base,
    )

    parts: dict[str, object] = {}
    for instrument_name in instruments:
        part = stream_mod.Part()
        instrument_class = INSTRUMENT_FACTORY.get(instrument_name, "Piano")
        part.insert(0, getattr(instrument_mod, instrument_class)())
        part.partName = instrument_name
        parts[instrument_name] = part

    section_start_bar = 0
    for section in sections:
        section_bars = int(section.get("bars", 4))
        section_key = section.get("key", request.key)
        section_instruments_str = section.get("instruments", "")
        section_parts = instruments
        if section_instruments_str:
            section_parts = [s.strip() for s in str(section_instruments_str).split(",") if s.strip()]

        if section_key != request.key:
            for part_obj in parts.values():
                ks = key_mod.Key(section_key)
                part_obj.append(ks)

        for inst_name in section_parts:
            if inst_name in parts:
                _append_bars_for_section(
                    stream_mod, note_mod, chord_mod, parts[inst_name],
                    request, inst_name, section, section_start_bar,
                )

        section_start_bar += section_bars

    for instrument_name in instruments:
        score.append(parts[instrument_name])

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
        "sections": sections,
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
