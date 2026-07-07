from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ErrorCode(str, Enum):
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_TOOL = "MISSING_TOOL"
    MISSING_DEPENDENCY = "MISSING_DEPENDENCY"
    INTEGRATION_UNAVAILABLE = "INTEGRATION_UNAVAILABLE"
    RUNTIME_FAILURE = "RUNTIME_FAILURE"
    CONFIG_ERROR = "CONFIG_ERROR"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"


class EngineError(Exception):
    def __init__(self, code: ErrorCode, message: str, detail: str = "") -> None:
        self.code = code
        self.message = message
        self.detail = detail
        super().__init__(message)

    def to_dict(self) -> dict[str, Any]:
        return {
            "error": {
                "code": self.code.value,
                "message": self.message,
                "detail": self.detail,
            }
        }


@dataclass
class ProjectSettings:
    output_dir: str = "build/output"
    workflow_dir: str = "build/workflows"


@dataclass
class IntegrationSettings:
    meting_enabled: bool = True
    advanced_enabled: bool = False
    memory_enabled: bool = False
    research_enabled: bool = False
    midi_composer_enabled: bool = False
    midi_composer_command: str = "midi-composer-mcp"
    reaper_enabled: bool = False


@dataclass
class ToolSettings:
    ffmpeg_command: str = "ffmpeg"
    lilypond_command: str = "lilypond"
    fluidsynth_command: str = "fluidsynth"
    npx_command: str = "npx"
    meting_command: str = "npx"
    midi_composer_command: str = "midi-composer-mcp"
    reaper_command: str = "reaper-mcp"


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
    chord_progression: list[str] = field(default_factory=list)
    sections: list[dict[str, Any]] = field(default_factory=list)
    melody: dict[str, list[int]] = field(default_factory=dict)
    instrument_roles: dict[str, str] = field(default_factory=dict)


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
    chord_progression: list[str] = field(default_factory=list)
    sections: list[dict[str, Any]] = field(default_factory=list)
    melody: dict[str, list[int]] = field(default_factory=dict)
    instrument_roles: dict[str, str] = field(default_factory=dict)


@dataclass
class ReferenceSearchRequest:
    keyword: str
    platform: str = "netease"


@dataclass
class MidiDiffRequest:
    left_notes: list[int]
    right_notes: list[int]


@dataclass
class MidiInspectRequest:
    midi_path: str | None = None
    notes: list[int] = field(default_factory=list)


@dataclass
class MidiQueryRequest:
    midi_path: str | None = None
    min_pitch: int | None = None
    max_pitch: int | None = None
    notes: list[int] = field(default_factory=list)


@dataclass
class PlayabilityRequest:
    instrument: str
    notes: list[int]


@dataclass
class ArtifactManifest:
    workflow_id: str
    score: dict[str, Any]
    render: dict[str, Any] | None
    request: dict[str, Any]
    checkpoints: list[dict[str, Any]] = field(default_factory=list)
