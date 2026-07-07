from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProjectSettings:
    output_dir: str = "build/output"


@dataclass
class IntegrationSettings:
    meting_enabled: bool = True
    advanced_enabled: bool = False
    memory_enabled: bool = False
    research_enabled: bool = False


@dataclass
class ToolSettings:
    ffmpeg_command: str = "ffmpeg"
    lilypond_command: str = "lilypond"
    fluidsynth_command: str = "fluidsynth"
    npx_command: str = "npx"


@dataclass
class Settings:
    project: ProjectSettings = field(default_factory=ProjectSettings)
    integrations: IntegrationSettings = field(default_factory=IntegrationSettings)
    tools: ToolSettings = field(default_factory=ToolSettings)


@dataclass
class ToolCapability:
    available: bool
    command: str


@dataclass
class IntegrationCapability:
    enabled: bool
    available: bool
    reason: str = ""


@dataclass
class CapabilityReport:
    tools: dict[str, ToolCapability]
    integrations: dict[str, IntegrationCapability]

    def to_dict(self) -> dict[str, Any]:
        return {
            "tools": {
                name: {"available": item.available, "command": item.command}
                for name, item in self.tools.items()
            },
            "integrations": {
                name: {
                    "enabled": item.enabled,
                    "available": item.available,
                    "reason": item.reason,
                }
                for name, item in self.integrations.items()
            },
        }


@dataclass
class ScoreRequest:
    lyrics: str
    output_base: str
    key: str = "C"
    bpm: int = 120
    time_signature: str = "4/4"
    instruments: str = "piano,vocals"
    style: str = "pop"
    mode: str = "all"


@dataclass
class RenderRequest:
    midi_path: str
    output_base: str
    format: str = "mp3"
    soundfont_path: str | None = None


@dataclass
class WorkflowRequest:
    lyrics: str
    output_base: str
    key: str = "C"
    bpm: int = 120
    instruments: str = "piano,vocals"
    style: str = "pop"
    render_demo: bool = True


@dataclass
class ReferenceSearchRequest:
    keyword: str
    platform: str = "netease"
