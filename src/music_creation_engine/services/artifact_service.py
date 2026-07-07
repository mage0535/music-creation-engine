from __future__ import annotations

import json
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Any

from music_creation_engine.models import ArtifactManifest


class ArtifactService:
    def __init__(self, base_dir: str | Path) -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def create_workflow_id(self) -> str:
        return uuid.uuid4().hex[:12]

    def workflow_dir(self, workflow_id: str) -> Path:
        path = self.base_dir / workflow_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def manifest_path(self, workflow_id: str) -> Path:
        return self.workflow_dir(workflow_id) / "manifest.json"

    def checkpoints_path(self, workflow_id: str) -> Path:
        return self.workflow_dir(workflow_id) / "checkpoints.json"

    def save_manifest(self, manifest: ArtifactManifest) -> None:
        self.manifest_path(manifest.workflow_id).write_text(
            json.dumps(asdict(manifest), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def load_manifest(self, workflow_id: str) -> dict[str, Any]:
        return json.loads(self.manifest_path(workflow_id).read_text(encoding="utf-8"))

    def save_checkpoint(self, workflow_id: str, stage: str, payload: dict[str, Any]) -> None:
        path = self.checkpoints_path(workflow_id)
        data = []
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
        data.append({"stage": stage, "payload": payload})
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def load_checkpoints(self, workflow_id: str) -> list[dict[str, Any]]:
        path = self.checkpoints_path(workflow_id)
        if not path.exists():
            return []
        return json.loads(path.read_text(encoding="utf-8"))
