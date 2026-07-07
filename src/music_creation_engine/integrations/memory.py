from __future__ import annotations

from dataclasses import dataclass

from music_creation_engine.integrations.base import IntegrationResult


@dataclass
class MemoryIntegration:
    enabled: bool = False

    def status(self) -> IntegrationResult:
        return IntegrationResult(
            payload={"enabled": self.enabled, "mode": "advanced-optional"},
            source="memory",
        )
