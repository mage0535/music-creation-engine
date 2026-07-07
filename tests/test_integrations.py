import json
import subprocess

from music_creation_engine.integrations.meting import MetingIntegration
from music_creation_engine.integrations.sidecar_midi_composer import MidiComposerSidecarIntegration


def test_meting_integration_parses_subprocess_json(monkeypatch):
    payload = {"songs": [{"title": "Song A", "artist": "Artist A"}]}

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args=args[0], returncode=0, stdout=json.dumps(payload), stderr="")

    monkeypatch.setattr("music_creation_engine.integrations.meting.subprocess.run", fake_run)

    result = MetingIntegration(enabled=True, command="npx").search("test", "netease")

    assert result.payload["songs"][0]["title"] == "Song A"


def test_midi_composer_sidecar_returns_capability_probe(monkeypatch):
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args=args[0], returncode=0, stdout=json.dumps({"status": "ok"}), stderr="")

    monkeypatch.setattr("music_creation_engine.integrations.sidecar_midi_composer.subprocess.run", fake_run)

    integration = MidiComposerSidecarIntegration(enabled=True, command="midi-composer-mcp")
    result = integration.probe()

    assert result.payload["status"] == "ok"
