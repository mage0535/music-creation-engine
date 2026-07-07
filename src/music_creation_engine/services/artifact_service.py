from __future__ import annotations

import json
import uuid
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
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

    def workflow_dir_path(self, workflow_id: str) -> Path:
        return self.base_dir / workflow_id

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

    def artifacts_subdir(self, workflow_id: str) -> Path:
        path = self.workflow_dir(workflow_id) / "artifacts"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def resolve_file(self, workflow_id: str, filename: str) -> Path:
        return self.artifacts_subdir(workflow_id) / filename

    def list_workflows(self) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for child in sorted(self.base_dir.iterdir()):
            if not child.is_dir():
                continue
            results.append(
                {
                    "workflow_id": child.name,
                    "has_manifest": (child / "manifest.json").exists(),
                    "has_status": (child / "status.json").exists(),
                }
            )
        return results

    def delete_workflow(self, workflow_id: str) -> None:
        path = self.workflow_dir_path(workflow_id)
        if path.exists():
            import shutil

            shutil.rmtree(path)

    def cancel_requested_path(self, workflow_id: str) -> Path:
        return self.workflow_dir(workflow_id) / "cancel.requested"

    def request_cancel(self, workflow_id: str) -> None:
        self.cancel_requested_path(workflow_id).write_text("cancelled\n", encoding="utf-8")

    def is_cancel_requested(self, workflow_id: str) -> bool:
        return self.cancel_requested_path(workflow_id).exists()

    def cleanup_expired(self, retention_days: int) -> list[str]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
        deleted: list[str] = []
        for item in list(self.base_dir.iterdir()):
            if not item.is_dir():
                continue
            modified = datetime.fromtimestamp(item.stat().st_mtime, tz=timezone.utc)
            if modified <= cutoff:
                try:
                    self.delete_workflow(item.name)
                    deleted.append(item.name)
                except PermissionError:
                    continue
        return deleted
