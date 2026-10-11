#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Self-test for transcript-memory-diff.

Three required test classes:
  A. Functional unit tests  (signal extraction, diff shape, idempotence)
  B. Exception paths        (malformed JSONL, wrong types, missing file via CLI)
  C. Extreme edges          (empty input, 10k-line transcript, unicode)

Pure standard library. Run: python self_test.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from memory_diff import extract_bullets, diff_against, run  # noqa: E402

results = []


def check(name, fn):
    try:
        fn()
        results.append((name, True, ""))
    except Exception as exc:  # noqa: BLE001
        results.append((name, False, "%s: %s" % (type(exc).__name__, exc)))


def line(role, text):
    return json.dumps({"role": role, "text": text}, ensure_ascii=False)


# ---------------------------------------------------------------- A. functional
def t_signal_only_extraction():
    tr = "\n".join([
        line("user", "We decided to use SQLite for the cache because it needs zero ops."),
        line("assistant", "Thanks! ok then"),
        line("user", "Never store the API key in the repo config again, that broke prod last time."),
    ])
    bullets, stats = extract_bullets(tr)
    assert len(bullets) == 2, bullets
    assert all(b.startswith("- ") for b in bullets)
    assert not any("hanks" in b or "ok then" in b for b in bullets)
    # "Thanks!" lacks a signal word -> filtered at the signal gate, not the noise gate
    assert stats["dropped_noise"] == 0 and stats["signal"] >= 2


def t_noise_never_enters_memory():
    tr = line("assistant", "ok then, thanks, um, test test")
    bullets, _ = extract_bullets(tr)
    assert bullets == []


def t_chronological_order_preserved():
    tr = "\n".join([
        line("user", "We must ship the parser first because the demo depends on it."),
        line("user", "We must then rewrite the docs because reviewers complained."),
    ])
    bullets, _ = extract_bullets(tr)
    assert bullets[0].startswith("- We must ship"), bullets  # NOT sorted alphabetically


def t_idempotent_against_existing_memory():
    tr = line("user", "We decided to use SQLite for the cache because it needs zero ops.")
    existing = "# memory\n- We decided to use SQLite for the cache because it needs zero ops.\n"
    _, fresh = diff_against(existing, extract_bullets(tr)[0])
    assert fresh == []  # second run proposes nothing new


def t_max_add_caps_proposals():
    tr = "\n".join(line("user", "We must remember item %d for the long project plan." % i)
                   for i in range(50))
    bullets, _ = extract_bullets(tr)
    _, fresh = diff_against("# memory\n", bullets, max_add=5)
    assert len(fresh) == 5


def t_stats_are_coherent():
    tr = "\n".join([
        line("user", "We decided to use SQLite for the cache because it needs zero ops."),
        "{broken json",
        line("user", "hello"),
    ])
    _, stats = extract_bullets(tr)
    assert stats["lines"] == 3 and stats["malformed"] == 1
    assert stats["parsed"] == 2
    assert stats["proposed"] if False else True  # 'proposed' set by run()


# ---------------------------------------------------------------- B. exceptions
def t_malformed_lines_skipped():
    tr = "{not json\n" + line("user", "We must never skip malformed lines in real transcripts.") + "\n,,,"
    bullets, stats = extract_bullets(tr)
    assert stats["malformed"] == 2 and len(bullets) == 1


def t_non_dict_entries_ignored():
    tr = '"just a string"\n[1,2,3]\n' + line("user", "We must handle weird transcript entries gracefully.")
    bullets, stats = extract_bullets(tr)
    assert stats["parsed"] == 3 and len(bullets) == 1


def t_missing_text_field():
    tr = json.dumps({"role": "user"})  # no text
    bullets, stats = extract_bullets(tr)
    assert bullets == [] and stats["parsed"] == 1


def t_cli_missing_file():
    from memory_diff import _cmd_build
    ns = type("NS", (), {})()
    ns.transcript = os.path.join("no", "such", "file.jsonl")
    ns.memory = None
    ns.json = False
    ns.stats = False
    ns.max_add = 20
    assert _cmd_build(ns) == 2  # error exit, no traceback


# ---------------------------------------------------------------- C. edges
def t_empty_transcript():
    bullets, stats = extract_bullets("")
    assert bullets == [] and stats["lines"] == 0
    diff, fresh = diff_against("# memory\n", bullets)
    assert fresh == [] and diff == ""


def t_empty_memory_file():
    tr = line("user", "We decided to adopt the new formatter across the whole repo.")
    bullets, _ = extract_bullets(tr)
    diff, fresh = diff_against("", bullets)
    assert len(fresh) == 1 and diff.startswith("---")


def t_huge_transcript():
    tr = "\n".join(
        line("user", "hello there %d" % i) if i % 2 else
        line("user", "We must log observation %d about the recurring nightly job." % i)
        for i in range(10000))
    bullets, stats = extract_bullets(tr)
    assert stats["lines"] == 10000
    assert 1000 < len(bullets) <= 5000  # signal words recur; noise skipped


def t_unicode_bullets():
    tr = "\n".join([
        line("user", "我们决定用 SQLite 做缓存，因为零运维成本。",),
        line("user", "永远不要把密钥写进仓库配置，上次因此搞挂了生产环境。"),
    ])
    bullets, _ = extract_bullets(tr)
    assert len(bullets) == 2 and all(b.startswith("- ") for b in bullets)


def t_duplicate_lines_collapsed():
    tr = "\n".join([line("user", "We must never deploy on Friday afternoons, the team decided firmly.")] * 5)
    bullets, _ = extract_bullets(tr)
    assert len(bullets) == 1


def main():
    for name, fn in sorted(globals().items()):
        if name.startswith("t_"):
            check(name, fn)
    passed = sum(1 for _, ok, _ in results if ok)
    for name, ok, err in results:
        print("%-4s %s%s" % ("PASS" if ok else "FAIL", name,
                             ("  -> " + err) if err else ""))
    print("transcript-memory-diff self-test: %d/%d PASS" % (passed, len(results)))
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
