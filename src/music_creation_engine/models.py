from __future__ import annotations

import re
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
    REVISION_FAILED = "REVISION_FAILED"



class WorkflowStatus(str, Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


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


NOTE_NAME_MAP: dict[str, int] = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
    "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11,
}

VALID_KEYS = frozenset({
    "C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B",
    "Cm", "C#m", "Dbm", "Dm", "D#m", "Ebm", "Em", "Fm", "F#m", "Gbm", "Gm", "G#m", "Abm", "Am", "A#m", "Bbm", "Bm",
})

CHORD_NAME_RE = re.compile(r"^[A-G][#b]?(m|maj|min|dim|aug|sus\d?)?\d*(/[A-G][#b]?)?$")

INSTRUMENT_WHITELIST = frozenset({
    "piano", "vocals", "guitar", "bass", "drums", "strings", "flute", "sax", "trumpet", "synth",
})

INSTRUMENT_ROLE_WHITELIST = frozenset({"chord", "melody", "bass", "pad", "rhythm"})


def parse_note_to_midi(value: str | int) -> int:
    if isinstance(value, int):
        return value
    match = re.match(r"^([A-G][#b]?)(\d+)$", value.strip())
    if not match:
        raise EngineError(
            code=ErrorCode.INVALID_INPUT,
            message=f"Invalid note name: {value}",
            detail="Expected format like C4, D#4, Eb4.",
        )
    note_name, octave_str = match.groups()
    semitone = NOTE_NAME_MAP.get(note_name)
    if semitone is None:
        raise EngineError(
            code=ErrorCode.INVALID_INPUT,
            message=f"Unknown note: {note_name}",
            detail=f"Valid notes: {sorted(NOTE_NAME_MAP)}",
        )
    return (int(octave_str) + 1) * 12 + semitone


def normalize_melody(raw: dict[str, list[int | str]]) -> dict[str, list[int]]:
    result: dict[str, list[int]] = {}
    for instrument, notes in raw.items():
        result[instrument] = [parse_note_to_midi(n) for n in notes]
    return result


def normalize_instrument_roles(raw: dict[str, str]) -> dict[str, str]:
    for instrument, role in raw.items():
        if role not in INSTRUMENT_ROLE_WHITELIST:
            raise EngineError(
                code=ErrorCode.INVALID_INPUT,
                message=f"Unknown role '{role}' for instrument '{instrument}'",
                detail=f"Valid roles: {sorted(INSTRUMENT_ROLE_WHITELIST)}",
            )
    return raw


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
    melody: dict[str, list[int] | list[int | str]] = field(default_factory=dict)
    instrument_roles: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self._validate()
        self._normalize()

    def _validate(self) -> None:
        if not 20 <= self.bpm <= 300:
            raise EngineError(
                code=ErrorCode.INVALID_INPUT,
                message=f"BPM must be 20-300, got {self.bpm}",
            )
        if self.key not in VALID_KEYS:
            raise EngineError(
                code=ErrorCode.INVALID_INPUT,
                message=f"Invalid key: {self.key}",
                detail=f"Valid keys include: {sorted(VALID_KEYS)[:10]}...",
            )
        total_bars = sum(int(s.get("bars", 0)) for s in self.sections)
        if total_bars > 2000:
            raise EngineError(
                code=ErrorCode.INVALID_INPUT,
                message=f"Total bars {total_bars} exceeds limit of 2000",
            )
        if len(self.sections) > 50:
            raise EngineError(
                code=ErrorCode.INVALID_INPUT,
                message=f"{len(self.sections)} sections exceeds limit of 50",
            )
        for chord_str in self.chord_progression:
            if not CHORD_NAME_RE.match(chord_str):
                raise EngineError(
                    code=ErrorCode.INVALID_INPUT,
                    message=f"Invalid chord name: {chord_str}",
                    detail="Examples: C, Dm, F#m7, G7/B",
                )
        raw_instruments = [s.strip() for s in self.instruments.split(",") if s.strip()]
        for inst in raw_instruments:
            if inst not in INSTRUMENT_WHITELIST:
                raise EngineError(
                    code=ErrorCode.INVALID_INPUT,
                    message=f"Unknown instrument: {inst}",
                    detail=f"Valid: {sorted(INSTRUMENT_WHITELIST)}",
                )

    def _normalize(self) -> None:
        if self.melody:
            self.melody = normalize_melody(self.melody)
        if self.instrument_roles:
            self.instrument_roles = normalize_instrument_roles(self.instrument_roles)


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
    melody: dict[str, list[int] | list[int | str]] = field(default_factory=dict)
    instrument_roles: dict[str, str] = field(default_factory=dict)
    async_mode: bool = False


@dataclass
class WorkflowRevisionRequest:
    sections: list[dict[str, Any]] = field(default_factory=list)
    chord_progression: list[str] = field(default_factory=list)
    melody: dict[str, list[int] | list[int | str]] = field(default_factory=dict)
    instrument_roles: dict[str, str] = field(default_factory=dict)
    key: str = ""
    bpm: int = 0
    instruments: str = ""
    style: str = ""
    render_demo: bool = True


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
    status: str = "completed"
    files: list[str] = field(default_factory=list)
