import json
import subprocess
from io import StringIO

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


def test_meting_integration_can_parse_mcp_protocol(monkeypatch):
    messages = [
        {"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2025-03-26"}},
        {"jsonrpc": "2.0", "id": 2, "result": {"tools": [{"name": "search"}]}},
        {"jsonrpc": "2.0", "id": 3, "result": {"content": [{"type": "text", "text": json.dumps({"songs": [{"title": "Song B"}]})}]}}
    ]
    framed = "".join(
        f"Content-Length: {len(json.dumps(msg).encode())}\r\n\r\n{json.dumps(msg)}"
        for msg in messages
    )

    class FakeProcess:
        def __init__(self):
            self.stdin = StringIO()
            self.stdout = StringIO(framed)
            self.stderr = StringIO()

        def kill(self):
            return None

    monkeypatch.setattr("music_creation_engine.integrations.meting.subprocess.Popen", lambda *a, **k: FakeProcess())
    monkeypatch.setattr("music_creation_engine.integrations.meting.subprocess.run", lambda *a, **k: subprocess.CompletedProcess(a[0], 1, "", ""))

    result = MetingIntegration(enabled=True, command="npx").search("test", "netease")

    assert result.payload["songs"][0]["title"] == "Song B"


def test_meting_integration_falls_back_to_http_search(monkeypatch):
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return json.dumps(
                {
                    "results": [
                        {
                            "trackName": "Blue Train",
                            "artistName": "John Coltrane",
                            "collectionName": "Blue Train",
                            "previewUrl": "https://example.test/preview.mp3",
                        }
                    ]
                }
            ).encode()

    monkeypatch.setattr("music_creation_engine.integrations.meting.subprocess.run", lambda *a, **k: subprocess.CompletedProcess(a[0], 1, "", ""))
    monkeypatch.setattr("music_creation_engine.integrations.meting.subprocess.Popen", lambda *a, **k: (_ for _ in ()).throw(FileNotFoundError()))
    monkeypatch.setattr("music_creation_engine.integrations.meting.urlopen", lambda *a, **k: FakeResponse())

    result = MetingIntegration(enabled=True, command="npx").search("blue train", "netease")

    assert result.payload["provider"] == "itunes"
    assert result.payload["songs"][0]["title"] == "Blue Train"
