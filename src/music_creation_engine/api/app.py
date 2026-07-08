from __future__ import annotations

import json
import logging
import threading
from typing import Any, Union

from fastapi import FastAPI, Query, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from music_creation_engine.capabilities import detect_capabilities
from music_creation_engine.config import load_settings
from music_creation_engine.integrations.meting import MetingIntegration
from music_creation_engine.models import (
    EngineError,
    ErrorCode,
    MidiDiffRequest,
    MidiInspectRequest,
    MidiQueryRequest,
    MidiTransformRequest,
    PlayabilityRequest,
    ReferenceSearchRequest,
    RenderRequest,
    ScoreRequest,
    WorkflowRequest,
    WorkflowRevisionRequest,
)
from music_creation_engine.security import RequestGate
from music_creation_engine.services.artifact_service import ArtifactService
from music_creation_engine.services.midi_service import MidiService
from music_creation_engine.services.playability_service import PlayabilityService
from music_creation_engine.services.reference_service import ReferenceService
from music_creation_engine.services.render_service import RenderService
from music_creation_engine.services.score_service import ScoreService
from music_creation_engine.services.workflow_service import WorkflowService

logger = logging.getLogger(__name__)


class ReferenceSearchBody(BaseModel):
    keyword: str
    platform: str = "netease"


class ScoreBody(BaseModel):
    lyrics: str
    output_base: str
    key: str = "C"
    bpm: int = 120
    time_signature: str = "4/4"
    instruments: str = "piano,vocals"
    style: str = "pop"
    mode: str = "all"
    chord_progression: list[str] = []
    sections: list[dict] = []
    melody: dict[str, list[Union[int, str]]] = {}
    instrument_roles: dict[str, str] = {}


class WorkflowBody(BaseModel):
    lyrics: str
    output_base: str
    key: str = "C"
    bpm: int = 120
    instruments: str = "piano,vocals"
    style: str = "pop"
    render_demo: bool = True
    chord_progression: list[str] = []
    sections: list[dict] = []
    melody: dict[str, list[Union[int, str]]] = {}
    instrument_roles: dict[str, str] = {}


class RenderBody(BaseModel):
    midi_path: str
    output_base: str
    format: str = "mp3"
    soundfont_path: str | None = None


class MidiDiffBody(BaseModel):
    left_notes: list[int]
    right_notes: list[int]


class MidiInspectBody(BaseModel):
    notes: list[int] = []
    midi_path: str | None = None


class MidiQueryBody(BaseModel):
    notes: list[int] = []
    midi_path: str | None = None
    min_pitch: int | None = None
    max_pitch: int | None = None


class MidiDiffFilesBody(BaseModel):
    left_path: str
    right_path: str


class MidiTransformBody(BaseModel):
    notes: list[int]
    operation: str
    semitones: int = 0
    start: int = 0
    end: int = 0
    replacement: list[int] = []


class PlayabilityBody(BaseModel):
    instrument: str
    notes: list[int]


class RevisionBody(BaseModel):
    sections: list[dict] = []
    chord_progression: list[str] = []
    melody: dict[str, list[Union[int, str]]] = {}
    instrument_roles: dict[str, str] = {}
    key: str = ""
    bpm: int = 0
    instruments: str = ""
    style: str = ""
    render_demo: bool | None = None


class WorkflowListBody(BaseModel):
    pass


def _build_score_request(body: ScoreBody | WorkflowBody) -> ScoreRequest:
    return ScoreRequest(
        lyrics=body.lyrics,
        output_base=body.output_base,
        key=body.key,
        bpm=body.bpm,
        time_signature=getattr(body, "time_signature", "4/4"),
        instruments=body.instruments,
        style=body.style,
        mode=getattr(body, "mode", "all"),
        chord_progression=body.chord_progression,
        sections=body.sections,
        melody=body.melody,
        instrument_roles=body.instrument_roles,
    )


