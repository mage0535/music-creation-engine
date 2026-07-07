from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from music_creation_engine.models import ScoreRequest
from music_creation_engine.runtime.score_runtime import generate_score_artifacts


class ScoreBackend(Protocol):
    def generate(self, request: ScoreRequest) -> dict[str, Any]: ...


@dataclass
class DefaultScoreBackend:
    def generate(self, request: ScoreRequest) -> dict[str, Any]:
        try:
            return generate_score_artifacts(request)
        except RuntimeError as exc:
            base = Path(request.output_base)
            return {
                "status": "dry-run",
                "reason": str(exc),
                "midi": str(base.with_suffix(".mid")),
                "pdf": str(base.with_suffix(".pdf")),
                "musicxml": str(base.with_suffix(".musicxml")),
            }


@dataclass
class ScoreService:
    backend: ScoreBackend | None = None

    def __post_init__(self) -> None:
        if self.backend is None:
            self.backend = DefaultScoreBackend()

    def generate(self, request: ScoreRequest) -> dict[str, Any]:
        return self.backend.generate(request)
