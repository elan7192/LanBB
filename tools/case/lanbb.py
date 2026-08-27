#!/usr/bin/python3
"""LanBB authorized CASE CLI.

  lanbb case new <program>
  lanbb case score <program>
  lanbb case report <program>
  lanbb case memory emit <program> --score n/N --hardened TEXT --semantic-file PATH
  lanbb scope parse <program>
  lanbb recon <program> [--domain HOST] [--run-subfaster]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import memory as memory_mod  # noqa: E402
import recon as recon_mod  # noqa: E402
import report as report_mod  # noqa: E402
import score as score_mod  # noqa: E402
import scope as scope_mod  # noqa: E402

JUICE_SCOPE = """---
program: juice-shop
kind: lab
authorization: local-docker
wall: v7-hardened
hunted: v6-hardened
---

# OWASP Juice Shop (local lab)

Hypothetical in-scope shop. Not a live bounty program. Not random internet.

## In scope

- http://127.0.0.1:3000
- http://localhost:3000

## Out of scope

- Any host that is not this local lab
- Live bug-bounty programs
- Random internet
- Adult or porn programs
"""

GENERIC_SCOPE = """---
program: {slug}
kind: lab
authorization: replace-with-written-authorization
---

# {slug}

Fill this file before any recon. Fail-closed: empty in-scope allows no targets.

## In scope

- # add authorized hosts only

## Out of scope

- Any host not listed above
- Live bug-bounty programs unless this file records written authorization
- Random internet
- Adult or porn programs
"""

NOTES = """# {slug} case notes

Authorized CASE file. Evidence dumps, screenshots, and HTTP traffic stay gitignored.

