from __future__ import annotations

from music_creation_engine.models import PlayabilityRequest


class PlayabilityService:
    def evaluate(self, request: PlayabilityRequest) -> dict[str, object]:
        notes = request.notes
        warnings: list[str] = []
        playable = True
        if not notes:
            return {"playable": True, "warnings": warnings}
        span = max(notes) - min(notes)
        if request.instrument == "piano" and span > 24:
            playable = False
            warnings.append(f"Pitch span {span} exceeds practical two-hand comfort range.")
        leaps = [abs(notes[index + 1] - notes[index]) for index in range(len(notes) - 1)]
        if any(leap > 12 for leap in leaps):
            warnings.append("Contains leaps larger than an octave.")
        if warnings and playable:
            playable = False
        return {"playable": playable, "warnings": warnings}
