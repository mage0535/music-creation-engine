from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from music_creation_engine.capabilities import detect_capabilities
from music_creation_engine.config import load_settings
from music_creation_engine.models import ReferenceSearchRequest, RenderRequest, ScoreRequest, WorkflowRequest
from music_creation_engine.services.reference_service import ReferenceService
from music_creation_engine.services.render_service import RenderService
from music_creation_engine.services.score_service import ScoreService
from music_creation_engine.services.workflow_service import WorkflowService


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


class WorkflowBody(BaseModel):
    lyrics: str
    output_base: str
    key: str = "C"
    bpm: int = 120
    instruments: str = "piano,vocals"
    style: str = "pop"
    render_demo: bool = True


class RenderBody(BaseModel):
    midi_path: str
    output_base: str
    format: str = "mp3"
    soundfont_path: str | None = None


def create_app() -> FastAPI:
    app = FastAPI(title="Music Creation Engine")
    score_service = ScoreService()
    render_service = RenderService()
    workflow_service = WorkflowService(
        score_service=score_service,
        render_service=render_service,
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/capabilities")
    def capabilities() -> dict[str, object]:
        settings = load_settings()
        return detect_capabilities(settings).to_dict()

    @app.post("/v1/references/search")
    def reference_search(body: ReferenceSearchBody) -> dict[str, object]:
        service = ReferenceService()
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

    return app
