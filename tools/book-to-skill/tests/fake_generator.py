#!/usr/bin/env python3
"""Test double: write a minimal skill bundle from BOOK_TO_SKILL_BUNDLE_DIR."""

from __future__ import annotations

import os
from pathlib import Path


def main() -> int:
    bundle = Path(os.environ["BOOK_TO_SKILL_BUNDLE_DIR"])
    chapters = bundle / "chapters"
    chapters.mkdir(parents=True, exist_ok=True)
    (bundle / "SKILL.md").write_text(
        """---
name: widget-protocol
description: "Knowledge base from Widget Protocol Handbook by Ada Example."
---

# Widget Protocol Handbook
**Author**: Ada Example | **Chapters**: 3

## Core Frameworks & Mental Models
- **Three-way handshake**: Use SYN / SYN-ACK / ACK when opening a stream.
- **Credit-based flow control**: Prefer credits over unbounded queues.
- **Bounded waits**: Every wait has a timeout.

## Chapter Index
| # | Title | Key Frameworks |
|---|-------|----------------|
| [ch01](chapters/ch01-handshake.md) | Handshake | three-way handshake |
| [ch02](chapters/ch02-backpressure.md) | Backpressure | credits |
| [ch03](chapters/ch03-timeouts.md) | Timeouts | bounded waits |

## Supporting Files
- [glossary.md](glossary.md)
- [patterns.md](patterns.md)
- [cheatsheet.md](cheatsheet.md)
""",
        encoding="utf-8",
    )
    (chapters / "ch01-handshake.md").write_text(
        "# Chapter 1: Handshake\n\n## Core Idea\nOpen every stream with SYN / SYN-ACK / ACK.\n",
        encoding="utf-8",
    )
    (chapters / "ch02-backpressure.md").write_text(
        "# Chapter 2: Backpressure\n\n## Core Idea\nAdvertise credits; stop at zero.\n",
        encoding="utf-8",
    )
    (chapters / "ch03-timeouts.md").write_text(
        "# Chapter 3: Timeouts\n\n## Core Idea\nBound every wait.\n",
        encoding="utf-8",
    )
    (bundle / "glossary.md").write_text(
        "**ACK** — final handshake step (Ch 1)\n**Credit** — advertised remaining buffer (Ch 2)\n",
        encoding="utf-8",
    )
    (bundle / "patterns.md").write_text(
        "## Three-way handshake\n**When to use**: new stream.\n**How**: SYN, SYN-ACK, ACK.\n",
        encoding="utf-8",
    )
    (bundle / "cheatsheet.md").write_text(
        "| Situation | Do |\n|-----------|----|\n| New stream | Three-way handshake |\n| Slow consumer | Credit-based flow control |\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
