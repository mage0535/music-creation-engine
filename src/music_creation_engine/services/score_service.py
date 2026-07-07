from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from music_creation_engine.models import ErrorCode, EngineError, ScoreRequest
from music_creation_engine.runtime.score_runtime import generate_score_artifacts

logger = logging.getLogger(__name__)


class ScoreBackend(Protocol):
    def generate(self, request: ScoreRequest) -> dict[str, Any]: ...


@dataclass
class DefaultScoreBackend:
    def generate(self, request: ScoreRequest) -> dict[str, Any]:
        try:
            return generate_score_artifacts(request)
        except EngineError as exc:
            logger.error("score: engine error code=%s message=%s", exc.code.value, exc.message)
            if exc.code == ErrorCode.MISSING_DEPENDENCY:
                raise
            base = Path(request.output_base)
            return {
                "status": "dry-run",
                "reason": exc.message,
                "error_code": exc.code.value,
                "midi": str(base.with_suffix(".mid")),
                "pdf": str(base.with_suffix(".pdf")),
                "musicxml": str(base.with_suffix(".musicxml")),
            }
        except Exception as exc:
            logger.exception("score: unexpected error")
            raise EngineError(
                code=ErrorCode.RUNTIME_FAILURE,
                message="Score generation failed unexpectedly",
                detail=str(exc),
            ) from exc


@dataclass
class ScoreService:
    backend: ScoreBackend | None = None

    def __post_init__(self) -> None:
        if self.backend is None:
            self.backend = DefaultScoreBackend()

    def generate(self, request: ScoreRequest) -> dict[str, Any]:
        return self.backend.generate(request)
