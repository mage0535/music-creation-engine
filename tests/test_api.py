from fastapi.testclient import TestClient

from music_creation_engine.api.app import create_app


def test_health_endpoint_returns_ok():
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_capabilities_endpoint_returns_tools():
    client = TestClient(create_app())

    response = client.get("/capabilities")

    assert response.status_code == 200
    assert "tools" in response.json()


def test_reference_search_endpoint_returns_payload():
    client = TestClient(create_app())

    response = client.post("/v1/references/search", json={"keyword": "test"})

    assert response.status_code == 200
    assert response.json()["source"] == "meting"


def test_score_endpoint_returns_artifacts():
    client = TestClient(create_app())

    response = client.post(
        "/v1/score",
        json={"lyrics": "hello world", "output_base": "build/output/song"},
    )

    assert response.status_code == 200
    assert response.json()["midi"].endswith("song.mid")


def test_workflow_endpoint_returns_score_and_render():
    client = TestClient(create_app())

    response = client.post(
        "/v1/workflows/full",
        json={"lyrics": "hello world", "output_base": "build/output/song", "render_demo": True},
    )

    assert response.status_code == 200
    assert response.json()["score"]["pdf"].endswith("song.pdf")
    assert response.json()["render"]["mp3"].endswith("song.mp3")


def test_render_endpoint_returns_artifacts():
    client = TestClient(create_app())

    response = client.post(
        "/v1/render",
        json={"midi_path": "build/output/song.mid", "output_base": "build/output/song"},
    )

    assert response.status_code == 200
    assert response.json()["mp3"].endswith("song.mp3")


def test_render_missing_midi_returns_dry_run():
    client = TestClient(create_app())

    response = client.post(
        "/v1/render",
        json={"midi_path": "/nonexistent/file.mid", "output_base": "build/output/bad"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "dry-run"
    assert "error_code" in response.json()


def test_api_unhandled_exception_returns_500(monkeypatch):
    def raise_runtime(*_args, **_kwargs):
        raise RuntimeError("simulated crash")

    monkeypatch.setattr(
        "music_creation_engine.services.score_service.ScoreService.generate",
        raise_runtime,
    )
    client = TestClient(create_app(), raise_server_exceptions=False)

    response = client.post(
        "/v1/score",
        json={"lyrics": "test", "output_base": "build/output/crash"},
    )

    assert response.status_code == 500
    body = response.json()
    assert body["error"]["code"] == "RUNTIME_FAILURE"


def test_workflow_endpoint_persists_manifest():
    client = TestClient(create_app())

    response = client.post(
        "/v1/workflows/full",
        json={
            "lyrics": "hello world",
            "output_base": "build/output/song",
            "render_demo": False,
        },
    )

    assert response.status_code == 200
    assert "workflow_id" in response.json()


def test_midi_diff_endpoint_returns_changes():
    client = TestClient(create_app())

    response = client.post("/v1/midi/diff", json={"left_notes": [60, 62], "right_notes": [60, 64]})

    assert response.status_code == 200
    assert response.json()["added"] == [64]


def test_playability_endpoint_returns_warnings():
    client = TestClient(create_app())

    response = client.post("/v1/playability", json={"instrument": "piano", "notes": [48, 60, 72, 84]})

    assert response.status_code == 200
    assert response.json()["playable"] is False


def test_artifact_manifest_endpoint_returns_saved_manifest():
    client = TestClient(create_app())

    workflow = client.post(
        "/v1/workflows/full",
        json={"lyrics": "hello world", "output_base": "build/output/song", "render_demo": False},
    ).json()

    response = client.get(f"/v1/artifacts/{workflow['workflow_id']}")

    assert response.status_code == 200
    assert response.json()["workflow_id"] == workflow["workflow_id"]


def test_workflow_checkpoints_endpoint_returns_list():
    client = TestClient(create_app())

    workflow = client.post(
        "/v1/workflows/full",
        json={"lyrics": "hello world", "output_base": "build/output/song", "render_demo": False},
    ).json()

    response = client.get(f"/v1/workflows/{workflow['workflow_id']}/checkpoints")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
