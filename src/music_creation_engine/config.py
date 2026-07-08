from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from music_creation_engine.models import (
    IntegrationSettings,
    ProjectSettings,
    SecuritySettings,
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
    *,
    resolve_paths: bool = False,
) -> Settings:
    repo_root = Path.cwd()
    defaults_path = defaults_path or (repo_root / "config" / "defaults.yaml")
    local_path = local_path or (repo_root / "config" / "local.yaml")

    data = _deep_merge(_read_yaml(defaults_path), _read_yaml(local_path))

    project = ProjectSettings(**data.get("project", {}))
    integrations = IntegrationSettings(**data.get("integrations", {}))
    tools = ToolSettings(**data.get("tools", {}))
    security = SecuritySettings(**data.get("security", {}))

    output_dir_override = os.getenv("MCE_OUTPUT_DIR")
    if output_dir_override:
        project.output_dir = output_dir_override
    workflow_dir_override = os.getenv("MCE_WORKFLOW_DIR")
    if workflow_dir_override:
        project.workflow_dir = workflow_dir_override
    api_keys_override = os.getenv("MCE_API_KEYS")
    if api_keys_override is not None:
        security.api_keys = [item.strip() for item in api_keys_override.split(",") if item.strip()]
    rate_limit_override = os.getenv("MCE_RATE_LIMIT_PER_MINUTE")
    if rate_limit_override:
        security.rate_limit_per_minute = int(rate_limit_override)
    auth_header_override = os.getenv("MCE_AUTH_HEADER_NAME")
    if auth_header_override:
        security.auth_header_name = auth_header_override.strip().lower()

    if resolve_paths:
        if not Path(project.output_dir).is_absolute():
            project.output_dir = str(repo_root / project.output_dir)
        if not Path(project.workflow_dir).is_absolute():
            project.workflow_dir = str(repo_root / project.workflow_dir)

    return Settings(project=project, integrations=integrations, tools=tools, security=security)
