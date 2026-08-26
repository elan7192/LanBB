#!/usr/bin/python3
"""Pawel four memories after a hunt→harden loop.

1. SEMANTIC — 5–15 line method note (markdown file for Vault/PM).
2. EPISODIC — one CSV row (Taipei date, loop, score, SHA/PR, what hardened).
3. PROCEDURAL — only if a reusable procedure appeared; otherwise skip (SKILL.md lives elsewhere).
4. WORKING — do not write. Chat is working memory.

No transcripts. No vector DB. No wiki/second-brain.
"""

from __future__ import annotations

import csv
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

from scope import load_scope

EPISODIC_FIELDS = ("date_taipei", "loop", "score", "sha_pr", "hardened")
SEMANTIC_RE = re.compile(r"semantic-loop-(\d+)\.md$")


class MemoryError(Exception):
    """Memory emit refused."""


def memory_dir(slug: str, root: Optional[Path] = None) -> Path:
    scope = load_scope(slug, root)
    dest = scope.path.parent / "memory"
    dest.mkdir(parents=True, exist_ok=True)
    return dest


def next_loop(dest: Path) -> int:
    nums = []
    for path in dest.glob("semantic-loop-*.md"):
        match = SEMANTIC_RE.search(path.name)
        if match:
            nums.append(int(match.group(1)))
    return (max(nums) + 1) if nums else 1


def git_sha(root: Path) -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(root),
            text=True,
        )
        return out.strip() or "unknown"
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def taipei_date() -> str:
    return datetime.now(ZoneInfo("Asia/Taipei")).date().isoformat()


def _line_count(text: str) -> int:
    lines = [ln for ln in text.strip().splitlines() if ln.strip()]
    return len(lines)


def emit(
    slug: str,
    semantic: str,
    score: str,
    hardened: str,
    sha_pr: str = "",
    loop: Optional[int] = None,
    root: Optional[Path] = None,
    procedural: str = "skip",
) -> dict:
    """Write semantic note + one episodic row. Never writes working memory."""
    scope = load_scope(slug, root)
    dest = memory_dir(slug, root)
    n = loop if loop is not None else next_loop(dest)
    note = semantic.strip() + "\n"
    nlines = _line_count(note)
    if nlines < 5 or nlines > 15:
        raise MemoryError(
            f"semantic note must be 5–15 non-empty lines, got {nlines}"
        )
    sem_path = dest / f"semantic-loop-{n}.md"
    header = f"# Semantic memory — loop {n}\n\n"
    sem_path.write_text(header + note, encoding="utf-8")
    epi = dest / "episodic.csv"
    sha = sha_pr or git_sha(scope.path.parent.parent.parent)
    row = {
        "date_taipei": taipei_date(),
        "loop": str(n),
        "score": score,
        "sha_pr": sha,
        "hardened": hardened,
    }
    new_file = not epi.is_file()
    with epi.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=EPISODIC_FIELDS)
        if new_file:
            writer.writeheader()
        writer.writerow(row)
    working = dest / "working.md"
    if working.exists():
        working.unlink()
    return {
        "loop": n,
        "semantic": str(sem_path),
        "episodic": str(epi),
        "procedural": procedural,
        "working": "not-written",
        "row": row,
    }
