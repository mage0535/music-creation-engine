from pathlib import Path

from music_creation_engine.models import (
    MidiDiffRequest,
    PlayabilityRequest,
    RenderRequest,
    ScoreRequest,
    WorkflowRequest,
)
from music_creation_engine.services.artifact_service import ArtifactService
from music_creation_engine.services.midi_service import MidiService
from music_creation_engine.services.playability_service import PlayabilityService
from music_creation_engine.services.render_service import RenderService
from music_creation_engine.services.score_service import ScoreService
from music_creation_engine.services.workflow_service import WorkflowService


class FakeScoreBackend:
    def generate(self, request: ScoreRequest):
        return {
            "midi": str(Path(request.output_base).with_suffix(".mid")),
            "pdf": str(Path(request.output_base).with_suffix(".pdf")),
            "request_echo": {
                "chord_progression": request.chord_progression,
                "sections": request.sections,
                "melody": request.melody,
                "instrument_roles": request.instrument_roles,
            },
        }


class FakeRenderBackend:
    def render(self, request: RenderRequest):
        return {
            "mp3": str(Path(request.output_base).with_suffix(".mp3")),
        }


def test_score_service_returns_artifact_map(tmp_path):
    service = ScoreService(backend=FakeScoreBackend())

    result = service.generate(
        ScoreRequest(
            lyrics="hello world",
            output_base=str(tmp_path / "song"),
            chord_progression=["Am", "F", "C", "G"],
            sections=[{"name": "verse", "bars": 8}],
            melody={"vocals": [60, 62, 64]},
            instrument_roles={"piano": "chord", "vocals": "melody"},
        )
    )

    assert result["midi"].endswith("song.mid")
    assert result["request_echo"]["chord_progression"] == ["Am", "F", "C", "G"]


def test_workflow_service_runs_score_then_render(tmp_path):
    artifact_service = ArtifactService(base_dir=tmp_path)
    workflow = WorkflowService(
        score_service=ScoreService(backend=FakeScoreBackend()),
        render_service=RenderService(backend=FakeRenderBackend()),
        artifact_service=artifact_service,
    )

    result = workflow.run_full(
        WorkflowRequest(
            lyrics="hello world",
            output_base=str(tmp_path / "song"),
            render_demo=True,
        )
    )

    assert result["score"]["pdf"].endswith("song.pdf")
    assert result["render"]["mp3"].endswith("song.mp3")
    assert result["workflow_id"]
    manifest = artifact_service.load_manifest(result["workflow_id"])
    assert manifest["score"]["pdf"].endswith("song.pdf")


def test_midi_service_can_diff_simple_note_lists():
    service = MidiService()

    result = service.diff(
        MidiDiffRequest(
            left_notes=[60, 62, 64],
            right_notes=[60, 64, 65],
        )
    )

    assert result["added"] == [65]
    assert result["removed"] == [62]


def test_playability_service_flags_large_piano_span():
    service = PlayabilityService()

    result = service.evaluate(
        PlayabilityRequest(
            instrument="piano",
            notes=[48, 60, 72, 84],
        )
    )

    assert result["playable"] is False
    assert result["warnings"]
