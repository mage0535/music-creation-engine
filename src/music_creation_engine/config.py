from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from music_creation_engine.models import (
    IntegrationSettings,
    ProjectSettings,
    Settings,
    ToolSettings,
)


def _read_yaml(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Configuration file must contain a mapping: {path}")
    return data


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_settings(
    defaults_path: Path | None = None,
    local_path: Path | None = None,
) -> Settings:
    repo_root = Path.cwd()
    defaults_path = defaults_path or (repo_root / "config" / "defaults.yaml")
    local_path = local_path or (repo_root / "config" / "local.yaml")

    data = _deep_merge(_read_yaml(defaults_path), _read_yaml(local_path))

    project = ProjectSettings(**data.get("project", {}))
    integrations = IntegrationSettings(**data.get("integrations", {}))
    tools = ToolSettings(**data.get("tools", {}))

    output_dir_override = os.getenv("MCE_OUTPUT_DIR")
    if output_dir_override:
        project.output_dir = output_dir_override
    workflow_dir_override = os.getenv("MCE_WORKFLOW_DIR")
    if workflow_dir_override:
        project.workflow_dir = workflow_dir_override

    return Settings(project=project, integrations=integrations, tools=tools)
