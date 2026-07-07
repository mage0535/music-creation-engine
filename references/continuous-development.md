# Continuous Development Log

---

## 2026-07-07 — External Project Survey & Integration Analysis

> **Status:** Research document for colleague discussion. Covers 10 user-nominated projects + 10 independently discovered projects.
> **Method:** GitHub analysis via web search, README parsing, architecture extraction.

### Part A: User-Nominated Projects

#### A1. hgsanyang/SoulTuner-Agent
- **What:** AI music recommendation agent. LangGraph multi-node workflow, Hybrid RAG (Neo4j knowledge graph + dual audio embeddings M2D-CLAP/OMAR-RQ), GraphZep long-term memory, SSE streaming, music journey curation.
- **Tech:** Python, Next.js, LangGraph, Neo4j, SearxNG, Tavily.
- **Relevance to us:** **LOW** for direct integration. It's a music *recommendation* system, not a *composition* system. Requires GPU (dual audio embeddings). However, three patterns are instructive:
  - **Hybrid RAG pattern** (GraphRAG + semantic search → merge & dedup) could inform our reference search enhancement.
  - **GraphZep long-term memory** — cross-session user preference retention pattern could inform artifact tracking.
  - **Data flywheel** (search → download → tag → embed → Neo4j) is a mature ingestion pipeline reference.
- **Verdict:** ❌ Not integratable (GPU required, different domain). 📖 Pattern reference only.

#### A2. XUTENGXIANG/ai-music-creator
- **What:** Demo-level AI music creator. Original architecture-report flagged as "too little to adopt."
- **Relevance to us:** **NONE**. Insufficient maturity.
- **Verdict:** ❌ Skip.

#### A3. fa1314/ip-human-agent
- **What:** Super-IP digital human agent 4.0. Cloud compute scheduling, NLP, TTS, digital human rendering, video editing, multi-platform publishing. Full pipeline: extract reference copy → rewrite → voice clone → digital human video → subtitles/BGM → title/cover → publish.
- **Tech:** Python, cloud APIs.
- **Relevance to us:** **LOW** for music composition. **MEDIUM** for one specific pattern:
  - **Multi-platform publishing pipeline**: The 7-stage "extract → rewrite → render → publish" chain mirrors our planned publish phase. The error handling, retry logic, and platform-specific formatting layers are directly reusable design patterns.
- **Verdict:** ❌ Not integratable (unrelated domain). 📖 Publishing pipeline pattern reference.

#### A4. Tz-WIND/ATRI_AGENT ⭐⭐⭐
- **What:** Local-first AI Agent native music workstation. Python backend + Rust audio engine + Web DAW frontend. The most architecturally complete open-source AI music workstation found.
- **Key capabilities:**
  - **MIDI tools for agents**: `midi_query`, `midi_inspect`, `midi_write`, `midi_diff`, `midi_batch_edit` — agents can read and write MIDI at the note/controller level.
  - **Piano playability checker**: Checks span, density, leaps, hand crossings.
  - **Rust Audio Host**: CPAL-based, VST3 scanning/loading, Basic Synth, MIDI → audio playback.
  - **VST3 Bridge**: Embeds agent directly into Studio One / REAPER as a VST3 plugin.
  - **MCP/Skills extension**: Compatible with our adapter model.
  - **DAWproject import/export**: Interoperability with external DAWs.
  - **Agent Runtime**: OpenAI + Anthropic API, tool calling, sub-agent scheduling, session persistence.
- **Tech:** Python (Quart, music21, mido), Rust (CPAL, VST3), TypeScript (React DAW UI).
- **Relevance to us:** **HIGH**. This is the closest project to our vision. Key integration/reference points:
  - **MIDI tool definitions** — We could adopt `midi_write`/`midi_diff`/`midi_inspect` as API endpoints in our Engine, giving agents granular control over generated MIDI.
  - **Piano playability check** — Directly useful as a quality validation step in our pipeline (Stage 6).
  - **Rust audio engine pattern** — If we ever need local real-time playback, this is the reference architecture.
  - **DAWproject interoperability** — If we want to support Studio One / REAPER round-tripping.
- **Constraint:** Requires significant Rust toolchain. The MIDI tools are Python and could be extracted without the Rust host.
- **Verdict:** 📖 **High-value pattern reference.** Extract MIDI tool definitions, piano playability checker. Full integration too heavy (Rust + frontend).

