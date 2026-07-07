from __future__ import annotations

import shutil

from music_creation_engine.models import (
    CapabilityReport,
    IntegrationCapability,
    Settings,
    ToolCapability,
)


def detect_capabilities(settings: Settings) -> CapabilityReport:
    tools = {
        "ffmpeg": ToolCapability(
            available=shutil.which(settings.tools.ffmpeg_command) is not None,
            command=settings.tools.ffmpeg_command,
        ),
        "lilypond": ToolCapability(
            available=shutil.which(settings.tools.lilypond_command) is not None,
            command=settings.tools.lilypond_command,
        ),
        "fluidsynth": ToolCapability(
            available=shutil.which(settings.tools.fluidsynth_command) is not None,
            command=settings.tools.fluidsynth_command,
        ),
        "npx": ToolCapability(
            available=shutil.which(settings.tools.npx_command) is not None,
            command=settings.tools.npx_command,
        ),
    }

    integrations = {
        "meting": IntegrationCapability(
            enabled=settings.integrations.meting_enabled,
            available=tools["npx"].available,
            reason="" if tools["npx"].available else "npx not found",
        ),
        "memory": IntegrationCapability(
            enabled=settings.integrations.advanced_enabled and settings.integrations.memory_enabled,
            available=settings.integrations.advanced_enabled,
            reason="" if settings.integrations.advanced_enabled else "advanced integrations disabled",
        ),
        "research": IntegrationCapability(
            enabled=settings.integrations.advanced_enabled and settings.integrations.research_enabled,
            available=settings.integrations.advanced_enabled,
            reason="" if settings.integrations.advanced_enabled else "advanced integrations disabled",
        ),
    }
    return CapabilityReport(tools=tools, integrations=integrations)
