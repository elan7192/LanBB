#!/usr/bin/env python3
"""Offline stub of a persistent RLM-style loop for LanBB.

No LLM, no AgentSky, no network, no secrets. See README.md.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SECRETISH = re.compile(
    r"(?i)(api[_-]?key|secret|passwd|password|bearer\s+[a-z0-9._\-]+|"
    r"sk-[a-z0-9]{8,}|sk-ant-|sk-or-|xox[baprs]-|ghp_[a-z0-9]+|"
    r"agentsky)"
)

TRAJ_NAME = "trajectory.jsonl"


def default_home() -> Path:
    return Path(__file__).resolve().parent / ".run"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def traj_path(home: Path) -> Path:
    return home / TRAJ_NAME


def refuse_secrets(text: str) -> None:
    if SECRETISH.search(text or ""):
        raise SystemExit(
            "headlong stub: refusing text that looks like a secret or AgentSky credential"
        )


def append_step(home: Path, step: dict) -> dict:
    home.mkdir(parents=True, exist_ok=True)
    path = traj_path(home)
    n = 0
    if path.exists():
        with path.open(encoding="utf-8") as fh:
            n = sum(1 for line in fh if line.strip())
    record = {
        "step_id": n + 1,
        "ts": utc_now(),
        **step,
    }
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def load_steps(home: Path) -> list[dict]:
    path = traj_path(home)
    if not path.exists():
        return []
    steps = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                steps.append(json.loads(line))
    return steps


def pending_observations(steps: list[dict]) -> list[dict]:
    last_thought = 0
    for step in steps:
        if step.get("type") == "thought":
            last_thought = step["step_id"]
    return [
        s
        for s in steps
        if s.get("type") in ("observation", "human") and s["step_id"] > last_thought
    ]


def observe(home: Path, text: str, source: str = "human") -> dict:
    refuse_secrets(text)
    return append_step(
        home,
        {
            "type": "observation",
            "source": source,
            "content": text,
        },
    )


def rlm_sub_tick(home: Path, query: str) -> dict:
    """Nested RLM step: isolated CONTEXT, no new product session."""
    refuse_secrets(query)
    return append_step(
        home,
        {
            "type": "rlm_sub",
            "source": "stub",
            "content": f"CONTEXT={query!r}; FINAL=stub-answer",
            "query": query,
        },
    )


def think(home: Path) -> dict:
    steps = load_steps(home)
    pending = pending_observations(steps)
    if not pending:
        thought = "idle: no new observations; mind stays on the same trajectory"
        record = append_step(
            home, {"type": "thought", "source": "stub", "content": thought}
        )
        return record

    lines = []
    for obs in pending:
        body = (obs.get("content") or "").strip()
        lines.append(f"noticed observation #{obs['step_id']}: {body}")
        if body.lower().startswith("sub:"):
            query = body[4:].strip()
            rlm_sub_tick(home, query)
            lines.append(f"nested RLM tick on isolated CONTEXT ({query!r})")
    thought = " | ".join(lines)
    return append_step(
        home, {"type": "thought", "source": "stub", "content": thought}
    )


def tick(home: Path, n: int) -> list[dict]:
    if n < 1:
        raise SystemExit("headlong stub: --ticks must be >= 1")
    return [think(home) for _ in range(n)]


def status(home: Path) -> dict:
    steps = load_steps(home)
    types: dict[str, int] = {}
    for step in steps:
        types[step.get("type", "?")] = types.get(step.get("type", "?"), 0) + 1
    return {
        "home": str(home),
        "trajectory": str(traj_path(home)) if traj_path(home).exists() else None,
        "steps": len(steps),
        "types": types,
        "same_session": True,
        "agentsky": False,
        "llm": False,
        "secrets_files": False,
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Offline persistent RLM-style loop stub (no AgentSky, no secrets)."
    )
    p.add_argument(
        "--home",
        type=Path,
        default=None,
        help="State directory (default: tools/headlong/.run)",
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    obs = sub.add_parser("observe", help="Inject a human message as an observation")
    obs.add_argument("text", nargs="+", help="Message text")
    tk = sub.add_parser("tick", help="Run N think ticks on the same trajectory")
    tk.add_argument("--ticks", type=int, default=1)
    sub.add_parser("status", help="Print trajectory stats as JSON")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    home = (args.home or default_home()).expanduser().resolve()
    if args.cmd == "observe":
        rec = observe(home, " ".join(args.text))
        print(json.dumps(rec, ensure_ascii=False))
        return 0
    if args.cmd == "tick":
        for rec in tick(home, args.ticks):
            print(json.dumps(rec, ensure_ascii=False))
        return 0
    if args.cmd == "status":
        print(json.dumps(status(home), indent=2, ensure_ascii=False))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
