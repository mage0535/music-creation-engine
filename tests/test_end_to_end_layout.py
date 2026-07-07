from pathlib import Path


def test_expected_project_layout_exists():
    assert Path("src/music_creation_engine/cli.py").exists()
    assert Path("src/music_creation_engine/api/app.py").exists()
    assert Path("src/music_creation_engine/adapters/install.py").exists()
    assert Path("config/defaults.yaml").exists()


def test_root_namespace_hack_is_absent():
    assert not Path("music_creation_engine/__init__.py").exists()


def test_src_package_is_the_real_package():
    assert Path("src/music_creation_engine/__init__.py").exists()
    assert Path("src/music_creation_engine/models.py").exists()
