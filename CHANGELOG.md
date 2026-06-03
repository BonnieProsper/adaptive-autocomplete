# Changelog

All notable changes to this project are documented here.

---

## [1.0.4] - 2026-05-17

### Added
- `aac serve`: minimal JSON API server (GET /suggest, GET /explain, POST /record,
  GET /health) using only the standard library. 20 tests. Documented in README.
- `RankerContractTestMixin` in `tests/contracts/ranker_contract.py` with 80 contract
  tests covering ScoreRanker, LearningRanker, and DecayRanker (both empty-history
  and with-history variants).
- `scripts/demo.tape` and `scripts/record_demo.sh` for recording the README demo GIF
  using VHS. `make record-demo` runs the recorder.
- `Changelog` and `Bug Tracker` project URLs in `pyproject.toml` (appear as sidebar
  links on PyPI).

### Fixed
- `explain()` and `explain_as_dicts()` lacked a `limit` parameter, inconsistent with
  `suggest()` and all other engine methods. Both now accept `limit`.
- `aac tune --from-history` failed with stateless (and any other history-ignoring) preset
  because it used `engine.history` which is empty for presets that don't attach history.
  Now uses the persisted history loaded from disk directly.
- `explain_async()` lacked a `limit` parameter, inconsistent with `suggest_async()`.
  Added.
- `load_jsonl()` crashed with `TypeError` when given a JSON array instead of JSONL.
  Now raises `ValueError` with a clear message.
- `average_precision` was missing from `aac.evaluation.__all__`.
- `_scoring.py` helpers were incorrectly re-exported from `aac.predictors.__all__`.
- Optimiser ranker cache key had a spurious `:rankers` suffix.
- `evaluation.harness`: `defaultdict` imported inside function body; `"n"` stored
  as int in a `dict[str, float]`.
- `vocabulary_from_text` silently accepted `min_count=0` and `min_length=0`.
- `aac debug` printed 200+ unsorted candidates. Now shows top 20 scored, top 10 ranked.
- Stale `# noqa: E402` in the CLI demo import block.

### Changed
- `pyproject.toml` migrated to PEP 621. Removed broken `fastapi`/`uvicorn` extras
  declaration (packages were listed as extras but not as optional dependencies).
- `scripts/check_version.py` now also checks `CHANGELOG.md` heading.

---

## [1.0.1] - 2026-05-12

### Added
- `AutocompleteEngine.predictors` property.
- Coverage configuration in `pyproject.toml`.
- Regression tests for engine invariants, persistence, evaluation, and batch APIs.

### Fixed
- Preserved `LearningRanker` parameters during `EngineConfig` serialisation.
- Fixed performance-test collection and disabled coverage gates for the
  dedicated performance regression step.
- Marked platform-specific and unreachable defensive paths with documented
  `# pragma: no cover` comments.

---

## [1.0.0-rc.3] - 2026-05-09 to 2026-05-11

### Added
- BENCHMARK and DESIGN docs.
- Docker/browser demo support and updated FastAPI, evaluation,
  contextual history, and custom vocabulary examples.
- Public vocabulary helper exports at the package root.

### Changed
- Reworked CLI demo, record, explain, and benchmark output.
- Tightened engine invariant checks and type annotations.
- Improved ranking explanation docs and JSON storage error handling.
- Regenerated `poetry.lock` after project metadata changes.

### Fixed
- Preserved caller-provided history instances across preset construction.
- Fixed CLI vocabulary argument naming and root vocabulary exports.
- Stabilised CLI parsing and the demo record route.
- Made history length checks constant-time.
- Relaxed performance thresholds for loaded CI runners.

---

## [1.0.0-rc.2] - 2026-04-28 to 2026-05-01

### Added
- `AdaptiveSymSpellPredictor`, `ThreadSafeHistory`,
  `ContextualHistory`, `EngineConfig`, `PredictorRegistry`, and vocabulary
  utilities.
- Single-pass `explain()` output with contribution percentages and
  `reset_history()` propagation.
- `History.copy()` for independent snapshots.
- Tests for async APIs, CLI integration, engine config, evaluation,
  explanation ordering, SymSpell, vocabulary utilities, persistence, and
  thread-safe history.

### Changed
- Replaced the BK-tree robust preset with SymSpell; BK-tree remains available
  for comparison.
- Moved frequency and history predictors to log-normalised scoring.
- Excluded exact matches from approximate predictors.
- Updated package classifiers, examples, Makefile targets, README, and release
  docs.

### Fixed
- Fixed a Windows file descriptor leak in `JsonHistoryStore`.
- Fixed tests and docs after the scoring/explanation redesign.

---

## [1.0.0-rc.1] - 2026-04-04 to 2026-04-22

### Added
- Real word-frequency data, default vocabulary constants, vocabulary-file
  loading, and word-list support.
- BK-tree and trigram fuzzy predictors with tests and benchmarks.
- JSON history persistence with timestamped `HistoryEntry` objects and
  backwards-compatible loading.
- Hypothesis tests and performance regression checks.
- CHANGELOG, CONTRIBUTING, BENCHMARK, DESIGN, SECURITY, and Makefile
  workflow docs.

### Changed
- Replaced hardcoded demo vocabularies with configurable vocabulary sources.
- Improved history and decay lookups with prefix indexing.
- Improved frequency/history scoring, deterministic sorting, and typo-recovery
  weighting.
- Updated CI for benchmark and test coverage work.

### Fixed
- Fixed incorrect invariant checks and an `explain()` double-counting bug.
- Fixed fake predictor test signatures, predictor imports, vocabulary range
  handling, CLI defaults, and demo docs.
- Fixed JSON persistence with atomic temp-file replacement.
- Fixed shared-history behaviour so learning rankers use the intended history.

---

## [1.0.0] - 2026-01-17

Initial release.

---

## Before 1.0.0 - 2025-12-13 to 2026-01-16

Initial development: project scaffold, domain model, engine, predictors,
rankers, CLI, persistence, and tests. Iterated on typing and invariants
before tagging `v1.0.0`.
