# Changelog

All notable changes to this project will be documented in this file.

The format follows the spirit of Keep a Changelog and uses semantic project releases.

## [Unreleased]

### Added

- Short source-of-truth project summary at `references/project-status.md`.
- API key auth and in-memory rate limiting for `/v1/*`.
- GitHub Actions CI workflow for pushes and pull requests.
- Real score-runtime integration test using actual `music21` output.

### Changed

- Rewrote both public READMEs into clean, non-corrupted source files.
- `workflow revise` now reuses score and render stages when the request does not change score-affecting inputs.

### Fixed

- Removed the corrupted Chinese README source content.
- Corrected the revision strategy so BPM changes are treated as score-affecting, not render-only.

## [0.4.0] - 2026-07-07

### Added

- Chinese-first public documentation entry page with a dedicated English companion page.
- Interactive installer confirmations for package install, render dependencies, public reference integration, and agent bundle copy targets.
- GitHub Release automation through `.github/workflows/release.yml`.
- Structured public release documentation for project workflow, installation choices, outputs, and acknowledgements.

### Changed

- Unified version metadata across package metadata, runtime package version, and Meting MCP client identity.
- Formalized the release surface around `v0.4.0` tags and GitHub Releases publishing.
- Expanded Meting normalization to handle multiple provider payload shapes instead of only a narrow `songs/ar/al` structure.

### Improved

- Meting search now prefers normalized provider results from node-module and MCP paths before falling back to public HTTP search.
- MCP search parsing now tolerates code-fenced JSON, structured MCP content payloads, alternate argument names, and richer song metadata extraction.
- Song normalization now preserves fields such as `song_id`, `album_id`, `artist_id`, `duration_ms`, `artwork_url`, and `preview_url` when upstream data is available.

### Fixed

- Prevented path-resolution regressions by keeping raw config values intact during config loading and resolving them only at runtime entrypoints.
- Reduced duplicate Meting result rows through normalized song de-duplication.

### Documentation

- Updated the public-facing explanation of project goals, workflow steps, generated artifacts, installer prompts, and release posture.
- Recorded the release-packaging and Meting-normalization work in the continuous development log.
