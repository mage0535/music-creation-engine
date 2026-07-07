#!/usr/bin/env python3
"""Full end-to-end workflow test via HTTP TestClient."""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
os.environ["MCE_OUTPUT_DIR"] = "build/test_output"

from fastapi.testclient import TestClient
from music_creation_engine.api.app import create_app

client = TestClient(create_app())
passed = 0
failed = 0

def check(name: str, condition: bool, detail: str = ""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS: {name}")
    else:
        failed += 1
        print(f"  FAIL: {name} — {detail}")

# 1. Health
r = client.get("/health")
check("Health endpoint", r.status_code == 200 and r.json()["status"] == "ok")

# 2. Capabilities
r = client.get("/capabilities")
check("Capabilities endpoint", r.status_code == 200 and "tools" in r.json())

# 3. Score with note-name melody (the critical LLM-friendly feature)
r = client.post("/v1/score", json={
    "lyrics": "hello world test song",
    "output_base": "build/test_output/note_name_test",
    "key": "Am", "bpm": 72,
    "instruments": "piano,vocals",
    "chord_progression": ["Am", "F", "C", "G"],
    "sections": [{"name": "intro", "bars": 4, "key": "Am"}, {"name": "verse", "bars": 8, "key": "Am"}],
    "melody": {"vocals": ["A4", "B4", "C5", "A4", "G4", "E4", "F4", "E4"]},
    "instrument_roles": {"piano": "chord", "vocals": "melody"},
})
check("Score with note names", r.status_code == 200)
if r.status_code == 200:
    j = r.json()
    check("MIDI generated", ".mid" in j.get("midi", ""))
    check("Chords used", j["request_echo"]["chord_progression"] == ["Am", "F", "C", "G"])
    melody_echo = j["request_echo"]["melody"]
    expected_midi = {"vocals": [69, 71, 72, 69, 67, 64, 65, 64]}
    check("Note names parsed correctly (A4=69, B4=71, C5=72)",
          melody_echo.get("vocals") == expected_midi["vocals"],
          f"got {melody_echo.get('vocals')}")

# 4. Score with MIDI numbers (backward compat)
r = client.post("/v1/score", json={
    "lyrics": "test",
    "output_base": "build/test_output/midi_num_test",
    "key": "C", "bpm": 120,
    "chord_progression": ["C", "G", "Am", "F"],
    "melody": {"vocals": [60, 62, 64, 65, 67, 69, 71, 72]},
})
check("Score with MIDI numbers (backward compat)", r.status_code == 200 and ".mid" in r.json().get("midi", ""))

# 5. Full workflow with artifact tracking
r = client.post("/v1/workflows/full", json={
    "lyrics": "full workflow test",
    "output_base": "build/test_output/wf_test",
    "key": "Dm", "bpm": 60,
    "render_demo": False,
})
check("Workflow creates workflow_id", r.status_code == 200 and "workflow_id" in r.json())
if r.status_code == 200:
    wid = r.json()["workflow_id"]
    check("workflow_id not empty", len(wid) == 12)

    # 6. Artifact manifest
    r2 = client.get(f"/v1/artifacts/{wid}")
    check("Manifest retrievable", r2.status_code == 200)
    if r2.status_code == 200:
        m = r2.json()
        check("Manifest has workflow_id", m.get("workflow_id") == wid)
        check("Manifest has files list", isinstance(m.get("files"), list))

    # 7. Checkpoints
    r3 = client.get(f"/v1/workflows/{wid}/checkpoints")
    check("Checkpoints retrievable", r3.status_code == 200)
    if r3.status_code == 200:
        check("Checkpoints non-empty", len(r3.json()) > 0)

    # 8. File download
    r4 = client.get(f"/v1/artifacts/{wid}/files/composition.mid")
    check("File download works", r4.status_code == 200)
    if r4.status_code == 200:
        check("File has content", len(r4.content) > 0)

    # 9. Revision
    r5 = client.post(f"/v1/workflows/{wid}/revise", json={"bpm": 80})
    check("Revision creates new workflow", r5.status_code == 200 and "workflow_id" in r5.json())
    if r5.status_code == 200:
        check("Revision tracks parent", r5.json().get("revision_of") == wid)

# 10. MIDI inspect (note list)
r = client.post("/v1/midi/inspect", json={"notes": [60, 62, 64, 65, 67]})
check("MIDI inspect notes", r.status_code == 200)
if r.status_code == 200:
    check("MIDI inspect counts correctly", r.json()["count"] == 5)

# 11. MIDI query
r = client.post("/v1/midi/query", json={"notes": [60, 62, 64, 65, 67], "min_pitch": 64})
check("MIDI query filters", r.status_code == 200)
if r.status_code == 200:
    check("MIDI query min_pitch=64 gives 3 notes", r.json()["count"] == 3)

# 12. MIDI diff
r = client.post("/v1/midi/diff", json={"left_notes": [60, 62, 64], "right_notes": [60, 64, 65]})
check("MIDI diff", r.status_code == 200)
if r.status_code == 200:
    check("Diff added [65]", r.json()["added"] == [65])
    check("Diff removed [62]", r.json()["removed"] == [62])

# 13. Playability
r = client.post("/v1/playability", json={"instrument": "piano", "notes": [48, 60, 72, 84, 96]})
check("Playability", r.status_code == 200)
if r.status_code == 200:
    check("Playability flags wide span", r.json()["playable"] is False)
    check("Playability returns warnings", len(r.json().get("warnings", [])) > 0)

# 14. Reference search
r = client.post("/v1/references/search", json={"keyword": "test song", "platform": "netease"})
check("Reference search", r.status_code == 200)
if r.status_code == 200:
    check("Reference search returns source", r.json().get("source") == "meting")

# Summary
print()
print(f"=== RESULTS: {passed} passed, {failed} failed, {passed + failed} total ===")
sys.exit(1 if failed > 0 else 0)
