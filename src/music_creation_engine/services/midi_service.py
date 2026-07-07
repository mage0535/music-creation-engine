from __future__ import annotations

import logging
from collections import Counter
from pathlib import Path

from music_creation_engine.models import MidiDiffRequest, MidiInspectRequest, MidiQueryRequest

logger = logging.getLogger(__name__)


def _parse_midi_to_notes(midi_path: str) -> list[int]:
    try:
        from music21 import converter
    except ModuleNotFoundError:
        logger.warning("music21 not available for MIDI parsing")
        return []
    score = converter.parse(midi_path)
    notes = [n for n in score.flatten().notes if n.isNote]
    if notes:
        return sorted(int(n.pitch.ps) for n in notes)
    return sorted(int(p.ps) for p in score.pitches)


def _notes_from_request(request: MidiInspectRequest | MidiQueryRequest) -> list[int]:
    if request.notes:
        return request.notes
    if isinstance(request, (MidiInspectRequest, MidiQueryRequest)) and request.midi_path:
        return _parse_midi_to_notes(request.midi_path)
    return []


class MidiService:
    def diff(self, request: MidiDiffRequest) -> dict[str, list[int]]:
        left = Counter(request.left_notes)
        right = Counter(request.right_notes)
        added = sorted((right - left).elements())
        removed = sorted((left - right).elements())
        return {"added": added, "removed": removed}

    def diff_files(self, left_path: str, right_path: str) -> dict[str, list[int]]:
        return self.diff(
            MidiDiffRequest(
                left_notes=_parse_midi_to_notes(left_path),
                right_notes=_parse_midi_to_notes(right_path),
            )
        )

    def inspect(self, request: MidiInspectRequest) -> dict[str, object]:
        notes = _notes_from_request(request)
        if not notes:
            return {"count": 0, "min_pitch": None, "max_pitch": None, "unique_pitches": [], "source": "empty"}
        result: dict[str, object] = {
            "count": len(notes),
            "min_pitch": min(notes),
            "max_pitch": max(notes),
            "unique_pitches": sorted(set(notes)),
        }
        if request.midi_path:
            result["source"] = request.midi_path
        return result

    def query(self, request: MidiQueryRequest) -> dict[str, object]:
        notes = _notes_from_request(request)
        if request.min_pitch is not None:
            notes = [note for note in notes if note >= request.min_pitch]
        if request.max_pitch is not None:
            notes = [note for note in notes if note <= request.max_pitch]
        return {"notes": notes, "count": len(notes)}
