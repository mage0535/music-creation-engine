from pathlib import Path

from music_creation_engine.services.artifact_service import ArtifactService


def test_artifact_service_can_list_and_delete_workflows(tmp_path):
    service = ArtifactService(tmp_path)
    workflow_id = service.create_workflow_id()
    service.workflow_dir(workflow_id)

    listed = service.list_workflows()
    assert workflow_id in [item["workflow_id"] for item in listed]

    service.delete_workflow(workflow_id)
    assert not service.workflow_dir_path(workflow_id).exists()


def test_artifact_service_cleanup_expired(tmp_path):
    service = ArtifactService(tmp_path)
    workflow_id = service.create_workflow_id()
    path = service.workflow_dir(workflow_id)
    old_time = 1
    import os
    os.utime(path, (old_time, old_time))

    deleted = service.cleanup_expired(retention_days=0)

    assert workflow_id in deleted
