from pathlib import Path

from music_creation_engine.adapters.install import resolve_adapter_targets


def test_resolve_adapter_targets_for_codex_and_hermes(monkeypatch, tmp_path):
    home = tmp_path / "home"
    codex_home = tmp_path / "codex"
    (home / ".hermes").mkdir(parents=True)
    (codex_home / "skills").mkdir(parents=True)

    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("CODEX_HOME", str(codex_home))

    targets = resolve_adapter_targets()

    assert targets["hermes"].name == "music-creation-engine"
    assert "codex" in targets
