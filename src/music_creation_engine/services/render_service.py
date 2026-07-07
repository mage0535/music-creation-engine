from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from music_creation_engine.models import ErrorCode, EngineError, RenderRequest
from music_creation_engine.runtime.render_runtime import render_demo_artifacts

logger = logging.getLogger(__name__)


class RenderBackend(Protocol):
    def render(self, request: RenderRequest) -> dict[str, Any]: ...


@dataclass
class DefaultRenderBackend:
    def render(self, request: RenderRequest) -> dict[str, Any]:
        try:
            return render_demo_artifacts(request)
        except EngineError as exc:
            logger.error("render: engine error code=%s message=%s", exc.code.value, exc.message)
            return {
                "status": "dry-run",
                "reason": exc.message,
                "error_code": exc.code.value,
                "mp3": str(Path(request.output_base).with_suffix(".mp3")),
            }
        except Exception as exc:
            logger.exception("render: unexpected error")
            return {
                "status": "dry-run",
                "reason": str(exc),
                "error_code": ErrorCode.RUNTIME_FAILURE.value,
                "mp3": str(Path(request.output_base).with_suffix(".mp3")),
            }


@dataclass
class RenderService:
    backend: RenderBackend | None = None

    def __post_init__(self) -> None:
        if self.backend is None:
            self.backend = DefaultRenderBackend()

    def render(self, request: RenderRequest) -> dict[str, Any]:
        return self.backend.render(request)
