from pathlib import Path

from music_creation_engine.config import load_settings


def test_load_settings_reads_defaults_and_env_override(monkeypatch, tmp_path):
    defaults = tmp_path / "defaults.yaml"
    defaults.write_text(
        """
project:
  output_dir: build/output
integrations:
  meting_enabled: true
  advanced_enabled: false
tools:
  ffmpeg_command: ffmpeg
""".strip(),
        encoding="utf-8",
    )

    monkeypatch.setenv("MCE_OUTPUT_DIR", "custom/output")

    settings = load_settings(defaults_path=defaults)

    assert settings.project.output_dir == "custom/output"
    assert settings.integrations.meting_enabled is True
    assert settings.integrations.advanced_enabled is False
    assert settings.tools.ffmpeg_command == "ffmpeg"


def test_load_settings_prefers_local_override(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "defaults.yaml").write_text(
        """
project:
  output_dir: build/output
integrations:
  meting_enabled: true
  advanced_enabled: false
""".strip(),
        encoding="utf-8",
    )
    (config_dir / "local.yaml").write_text(
        """
integrations:
  advanced_enabled: true
""".strip(),
        encoding="utf-8",
    )

    settings = load_settings(
        defaults_path=config_dir / "defaults.yaml",
        local_path=config_dir / "local.yaml",
    )

    assert settings.project.output_dir == "build/output"
    assert settings.integrations.advanced_enabled is True
