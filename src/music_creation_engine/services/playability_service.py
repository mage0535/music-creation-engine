from __future__ import annotations

from music_creation_engine.models import PlayabilityRequest

INSTRUMENT_RANGES = {
    "piano": (21, 108),
    "vocals": (55, 84),
    "guitar": (40, 84),
    "bass": (28, 60),
    "violin": (55, 106),
    "flute": (60, 98),
    "sax": (49, 81),
    "trumpet": (55, 82),
    "cello": (36, 72),
}


class PlayabilityService:
    def evaluate(self, request: PlayabilityRequest) -> dict[str, object]:
        notes = request.notes
        warnings: list[str] = []
        if not notes:
            return {"playable": True, "warnings": [], "instrument": request.instrument}

        low, high = min(notes), max(notes)
        playable = True
        inst = request.instrument

        if inst in INSTRUMENT_RANGES:
            inst_low, inst_high = INSTRUMENT_RANGES[inst]
            if low < inst_low:
                playable = False
                warnings.append(f"Lowest pitch {low} is below {inst} range (≥{inst_low}).")
            if high > inst_high:
                playable = False
                warnings.append(f"Highest pitch {high} exceeds {inst} range (≤{inst_high}).")

        if inst == "piano":
            span = high - low
            if span > 24:
                playable = False
                warnings.append(f"Pitch span {span} exceeds two-hand comfort range (≤24 semitones).")

        if inst in ("guitar", "bass"):
            max_leap = max(abs(notes[i + 1] - notes[i]) for i in range(len(notes) - 1)) if len(notes) > 1 else 0
            if max_leap > 12:
                warnings.append(f"Contains leap of {max_leap} semitones — may require position shift on {inst}.")

        leaps = [abs(notes[i + 1] - notes[i]) for i in range(len(notes) - 1)]
        if any(leap > 12 for leap in leaps) and inst not in ("guitar", "bass"):
            warnings.append("Contains leaps larger than an octave.")

        if inst == "piano" and len(notes) > 1:
            mid = (low + high) // 2
            left_hand = [n for n in notes if n <= mid]
            right_hand = [n for n in notes if n > mid]
            if left_hand and max(left_hand) - min(left_hand) > 12:
                warnings.append("Left-hand span exceeds one octave — may be unplayable for some players.")
            if right_hand and max(right_hand) - min(right_hand) > 12:
                warnings.append("Right-hand span exceeds one octave — may be unplayable for some players.")
            if len(notes) > 10:
                warnings.append("More than 10 simultaneous notes — likely unplayable on piano.")

        if warnings and playable:
            playable = False

        return {"playable": playable, "warnings": warnings, "instrument": inst}
