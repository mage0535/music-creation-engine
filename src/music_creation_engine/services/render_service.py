from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from music_creation_engine.models import RenderRequest
from music_creation_engine.runtime.render_runtime import render_demo_artifacts


class RenderBackend(Protocol):
    def render(self, request: RenderRequest) -> dict[str, Any]: ...


@dataclass
class DefaultRenderBackend:
    def render(self, request: RenderRequest) -> dict[str, Any]:
        try:
            return render_demo_artifacts(request)
        except RuntimeError as exc:
            return {
                "status": "dry-run",
                "reason": str(exc),
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
