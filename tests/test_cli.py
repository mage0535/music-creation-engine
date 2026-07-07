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
    assert payload["source"] == "meting"


def test_cli_score_command_prints_artifacts(capsys):
    exit_code = main(["score", "--lyrics", "hello", "--output", "build/output/song"])

    captured = capsys.readouterr()

    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["midi"].endswith("song.mid")
