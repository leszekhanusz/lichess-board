# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - Unreleased

### Added
- Added `make fix` target to Makefile for auto-formatting code with `isort` and `black`.
- Added single source of truth for versioning in `src/lichess_board/__version__.py`.
- Added `interactive` flag to `move_played` signal payload (inside `move_info` dictionary).
- Added functionality to hide the mouse cursor while dragging pieces for a better visual experience.

### Changed
- **Breaking Change**: Dropped support for Python 3.9. Now requires Python 3.10 or later.
- **Breaking Change**: The `move_played` signal now emits `(chess.Move, dict)` instead of `(chess.Move, bool)`. The dictionary contains move information, currently `{'interactive': bool}`.
- Updated `play_move` and `undo_move` to clear legal move highlights (dots) before executing/undoing moves.
- Pinned development dependencies to specific versions in `pyproject.toml`.
- Added version constraints to runtime dependencies (`PySide6`, `python-chess`) to prevent breaking changes from major version updates.

### Fixed
- Fixed an issue where legal move highlights would persist when navigating through move history.

## [0.1.0] - 2023-10-27

### Added
- Initial release of `lichess-board`.
- Basic chess board widget with Lichess-like aesthetics.
- Support for drag-and-drop and click-to-move interactions.
- Move animation support.
- Board flipping support.
- Legal move highlighting.
- Check indicator.
