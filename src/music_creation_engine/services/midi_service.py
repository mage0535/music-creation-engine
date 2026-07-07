from __future__ import annotations

from collections import Counter

from music_creation_engine.models import MidiDiffRequest, MidiInspectRequest, MidiQueryRequest


class MidiService:
    def diff(self, request: MidiDiffRequest) -> dict[str, list[int]]:
        left = Counter(request.left_notes)
        right = Counter(request.right_notes)
        added = sorted((right - left).elements())
        removed = sorted((left - right).elements())
        return {"added": added, "removed": removed}

    def inspect(self, request: MidiInspectRequest) -> dict[str, object]:
        notes = request.notes
        if not notes:
            return {"count": 0, "min_pitch": None, "max_pitch": None, "unique_pitches": []}
        return {
            "count": len(notes),
            "min_pitch": min(notes),
            "max_pitch": max(notes),
            "unique_pitches": sorted(set(notes)),
        }

    def query(self, request: MidiQueryRequest) -> dict[str, object]:
        notes = request.notes
        if request.min_pitch is not None:
            notes = [note for note in notes if note >= request.min_pitch]
        if request.max_pitch is not None:
            notes = [note for note in notes if note <= request.max_pitch]
        return {"notes": notes, "count": len(notes)}
