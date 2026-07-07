import json

from music_creation_engine.cli import main


def test_cli_health_command_prints_ok(capsys):
    exit_code = main(["health"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert '"status": "ok"' in captured.out


def test_cli_capabilities_command_prints_json(capsys):
    exit_code = main(["capabilities"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert '"tools"' in captured.out


def test_cli_references_search_command_prints_result(capsys):
    exit_code = main(["references", "search", "--keyword", "test"])

    captured = capsys.readouterr()

    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["source"] in {"meting", "reference-fallback"}


def test_cli_score_command_prints_artifacts(capsys):
    exit_code = main(["score", "--lyrics", "hello", "--output", "build/output/song"])

    captured = capsys.readouterr()

    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["midi"].endswith("song.mid")


def test_cli_missing_command_prints_help(capsys):
    exit_code = main([])

    captured = capsys.readouterr()

    assert exit_code == 1


def test_cli_score_missing_dep_returns_error_json(monkeypatch, capsys):
    def raise_missing(*_args, **_kwargs):
        from music_creation_engine.models import EngineError, ErrorCode
        raise EngineError(code=ErrorCode.MISSING_DEPENDENCY, message="mock missing dep")

    monkeypatch.setattr("music_creation_engine.runtime.score_runtime._load_music21", raise_missing)

    exit_code = main(["score", "--lyrics", "hello", "--output", "build/output/song"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 1
    assert payload["error"]["code"] == "MISSING_DEPENDENCY"


def test_cli_midi_diff_command_prints_changes(capsys):
    exit_code = main(["midi", "diff", "--left-notes", "60,62", "--right-notes", "60,64"])

    captured = capsys.readouterr()

    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["added"] == [64]


def test_cli_workflow_status_and_manifest(capsys):
    create = main(["workflow", "full", "--lyrics", "hello", "--output", "build/output/song", "--no-render-demo"])
    created = json.loads(capsys.readouterr().out)
    assert create == 0
    workflow_id = created["workflow_id"]

    status_code = main(["workflow", "status", "--workflow-id", workflow_id])
    status_payload = json.loads(capsys.readouterr().out)
    assert status_code == 0
    assert status_payload["status"] in {"completed", "processing", "cancelled", "failed"}

    manifest_code = main(["artifacts", "manifest", "--workflow-id", workflow_id])
    manifest_payload = json.loads(capsys.readouterr().out)
    assert manifest_code == 0
    assert manifest_payload["workflow_id"] == workflow_id
