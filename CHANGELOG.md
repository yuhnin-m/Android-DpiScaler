# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]
### Added

### Planned
- Safety and export pipeline hardening.
- Architecture refactoring.
- Threading model improvements and tests expansion.

## [0.1.0] - 2025-09-25
### Added
- Public repository baseline files (`README`, `LICENSE`, `CONTRIBUTING`, `SECURITY`, CI, templates).
- Python project metadata and dependency manifests.
- Layered export architecture (`domain/services/infrastructure`) with preview planner and export service.
- New tests for export planning and export execution.
- Background job worker abstraction (`FunctionWorker`) for non-blocking UI operations.
- Async project scan and async preview generation before export.
- Export reliability tests (progress callback, overwrite behavior, write-failure safety).
- CI quality gates extended to lint/compile the full app layers and run an offscreen UI smoke test.
- Unified packaging layout with a single PyInstaller spec and cross-platform build scripts.
- Tag-based GitHub Release workflow with uploaded artifacts and generated checksums.
- Project renamed to **Android DpiScaler** (app metadata, package name, packaging spec/scripts).
- Local development baseline aligned with Python 3.11+ (`pip install -e .` now works in fresh `.venv`).
