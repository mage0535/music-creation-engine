from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass

from music_creation_engine.integrations.base import IntegrationResult


@dataclass
class MidiComposerSidecarIntegration:
    enabled: bool = False
    command: str = "midi-composer-mcp"

    def probe(self) -> IntegrationResult:
        if not self.enabled:
            return IntegrationResult(payload={"status": "disabled"}, source="midi-composer")
        result = subprocess.run(
            [self.command, "--help"],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        if result.returncode != 0 and result.stdout.strip().startswith("{"):
            payload = json.loads(result.stdout)
        else:
            payload = {"status": "ok" if result.returncode == 0 else "unavailable", "stdout": result.stdout.strip()}
        return IntegrationResult(payload=payload, source="midi-composer")
