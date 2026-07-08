from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from music_creation_engine.models import ScoreRequest
from music_creation_engine.services.score_service import ScoreService


@pytest.mark.skipif(importlib.util.find_spec("music21") is None, reason="music21 not installed")
def test_real_score_service_generates_parseable_midi(tmp_path):
    service = ScoreService()
    output_base = tmp_path / "real_song"

    result = service.generate(
        ScoreRequest(
            lyrics="hello world\nthis is a real integration test",
            output_base=str(output_base),
            key="Am",
            bpm=72,
            instruments="piano,vocals",
            chord_progression=["Am", "F", "C", "G"],
            sections=[{"name": "verse", "bars": 4, "key": "Am"}],
            melody={"vocals": ["A4", "B4", "C5", "A4"]},
            instrument_roles={"piano": "chord", "vocals": "melody"},
        )
    )

    midi_path = Path(result["midi"])
    assert midi_path.exists()
    assert midi_path.stat().st_size > 0

    from music21 import converter

    parsed = converter.parse(str(midi_path))
    notes = list(parsed.flatten().notes)
    assert notes
    assert len(parsed.parts) >= 1
