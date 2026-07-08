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
    assert response.json()["source"] in {"meting", "reference-fallback"}


def test_score_endpoint_returns_artifacts():
    client = TestClient(create_app())

    response = client.post(
        "/v1/score",
        json={
            "lyrics": "hello world",
            "output_base": "build/output/song",
            "melody": {"vocals": ["A4", "B4", "C5"]},
        },
    )

    assert response.status_code == 200
    assert response.json()["midi"].endswith("song.mid")
    assert response.json()["request_echo"]["melody"]["vocals"] == [69, 71, 72]


def test_workflow_endpoint_returns_score_and_render():
    client = TestClient(create_app())

    response = client.post(
        "/v1/workflows/full",
        json={"lyrics": "hello world", "output_base": "build/output/song", "render_demo": False},
    )

    assert response.status_code == 200
    assert "workflow_id" in response.json()
    assert ".mid" in response.json()["score"]["midi"]


def test_render_endpoint_missing_midi_returns_error():
    client = TestClient(create_app())

    response = client.post(
        "/v1/render",
        json={"midi_path": "build/output/nonexistent.mid", "output_base": "build/output/song"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "FILE_NOT_FOUND"


def test_render_missing_midi_returns_error():
    client = TestClient(create_app())

    response = client.post(
        "/v1/render",
        json={"midi_path": "/nonexistent/file.mid", "output_base": "build/output/bad"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "FILE_NOT_FOUND"


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


def test_midi_transform_endpoint_returns_transposed_notes():
    client = TestClient(create_app())

    response = client.post(
        "/v1/midi/transform",
        json={"notes": [60, 62, 64], "operation": "transpose", "semitones": 2},
    )

    assert response.status_code == 200
    assert response.json()["notes"] == [62, 64, 66]


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
    assert ".mid" in response.json()["score"]["midi"]
    assert isinstance(response.json().get("files", []), list)


def test_workflow_checkpoints_endpoint_returns_list():
    client = TestClient(create_app())

    workflow = client.post(
        "/v1/workflows/full",
        json={"lyrics": "hello world", "output_base": "build/output/song", "render_demo": False},
    ).json()

    response = client.get(f"/v1/workflows/{workflow['workflow_id']}/checkpoints")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_async_workflow_returns_processing_and_status():
    client = TestClient(create_app())

    workflow = client.post(
        "/v1/workflows/full?async=true",
        json={"lyrics": "hello world", "output_base": "build/output/song", "render_demo": False},
    ).json()

    assert workflow["status"] == "processing"
    status = client.get(f"/v1/workflows/{workflow['workflow_id']}/status")
    assert status.status_code == 200
    assert status.json()["status"] in {"processing", "completed", "failed"}


def test_artifact_file_endpoint_returns_content():
    client = TestClient(create_app())

    workflow = client.post(
        "/v1/workflows/full",
        json={"lyrics": "hello world", "output_base": "build/output/song", "render_demo": False},
    ).json()

    response = client.get(f"/v1/artifacts/{workflow['workflow_id']}/files/composition.mid")

    assert response.status_code == 200
    assert len(response.content) > 0


def test_workflow_revise_returns_revision_marker():
    client = TestClient(create_app())

    workflow = client.post(
        "/v1/workflows/full",
        json={"lyrics": "hello world", "output_base": "build/output/song", "render_demo": False},
    ).json()

    response = client.post(f"/v1/workflows/{workflow['workflow_id']}/revise", json={"bpm": 90})

    assert response.status_code == 200
    assert response.json()["revision_of"] == workflow["workflow_id"]


def test_workflow_delete_removes_manifest():
    client = TestClient(create_app())

    workflow = client.post(
        "/v1/workflows/full",
        json={"lyrics": "hello world", "output_base": "build/output/song", "render_demo": False},
    ).json()

    deleted = client.delete(f"/v1/workflows/{workflow['workflow_id']}")
    assert deleted.status_code == 200
    missing = client.get(f"/v1/artifacts/{workflow['workflow_id']}")
    assert missing.status_code == 400


def test_workflow_list_and_retry():
    client = TestClient(create_app())

    workflow = client.post(
        "/v1/workflows/full",
        json={"lyrics": "hello world", "output_base": "build/output/song", "render_demo": False},
    ).json()

    listed = client.get("/v1/workflows")
    assert listed.status_code == 200
    assert workflow["workflow_id"] in [item["workflow_id"] for item in listed.json()["workflows"]]

    retried = client.post(f"/v1/workflows/{workflow['workflow_id']}/retry")
    assert retried.status_code == 200
    assert retried.json()["retry_of"] == workflow["workflow_id"]


def test_workflow_cancel_and_cleanup():
    client = TestClient(create_app())

    workflow = client.post(
        "/v1/workflows/full?async=true",
        json={"lyrics": "hello world", "output_base": "build/output/song", "render_demo": False},
    ).json()

    cancelled = client.post(f"/v1/workflows/{workflow['workflow_id']}/cancel")
    assert cancelled.status_code == 200
    assert cancelled.json()["cancel_requested"] == workflow["workflow_id"]

    cleaned = client.post("/v1/workflows/cleanup", params={"retention_days": 0})
    assert cleaned.status_code == 200
    assert "deleted" in cleaned.json()


def test_async_workflow_keeps_same_workflow_id_in_status_result():
    client = TestClient(create_app())

    started = client.post(
        "/v1/workflows/full?async=true",
        json={"lyrics": "hello world", "output_base": "build/output/song", "render_demo": False},
    ).json()

    workflow_id = started["workflow_id"]
    status = client.get(f"/v1/workflows/{workflow_id}/status").json()
    if status.get("status") == "completed":
        assert status["result"]["workflow_id"] == workflow_id


def test_revision_can_disable_render():
    client = TestClient(create_app())

    workflow = client.post(
        "/v1/workflows/full",
        json={"lyrics": "hello world", "output_base": "build/output/song", "render_demo": False},
    ).json()

    revised = client.post(
        f"/v1/workflows/{workflow['workflow_id']}/revise",
        json={"render_demo": False},
    ).json()

    assert revised["render"] is None


def test_midi_inspect_from_file_returns_note_data():
    client = TestClient(create_app())

    workflow = client.post(
        "/v1/workflows/full",
        json={"lyrics": "hello world", "output_base": "build/output/song", "render_demo": False},
    ).json()

    inspected = client.post("/v1/midi/inspect", json={"midi_path": workflow["score"]["midi"]})

    assert inspected.status_code == 200
    assert inspected.json()["count"] > 0


def test_v1_routes_require_api_key_when_configured(monkeypatch):
    monkeypatch.setenv("MCE_API_KEYS", "secret-key")
    client = TestClient(create_app())

    denied = client.post(
        "/v1/score",
        json={"lyrics": "hello world", "output_base": "build/output/song"},
    )
    allowed = client.post(
        "/v1/score",
        headers={"x-api-key": "secret-key"},
        json={"lyrics": "hello world", "output_base": "build/output/song"},
    )

    assert denied.status_code == 401
    assert denied.json()["error"]["code"] == "UNAUTHORIZED"
    assert allowed.status_code == 200


def test_v1_routes_rate_limit_when_enabled(monkeypatch):
    monkeypatch.setenv("MCE_API_KEYS", "secret-key")
    monkeypatch.setenv("MCE_RATE_LIMIT_PER_MINUTE", "2")
    client = TestClient(create_app())
    headers = {"x-api-key": "secret-key"}

    first = client.post("/v1/references/search", headers=headers, json={"keyword": "test"})
    second = client.post("/v1/references/search", headers=headers, json={"keyword": "test"})
    third = client.post("/v1/references/search", headers=headers, json={"keyword": "test"})

    assert first.status_code == 200
    assert second.status_code == 200
    assert third.status_code == 429
    assert third.json()["error"]["code"] == "RATE_LIMITED"
    assert "Retry-After" in third.headers


def test_workflow_revise_reuses_score_when_only_render_flag_changes(monkeypatch):
    monkeypatch.setattr(
        "music_creation_engine.services.render_service.render_demo_artifacts",
        lambda request: {"mp3": f"{request.output_base}.mp3"},
    )
    client = TestClient(create_app())

    workflow = client.post(
        "/v1/workflows/full",
        json={"lyrics": "hello world", "output_base": "build/output/song", "render_demo": False},
    ).json()

    revised = client.post(
        f"/v1/workflows/{workflow['workflow_id']}/revise",
        json={"render_demo": True},
    )

    assert revised.status_code == 200
    payload = revised.json()
    assert payload["revision_of"] == workflow["workflow_id"]
    assert "score" in payload.get("reused_stages", [])
    assert payload["render"] is not None
