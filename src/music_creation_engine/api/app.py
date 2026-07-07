from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
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
    PlayabilityRequest,
    ReferenceSearchRequest,
    RenderRequest,
    ScoreRequest,
    WorkflowRequest,
)
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
    melody: dict[str, list[int]] = {}
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
    melody: dict[str, list[int]] = {}
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


class MidiQueryBody(BaseModel):
    notes: list[int] = []
    min_pitch: int | None = None
    max_pitch: int | None = None


class PlayabilityBody(BaseModel):
    instrument: str
    notes: list[int]


def create_app() -> FastAPI:
    app = FastAPI(title="Music Creation Engine")
    settings = load_settings()
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
        return score_service.generate(
            ScoreRequest(
                lyrics=body.lyrics,
                output_base=body.output_base,
                key=body.key,
                bpm=body.bpm,
                time_signature=body.time_signature,
                instruments=body.instruments,
                style=body.style,
                mode=body.mode,
                chord_progression=body.chord_progression,
                sections=body.sections,
                melody=body.melody,
                instrument_roles=body.instrument_roles,
            )
        )

    @app.post("/v1/workflows/full")
    def workflow_full(body: WorkflowBody) -> dict[str, object]:
        return workflow_service.run_full(
            WorkflowRequest(
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
        )

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
        return midi_service.inspect(MidiInspectRequest(notes=body.notes))

    @app.post("/v1/midi/query")
    def midi_query(body: MidiQueryBody) -> dict[str, object]:
        return midi_service.query(
            MidiQueryRequest(notes=body.notes, min_pitch=body.min_pitch, max_pitch=body.max_pitch)
        )

    @app.post("/v1/playability")
    def playability(body: PlayabilityBody) -> dict[str, object]:
        return playability_service.evaluate(
            PlayabilityRequest(instrument=body.instrument, notes=body.notes)
        )

    @app.get("/v1/artifacts/{workflow_id}")
    def artifact_manifest(workflow_id: str) -> dict[str, object]:
        return artifact_service.load_manifest(workflow_id)

    @app.get("/v1/workflows/{workflow_id}/checkpoints")
    def workflow_checkpoints(workflow_id: str) -> list[dict[str, object]]:
        return artifact_service.load_checkpoints(workflow_id)

    return app
