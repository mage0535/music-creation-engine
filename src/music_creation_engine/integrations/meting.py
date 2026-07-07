from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass

from music_creation_engine.integrations.base import IntegrationResult


@dataclass
class MetingIntegration:
    enabled: bool = True
    command: str = "npx"

    def search(self, keyword: str, platform: str = "netease") -> IntegrationResult:
        if self.enabled:
            try:
                result = subprocess.run(
                    [self.command, "@eldment/meting-agent", "search", "--platform", platform, "--keyword", keyword],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False,
                )
                if result.returncode == 0 and result.stdout.strip():
                    try:
                        payload = json.loads(result.stdout)
                        return IntegrationResult(payload=payload, source="meting")
                    except json.JSONDecodeError:
                        pass
            except (FileNotFoundError, subprocess.SubprocessError):
                pass
        return IntegrationResult(
            payload={
                "keyword": keyword,
                "platform": platform,
                "enabled": self.enabled,
                "note": "Meting integration wiring is available; runtime command execution is optional.",
            },
            source="meting",
        )