1. Parse `scope.md` (fail-closed).
2. Passive recon only on in-scope domains. Local labs skip subfaster.
3. Record findings, then write a report. No exploit PoC generator.
"""


def _write(path: Path, text: str, overwrite: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        return
    path.write_text(text, encoding="utf-8")


def case_new(slug: str, root: Optional[Path] = None) -> Path:
    slug = scope_mod.validate_slug(slug)
    root = root or scope_mod.repo_root()
    dest = scope_mod.program_dir(slug, root)
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "recon" / "subdomains").mkdir(parents=True, exist_ok=True)
    (dest / "findings").mkdir(parents=True, exist_ok=True)
    (dest / "reports").mkdir(parents=True, exist_ok=True)
    (dest / "memory").mkdir(parents=True, exist_ok=True)
    _write(dest / "recon" / "subdomains" / ".gitkeep", "")
    _write(dest / "findings" / ".gitkeep", "")
    _write(dest / "reports" / ".gitkeep", "")
    _write(dest / "memory" / ".gitkeep", "")
    scope_text = JUICE_SCOPE if slug == "juice-shop" else GENERIC_SCOPE.format(slug=slug)
    scope_file = dest / "scope.md"
    if not scope_file.is_file():
        scope_file.write_text(scope_text, encoding="utf-8")
    _write(dest / "notes.md", NOTES.format(slug=slug))
    return dest


def _cmd_case_new(args: argparse.Namespace) -> int:
    dest = case_new(args.program, Path(args.root) if args.root else None)
    print(f"case ready: {dest}")
    print("  scope.md recon/subdomains/ findings/ reports/ notes.md memory/")
    return 0


def _cmd_case_report(args: argparse.Namespace) -> int:
    root = Path(args.root) if args.root else None
    dest = report_mod.write_report(args.program, root)
    print(f"report: {dest}")
    return 0


def _cmd_case_memory(args: argparse.Namespace) -> int:
    root = Path(args.root) if args.root else None
    note = Path(args.semantic_file).read_text(encoding="utf-8")
    result = memory_mod.emit(
        args.program,
        semantic=note,
        score=args.score,
        hardened=args.hardened,
        sha_pr=args.sha_pr or "",
        loop=args.loop,
        root=root,
        procedural=args.procedural,
    )
    print(json.dumps(result, indent=2))
    return 0


def _cmd_case_score(args: argparse.Namespace) -> int:
    root = Path(args.root) if args.root else None
    result = score_mod.score_program(
        args.program,
        root=root,
        base=args.base_url,
        start=args.start,
    )
    print(result["score"])
    print(json.dumps(result, indent=2))
    return 0


def _cmd_scope_parse(args: argparse.Namespace) -> int:
    root = Path(args.root) if args.root else None
    parsed = scope_mod.load_scope(args.program, root)
    print(
        json.dumps(
            {
                "slug": parsed.slug,
                "kind": parsed.kind,
                "path": str(parsed.path),
                "in_scope": parsed.in_scope,
                "out_of_scope": parsed.out_of_scope,
                "in_scope_hosts": parsed.in_scope_hosts(),
            },
            indent=2,
        )
    )
    return 0


def _cmd_recon(args: argparse.Namespace) -> int:
    root = Path(args.root) if args.root else None
    result = recon_mod.run_passive_recon(
        args.program,
        domain=args.domain,
        root=root,
        run_subfaster=args.run_subfaster,
    )
    print(json.dumps(result, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lanbb",
        description="LanBB authorized CASE CLI. Fail-closed without a program scope file.",
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Repository root (default: detect from this file)",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    case = sub.add_parser("case", help="Case folder and lab score")
    case_sub = case.add_subparsers(dest="case_cmd", required=True)
    new = case_sub.add_parser("new", help="Create programs/<slug>/ layout")
    new.add_argument("program")
    new.set_defaults(func=_cmd_case_new)

    sc = case_sub.add_parser("score", help="Read Juice Shop solved/total (no auto-pwn)")
    sc.add_argument("program")
    sc.add_argument("--base-url", default=score_mod.DEFAULT_BASE)
    sc.add_argument(
        "--start",
        action="store_true",
        help="Try docker run of Juice Shop, or print the documented docker command",
    )
    sc.set_defaults(func=_cmd_case_score)

    rp = case_sub.add_parser("report", help="Write reports/draft.md (no PoC)")
    rp.add_argument("program")
    rp.set_defaults(func=_cmd_case_report)

    mem = case_sub.add_parser("memory", help="Emit Pawel memories after a hunt→harden loop")
    mem_sub = mem.add_subparsers(dest="memory_cmd", required=True)
    emit = mem_sub.add_parser("emit", help="Semantic note + one episodic row. No working memory.")
    emit.add_argument("program")
    emit.add_argument("--score", required=True, help="Lab score n/N")
    emit.add_argument("--hardened", required=True, help="What this loop hardened")
    emit.add_argument("--semantic-file", required=True, help="5–15 line method note")
    emit.add_argument("--sha-pr", default="", help="Commit SHA and/or PR URL")
    emit.add_argument("--loop", type=int, default=None)
    emit.add_argument(
        "--procedural",
        default="skip",
        help="skip, or path to a SKILL.md if a reusable procedure appeared",
    )
    emit.set_defaults(func=_cmd_case_memory)

    sp = sub.add_parser("scope", help="Parse program scope / OOS")
    scope_sub = sp.add_subparsers(dest="scope_cmd", required=True)
    parse = scope_sub.add_parser("parse", help="Parse programs/<slug>/scope.md")
    parse.add_argument("program")
    parse.set_defaults(func=_cmd_scope_parse)

    rec = sub.add_parser("recon", help="Passive recon on in-scope domains only")
    rec.add_argument("program")
    rec.add_argument("--domain", default=None, help="Single host; must be in-scope")
    rec.add_argument(
        "--run-subfaster",
        action="store_true",
        help="Invoke optional subfaster if installed (skipped for local labs)",
    )
    rec.set_defaults(func=_cmd_recon)
    return parser


def main(argv: Optional[list] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (scope_mod.ScopeError, memory_mod.MemoryError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
