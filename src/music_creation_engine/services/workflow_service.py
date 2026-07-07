from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from music_creation_engine.models import ArtifactManifest
from music_creation_engine.models import RenderRequest, ScoreRequest, WorkflowRequest
from music_creation_engine.services.artifact_service import ArtifactService
from music_creation_engine.services.render_service import RenderService
from music_creation_engine.services.score_service import ScoreService


@dataclass
class WorkflowService:
    score_service: ScoreService
    render_service: RenderService
    artifact_service: ArtifactService | None = None

    def run_full(self, request: WorkflowRequest, workflow_id: str | None = None) -> dict[str, object]:
        if self.artifact_service is None:
            self.artifact_service = ArtifactService("build/workflows")
        workflow_id = workflow_id or self.artifact_service.create_workflow_id()
        artifacts_dir = self.artifact_service.artifacts_subdir(workflow_id)
        output_base = str(artifacts_dir / "composition")
        score_result = self.score_service.generate(
            ScoreRequest(
                lyrics=request.lyrics,
                output_base=output_base,
                key=request.key,
                bpm=request.bpm,
                instruments=request.instruments,
                style=request.style,
                chord_progression=request.chord_progression,
                sections=request.sections,
                melody=request.melody,
                instrument_roles=request.instrument_roles,
            )
        )
        self.artifact_service.save_checkpoint(workflow_id, "score", score_result)
        render_result = None
        if request.render_demo and "midi" in score_result:
            render_result = self.render_service.render(
                RenderRequest(
                    midi_path=score_result["midi"],
                    output_base=output_base,
                )
            )
            self.artifact_service.save_checkpoint(workflow_id, "render", render_result)
        manifest = ArtifactManifest(
            workflow_id=workflow_id,
            score=score_result,
            render=render_result,
            request=asdict(request),
            checkpoints=self.artifact_service.load_checkpoints(workflow_id),
        )
        self.artifact_service.save_manifest(manifest)
        return {"workflow_id": workflow_id, "score": score_result, "render": render_result}