#### A5. shaozheng0503/aimv-studio
- **What:** AI music video generation via multi-agent collaboration. CrewAI orchestrates 4 agents: screenwriter, director, music producer, verifier. Generates images (Z-image), video (Wan2.2/Seedance/Veo), music (ACEStep/Suno/Lyria).
- **Tech:** Python, CrewAI, various cloud APIs.
- **Relevance to us:** **LOW** for music composition (it consumes music APIs, doesn't generate scores). **MEDIUM** for:
  - **CrewAI multi-agent orchestration pattern** — The way roles are defined, tasks delegated, and results validated could inform our eventual multi-agent lyrics workflow.
  - **Verifier agent pattern** — Having a dedicated validation agent that checks outputs before presenting to user is a good architecture pattern.
- **Constraint:** Requires GPU (Wan2.2 video generation).
- **Verdict:** ❌ Not integratable. 📖 CrewAI orchestration pattern reference.

#### A6. FF0214/ai-music-studio
- **What:** Original architecture-report description: "Multi-agent music industrialization using Suno API. Hot topics → lyrics → music → review, fully automated."
- **Relevance to us:** **LOW**. Suno API-dependent, no score generation, no local rendering.
- **Verdict:** ❌ Skip. The "hot topic → lyrics" pipeline concept is noted but Suno-centric.

#### A7. YoungB1oodXD/music-agent
- **What:** Original architecture-report: contains torch dependency, requires FMA dataset (106,573 songs, large disk).
- **Relevance to us:** **NONE**. GPU/dataset-dependent, incompatible with our CPU-only strategy.
- **Verdict:** ❌ Skip.

#### A8. GuJiV/TikTok-Agent-Script-Studio
- **What:** Multi-stage pipeline + compliance review pattern for TikTok content. Original architecture-report noted "multi-stage pipeline + compliance review design pattern."
- **Relevance to us:** **LOW** for music. **MEDIUM** for pipeline architecture:
  - **Multi-stage pipeline with gates**: Each stage has input validation → processing → output check → gate decision. This is the right architecture for our 7-stage workflow.
  - **Compliance review pattern**: Equivalent to our planned quality evaluation stage.
- **Verdict:** ❌ Not integratable. 📖 Pipeline gating pattern reference.

#### A9. treesan/vcutclaw (CutClaw)
- **What:** Multi-agent long-form video editing with music synchronization. LLM-driven Screenwriter → Editor → Reviewer loop. Extracts musical beats and energy signals (madmom) for rhythm-aware cuts.
- **Tech:** Python, LLM (OpenAI-compatible via LiteLLM), madmom (beat detection), moviepy.
- **Relevance to us:** **LOW** for composition. **MEDIUM** for:
  - **Multi-agent review loop pattern**: Screenwriter plans → Editor executes → Reviewer validates → loop back. This three-role loop is directly applicable to our lyrics generation or composition planning phases.
  - **LiteLLM integration pattern**: Using a unified LLM gateway to support multiple providers. Relevant if we ever add LLM-calling capability to the Engine (though this is currently Agent's responsibility).
  - **Music-aware sync (madmom)**: beat/BPM detection from audio could be useful for our planned "recording analysis" feature (Stage 8).
- **Constraint:** GPU recommended (torch video decoding).
- **Verdict:** ❌ Not integratable for core. 📖 Review loop + madmom beat detection patterns.

#### A10. elfbobo/yinova
- **What:** Architecture-report mentions this as a Hermes branch already covered by our core capabilities. The author (elfbobo) has a more relevant project: **SingerOS** — an enterprise multi-agent AI OS with agent runtime, skill governance, workflow engine, model routing, and multi-tenant deployment.
- **Relevance to us:** **LOW** for music. The SingerOS architecture (agent runtime + skill proxy + model cost governance) is a deployment-pattern reference only.
- **Verdict:** ❌ Skip. Architecture-report already assessed as overlapping with our core.

---

### Part B: Independently Discovered Projects

#### B1. voho/midi-composer-mcp ⭐⭐⭐⭐⭐
- **Repo:** https://github.com/voho/midi-composer-mcp
- **What:** A comprehensive MCP server with **40+ deterministic music-theory and composition tools**. Design philosophy: "the tools contain the rules, the LLM contains the creativity."
- **Tool categories:**
  - **Scales**: 40+ scale types (common/modal/jazz/symmetric/world), note generation, scale matching.
  - **Chords**: 35+ chord types (triads through 13ths), chord matching, inversion detection.
  - **Harmony**: Diatonic chords, degree→chord resolution, voice leading, secondary dominants, tritone substitution, negative harmony, harmonize_melody.
  - **Melody**: Scale degrees→notes, motif grammar (ABAC forms), melodic walk, sequence, arpeggiate, tintinnabuli (Arvo Pärt style), species counterpoint (1-5), snap_to_scale, transpose.
  - **Rhythm**: Euclidean rhythms, groove presets (four-on-the-floor, backbeat, clave, bossa, dembow).
  - **Song Structure**: `plan_sections` (intro/verse/chorus/bridge/outro), `arrange_song` (assemble into whole-song MIDI).
  - **Rendering**: notes_to_midi, chords_to_midi, drums_to_midi, arrange_to_midi, song_to_midi, **midi_to_audio** (built-in synth, no soundfont needed!).
- **Tech:** Python, mido (MIDI), FastMCP. No GPU. No soundfont required.
- **Relevance to us:** **EXTREMELY HIGH**. This is essentially what our Engine's runtime layer *should* be — a rich set of deterministic music theory tools that an Agent can call via MCP. Key alignment points:
  - Same philosophy: Agent decides creatively, Engine executes deterministically.
  - All tools are compatible (output of one is valid input to another) — our API endpoints should follow this contract.
  - Built-in audio synthesis without soundfont — could eliminate our fluidsynth/ffmpeg dependency chain.
  - Song structure tools (`plan_sections`, `arrange_song`) directly address our "API parameter surface too coarse" gap.
- **Integration strategy:**
  - **Option A (Light)**: Study the tool definitions and add equivalent capabilities to our API surface (Section structure, chord progression, melody note sequence parameters).
  - **Option B (Medium)**: Register midi-composer-mcp as an MCP server alongside our Engine. Agent calls both: our Engine for the full pipeline, midi-composer-mcp for granular MIDI operations.
  - **Option C (Deep)**: Fork and merge the tool implementations into our runtime layer, providing both MCP tools and HTTP endpoints.
- **Verdict:** 📖🔧 **Highest-priority reference. Strongly recommend Option A or B.**

#### B2. tskovlund/mcp-score ⭐⭐⭐⭐
- **Repo:** https://github.com/tskovlund/mcp-score
- **What:** MCP server for AI-driven music score generation. Natural language → music21 Python script generation → MusicXML. Live MuseScore integration via WebSocket plugin. 19 commands for live score manipulation (note input, chord symbols, rehearsal marks, barlines, key/time signatures, transposition).
- **Tech:** Python (music21, FastMCP), QML (MuseScore plugin), WebSocket.
- **Key design insight:** Claude writes a complete music21 script, executes it, hands back MusicXML. No MCP round-trips needed for initial generation — just code generation + execution. Then MCP for live editing.
- **Relevance to us:** **HIGH**. 
  - **Code generation pattern**: Instead of building a huge API surface, let the Agent generate a music21 Python script and execute it. This is a powerful alternative to our "expand API parameters" approach — it side-steps the parameter surface problem entirely.
  - **MuseScore integration**: If we ever want live score preview/editing (beyond static PDF), this WebSocket plugin architecture is the reference.
  - **mcp-score install-skill**: Shows how to package a Claude Code skill alongside an MCP server — our adapter model could follow this.
- **Verdict:** 📖🔧 **High-value reference. The code-generation pattern is a compelling architectural alternative to parameter expansion.**

#### B3. mage0535/music-creation-engine ⭐⭐⭐⭐⭐
- **Repo:** https://github.com/mage0535/music-creation-engine
- **What:** **This is a derivative/fork of OUR project!** Released as v1.0.0 on 2026-06-10. Has added features that our v0.2.0 doesn't have:
  - **Multi-agent lyric writing**: Lyricist Agent, Composer Agent, Producer Agent.
  - **Quality evaluation**: 4 parallel agents (melody/rhythm/emotion/structure).
  - **Platform publishing**: AiToEarn MCP integration.
  - **Conversational workflow**: Agent detects music intent naturally, guides through full pipeline in dialogue.
  - **SKILL.md orchestrator**: `delegate_task` for multi-agent coordination.
  - Detailed dependency table with sizes.
  - Environment compatibility matrix (Linux ✅, macOS ⚠️).
- **Tech:** Identical stack to ours (music21, abjad, lilypond, fluidsynth, ffmpeg, meting-agent).
- **Relevance to us:** **CRITICAL**. This shows what another developer already built on top of our codebase. We should:
  - Diff their v1.0.0 against our v0.2.0 to identify all added features.
  - Evaluate which additions fit our architecture (multi-agent lyrics → Agent layer, not Engine layer? Quality eval → could be both?).
  - Check if their SKILL.md pattern is compatible with our adapter model.
- **Verdict:** 🔧🔍 **Must review. Diff analysis recommended as next step.**

#### B4. viktorkelemen/music21-composer-mcp ⭐⭐⭐
- **Repo:** https://github.com/viktorkelemen/music21-composer-mcp
- **What:** Composition-focused MCP server built on music21. Tools: generate_melody (constraint-based), transform_phrase (sequence/inversion/retrograde), reharmonize, add_voice (counterpoint), realize_chord, export_midi.
- **Status:** Early stage (only export_midi fully implemented, rest in Phase 2-6).
- **Relevance to us:** **MEDIUM**. Good concept but immature. Tool definitions could inform our API design. Overlaps significantly with B1 (midi-composer-mcp) which is more complete.
- **Verdict:** 📖 Pattern reference. Superseded by B1 for practical purposes.

#### B5. deer/music.build ⭐⭐⭐
- **Repo:** https://github.com/deer/music.build
- **What:** MCP server for AI music composition. Typed, immutable music theory library — pitches, rhythms, harmony, form, transforms. 47 MCP tools. Exports to MIDI and LilyPond. Agents compose incrementally.
- **Tech:** Java 25 (not Python).
- **Key features:** Walking bass generation, chord voicings, diatonic harmonization, multi-section forms with volta endings, voice leading checks, range rules.
- **Relevance to us:** **MEDIUM**. Impressive feature set but Java-based (not integratable into our Python stack). The tool taxonomy and API design are excellent references:
  - Music theory as first-class types (Pitch, Voice, Score, Form).
  - Immutable data flow — every transform returns a new value.
  - Session event log for replayability.
- **Verdict:** 📖 Design pattern reference. Java stack incompatible.

#### B6. XIAODUOLU/Midra ⭐⭐⭐⭐
- **Repo:** https://github.com/XIAODUOLU/Midra (46 stars, Apache 2.0)
- **What:** Agentic prompt-to-code MIDI composition framework. Turns natural language → structured music code → editable MIDI. Checkpoint-native pipeline with resume support.
- **Pipeline stages:** Intent Agent → Song Agent → Arrangement Agent → Note Planning Agent → MIDI assembly → audio rendering (fluidsynth/ffmpeg).
- **Key design:** Prompt-to-code first (not prompt-to-audio). Intermediate planning artifacts as checkpoint JSON. Editable MIDI output. Rule mode (deterministic) + LLM mode side by side.
- **Tech:** Python, music21, fluidsynth, ffmpeg, FastAPI.
- **Relevance to us:** **HIGH**. This is architecturally closest to what our pipeline *should* be:
  - **Checkpoint-native**: Each stage persists JSON, can resume from any stage. Our current workflow has no checkpointing.
  - **Agent-per-stage**: Intent → Song → Arrangement → Note — maps cleanly to our 7-stage blueprint.
  - **Dual mode**: Rule-based (deterministic, our current mode) and LLM-based side by side — exactly the fallback pattern we need.
  - **Docker support**: Frontend + Backend, config.yaml for runtime values.
- **Verdict:** 📖🔧 **High-value pattern reference. The checkpoint pipeline architecture should be our target for workflow persistence.**

#### B7. bonfire-audio/reaper-mcp ⭐⭐⭐⭐
- **Repo:** https://github.com/bonfire-audio/reaper-mcp (49 stars)
- **What:** MCP server enabling AI agents to control REAPER DAW. 58 tools: project management, tracks, MIDI (`create_midi_item`, `add_midi_note`, `create_chord_progression`, `create_drum_pattern`), FX, mixing, mastering, rendering, audio analysis.
- **Tech:** Python (python-reapy), communicates with REAPER via distant API.
- **Relevance to us:** **HIGH**. Already listed in our architecture-report as a core tool. Key tools relevant to us:
  - `create_chord_progression` — direct chord progression → MIDI item conversion.
  - `create_drum_pattern` — drum pattern generation.
  - `add_midi_note` — granular note insertion.
  - Mastering tools: EQ, compression, limiting, stereo widening.
  - Render with format options.
- **Constraint:** Requires REAPER DAW installed. Not headless-friendly.
- **Verdict:** 🔧 **Integratable for users with REAPER. Register as optional MCP server in our config.**

#### B8. truffle-ai/music-creator-mcp ⭐⭐
- **Repo:** https://github.com/truffle-ai/mcp-servers/tree/main/src/music
- **What:** Lean MCP server: `create_music` (melody/chord/harmony), `create_pattern` (drums/rhythm), `analyze_music`, `mix_tracks`, `convert_audio`, `apply_effect`.
- **Tech:** Python (music21, librosa, pydub, pretty_midi).
- **Relevance to us:** **MEDIUM**. Simple, clean toolset. Could serve as a lightweight alternative to more complex solutions. The `analyze_music` (tempo, key, spectral analysis) tool fills a gap we currently have.
- **Verdict:** 📖 Lightweight reference. The audio analysis capability is worth noting.

#### B9. brightlikethelight/music21-mcp-server ⭐
- **What:** MCP server providing multiple pathways to music21 analysis functions.
- **Relevance to us:** **LOW**. Overlaps with viktorkelemen and truffle-ai solutions.
- **Verdict:** ❌ Redundant.

#### B10. Ratnesh-181998/GenAI-Music-Composer ⭐⭐
- **Repo:** https://github.com/Ratnesh-181998/GenAI-Music-Composer (1 star)
- **What:** Production-grade GenAI music composer. LLM (Groq/Llama-3.1) → music21 → NumPy/SciPy audio synthesis. Streamlit UI. Docker + GKE deployment.
- **Pipeline:** LLM Analysis → Music Theory Layer (music21 validation) → Sequence Generation → Waveform Synthesis → UI Presentation.
- **Relevance to us:** **LOW** for architecture (standalone app, not agent-native). **MEDIUM** for:
  - **Docker/K8s deployment pattern**: Complete CI/CD pipeline (GitLab) + GKE deployment reference.
  - **LangChain prompt orchestration**: Shows how to structure multi-step LLM calls for music generation.
- **Verdict:** 📖 Deployment pattern reference. Architecture incompatible (standalone, not agent-tool).

---

### Part C: Summary Matrix

| Project | Stars | Stack | Domain | Integratable? | Pattern Value | Priority |
|---------|-------|-------|--------|---------------|---------------|----------|
| **voho/midi-composer-mcp** | — | Python, mido, MCP | Composition tools | 🔧 MCP register | ⭐⭐⭐⭐⭐ | P0 review |
| **mage0535/music-creation-engine** | 0 | Python (ours) | **Our fork!** | 🔧 Diff + merge | ⭐⭐⭐⭐⭐ | P0 diff |
| **XIAODUOLU/Midra** | 46 | Python, music21 | Prompt→MIDI pipeline | 📖 Architecture | ⭐⭐⭐⭐ | P1 review |
| **tskovlund/mcp-score** | 11 | Python, QML | Score gen + live edit | 🔧 MCP + pattern | ⭐⭐⭐⭐ | P1 review |
| **bonfire-audio/reaper-mcp** | 49 | Python, REAPER | DAW control | 🔧 MCP register | ⭐⭐⭐⭐ | P1 (existing plan) |
| **Tz-WIND/ATRI_AGENT** | 13 | Python, Rust, TS | AI DAW workstation | 📖 MIDI tools | ⭐⭐⭐ | P2 extract |
| **deer/music.build** | 1 | Java | MCP composition | 📖 Design ref | ⭐⭐⭐ | P2 reference |
| **viktorkelemen/music21-composer-mcp** | 0 | Python | Composition MCP | 📖 Tool defs | ⭐⭐ | P2 (superseded) |
| **truffle-ai/music-creator-mcp** | — | Python | Music tools | 📖 Analysis tool | ⭐⭐ | P3 reference |
| **hgsanyang/SoulTuner-Agent** | 6 | Python, Neo4j | Recommendation | ❌ GPU required | ⭐⭐ (RAG pattern) | P3 reference |
| **fa1314/ip-human-agent** | 18 | Python | Video publishing | ❌ Unrelated | ⭐⭐ (publish pipeline) | P3 reference |
| **treesan/vcutclaw** | — | Python, LLM | Video editing | ❌ GPU recommended | ⭐⭐ (review loop) | P3 reference |
| **shaozheng0503/aimv-studio** | 10 | Python, CrewAI | MV generation | ❌ GPU required | ⭐ (CrewAI pattern) | P4 reference |
| **Ratnesh-181998/GenAI-Music-Composer** | 1 | Python, Docker | Music composer | ❌ Standalone | ⭐ (deploy pattern) | P4 reference |
| **GuJiV/TikTok-Agent-Script-Studio** | — | Python | TikTok content | ❌ Unrelated | ⭐ (pipeline gates) | P4 reference |
| **All others (6 projects)** | — | — | — | ❌ Skip | — | — |

### Part D: Recommended Action Items (For Discussion)

| # | Action | Based on | Effort |
|---|--------|----------|--------|
| 1 | **Diff mage0535/music-creation-engine v1.0.0 vs our v0.2.0** | B3 | 1h |
| 2 | **Evaluate midi-composer-mcp as MCP server alongside Engine** | B1 | 2h |
| 3 | **Study Midra's checkpoint pipeline architecture for workflow persistence** | B6 | 1h read |
| 4 | **Study mcp-score's code-generation pattern** (Agent generates music21 script, Engine executes) | B2 | 1h read |
| 5 | **Integrate reaper-mcp as optional MCP server in config** | B7 | 1h |
| 6 | **Extract ATRI_AGENT's MIDI tool definitions as API design reference** | A4 | 1h |
| 7 | **Evaluate built-in audio synthesis (midi-composer-mcp's approach)** to potentially remove fluidsynth dependency | B1 | 2h |

### Part E: Analysis & Opinion

> Personal assessment from Session 3 operator for colleague discussion.

#### Core Judgment: We Are Not Alone, and That's Good

After surveying 20 projects, the landscape is clear: **at least 4-5 teams are building the same thing.** The architecture-report from Dev 1 mapped the territory correctly — the vision of "LLM Agent as composer, local tools as executor" is the emerging consensus. The difference is execution maturity:

| Team | What they have | What we lack |
|------|---------------|--------------|
| **mage0535** (our fork) | Multi-agent lyrics, quality eval, publish pipeline, SKILL.md orchestrator | v0.2.0 stopped at scaffold |
| **Midra** | Checkpoint pipeline, intent→song→arrangement→notes agent chain, Docker | No checkpointing, no agent-per-stage |
| **ATRI_AGENT** | MIDI query/diff/write tools, piano playability, Rust audio host, VST3 bridge | Monolithic score generation, no MIDI editing tools |
| **midi-composer-mcp** | 40+ deterministic theory tools, built-in audio synth, LLM-tool-calling native | Template-based generation, external synth dependency |

**Conclusion:** Our v0.2.0 is not ahead of the curve. It is structurally correct but functionally about 6-12 months behind the leading edge of open-source music-agent tooling. The good news: our architecture (Agent ↔ Engine separation, Protocol backend injection, adapter model) is the right foundation to absorb these advances.

#### What We Should NOT Do

1. **Do not add LLM calling to the Engine.** Multiple projects (SoulTuner, GenAI-Music-Composer) embed LLM directly in the pipeline. This coupling is the wrong choice for us. Our adapter architecture already delegates LLM to the Agent layer. Adding LLM to the Engine would create dual decision-making that: duplicates the Agent's role, creates inconsistency (which LLM call "wins"?), complicates testing (LLM calls are non-deterministic), and violates our own `AGENTS.md` rule: "Prefer package entrypoints over directly re-implementing workflow logic."

2. **Do not adopt the code-generation pattern (mcp-score) as primary interface.** The idea of letting the Agent generate a music21 Python script and executing it is elegant. But it trades API stability for flexibility — Agent-generated code can fail silently, produce malformed MIDI, or have security implications. Our existing API contract (structured JSON in, structured JSON out) is safer and more testable. Use code-generation as a power-user escape hatch, not the default.

3. **Do not chase the DAW integration (ATRI, reaper-mcp) right now.** These are impressive but require heavy external dependencies (REAPER DAW, Rust toolchain, VST3). Our core value is headless, CPU-only, dependency-light execution. DAW integration is a P3 feature for users who happen to have REAPER.

#### What We SHOULD Do (Priority Order)

##### P0 — Absorb mage0535's v1.0.0 Diff

This is not optional. Someone already extended our codebase. We need to: clone their repo, diff against ours, identify what they added, evaluate whether additions should merge into the Engine or stay in the Agent layer. **Risk:** If they changed our core generation logic, we may have divergent codebases. The license (no LICENSE file in our repo) means we need to clarify IP before merging.

##### P0 — Integrate midi-composer-mcp as a Sidecar MCP Server

The single highest-leverage move available. This one project fills 80% of our parameter-surface gap without us writing a single music theory tool. Agent calls midi-composer-mcp for granular theory operations (walking bass, voice leading, chord voicing, arrangement); our Engine orchestrates the pipeline and manages artifacts (MIDI → MusicXML → LilyPond → PDF → MP3). Implementation: add to `config/defaults.yaml` integrations, document in adapters, add wrapper in `integrations/`.

##### P1 — Implement Checkpoint Pipeline (Inspired by Midra)

Our current `POST /v1/workflows/full` is a fire-and-forget black box. Midra's checkpoint architecture solves the real user problem: "I like the verse but not the chorus. Let me redo just the chorus." Implementation: `PipelineCheckpoint` model, stage-by-stage JSON checkpoint files, `POST /v1/score/revision {workflow_id, stage, changes}`, `GET /v1/workflows/{workflow_id}/checkpoints`.

##### P1 — Expand API Parameters (Our Own Design, Informed by MCP Tools)

Even with midi-composer-mcp as a sidecar, our own API needs to accept structured musical parameters. The MCP tools show us WHAT parameters matter. Our implementation adds to ScoreRequest: `chord_progression: list[str]`, `sections: list[Section]`, `melody: dict[str, list[int]]`, `articulation: dict[str, str]`. All optional, backward compatible. This is the bridge between "Agent can think it" and "Engine can execute it."

##### P2 — Replace fluidsynth with Built-in Audio Synthesis

midi-composer-mcp has a built-in Python audio synthesizer that generates playable WAV without any soundfont. If we adopt this: eliminate ~150MB dependency (fluid-soundfont-gm), eliminate "SoundFont not found" errors (our top crash on Windows), faster render (no subprocess), simpler Docker image. Trade-off: lower audio quality (additive synthesis vs. GM soundfont) — acceptable for "demo" tier. Keep fluidsynth as optional "production" backend (pluggable via existing Protocol pattern).

##### P2 — Add Piano Playability Check (from ATRI_AGENT)

A cheap, high-value quality gate. Before returning a score, check: hand span, note density, leaps, hand crossings. Returns warnings in the artifact manifest. Agent can surface: "This piano part has a 12th interval in bar 8 — most players can't reach that."

##### P3 — Register reaper-mcp as Optional Integration

Already in our architecture-report. Just needs the `integrations/` wrapper and config entry. Low effort, high optionality for users with REAPER.

#### What Remains the Agent's Job (Not Ours)

To be crystal clear about boundaries:

| Capability | Where It Lives | Why |
|-----------|---------------|-----|
| Multi-agent lyrics | Agent (via prompt templates) | LLM reasoning, no local tools needed |
| Style analysis & reference | Agent + Meting-Agent MCP | LLM interprets search results |
| Composition planning (key/BPM/chords/structure) | Agent (LLM) → Engine (execution) | Agent decides, Engine executes |
| Quality evaluation (scoring) | Agent (LLM) | Subjective judgment, no deterministic rules |
| Publishing | Agent + external MCPs (AiToEarn) | Platform APIs, auth, rate limiting — not Engine's domain |
| User dialogue & iteration | Agent | Conversation management is Agent's core competency |

#### Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| mage0535 v1.0.0 diverged significantly from our codebase | Medium | High | Do the diff first, decide merge vs. cherry-pick before writing code |
| midi-composer-mcp has license incompatibility | Low | Medium | Check license before integration; can vendor tool implementations if needed |
| midi-composer-mcp is abandoned/unmaintained | Medium | Medium | We only need the tool implementations, not active maintenance |
| API parameter expansion breaks existing Agent integrations | Low | Low | All new params optional, defaults preserve existing behavior |
| Built-in audio synthesis quality too poor for demo use | Medium | Low | Keep fluidsynth as fallback; rendering backend already Protocol-pluggable |

#### Next Step Recommendation

**Do in parallel (2-3 person team):**
1. Person A: Git clone + diff mage0535/music-creation-engine → report findings (1-2h)
2. Person B: Clone + evaluate midi-composer-mcp, test tool calls, write integration wrapper (2-3h)
3. Person C (optional): Study Midra checkpoint schema, draft PipelineCheckpoint model (1h)

**Then sequential decision meeting (30min):**
- Review mage0535 diff → decide merge/cherry-pick/skip
- Review midi-composer-mcp evaluation → decide sidecar integration strategy
- Align on checkpoint pipeline scope for next sprint

---

## 2026-07-07 — Architecture Review & Recommendation

> **Status:** Discussion document for colleague review. Not yet implemented.
> **Author:** Session 3 operator

### Architecture Positioning (Corrected)

After deeper review, the correct architectural boundary is:

```
Agent (Hermes / Codex / OpenClaw)     ← Decision layer
  ├── User dialogue, intent parsing
  ├── LLM composition planning (key, BPM, chord progression, structure, melody contour)
  ├── Multi-agent role-play (lyricist, composer, arranger, evaluator)
  └── Quality review & iteration
        │
        ▼ calls CLI / HTTP API with structured parameters
        │
music-creation-engine                 ← Execution layer
  ├── Receive structured ScoreRequest → music21 → MIDI / MusicXML / LilyPond / PDF
  ├── Receive MIDI path → fluidsynth / ffmpeg → WAV / MP3
  └── Search external references → return structured metadata
```

**Key insight:** This project is NOT an AI engine. It is a tool executor. The Agent handles all LLM reasoning; the Engine handles artifact generation. The adapters (`adapters/`) already codify this — all three instruct the Agent to "prefer package entrypoints over directly re-implementing workflow logic." LLM integration should NOT be added here.

### Blueprint vs Reality: 7-Stage Workflow Gap Matrix

| Stage | Blueprint Vision | What Exists | Gap |
|-------|-----------------|-------------|-----|
| 1. Inspiration | Multi-agent role-play with style distillation | Agent responsibility — Engine has no role here | No gap — correct boundary |
| 2. Lyrics | Multi-agent collaboration + user iteration | Agent responsibility | No gap — correct boundary |
| 3. Composition Planning | LLM decides BPM / key / chords / instrumentation | **Engine receives none of this** — API has no fields for chord progression, section structure, or melody contour | **Gap: API parameter surface too coarse** |
| 4. Score Generation | Abjad + music21 → full score / part scores / numbered notation | Exists but template-based (`CHORD_PROGRESSIONS` dict, hardcoded pitch maps). Cannot accept Agent's LLM-generated plan. | **Gap: cannot consume structured plans** |
| 5. Audio Rendering | FluidSynth / REAPER MCP / Suno API / kokoro TTS | FluidSynth → WAV → MP3 works. No REAPER, no Suno, no TTS. | Functional for basic path |
| 6. Quality Evaluation | 6-expert-agent scoring (melody / rhythm / emotion / structure) | Agent responsibility — but Engine has no API for "evaluate this MIDI" | **Gap: no evaluation endpoint** |
| 7. Publishing | Multi-platform distribution | Agent + external responsibility | Low priority |
| 8. Recording Analysis | Audio → music21 note recognition + mixing advice | Agent responsibility | Deferred |

### Root-Cause Diagnosis

**The primary bottleneck:** The Engine's API parameter surface is too granularity-poor for an Agent that does rich LLM reasoning. When an Agent's LLM determines:

```
This song should be Am-F-C-G, 72 BPM, Intro(4 bars) → Verse(8) → Chorus(8) → Bridge(4, key change to C) → Outro(4).
Melody: E4-F4-G4-A4 quarter notes, with D4 eighth-note pickup.
Instruments: piano (left-hand chords + right-hand melody), strings (pad), bass (root notes).
```

...the current `POST /v1/score` accepts only `{lyrics, key, bpm, instruments, style}`. The Agent's rich LLM output has no path into the Engine. The Engine falls back to its hardcoded templates, and the result is musically unrelated to the Agent's plan.

In other words: **the Agent can think deeply, but the Engine cannot listen deeply.**

### Prioritized Recommendations

#### P0 — Expand API Parameter Surface (Unblocks Agent Capability)

These changes allow the Agent to pass its LLM-generated composition plan into the Engine:

| # | Change | Current | Target |
|---|--------|---------|--------|
| 1 | Chord progression parameter | `style="pop"` → hardcoded `["C","G","Am","F"]` | `POST /v1/score` accepts `chord_progression: list[str]`, e.g. `["Am","F","C","G"]` |
| 2 | Section structure parameter | Measures computed mechanically from lyric line count | Accept `sections: list[{name, bars, key?, instruments}]`, e.g. `[{name:"intro",bars:4},{name:"verse",bars:8},{name:"chorus",bars:8}]` |
| 3 | Melody note sequence | Fixed pitch maps per instrument (`base_map` dict) | Accept optional `melody: dict[instrument, list[int]]` (MIDI note numbers) via `POST /v1/score` |
| 4 | Instrument → role mapping | All instruments play the same arpeggio logic | Accept per-instrument role: `chord` / `melody` / `bass` / `pad` / `rhythm` |
| 5 | Abjad integration for fine control | Direct `score.write("lilypond")` | Abjad layer for articulation marks, dynamics, slurs, performance annotations |

**Rationale:** These are backward-compatible optional fields. Existing calls still work (defaults preserved). Agents that don't pass them get template behavior. Agents with LLM planning pass them and get AI-driven output. This is the single highest-leverage change in the project.

#### P0 — Activate Meting-Agent Integration (Unblocks Reference Workflows)

| # | Change | Current | Target |
|---|--------|---------|--------|
| 6 | Real subprocess call | `integrations/meting.py` returns mock `{"enabled":true,"note":"wiring..."}` | Call `npx @eldment/meting-agent search` via subprocess, parse JSON output |
| 7 | Structured reference metadata | Returns raw search result | Extract and return structured fields: `title`, `artist`, `bpm`, `key`, `genre`, `lyrics_preview` — fields an Agent needs for composition decisions |

#### P1 — Artifact Management (Enables Agent Iteration)

| # | Change | Current | Target |
|---|--------|---------|--------|
| 8 | Workflow ID + artifact manifest | Files scattered in `build/output/`, no catalog | Each `POST /v1/workflows/full` returns a `workflow_id`; artifacts register in a manifest JSON |
| 9 | Artifact lookup endpoint | No way to find past generations | `GET /v1/artifacts/{workflow_id}` returns manifest with all file paths |
| 10 | Score revision endpoint | Must regenerate entire score for any change | `POST /v1/score/revision` accepts `{base_workflow_id, changes: {key?, bpm?, chord_progression?, sections?}}` — merge changes into existing score |
| 11 | File serving | Agent gets file paths but cannot present to user | `GET /v1/artifacts/{workflow_id}/file/{name}` returns file stream + Content-Type |

#### P2 — Adapter Documentation (Makes Agents Self-Sufficient)

| # | Change | Current | Target |
|---|--------|---------|--------|
| 12 | Parameter value ranges | Adapter says "call `score`" with no parameter docs | Document valid instruments list, key format, BPM range, supported styles |
| 13 | Error code reference | No error documentation | Document `ErrorCode` values, when each occurs, and how Agent should respond |
| 14 | Example request/response | No examples in adapters | Add realistic example: `curl POST /v1/score` + full JSON response |

#### P3 — Engineering Infrastructure

| # | Change | Current | Target |
|---|--------|---------|--------|
| 15 | Dockerfile | Manual dependency install | `Dockerfile` + `docker-compose.yml` with music21, LilyPond, FluidSynth, SoundFont, ffmpeg |
| 16 | Contract tests for parameter surface | Only unit/route tests | Integration test: Agent sends structured plan → Engine generates matching output |
| 17 | Config for Meting-Agent path | Hardcoded `npx` | `config/defaults.yaml` entry `tools.meting_command` with path override |

### Proposed Next Session Scope (Pick One)

**Option A — Unblock Agent Capability (P0, ~6h)**
Items 1-7: expand parameter surface + activate Meting-Agent. After this, an Agent with a good LLM prompt can produce musically meaningful output through the Engine.

**Option B — Agent Self-Service (P1+P2, ~5h)**
Items 8-14: artifact management + adapter docs. After this, Agents can iterate on compositions, retrieve past work, and operate without reading source code.

**Option C — Production Readiness (P3, ~4h)**
Items 15-17: Docker + contract tests. After this, the project has a reproducible runtime environment and regression safety for the expanded parameter surface.

---

## 2026-07-07 (Session 3 — Hardening & Production Readiness)

### What changed

#### Structural
- **Removed vestigial root namespace package** (`music_creation_engine/` at repo root). The project deploys from `src/` only. The root-level `extend_path` + manual `__path__.append` hack was a leftover from pre-src-layout era and created ambiguity between `pip install -e .` and the root directory. Scripts continue to work because they explicitly inject `src/` into `sys.path`.
- Added `test_root_namespace_hack_is_absent` and `test_src_package_is_the_real_package` to enforce this.

#### Error Model
- Added `ErrorCode` enum and `EngineError` exception class in `src/music_creation_engine/models.py` (lines 10-36):
  - `INVALID_INPUT` / `MISSING_TOOL` / `MISSING_DEPENDENCY` / `INTEGRATION_UNAVAILABLE` / `RUNTIME_FAILURE` / `CONFIG_ERROR` / `FILE_NOT_FOUND`
  - `EngineError` carries `code`, `message`, `detail` and exposes `to_dict()` for JSON serialization.
- **Runtime layer**: `render_runtime.py` and `score_runtime.py` now raise `EngineError` instead of bare `RuntimeError`, with correct error codes (`MISSING_DEPENDENCY`, `FILE_NOT_FOUND`, `RUNTIME_FAILURE`).
- **Service layer**: `score_service.py` and `render_service.py` catch both `EngineError` (reported with `error_code` in dry-run payload) and `Exception` (generic fallback), and log both.
- **API layer**: `app.py` registers `@exception_handler(EngineError)` → 400 + structured JSON, and generic `@exception_handler(Exception)` → 500 + `{"error": {"code": "RUNTIME_FAILURE", ...}}`.
- **CLI layer**: `main()` wraps all command handlers in try/except that catches `EngineError` → exit 1 + JSON error on stdout, and `Exception` → exit 1 + `RUNTIME_FAILURE` JSON.

#### Logging
- All runtime modules (`score_runtime`, `render_runtime`), services, CLI, and API now use `logging.getLogger(__name__)`.
- Key log points: score start (key/bpm/instruments/measures), MIDI/xml/ly/pdf artifact creation, render start (midi/output/format), subprocess failures (fluidsynth/ffmpeg stderr captured), LilyPond warnings, engine error propagation, API unhandled exceptions.
- Logging level defaults to WARNING (root), consumers can configure via `logging.basicConfig(level=...)`.

#### CLI Refactor
- Extracted 7 command handlers from the monolithic `main()` into standalone functions: `cmd_health`, `cmd_capabilities`, `cmd_score`, `cmd_render`, `cmd_workflow_full`, `cmd_references_search`, `cmd_adapters_install`.
- `main()` now routes to handlers + error wrapper only.
- Added `_print_json()` and `_print_error_json()` helpers for consistent output formatting.

#### Cross-Platform
- `render_runtime.py` SoundFont detection now respects `sys.platform`:
  - Linux: `/usr/share/sounds/sf2/FluidR3_GM.sf2`, `/usr/share/sounds/sf2/fluid-soundfont.sf2`, `/usr/share/sounds/sf3/default.sf3`
  - Windows: `C:\Windows\System32\drivers\gm.dls`

#### Tests
- **New tests** (9 added, total 29):
  - `test_api.py`: `test_render_missing_midi_returns_dry_run` (200 + dry-run payload), `test_api_unhandled_exception_returns_500` (monkeypatch + raise_server_exceptions=False)
  - `test_cli.py`: `test_cli_missing_command_prints_help`, `test_cli_score_dry_run_when_music21_missing`
  - `test_config.py`: `test_load_settings_missing_defaults_file_returns_defaults`, `test_load_settings_corrupt_yaml_raises`, `test_load_settings_scalar_config_raises`
  - `test_end_to_end_layout.py`: `test_root_namespace_hack_is_absent`, `test_src_package_is_the_real_package`

### Why

The v0.2.0 scaffold had:
1. A namespace hack that created import ambiguity and could break with future packaging changes.
2. No structured error handling — bare `RuntimeError` propagated to CLI as stack traces, and API 500s had no JSON contract.
3. No logging — impossible to debug in production or trace agent-orchestrated workflows.
4. A monolithic CLI `main()` that mixed routing, execution, and output into 70+ lines of if-elif.
5. Linux-only SoundFont paths that would fail silently on Windows.
6. Tests covered "happy path" only — no error surface, bad config, or dry-run fallback coverage.

### Verification status

- All 29 tests pass (20 original + 9 new)
- Windows platform tests pass (this session runs on Windows)
- Backward compatibility: CLI stdout format remains valid JSON; API responses unchanged for success paths
- Script entrypoints (`scripts/*.py`) still work independently

### Follow-up candidates (unchanged from prior session)
- Add persistent job and artifact tracking
- Add deployment examples for Docker and systemd
- Replace dry-run fallback with richer dependency diagnostics and example remediation

---

## 2026-07-07 (Session 2 — Project Scaffold)
---

## 2026-07-07 (Session 5 — External Repo / Tool / Paper Review For Team Discussion)

> **Status:** Discussion memo. Based on GitHub repo review and literature scan. Focus is not "interesting projects" but "what should we actually absorb into `music-creation-engine`".

### A. User-provided repositories

| Project | Link | Fit | Recommendation |
|---|---|---|---|
| SoulTuner-Agent | https://github.com/hgsanyang/SoulTuner-Agent | Low direct fit | Not for direct integration. It is a recommendation system with Hybrid RAG, Neo4j, long-term memory, and optional GPU-heavy acoustic embedding paths. Worth borrowing only retrieval/memory architecture ideas. |
| ai-music-creator | https://github.com/XUTENGXIANG/ai-music-creator | Low | Too lightweight to justify direct integration. At most, use as a reference for multi-agent role decomposition language. |
| ip-human-agent | https://github.com/fa1314/ip-human-agent | Low direct fit | Not a composition engine. Relevant only as a reference for later publish/distribution pipeline design. |
| ATRI_AGENT | https://github.com/Tz-WIND/ATRI_AGENT | High pattern value | Strong reference project. Do not merge whole repo. Strongly consider selectively absorbing: `midi_query`, `midi_inspect`, `midi_write`, `midi_diff`, `midi_batch_edit`, and `piano_playability_check`. |
| aimv-studio | https://github.com/shaozheng0503/aimv-studio | Low direct fit | Mainly useful as a multi-agent verifier/orchestration reference. Video/GPU-heavy, so not suitable for current core. |
| ai-music-studio | https://github.com/FF0214/ai-music-studio | Low | Mostly orchestration around external music APIs. Low value for our symbolic-score-first architecture. |
| music-agent | https://github.com/YoungB1oodXD/music-agent | Low direct fit | Recommendation/dialogue-oriented, not score-generation oriented. Not a current integration target. |
| TikTok-Agent-Script-Studio | https://github.com/GuJiV/TikTok-Agent-Script-Studio | Low direct fit | Useful only as pipeline-gating / compliance-stage design reference. |
| vcutclaw | https://github.com/treesan/vcutclaw | Medium pattern value | Not for direct composition integration. Useful for review-loop design and audio-aware synchronization concepts. |
| yinova | https://github.com/elfbobo/yinova | Low direct fit | Broad multimodal Hermes-derived agent system. Not a focused music-engine dependency. At most, review its packaging/integration conventions. |

### B. Additional repositories discovered during review

| Project | Link | Fit | Recommendation |
|---|---|---|---|
| midi-composer-mcp | https://github.com/voho/midi-composer-mcp | Very high | Highest-value external project found. It offers deterministic theory/composition tools, section planning, arrangement, and built-in MIDI/audio rendering. Best near-term move: integrate as sidecar MCP or mirror selected tool concepts into our API surface. |
| mcp-score | https://github.com/tskovlund/mcp-score | High | Valuable for installable skill + MCP pairing, and the "Agent writes music21 script, tool executes it" pattern. Good reference for score-editing and MuseScore plugin strategy, but should remain optional rather than becoming our primary interface. |
| Midra | https://github.com/XIAODUOLU/Midra | High | Strong reference for checkpoint-native, prompt-to-code, editable prompt→MIDI pipeline. We should not copy the whole stack, but we should strongly consider its per-project checkpoint JSON layout and resume model. |
| reaper-mcp | https://github.com/bonfire-systems/reaper-mcp | High optional fit | Good optional integration for users with REAPER installed. Not for default path. Best treated as advanced pluggable backend for richer MIDI editing, mixing, mastering, and rendering. |

### C. Relevant research papers and why they matter

| Paper | Link | Relevance | Opinion |
|---|---|---|---|
| Text2midi: Generating Symbolic Music from Captions | https://arxiv.org/html/2412.16526v2 | Text→MIDI conditioning | Useful as evidence that text-driven symbolic generation is a valid direction, but our current architecture should stay tool-execution-first rather than model-training-first. |
| Text2Score: Generating Sheet Music From Textual Prompts | https://arxiv.org/html/2605.13431v1 | Text→notation / sheet generation | Relevant to future score-generation controllability. Good reference if we later want richer text-conditioned notation outputs beyond MIDI-first pathways. |
| ComposerX: Multi-Agent Symbolic Music Composition with LLMs | https://arxiv.org/html/2404.18081v1 | Multi-agent symbolic composition | Supports the idea that multi-agent composition should live in the Agent layer, while execution remains deterministic in the Engine layer. |
| Libretto: Giving LLM Agents a Sense of Musical Structure | https://arxiv.org/html/2606.22708v1 | Structural symbolic interface for agents | Important conceptual reference for giving agents structured, revision-friendly symbolic context rather than opaque audio output. |
| Can LLMs “Reason” in Music? | https://arxiv.org/html/2407.21531v1 | Limits of LLM reasoning over symbolic music | Reinforces that we should not over-trust LLM freeform reasoning without deterministic tool support. This supports our current Engine/Agent split. |
| The Modelling of Structure in Symbolic Music Generation | https://arxiv.org/html/2403.07995v1 | Long-form structure review | Useful justification for planned section/chord/checkpoint expansion. |
| MIDI-GPT | https://arxiv.org/html/2501.17011v1 | Track/bar-level controllability | Good reference for future fine-grained edit primitives such as infill, section-local revision, and attribute-conditioned generation. |
| MidiCaps | https://arxiv.org/html/2406.02255v1 | Captioned MIDI dataset | Relevant if we ever train or benchmark text-conditioned symbolic workflows, not a current runtime dependency. |

### D. Cross-source conclusions

#### 1. What is clearly worth integrating or absorbing soon

- **Deterministic theory + arrangement tools** from `midi-composer-mcp`
  - Immediate value: fills our current parameter-surface gap.
  - Best adoption path: first as sidecar MCP or wrapper; second phase, selectively internalize the most useful primitives.

- **Granular MIDI edit/query/playability concepts** from `ATRI_AGENT`
  - Immediate value: enables revision-oriented workflows and objective playability checks.
  - Best adoption path: add API/CLI endpoints and validations, not full workstation integration.

- **Checkpoint / resume model** from `Midra`
  - Immediate value: makes workflows iterative and teammate-friendly.
  - Best adoption path: add workflow manifests, per-stage JSON checkpoints, and artifact indexing.

- **Optional REAPER backend** from `reaper-mcp`
  - Immediate value: better advanced rendering/mixing for power users.
  - Best adoption path: keep behind advanced integration flag, never default.

#### 2. What is mostly architectural inspiration, not a dependency

- SoulTuner-Agent: retrieval/memory pattern only
- ip-human-agent: publish pipeline only
- aimv-studio / TikTok-Agent-Script-Studio / vcutclaw: workflow gating and multi-agent validation patterns only
- mcp-score: optional score-editing / script-execution mode, not the main path

#### 3. What should not drive current roadmap

- GPU-heavy or dataset-heavy recommendation/generation stacks
- broad multimodal agent frameworks that dilute the symbolic-music core
- direct in-engine LLM orchestration

### E. Recommended priority for our roadmap

#### P0

1. Activate real `Meting-Agent` execution instead of mock payloads.
2. Expand our score request surface:
   - `chord_progression`
   - `sections`
   - `melody`
   - `instrument_roles`
3. Fix install bundle completeness so copied agent bundles include runnable project code, not only docs and wrapper scripts.

#### P1

4. Add artifact manifest + workflow checkpoint JSON.
5. Add granular MIDI query / edit / diff endpoints.
6. Add piano playability validation.

#### P2

7. Register `midi-composer-mcp` as sidecar optional integration and map its outputs into our workflow.
8. Add optional `reaper-mcp` backend.

#### P3

9. Consider score-editing bridge patterns inspired by `mcp-score`.
10. Consider richer structure-aware revision loops inspired by Libretto / Midra / ComposerX.

### F. Session opinion

The project is now on the correct architectural foundation, but it is still behind the leading open symbolic-music-agent projects in one specific dimension: **the Engine cannot yet accept enough structured musical intent from the Agent**.

In plain terms:

- the Agent can already think more deeply than the Engine can execute
- external projects confirm that deterministic symbolic tools + checkpointed workflows are the right next step
- the best near-term strategy is **not** to replace our Engine, but to widen its parameter surface, add checkpointing, and selectively integrate deterministic sidecar tools

---

## 2026-07-07 (Session 6 — Cross-Review Response to Session 5)

> Response from Session 3/6 operator to the Session 5 colleague review.

### Areas of Strong Agreement

**1. Core diagnosis is shared.** Both sessions independently reached the same conclusion: "the Agent can already think more deeply than the Engine can execute." This is the project's existential bottleneck and fixing it is the right priority.

**2. Research papers are an excellent addition.** The 8 papers that Session 5 found were completely absent from the Session 3 survey. Specific highlights:
- **Text2Score** (arXiv 2605.13431v1) — directly relevant to our PDF/MusicXML output path. If the field is moving toward text-conditioned notation, our LilyPond pipeline is well-positioned.
- **Libretto** (arXiv 2606.22708v1) — "giving LLM agents structured, revision-friendly symbolic context" is exactly our API-parameter-expansion thesis, now backed by academic work.
- **ComposerX** (arXiv 2404.18081v1) — confirms that multi-agent composition should live in Agent layer. Validates our boundary decision.
- **Can LLMs "Reason" in Music?** (arXiv 2407.21531v1) — reinforces "don't over-trust LLM without deterministic tools." This is the strongest academic argument for our architecture.

**3. Install bundle fix (P0 #3) is correct and practical.** The `install.sh` currently copies `README.md`, `SKILL.md`, `pyproject.toml`, `scripts/`, `references/`, `config/`, `adapters/`, `examples/` — but notably does NOT copy `src/music_creation_engine/`. This means an Agent on a remote machine that gets the bundle via `install.sh` has the CLI entrypoints but not the actual Python package. This is a real bug, not a feature gap. Good catch.

**4. P1 MIDI query/edit/diff endpoints are the right north star.** Session 5's P1 (#5) advocates building `midi_query`, `midi_inspect`, `midi_diff`, `midi_edit` natively in our Engine. I agree this is the correct long-term architecture — having these as first-class endpoints under our own API contract, error model, and test coverage beats depending on an external MCP server. The question is sequencing (discussed below).

### Points of Divergence (Constructive Discussion)

**1. mage0535 fork — critical omission or intentional skip?**

Session 5 does not mention `mage0535/music-creation-engine` at all. This was flagged as P0 in Session 3 because it is a direct fork of our codebase at v1.0.0 with added features (multi-agent lyrics, quality evaluation, publishing). My position remains:

> We should clone and diff it immediately. Even if we decide to cherry-pick nothing, the diff tells us exactly what another developer considered important enough to add. That market signal alone is worth the 1-2 hours. If we skip this and they've solved problems we're about to spend weeks on, we're duplicating effort.

Recommendation: Add this as a parallel task (Person A, 1-2h) in the next sprint, regardless of which roadmap we pick.

**2. midi-composer-mcp at P0 vs P2 — the "build vs buy" question**

This is the most significant strategic difference between our analyses:

| | Session 3 | Session 5 |
|---|---|---|
| midi-composer-mcp priority | P0 (sidecar now) | P2 (optional later) |
| Granular MIDI tools | Use external MCP | Build natively in Engine (P1) |
| Strategy | Buy first, build later | Build first, buy later |

My thinking on why P0 sidecar is the right bridge strategy:

- **Speed to value.** midi-composer-mcp already has 40+ working tools. Building `midi_query`/`midi_diff`/`midi_write`/`arrange_song`/`plan_sections`/`voice_leading`/`counterpoint`/`harmonize_melody` natively in our Engine is weeks of work with music-theory-domain expertise required. Registering it as a sidecar MCP takes hours.
- **Validation before investment.** Let the Agent use midi-composer-mcp for 2-3 sprints. We'll learn which tools the Agent actually calls, which parameters matter, which operations are frequent vs rare. Then when we build our native equivalents (Session 5's P1 items), we build the right things the first time.
- **Not mutually exclusive.** Session 5's P1 (#5: "Add granular MIDI query / edit / diff endpoints") is the right long-term goal. The sidecar provides an immediate stepping stone while we build.

**Proposed compromise:** P0 sidecar integration (for immediate Agent capability) + P1 native MIDI tools (building only the high-usage subset validated by real Agent usage data). This gives us the best of both approaches.

**3. P0 priority ordering difference**

| Session 3 P0 | Session 5 P0 |
|---|---|
| 1. Diff mage0535 fork | 1. Activate Meting-Agent |
| 2. midi-composer-mcp sidecar | 2. Expand API parameters |
| | 3. Fix install bundle |

Session 5's #2 (API parameter expansion) and #3 (install bundle fix) are unequivocally correct. The disagreement is on #1: I'd put Meting-Agent activation at P1 rather than P0, because "searching reference songs" is a nice-to-have for the Agent but doesn't unblock the core bottleneck (Agent can't pass composition plans to Engine). An Agent without reference search can still compose; an Agent without structured parameter passing cannot.

However, Meting-Agent activation is quick (1-2h of subprocess integration) and was already planned in our architecture-report. I'm happy to accept P0 positioning if we can do it in parallel with parameter expansion.

### Merged Roadmap Proposal

Combining the strongest elements of both analyses:

| Priority | Task | From | Notes |
|----------|------|------|-------|
| **P0** | Fix install bundle to include `src/` | S5 | Bug fix, not feature |
| **P0** | Expand ScoreRequest: `chord_progression`, `sections`, `melody`, `instrument_roles` | S3 + S5 | Both sessions agree |
| **P0** | Diff mage0535 fork v1.0.0 vs our v0.2.0 | S3 | 1-2h, parallel task |
| **P0** | Register midi-composer-mcp as sidecar integration in config | S3 | Bridge strategy for P1 native tools |
| **P1** | Activate real Meting-Agent subprocess call | S5 | Quick win |
| **P1** | Add workflow checkpoint + artifact manifest JSON | S3 + S5 | Both sessions agree |
| **P1** | Add granular MIDI endpoints (query/inspect/diff) natively | S5 | Build only high-usage tools validated by sidecar usage |
| **P2** | Piano playability validation | S3 + S5 | Both sessions agree |
| **P2** | Adapter docs: parameter ranges, error codes, example req/res | S3 | |
| **P2** | Optional reaper-mcp backend | S3 + S5 | Both sessions agree |
| **P3** | Dockerfile + docker-compose | S3 | |
| **P3** | Score-editing bridge (mcp-score pattern) | S5 | |
| **P3** | Built-in audio synthesis evaluation | S3 | |

### Recommendation for Next Action

The two sessions produced remarkably aligned analyses. The differences are not about destination but about route. The merged roadmap above honors both perspectives. I suggest:

1. **Start immediately** with the 3 P0 items that have zero dependency on each other: install bundle fix, API parameter expansion, mage0535 diff (can be done in parallel by different people).

2. **Decide on midi-composer-mcp strategy** in the next team sync — my recommendation stays "sidecar now, build selectively later" but I'm open to the "build first" approach if the team has deep music-theory Python expertise and can deliver granular MIDI tools quickly.

3. **The research papers** that Session 5 found should be distributed as pre-reading before the next sprint planning. The Libretto paper in particular validates our entire architectural direction.
---

## 2026-07-07 (Session 7 — Consensus Roadmap Implemented)

### What was implemented

- `install.sh` now copies `src/` into installed agent bundles, fixing incomplete bundle installs.
- `ScoreRequest` and `WorkflowRequest` now support:
  - `chord_progression`
  - `sections`
  - `melody`
  - `instrument_roles`
- `score_runtime.py` now consumes those structured fields instead of only relying on static style templates.
- `Meting-Agent` integration now attempts a real subprocess call first, with safe fallback when the tool is unavailable.
- Added sidecar integration wrappers for:
  - `midi-composer-mcp`
  - `reaper-mcp`
- Added workflow manifest + checkpoint persistence via `ArtifactService`.
- Added API endpoints for:
  - MIDI diff
  - MIDI inspect
  - MIDI query
  - playability check
  - artifact manifest lookup
  - workflow checkpoint lookup
- Added native services for:
  - artifact persistence
  - MIDI diff / inspect / query
  - playability evaluation
- Updated CLI to expose the new capabilities.
- Updated compatibility scripts under `scripts/` to accept the expanded score parameters.

### Verification status

- Full local test suite passes.
- Install path shell validation passes.
- Structured score parameters are accepted by CLI, API, and compatibility scripts.
- Workflow runs now produce `workflow_id` plus manifest/checkpoint persistence.
- Real score/render generation remains verified on the Hermes server environment.

### Current implementation stance

- `midi-composer-mcp` is now represented as an optional sidecar integration shell, not yet a deep runtime merge.
- `reaper-mcp` is represented as optional advanced integration, not a default backend.
- Playability validation currently focuses on a basic piano span/leap check and is intentionally conservative.

### Remaining future work after this session

- deeper native MIDI edit/query primitives beyond diff/query/inspect
- workflow revision endpoint using stored manifests/checkpoints
- richer `Meting-Agent` result normalization
- optional REAPER-backed advanced render pipeline
