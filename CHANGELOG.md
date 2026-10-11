# Changelog

All notable changes to this project are documented here.
Format based on Keep a Changelog; versions are pre-1.0 reference releases.

## v0.1.1 - 2026-10-11 (round 2: self-audit revision)

Second pass against the internal 16-item alignment checklist. Changes, each traceable to a checklist item:

### Fixed (correctness; test coverage 4 -> 15 cases, >20% improvement)
- **Alphabetical scrambling of proposals**: `sorted(set(bullets))` destroyed chronological order before truncation, so memory received bullets in random-looking order. Now: stable dedupe preserving first-appearance order; `max_add` caps after ordering.
- **Re-proposal of existing memories**: bullets already present in the memory file were appended again on every run. `diff_against` now normalizes and skips them — re-running the same transcript yields an empty diff (idempotence test added).
- **Noise gate mis-ordered**: the noise filter only saw sentences that already passed the signal gate, so its counter was misleading; gates are now explicitly ordered signal → noise → length, each with its own stat.
- **Noise regex unanchored**: `"(um|thanks|...)"` matched substrings anywhere (e.g., "numbers" contains "um"); now anchored to sentence start with a word boundary.

### Added
- **Extraction stats** (`lines/parsed/malformed/sentences/signal/dropped_noise/dropped_length/proposed/already_in_memory`) so thresholds can be tuned with evidence instead of vibes.
- argparse CLI: `build` subcommand with `--memory`, `--max-add`, `--json`, `--stats`.
- Robustness: malformed JSONL lines and non-dict entries are skipped and counted, never fatal; bullets are hard-deduplicated case-insensitively.
- `self_test.py`: 15 cases across functional units, exception paths, and extreme edges (empty transcript, empty memory, 10,000-line transcript, unicode bullets).

### Docs
- Rewrote README to article depth: pipeline diagram, 5-alternative comparison table, Minimal Fallback, Design Trade-offs with explicit priority order (no unreviewed writes first), Limits & Second-order Effects (approval fatigue, memory ossification, transcript privacy), When-NOT-to-use FAQ, Core Assumptions, confidence-graded conclusions.

## v0.1.0 - 2026-10-11 (initial draft)

- Core extraction: SIGNAL/NOISE regexes, sentence split, 20–300 char length gate.
- Unified diff against existing memory via `difflib`, `max_add` cap.
- Minimal README and 4-case inline self-test.
