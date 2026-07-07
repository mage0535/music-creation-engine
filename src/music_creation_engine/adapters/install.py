from __future__ import annotations

import os
import shutil
from pathlib import Path


def resolve_adapter_targets() -> dict[str, Path]:
    home = Path(os.environ.get("HOME", Path.home()))
    targets: dict[str, Path] = {}

    hermes_root = home / ".hermes"
    if hermes_root.exists():
        targets["hermes"] = hermes_root / "skills" / "creative" / "music-creation-engine"

    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        targets["codex"] = Path(codex_home) / "skills" / "music-creation-engine"
    elif (home / ".codex").exists():
        targets["codex"] = home / ".codex" / "skills" / "music-creation-engine"

    openclaw_root = home / ".openclaw"
    if openclaw_root.exists():
        targets["openclaw"] = openclaw_root / "skills" / "music-creation-engine"

    return targets


def install_adapter_files(project_root: Path, targets: dict[str, Path] | None = None) -> dict[str, str]:
    targets = targets or resolve_adapter_targets()
    installed: dict[str, str] = {}
    adapter_sources = {
        "hermes": project_root / "adapters" / "hermes" / "SKILL.md",
        "codex": project_root / "adapters" / "codex" / "AGENTS.md",
        "openclaw": project_root / "adapters" / "openclaw" / "README.md",
    }

    for name, target in targets.items():
        source = adapter_sources.get(name)
        if source is None or not source.exists():
            continue
        target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target / source.name)
        installed[name] = str(target / source.name)
    return installed