def _build_workflow_request(body: WorkflowBody) -> WorkflowRequest:
    return WorkflowRequest(
        lyrics=body.lyrics,
        output_base=body.output_base,
        key=body.key,
        bpm=body.bpm,
        instruments=body.instruments,
        style=body.style,
        render_demo=body.render_demo,
        chord_progression=body.chord_progression,
        sections=body.sections,
        melody=body.melody,
        instrument_roles=body.instrument_roles,
    )


def _async_set_status(artifact_service: ArtifactService, workflow_id: str, status: str, result: Any = None) -> None:
    status_path = artifact_service.workflow_dir(workflow_id) / "status.json"
    data: dict[str, Any] = {"status": status}
    if result:
        data["result"] = result
    status_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _run_workflow_async(workflow_id: str, service: WorkflowService, artifact_service: ArtifactService, request: WorkflowRequest) -> None:
    try:
        if artifact_service.is_cancel_requested(workflow_id):
            _async_set_status(artifact_service, workflow_id, "cancelled")
            return
        result = service.run_full(request, workflow_id=workflow_id)
        if artifact_service.is_cancel_requested(workflow_id):
            _async_set_status(artifact_service, workflow_id, "cancelled", result)
            return
        _async_set_status(artifact_service, workflow_id, "completed", result)
    except Exception as exc:
        logger.exception("async workflow %s failed", workflow_id)
        _async_set_status(artifact_service, workflow_id, "failed", {"error": str(exc)})


