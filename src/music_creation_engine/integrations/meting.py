from __future__ import annotations

from dataclasses import dataclass

from music_creation_engine.integrations.base import IntegrationResult


@dataclass
class MetingIntegration:
    enabled: bool = True

    def search(self, keyword: str, platform: str = "netease") -> IntegrationResult:
        return IntegrationResult(
            payload={
                "keyword": keyword,
                "platform": platform,
                "enabled": self.enabled,
                "note": "Meting integration wiring is available; runtime command execution is optional.",
            },
            source="meting",
        )
