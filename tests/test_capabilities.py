from music_creation_engine.capabilities import detect_capabilities
from music_creation_engine.models import Settings, IntegrationSettings, ProjectSettings, ToolSettings


def test_detect_capabilities_marks_public_and_advanced_integrations(monkeypatch):
    monkeypatch.setattr(
        "music_creation_engine.capabilities.shutil.which",
        lambda command: "/bin/tool" if command in {"ffmpeg", "npx"} else None,
    )

    settings = Settings(
        project=ProjectSettings(output_dir="build/output"),
        integrations=IntegrationSettings(
            meting_enabled=True,
            advanced_enabled=True,
            memory_enabled=True,
            research_enabled=True,
        ),
        tools=ToolSettings(
            ffmpeg_command="ffmpeg",
            lilypond_command="lilypond",
            fluidsynth_command="fluidsynth",
            npx_command="npx",
        ),
    )

    capabilities = detect_capabilities(settings)

    assert capabilities.tools["ffmpeg"].available is True
    assert capabilities.integrations["meting"].enabled is True
    assert capabilities.integrations["memory"].enabled is True
    assert capabilities.integrations["research"].enabled is True


def test_detect_capabilities_reports_missing_tool(monkeypatch):
    monkeypatch.setattr("music_creation_engine.capabilities.shutil.which", lambda command: None)

    settings = Settings(
        project=ProjectSettings(output_dir="build/output"),
        integrations=IntegrationSettings(),
        tools=ToolSettings(),
    )

    capabilities = detect_capabilities(settings)

    assert capabilities.tools["ffmpeg"].available is False


def test_detect_capabilities_reports_sidecar_integrations(monkeypatch):
    monkeypatch.setattr(
        "music_creation_engine.capabilities.shutil.which",
        lambda command: "/bin/tool" if command in {"ffmpeg", "npx", "midi-composer-mcp"} else None,
    )

    settings = Settings(
        project=ProjectSettings(output_dir="build/output"),
        integrations=IntegrationSettings(
            meting_enabled=True,
            advanced_enabled=True,
            memory_enabled=False,
            research_enabled=False,
            midi_composer_enabled=True,
            reaper_enabled=True,
        ),
        tools=ToolSettings(
            ffmpeg_command="ffmpeg",
            lilypond_command="lilypond",
            fluidsynth_command="fluidsynth",
            npx_command="npx",
            midi_composer_command="midi-composer-mcp",
            reaper_command="reaper-mcp",
        ),
    )

    capabilities = detect_capabilities(settings)

    assert capabilities.integrations["midi_composer"].enabled is True
    assert capabilities.integrations["midi_composer"].available is True
    assert capabilities.integrations["reaper"].enabled is True
