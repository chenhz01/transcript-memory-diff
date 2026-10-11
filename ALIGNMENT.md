# Alignment Audit (Rules 85-100 / 16 items) — transcript-memory-diff

Audit date: 2026-10-11 · Auditor: W1 (repo construction agent) · Version audited: v0.1.1

| # | Check | Status | Evidence |
|---|-------|--------|----------|
| 1 | Safety/Ethics section (safety-domain repos) | N/A | Memory-diff utility; no security-research surface. Privacy-relevant posture covered in Limits (transcript privacy, sensitivity inheritance). |
| 2 | Privacy: zero keys/tokens/real names; placeholders only | PASS | `grep -rEn "(sk-\|ghp_\|api[_-]?key\s*=\s*['\"][A-Za-z0-9])" .` → 0 hits; contact only `hcac4735@agent.qq.com`; no real names in any file. |
| 3 | Copyright: no >50-word copied text; LICENSE present | PASS | LICENSE (MIT, "zhengming contributors") exists; independent stdlib implementation, upstream referenced conceptually only. |
| 4 | Fact-check labels on all numbers | PASS | Executable claims reproduce via `python self_test.py` (15/15 PASS); adoption-benefit claims marked [estimated] with a suggested A/B protocol. |
| 5 | Confidence grading (≥2 labeled conclusions) | PASS | Key conclusions: High ×2, Medium [estimated] ×1; FAQ adds High-confidence When-NOT-to-use rationale. |
| 6 | PLAN B / Minimal Fallback | PASS | README "Minimal Fallback": stdin one-shot + copy-the-signal-regex manual workflow. |
| 7 | Quickstart time budget | PASS | "~5 seconds" self-test, "~1 min" real diff, "~5 min" integration; staged path minimal → full. |
| 8 | Rule-conflict arbitration / priorities | PASS | Design Trade-offs opens with: no unreviewed writes > precision of signal > recall of signal. |
| 9 | CHANGELOG ≥2 iterations with improvements listed | PASS | CHANGELOG.md v0.1.0 → v0.1.1; round-2 items enumerated (order fix, idempotence fix, gate ordering, noise-regex anchoring, stats, CLI, tests 4→15). |
| 10 | Exemption instructions (session-governance rule) | N/A | Session-level rule; not applicable to static repo content. |
| 11 | Time-sensitive data dated | PASS | README bottom: "as of 2026-10-11". |
| 12 | Explicit assumptions (≥3) | PASS | "[Core Assumptions]": 5 items (line-oriented memory, lexical markers, human-apply-only, JSONL shape, append-only model). |
| 13 | Test triad: unit + exception + extreme edge, all PASS | PASS | `python self_test.py` → 15/15 PASS: functional (6), exception paths (4), extreme edges (5, incl. 10k-line transcript, empty transcript/memory, unicode). |
| 14 | Socratic FAQ incl. When NOT to use | PASS | FAQ Q1: "When should I NOT use this tool?" (structured memory, disposable single-user memory, archiving misuse). |
| 15 | Pareto iteration round 2 with ≥20% improvement, traceable | PASS | Round 2: correctness dimension — 4 bugs fixed (order, idempotence, gate order, regex anchoring), stats + CLI added, tests 4→15 (+275%); CHANGELOG v0.1.1 traceable per item. |
| 16 | ≤60-word first screen with need-to-use verdict | PASS | README first paragraph: 55 words, explicit "You need it if… / Skip it if…" judgment. |

**Summary: 13 PASS / 0 FAIL / 3 N-A (items 1, 10)**