def create_app() -> FastAPI:
    app = FastAPI(title="Music Creation Engine")
    settings = load_settings(resolve_paths=True)
    request_gate = RequestGate(settings.security)
    score_service = ScoreService()
    render_service = RenderService()
    artifact_service = ArtifactService(settings.project.workflow_dir)
    workflow_service = WorkflowService(
        score_service=score_service,
        render_service=render_service,
        artifact_service=artifact_service,
    )
    midi_service = MidiService()
    playability_service = PlayabilityService()

    @app.middleware("http")
    async def security_middleware(request: Request, call_next):
        decision = request_gate.validate(request)
        if not decision.allowed:
            headers = {}
            if decision.retry_after_seconds is not None:
                headers["Retry-After"] = str(decision.retry_after_seconds)
            return JSONResponse(status_code=decision.status_code, content=decision.payload or {}, headers=headers)
        return await call_next(request)

    @app.exception_handler(EngineError)
    async def engine_error_handler(_request: Request, exc: EngineError) -> JSONResponse:
        logger.error("api: EngineError code=%s message=%s detail=%s", exc.code.value, exc.message, exc.detail)
        return JSONResponse(status_code=400, content=exc.to_dict())

    @app.exception_handler(Exception)
    async def generic_error_handler(_request: Request, exc: Exception) -> JSONResponse:
        logger.exception("api: unhandled exception")
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": ErrorCode.RUNTIME_FAILURE.value,
                    "message": "Internal server error",
                    "detail": str(exc),
                }
            },
        )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/capabilities")
    def capabilities() -> dict[str, object]:
        return detect_capabilities(settings).to_dict()

    @app.post("/v1/references/search")
    def reference_search(body: ReferenceSearchBody) -> dict[str, object]:
        service = ReferenceService(
            meting=MetingIntegration(enabled=settings.integrations.meting_enabled, command=settings.tools.meting_command)
        )
        return service.search(
            ReferenceSearchRequest(keyword=body.keyword, platform=body.platform)
        )

    @app.post("/v1/score")
    def score(body: ScoreBody) -> dict[str, object]:
        return score_service.generate(_build_score_request(body))

    @app.post("/v1/workflows/full")
    def workflow_full(body: WorkflowBody, async_mode: bool = Query(False, alias="async")) -> dict[str, object]:
        request = _build_workflow_request(body)
        if async_mode:
            workflow_id = artifact_service.create_workflow_id()
            artifact_service.save_checkpoint(workflow_id, "queued", {"mode": "async"})
            _async_set_status(artifact_service, workflow_id, "processing")
            thread = threading.Thread(target=_run_workflow_async, args=(workflow_id, workflow_service, artifact_service, request), daemon=True)
            thread.start()
            return {"workflow_id": workflow_id, "status": "processing"}

        return workflow_service.run_full(request)

    @app.get("/v1/workflows/{workflow_id}/status")
    def workflow_status(workflow_id: str) -> dict[str, object]:
        status_path = artifact_service.workflow_dir(workflow_id) / "status.json"
        if status_path.exists():
            return json.loads(status_path.read_text(encoding="utf-8"))
        try:
            artifact_service.load_manifest(workflow_id)
            return {"status": "completed"}
        except Exception:
            return {"status": "not_found"}

    @app.get("/v1/workflows")
    def workflow_list() -> dict[str, object]:
        return {"workflows": artifact_service.list_workflows()}

    @app.delete("/v1/workflows/{workflow_id}")
    def workflow_delete(workflow_id: str) -> dict[str, object]:
        artifact_service.delete_workflow(workflow_id)
        return {"deleted": workflow_id}

    @app.post("/v1/workflows/{workflow_id}/retry")
    def workflow_retry(workflow_id: str) -> dict[str, object]:
        manifest = artifact_service.load_manifest(workflow_id)
        saved_request = manifest.get("request", {})
        retried = WorkflowRequest(
            lyrics=saved_request.get("lyrics", ""),
            output_base=saved_request.get("output_base", ""),
            key=saved_request.get("key", "C"),
            bpm=saved_request.get("bpm", 120),
            instruments=saved_request.get("instruments", "piano,vocals"),
            style=saved_request.get("style", "pop"),
            render_demo=saved_request.get("render_demo", True),
            chord_progression=saved_request.get("chord_progression", []),
            sections=saved_request.get("sections", []),
            melody=saved_request.get("melody", {}),
            instrument_roles=saved_request.get("instrument_roles", {}),
        )
        result = workflow_service.run_full(retried)
        result["retry_of"] = workflow_id
        return result

    @app.post("/v1/workflows/{workflow_id}/cancel")
    def workflow_cancel(workflow_id: str) -> dict[str, object]:
        artifact_service.request_cancel(workflow_id)
        _async_set_status(artifact_service, workflow_id, "cancelled")
        return {"cancel_requested": workflow_id}

    @app.post("/v1/workflows/cleanup")
    def workflow_cleanup(retention_days: int = 30) -> dict[str, object]:
        deleted = artifact_service.cleanup_expired(retention_days=retention_days)
        return {"deleted": deleted, "retention_days": retention_days}

    @app.post("/v1/workflows/{workflow_id}/revise")
    def workflow_revise(workflow_id: str, body: RevisionBody) -> dict[str, object]:
        manifest = artifact_service.load_manifest(workflow_id)
        saved_request = manifest.get("request", {})
        merged = dict(saved_request)
        if body.key:
            merged["key"] = body.key
        if body.bpm:
            merged["bpm"] = body.bpm
        if body.instruments:
            merged["instruments"] = body.instruments
        if body.style:
            merged["style"] = body.style
        if body.chord_progression:
            merged["chord_progression"] = body.chord_progression
        if body.sections:
            merged["sections"] = body.sections
        if body.melody:
            merged["melody"] = body.melody
        if body.instrument_roles:
            merged["instrument_roles"] = body.instrument_roles

        revised = WorkflowRequest(
            lyrics=merged.get("lyrics", ""),
            output_base=merged.get("output_base", f"build/workflows/{workflow_id}/artifacts/composition"),
            key=merged.get("key", "C"),
            bpm=merged.get("bpm", 120),
            instruments=merged.get("instruments", "piano,vocals"),
            style=merged.get("style", "pop"),
            render_demo=body.render_demo if body.render_demo is not None else merged.get("render_demo", True),
            chord_progression=merged.get("chord_progression", []),
            sections=merged.get("sections", []),
            melody=merged.get("melody", {}),
            instrument_roles=merged.get("instrument_roles", {}),
        )
        return workflow_service.revise(workflow_id, revised)

    @app.post("/v1/render")
    def render(body: RenderBody) -> dict[str, object]:
        return render_service.render(
            RenderRequest(
                midi_path=body.midi_path,
                output_base=body.output_base,
                format=body.format,
                soundfont_path=body.soundfont_path,
            )
        )

    @app.post("/v1/midi/diff")
    def midi_diff(body: MidiDiffBody) -> dict[str, object]:
        return midi_service.diff(MidiDiffRequest(left_notes=body.left_notes, right_notes=body.right_notes))

    @app.post("/v1/midi/inspect")
    def midi_inspect(body: MidiInspectBody) -> dict[str, object]:
        return midi_service.inspect(MidiInspectRequest(midi_path=body.midi_path, notes=body.notes))

    @app.post("/v1/midi/query")
    def midi_query(body: MidiQueryBody) -> dict[str, object]:
        return midi_service.query(
            MidiQueryRequest(notes=body.notes, midi_path=body.midi_path, min_pitch=body.min_pitch, max_pitch=body.max_pitch)
        )

    @app.post("/v1/midi/diff-files")
    def midi_diff_files(body: MidiDiffFilesBody) -> dict[str, object]:
        return midi_service.diff_files(left_path=body.left_path, right_path=body.right_path)

    @app.post("/v1/midi/transform")
    def midi_transform(body: MidiTransformBody) -> dict[str, object]:
        return midi_service.transform(
            MidiTransformRequest(
                notes=body.notes,
                operation=body.operation,
                semitones=body.semitones,
                start=body.start,
                end=body.end,
                replacement=body.replacement,
            )
        )

    @app.post("/v1/playability")
    def playability(body: PlayabilityBody) -> dict[str, object]:
        return playability_service.evaluate(
            PlayabilityRequest(instrument=body.instrument, notes=body.notes)
        )

    @app.get("/v1/artifacts/{workflow_id}")
    def artifact_manifest(workflow_id: str) -> dict[str, object]:
        try:
            manifest = artifact_service.load_manifest(workflow_id)
        except FileNotFoundError as exc:
            raise EngineError(
                code=ErrorCode.FILE_NOT_FOUND,
                message=f"Workflow not found: {workflow_id}",
                detail=str(exc),
            ) from exc
        artifacts_dir = artifact_service.artifacts_subdir(workflow_id)
        if artifacts_dir.exists():
            files = [f.name for f in artifacts_dir.iterdir() if f.is_file()]
            manifest["files"] = files
        else:
            manifest["files"] = []
        return manifest

    @app.get("/v1/workflows/{workflow_id}/checkpoints")
    def workflow_checkpoints(workflow_id: str) -> list[dict[str, object]]:
        return artifact_service.load_checkpoints(workflow_id)

    @app.get("/v1/artifacts/{workflow_id}/files/{filename}")
    def artifact_file(workflow_id: str, filename: str):
        file_path = artifact_service.resolve_file(workflow_id, filename)
        if not file_path.exists():
            raise EngineError(
                code=ErrorCode.FILE_NOT_FOUND,
                message=f"File not found: {filename}",
                detail=str(file_path),
            )
        media_types = {
            ".mid": "audio/midi",
            ".midi": "audio/midi",
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".pdf": "application/pdf",
            ".musicxml": "application/vnd.recordare.musicxml+xml",
            ".xml": "application/xml",
            ".ly": "text/x-lilypond",
            ".json": "application/json",
        }
        media_type = media_types.get(file_path.suffix, "application/octet-stream")
        return FileResponse(path=str(file_path), media_type=media_type, filename=filename)

    return app
