from pathlib import Path


def test_expected_project_layout_exists():
    assert Path("src/music_creation_engine/cli.py").exists()
    assert Path("src/music_creation_engine/api/app.py").exists()
    assert Path("src/music_creation_engine/adapters/install.py").exists()
    assert Path("config/defaults.yaml").exists()
