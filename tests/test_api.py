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
