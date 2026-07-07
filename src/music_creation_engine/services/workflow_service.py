from __future__ import annotations

from dataclasses import dataclass

from music_creation_engine.models import RenderRequest, ScoreRequest, WorkflowRequest
from music_creation_engine.services.render_service import RenderService
from music_creation_engine.services.score_service import ScoreService


@dataclass
class WorkflowService:
    score_service: ScoreService
    render_service: RenderService

    def run_full(self, request: WorkflowRequest) -> dict[str, object]:
        score_result = self.score_service.generate(
            ScoreRequest(
                lyrics=request.lyrics,
                output_base=request.output_base,
                key=request.key,
                bpm=request.bpm,
                instruments=request.instruments,
                style=request.style,
            )
        )
        render_result = None
        if request.render_demo and "midi" in score_result:
            render_result = self.render_service.render(
                RenderRequest(
                    midi_path=score_result["midi"],
                    output_base=request.output_base,
                )
            )
        return {"score": score_result, "render": render_result}
