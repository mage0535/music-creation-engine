from __future__ import annotations

import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from music_creation_engine.models import ArtifactManifest
from music_creation_engine.models import RenderRequest, ScoreRequest, WorkflowRequest
from music_creation_engine.services.artifact_service import ArtifactService
from music_creation_engine.services.render_service import RenderService
from music_creation_engine.services.score_service import ScoreService

SCORE_AFFECTING_FIELDS = (
    "lyrics",
    "key",
    "bpm",
    "instruments",
    "style",
    "chord_progression",
    "sections",
    "melody",
    "instrument_roles",
)


@dataclass
class WorkflowService:
    score_service: ScoreService
    render_service: RenderService
    artifact_service: ArtifactService | None = None

    def _artifact_service(self) -> ArtifactService:
        if self.artifact_service is None:
            self.artifact_service = ArtifactService("build/workflows")
        return self.artifact_service

    def _score_request_for(self, request: WorkflowRequest, output_base: str) -> ScoreRequest:
        return ScoreRequest(
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

    def _score_signature(self, request: WorkflowRequest) -> dict[str, Any]:
        normalized = self._score_request_for(request, output_base="build/output/signature")
        return {
            "lyrics": normalized.lyrics,
            "key": normalized.key,
            "bpm": normalized.bpm,
            "instruments": normalized.instruments,
            "style": normalized.style,
            "chord_progression": normalized.chord_progression,
            "sections": normalized.sections,
            "melody": normalized.melody,
            "instrument_roles": normalized.instrument_roles,
        }

    def _copy_result_artifacts(self, payload: dict[str, Any] | None, target_output_base: str) -> dict[str, Any] | None:
        if payload is None:
            return None
        target_dir = Path(target_output_base).parent
        target_dir.mkdir(parents=True, exist_ok=True)
        copied: dict[str, Any] = {}
        for key, value in payload.items():
            if isinstance(value, str):
                source_path = Path(value)
                if source_path.exists() and source_path.is_file():
                    destination = target_dir / source_path.name
                    if source_path.resolve() != destination.resolve():
                        shutil.copy2(source_path, destination)
                    copied[key] = str(destination)
                    continue
            copied[key] = value
        return copied

    def _build_manifest(
        self,
        workflow_id: str,
        request: WorkflowRequest,
        score_result: dict[str, Any],
        render_result: dict[str, Any] | None,
    ) -> ArtifactManifest:
        service = self._artifact_service()
        return ArtifactManifest(
            workflow_id=workflow_id,
            score=score_result,
            render=render_result,
            request=asdict(request),
            checkpoints=service.load_checkpoints(workflow_id),
        )

    def run_full(self, request: WorkflowRequest, workflow_id: str | None = None) -> dict[str, object]:
        service = self._artifact_service()
        workflow_id = workflow_id or service.create_workflow_id()
        artifacts_dir = service.artifacts_subdir(workflow_id)
        output_base = str(artifacts_dir / "composition")
        score_result = self.score_service.generate(self._score_request_for(request, output_base))
        service.save_checkpoint(workflow_id, "score", score_result)
        render_result = None
        if request.render_demo and "midi" in score_result:
            render_result = self.render_service.render(
                RenderRequest(
                    midi_path=score_result["midi"],
                    output_base=output_base,
                )
            )
            service.save_checkpoint(workflow_id, "render", render_result)
        manifest = self._build_manifest(workflow_id, request, score_result, render_result)
        service.save_manifest(manifest)
        return {"workflow_id": workflow_id, "score": score_result, "render": render_result}

    def revise(self, workflow_id: str, request: WorkflowRequest) -> dict[str, object]:
        service = self._artifact_service()
        parent_manifest = service.load_manifest(workflow_id)
        parent_request = WorkflowRequest(**parent_manifest["request"])
        if self._score_signature(parent_request) != self._score_signature(request):
            result = self.run_full(request)
            result["revision_of"] = workflow_id
            result["reused_stages"] = []
            return result

        new_workflow_id = service.create_workflow_id()
        output_base = str(service.artifacts_subdir(new_workflow_id) / "composition")
        copied_score = self._copy_result_artifacts(parent_manifest.get("score"), output_base) or {}
        reused_stages = ["score"]
        score_checkpoint = dict(copied_score)
        score_checkpoint["reused_from"] = workflow_id
        service.save_checkpoint(new_workflow_id, "score", score_checkpoint)

        render_result = None
        parent_render = parent_manifest.get("render")
        if request.render_demo:
            if parent_request.render_demo and parent_render:
                render_result = self._copy_result_artifacts(parent_render, output_base)
                if render_result is not None:
                    reused_stages.append("render")
                    render_checkpoint = dict(render_result)
                    render_checkpoint["reused_from"] = workflow_id
                    service.save_checkpoint(new_workflow_id, "render", render_checkpoint)
            elif copied_score.get("midi"):
                render_result = self.render_service.render(
                    RenderRequest(midi_path=copied_score["midi"], output_base=output_base)
                )
                service.save_checkpoint(new_workflow_id, "render", render_result)

        manifest = self._build_manifest(new_workflow_id, request, copied_score, render_result)
        service.save_manifest(manifest)
        return {
            "workflow_id": new_workflow_id,
            "score": copied_score,
            "render": render_result,
            "revision_of": workflow_id,
            "reused_stages": reused_stages,
        }
