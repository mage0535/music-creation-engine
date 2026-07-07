import json
import subprocess
from io import StringIO

from music_creation_engine.integrations.meting import MetingIntegration
from music_creation_engine.integrations.sidecar_midi_composer import MidiComposerSidecarIntegration


def test_meting_integration_parses_subprocess_json(monkeypatch):
    payload = {
        "result": {
            "songs": [
                {
                    "name": "Song A",
                    "id": 1,
                    "dt": 185000,
                    "ar": [{"name": "Artist A"}],
                    "al": {"name": "Album A", "picUrl": "https://img.test/a.jpg"},
                }
            ]
        }
    }

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args=args[0], returncode=0, stdout=json.dumps(payload), stderr="")

    monkeypatch.setattr("music_creation_engine.integrations.meting.subprocess.run", fake_run)

    result = MetingIntegration(enabled=True, command="npx").search("test", "netease")

    assert result.payload["songs"][0]["title"] == "Song A"
    assert result.payload["songs"][0]["artist"] == "Artist A"
    assert result.payload["songs"][0]["duration_ms"] == 185000
    assert result.payload["songs"][0]["artwork_url"] == "https://img.test/a.jpg"
    assert result.payload["song_count"] == 1


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
        {
            "jsonrpc": "2.0",
            "id": 2,
            "result": {"tools": [{"name": "search"}, {"name": "url"}, {"name": "pic"}]},
        },
        {
            "jsonrpc": "2.0",
            "id": 3,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {
                                "result": {
                                    "songs": [
                                        {
                                            "name": "Song B",
                                            "id": 2,
                                            "ar": [{"name": "Artist B"}],
                                            "al": {"name": "Album B"},
                                        }
                                    ]
                                }
                            }
                        ),
                    }
                ]
            },
        },
        {"jsonrpc": "2.0", "id": 100, "result": {"content": [{"type": "text", "text": "https://audio.test/b.mp3"}]}},
        {"jsonrpc": "2.0", "id": 101, "result": {"content": [{"type": "text", "text": "https://img.test/b.jpg"}]}},
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
    assert result.payload["songs"][0]["artist"] == "Artist B"
    assert result.payload["songs"][0]["preview_url"] == "https://audio.test/b.mp3"
    assert result.payload["songs"][0]["artwork_url"] == "https://img.test/b.jpg"


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
                            "artworkUrl100": "https://example.test/cover.jpg",
                            "trackTimeMillis": 64000,
                            "trackId": 99,
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
    assert result.payload["songs"][0]["duration_ms"] == 64000
    assert result.payload["songs"][0]["artwork_url"] == "https://example.test/cover.jpg"


def test_meting_integration_uses_node_module_path(monkeypatch):
    monkeypatch.setattr("music_creation_engine.integrations.meting.MetingIntegration._guess_package_root", lambda self: __import__("pathlib").Path("/fake/pkg"))
    monkeypatch.setattr("music_creation_engine.integrations.meting.MetingIntegration._guess_node_command", lambda self: "node")

    payload = {"result": {"songs": [{"name": "Song C", "id": 3, "ar": [{"name": "Artist C"}], "al": {"name": "Album C"}}]}}

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args=args[0], returncode=0, stdout=json.dumps(payload), stderr="")

    monkeypatch.setattr("music_creation_engine.integrations.meting.subprocess.run", fake_run)

    result = MetingIntegration(enabled=True, command="npx").search("song c", "netease")

    assert result.payload["songs"][0]["title"] == "Song C"
    assert result.payload["songs"][0]["artist"] == "Artist C"


def test_meting_guess_package_root_skips_npx_parent_package(monkeypatch):
    monkeypatch.setattr("music_creation_engine.integrations.meting.os.path.exists", lambda path: str(path) == "npx")
    monkeypatch.setattr("music_creation_engine.integrations.meting.os.path.basename", lambda path: "npx")
    monkeypatch.setattr("pathlib.Path.exists", lambda self: self.as_posix() == "/global/root/@eldment/meting-agent")
    monkeypatch.setattr(
        "music_creation_engine.integrations.meting.subprocess.run",
        lambda *a, **k: subprocess.CompletedProcess(a[0], 0, "/global/root\n", ""),
    )

    root = MetingIntegration(enabled=True, command="npx")._guess_package_root()

    assert root is not None
    assert root.as_posix() == "/global/root/@eldment/meting-agent"


def test_meting_normalization_supports_alternate_provider_shapes():
    payload = {
        "data": {
            "list": [
                {
                    "songname": "Alt Song",
                    "songmid": "abc123",
                    "singer": [{"name": "Alt Artist"}],
                    "albumname": "Alt Album",
                    "interval": 212,
                }
            ]
        }
    }

    normalized = MetingIntegration(enabled=True)._normalize_meting_payload(payload, "tencent")

    assert normalized is not None
    assert normalized["songs"][0]["title"] == "Alt Song"
    assert normalized["songs"][0]["artist"] == "Alt Artist"
    assert normalized["songs"][0]["duration_ms"] == 212000
    assert normalized["songs"][0]["song_id"] == "abc123"


def test_meting_normalization_extracts_json_from_code_fence():
    fenced = """```json
{"result":{"songs":[{"name":"Song D","id":4,"artist":"Artist D","album":"Album D"}]}}
```"""

    normalized = MetingIntegration(enabled=True)._normalize_meting_payload(fenced, "netease")

    assert normalized is not None
    assert normalized["songs"][0]["title"] == "Song D"
    assert normalized["songs"][0]["artist"] == "Artist D"


def test_meting_normalization_parses_double_encoded_json_string():
    payload = json.dumps({"result": {"songs": [{"name": "Song E", "id": 5, "artist": "Artist E"}]}})

    normalized = MetingIntegration(enabled=True)._normalize_meting_payload(json.dumps(payload), "netease")

    assert normalized is not None
    assert normalized["songs"][0]["title"] == "Song E"
    assert normalized["songs"][0]["artist"] == "Artist E"
