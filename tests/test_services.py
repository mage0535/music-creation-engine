from pathlib import Path

from music_creation_engine.models import (
    RenderRequest,
    ScoreRequest,
    WorkflowRequest,
)
from music_creation_engine.services.render_service import RenderService
from music_creation_engine.services.score_service import ScoreService
from music_creation_engine.services.workflow_service import WorkflowService


class FakeScoreBackend:
    def generate(self, request: ScoreRequest):
        return {
            "midi": str(Path(request.output_base).with_suffix(".mid")),
            "pdf": str(Path(request.output_base).with_suffix(".pdf")),
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
        )
    )

    assert result["midi"].endswith("song.mid")


def test_workflow_service_runs_score_then_render(tmp_path):
    workflow = WorkflowService(
        score_service=ScoreService(backend=FakeScoreBackend()),
        render_service=RenderService(backend=FakeRenderBackend()),
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
