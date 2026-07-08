import pytest
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


def test_load_settings_missing_defaults_file_returns_defaults():
    settings = load_settings(defaults_path=Path("/nonexistent/defaults.yaml"))

    assert settings.project.output_dir == "build/output"
    assert settings.integrations.meting_enabled is True


def test_load_settings_corrupt_yaml_raises(tmp_path):
    bad_yaml = tmp_path / "bad.yaml"
    bad_yaml.write_text(": invalid yaml ::", encoding="utf-8")

    with pytest.raises(Exception):
        load_settings(defaults_path=bad_yaml)


def test_load_settings_scalar_config_raises(tmp_path):
    scalar_yaml = tmp_path / "scalar.yaml"
    scalar_yaml.write_text("just a string", encoding="utf-8")

    with pytest.raises(ValueError, match="must contain a mapping"):
        load_settings(defaults_path=scalar_yaml)


def test_load_settings_supports_sidecar_and_workflow_paths(tmp_path):
    defaults = tmp_path / "defaults.yaml"
    defaults.write_text(
        """
project:
  output_dir: build/output
  workflow_dir: build/workflows
integrations:
  meting_enabled: true
  midi_composer_enabled: true
  midi_composer_command: midi-composer-mcp
  reaper_enabled: false
""".strip(),
        encoding="utf-8",
    )

    settings = load_settings(defaults_path=defaults)

    assert settings.project.workflow_dir == "build/workflows"
    assert settings.integrations.midi_composer_enabled is True
    assert settings.integrations.midi_composer_command == "midi-composer-mcp"


def test_load_settings_reads_security_env_overrides(monkeypatch, tmp_path):
    defaults = tmp_path / "defaults.yaml"
    defaults.write_text(
        """
security:
  api_keys: []
  rate_limit_per_minute: 0
  auth_header_name: x-api-key
""".strip(),
        encoding="utf-8",
    )
    monkeypatch.setenv("MCE_API_KEYS", "alpha,beta")
    monkeypatch.setenv("MCE_RATE_LIMIT_PER_MINUTE", "12")
    monkeypatch.setenv("MCE_AUTH_HEADER_NAME", "X-Test-Key")

    settings = load_settings(defaults_path=defaults)

    assert settings.security.api_keys == ["alpha", "beta"]
    assert settings.security.rate_limit_per_minute == 12
    assert settings.security.auth_header_name == "x-test-key"
