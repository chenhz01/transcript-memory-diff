#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
transcript-memory-diff -- Incremental memory bullets from agent transcripts.

Parse a JSONL transcript (one {"role": "...", "text": "..."} per line),
extract high-signal sentences ("decided", "must", "never", "root cause",
preferences, ...), and emit a unified diff against your existing memory
file. Nothing auto-merges: the diff is the artifact a human approves.

Pure standard library. MIT. See README.md for design trade-offs.
"""
import argparse
import difflib
import json
import re
import sys

# Sentences worth remembering (heuristic, deliberately simple & auditable).
SIGNAL = re.compile(
    r"(decided|must|never|always|prefer|broken|fixed|root cause|chose|"
    r"user (wants|prefers)|约定|决定|必须|不要|修复|根因|偏好)",
    re.I)
# Obvious chatter, dropped even if it happens to contain a signal word.
NOISE = re.compile(r"^(um+|uh+|test test|hello|hi there|thanks|ok then|yay)\b", re.I)

MIN_LEN = 20   # sentences shorter than this are chatter, not memory
MAX_LEN = 300  # sentences longer than this are documents, not memory


def extract_bullets(transcript_jsonl):
    """Return (bullets, stats).

    transcript_jsonl: str, one JSON object per line with a "text" field.
    stats: {"lines", "parsed", "malformed", "sentences", "signal",
            "dropped_noise", "dropped_length"}
    Bullets are ordered by first appearance (chronological), deduplicated
    (case-insensitive whitespace-normalized), each formatted as "- <text>".
    """
    stats = {"lines": 0, "parsed": 0, "malformed": 0, "sentences": 0,
             "signal": 0, "dropped_noise": 0, "dropped_length": 0}
    bullets, seen = [], set()
    for line in transcript_jsonl.splitlines():
        stats["lines"] += 1
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except ValueError:
            stats["malformed"] += 1
            continue
        stats["parsed"] += 1
        text = str(entry.get("text", "")) if isinstance(entry, dict) else ""
        for sent in re.split(r"(?<=[.!?。！？])\s+", text):
            sent = sent.strip()
            if not sent:
                continue
            stats["sentences"] += 1
            if SIGNAL.search(sent) is None:
                continue
            stats["signal"] += 1
            if NOISE.search(sent):
                stats["dropped_noise"] += 1
                continue
            if not (MIN_LEN < len(sent) < MAX_LEN):
                stats["dropped_length"] += 1
                continue
            key = re.sub(r"\s+", " ", sent).lower()
            if key not in seen:
                seen.add(key)
                bullets.append("- " + sent)
    return bullets, stats


def diff_against(existing_md, bullets, max_add=20):
    """Unified diff proposing new bullets appended to existing memory.

    - Bullets already present in the memory file (normalized compare) are
      skipped, so re-running on the same transcript yields an empty diff.
    - Order of proposals follows the transcript, not alphabetical order.
    - max_add caps the diff size so a noisy session cannot flood the gate.
    Returns (diff_text, proposed_bullets).
    """
    old = existing_md.splitlines()
    existing_norm = {re.sub(r"\s+", " ", ln.lstrip("- ")).strip().lower()
                     for ln in old}
    fresh = []
    for b in bullets:
        norm = re.sub(r"\s+", " ", b.lstrip("- ")).strip().lower()
        if norm not in existing_norm and b not in fresh:
            fresh.append(b)
    fresh = fresh[:max(0, int(max_add))]
    proposed = old + fresh
    diff = "\n".join(difflib.unified_diff(
        old, proposed, "memory.md", "memory.md (proposed)", lineterm="", n=1))
    return diff, fresh


def run(transcript_jsonl, existing_md, max_add=20):
    """Convenience pipeline: returns (diff_text, proposed_bullets, stats)."""
    bullets, stats = extract_bullets(transcript_jsonl)
    diff, fresh = diff_against(existing_md, bullets, max_add=max_add)
    stats["proposed"] = len(fresh)
    stats["already_in_memory"] = len(bullets) - len(fresh) \
        if len(bullets) >= len(fresh) else 0
    return diff, fresh, stats


# ---- CLI -------------------------------------------------------------------
def _cmd_build(args):
    try:
        with open(args.transcript, encoding="utf-8") as fh:
            transcript = fh.read()
    except OSError as exc:
        sys.stderr.write("error reading transcript: %s\n" % exc)
        return 2
    if args.memory:
        try:
            with open(args.memory, encoding="utf-8") as fh:
                existing = fh.read()
        except OSError as exc:
            sys.stderr.write("error reading memory: %s\n" % exc)
            return 2
    else:
        existing = "# memory\n"
    diff, fresh, stats = run(transcript, existing, max_add=args.max_add)
    if args.json:
        print(json.dumps({"stats": stats, "proposed": fresh}, indent=2,
                         ensure_ascii=False))
    else:
        print(diff if diff else
              "(no proposed changes — transcript holds no new high-signal bullets)")
        if args.stats:
            sys.stderr.write("stats: %s\n" % json.dumps(stats, sort_keys=True))
    return 0


def build_parser():
    p = argparse.ArgumentParser(
        prog="memory_diff",
        description="Extract high-signal memory bullets from an agent "
                    "transcript and emit a unified diff for human approval. "
                    "Nothing auto-merges.")
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="build a memory diff from a transcript")
    b.add_argument("transcript", help="path to transcript JSONL")
    b.add_argument("--memory", default=None,
                   help="existing memory markdown (default: fresh file)")
    b.add_argument("--max-add", type=int, default=20,
                   help="cap on proposed bullets (default 20)")
    b.add_argument("--json", action="store_true",
                   help="emit stats + proposed bullets as JSON")
    b.add_argument("--stats", action="store_true",
                   help="print extraction stats to stderr")
    b.set_defaults(func=_cmd_build)
    return p


if __name__ == "__main__":
    ns = build_parser().parse_args()
    sys.exit(ns.func(ns))
