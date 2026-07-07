from __future__ import annotations

from dataclasses import dataclass

from music_creation_engine.integrations.meting import MetingIntegration
from music_creation_engine.integrations.sidecar_midi_composer import MidiComposerSidecarIntegration
from music_creation_engine.models import ReferenceSearchRequest


@dataclass
class ReferenceService:
    meting: MetingIntegration | None = None
    midi_composer: MidiComposerSidecarIntegration | None = None

    def __post_init__(self) -> None:
        if self.meting is None:
            self.meting = MetingIntegration()
        if self.midi_composer is None:
            self.midi_composer = MidiComposerSidecarIntegration()

    def search(self, request: ReferenceSearchRequest) -> dict[str, object]:
        result = self.meting.search(keyword=request.keyword, platform=request.platform)
        payload = dict(result.payload)
        payload["source"] = result.source
        return payload
