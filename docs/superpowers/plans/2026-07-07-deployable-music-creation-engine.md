# Deployable Music Creation Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the repository into a deployable CLI + HTTP API application with agent adapters and configurable integrations.

**Architecture:** Build a layered Python package with shared services used by both CLI and FastAPI. Keep public integrations enabled by default, advanced integrations optional, and agent-specific files isolated under adapter directories.

**Tech Stack:** Python, FastAPI, pytest, PyYAML, music21, LilyPond, FluidSynth, FFmpeg

---

### Task 1: Create package skeleton and config model

**Files:**
- Create: `pyproject.toml`
- Create: `src/music_creation_engine/__init__.py`
- Create: `src/music_creation_engine/config.py`
- Create: `src/music_creation_engine/models.py`
- Create: `config/defaults.yaml`
- Test: `tests/test_config.py`

- [ ] **Step 1: Write the failing test**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Write minimal configuration and model code**
- [ ] **Step 4: Run test to verify it passes**

### Task 2: Create capability detection and integration registry

**Files:**
- Create: `src/music_creation_engine/capabilities.py`
- Create: `src/music_creation_engine/integrations/base.py`
- Create: `src/music_creation_engine/integrations/meting.py`
- Create: `src/music_creation_engine/integrations/memory.py`
- Create: `src/music_creation_engine/integrations/research.py`
- Test: `tests/test_capabilities.py`

- [ ] **Step 1: Write the failing tests**
- [ ] **Step 2: Run tests to verify they fail**
- [ ] **Step 3: Implement minimal capability registry**
- [ ] **Step 4: Run tests to verify they pass**

### Task 3: Move score and render workflows behind services

**Files:**
- Create: `src/music_creation_engine/services/score_service.py`
- Create: `src/music_creation_engine/services/render_service.py`
- Create: `src/music_creation_engine/services/workflow_service.py`
- Modify: `scripts/sheet_music_generator.py`
- Modify: `scripts/demo_renderer.py`
- Test: `tests/test_services.py`

- [ ] **Step 1: Write the failing tests**
- [ ] **Step 2: Run tests to verify they fail**
- [ ] **Step 3: Implement service wrappers and script compatibility**
- [ ] **Step 4: Run tests to verify they pass**

### Task 4: Add CLI entrypoint

**Files:**
- Create: `src/music_creation_engine/cli.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write the failing tests**
- [ ] **Step 2: Run tests to verify they fail**
- [ ] **Step 3: Implement CLI command routing**
- [ ] **Step 4: Run tests to verify they pass**

### Task 5: Add FastAPI application

**Files:**
- Create: `src/music_creation_engine/api/app.py`
- Test: `tests/test_api.py`

- [ ] **Step 1: Write the failing tests**
- [ ] **Step 2: Run tests to verify they fail**
- [ ] **Step 3: Implement API routes**
- [ ] **Step 4: Run tests to verify they pass**

### Task 6: Add agent adapters and installer support

**Files:**
- Create: `adapters/hermes/SKILL.md`
- Create: `adapters/codex/AGENTS.md`
- Create: `adapters/openclaw/README.md`
- Create: `examples/hermes-workflow.md`
- Create: `examples/codex-workflow.md`
- Create: `examples/openclaw-workflow.md`
- Modify: `install.sh`
- Test: `tests/test_adapter_install.py`

- [ ] **Step 1: Write the failing tests**
- [ ] **Step 2: Run tests to verify they fail**
- [ ] **Step 3: Implement adapter files and installer changes**
- [ ] **Step 4: Run tests to verify they pass**

### Task 7: Update deployment and continuous-development docs

**Files:**
- Modify: `README.md`
- Modify: `references/install-guide.md`
- Create: `references/integration-matrix.md`
- Create: `references/continuous-development.md`
- Modify: `references/sync-audit-2026-07-07.md`

- [ ] **Step 1: Document the new deployable structure**
- [ ] **Step 2: Document public vs advanced integrations**
- [ ] **Step 3: Document agent adapter installation and workflows**
- [ ] **Step 4: Update continuous-development handoff**

### Task 8: Verify end-to-end

**Files:**
- Modify: `tests/install_paths.sh`
- Create: `tests/test_end_to_end_layout.py`

- [ ] **Step 1: Add verification coverage for new paths and package layout**
- [ ] **Step 2: Run focused tests**
- [ ] **Step 3: Run full test suite**
- [ ] **Step 4: Confirm docs and install flow stay consistent**
