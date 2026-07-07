from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_sheet_music_script_runs_without_editable_install(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "scripts/sheet_music_generator.py",
            "--lyrics",
            "hello world",
            "--output",
            str(tmp_path / "song"),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    payload = json.loads(result.stdout)
    assert payload["midi"].endswith("song.mid")


def test_demo_renderer_script_reports_missing_midi(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "scripts/demo_renderer.py",
            "--midi",
            str(tmp_path / "nonexistent.mid"),
            "--output",
            str(tmp_path / "song"),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
