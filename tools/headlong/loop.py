#!/usr/bin/env python3
"""Thin Headlong-shaped loop for LanBB.

Stdlib only. No LLM, no AgentSky, no installer, no secrets. See README.md.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SECRETISH = re.compile(
    r"(?i)(api[_-]?key|secret|passwd|password|bearer\s+[a-z0-9._\-]+|"
    r"sk-[a-z0-9]{8,}|sk-ant-|sk-or-|xox[baprs]-|ghp_[a-z0-9]+|"
    r"agentsky)"
)

TRAJ_NAME = "trajectory.jsonl"
MAX_ROUNDS = 3
RUN_TIMEOUT_SEC = 10
TOY_TASK = "Print 6 times 7 as a single integer."
TOY_BASH = 'FINAL="$(python3 -c \'print(6 * 7)\')"\n'


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
    """Nested RLM step: isolated CONTEXT, same trajectory."""
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
        "max_rounds": MAX_ROUNDS,
    }


def fingerprint(bash: str) -> str:
    return hashlib.sha256(bash.strip().encode("utf-8")).hexdigest()[:16]


def think_bash_for_task(task: str, think_file: Path | None) -> str:
    if think_file is not None:
        text = think_file.read_text(encoding="utf-8")
        refuse_secrets(text)
        return text if text.endswith("\n") else text + "\n"
    if task.strip() == TOY_TASK:
        return TOY_BASH
    raise SystemExit(
        "headlong stub: no offline thinker for this task. "
        f"Use the toy ({TOY_TASK!r}) or pass --think-file."
    )


def _sandbox_env(sandbox: Path, final_path: Path) -> dict[str, str]:
    path = os.environ.get("PATH", "/usr/bin:/bin")
    env = {
        "PATH": path,
        "HOME": str(sandbox),
        "LC_ALL": "C",
        "HEADLONG_FINAL": str(final_path),
    }
    for key, value in os.environ.items():
        if key in env:
            continue
        if SECRETISH.search(key) or SECRETISH.search(value or ""):
            continue
        if key in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "OPENROUTER_API_KEY", "GEMINI_API_KEY"):
            continue
        # Keep the host env small: only PATH/HOME/LC_ALL plus HEADLONG_FINAL.
    return env


def run_bash(home: Path, bash: str, timeout: int = RUN_TIMEOUT_SEC) -> dict:
    refuse_secrets(bash)
    sandbox = home / "sandbox"
    sandbox.mkdir(parents=True, exist_ok=True)
    final_path = sandbox / "final.txt"
    if final_path.exists():
        final_path.unlink()
    script = sandbox / "think.sh"
    wrapper = (
        "#!/usr/bin/env bash\n"
        "set -u\n"
        'FINAL=""\n'
        'FINAL_FILE=""\n'
        f"{bash}"
        "\n"
        'if [ -n "${FINAL:-}" ]; then\n'
        '  printf "%s" "$FINAL" > "$HEADLONG_FINAL"\n'
        'elif [ -n "${FINAL_FILE:-}" ] && [ -f "$FINAL_FILE" ]; then\n'
        '  cat "$FINAL_FILE" > "$HEADLONG_FINAL"\n'
        "fi\n"
    )
    script.write_text(wrapper, encoding="utf-8")
    try:
        proc = subprocess.run(
            ["bash", str(script)],
            cwd=str(sandbox),
            env=_sandbox_env(sandbox, final_path),
            capture_output=True,
            text=True,
            timeout=timeout,
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "exit": 124,
            "stdout": (exc.stdout or "")[-2000:] if isinstance(exc.stdout, str) else "",
            "stderr": f"headlong stub: run timed out after {timeout}s",
            "final": "",
        }
    final = ""
    if final_path.exists():
        final = final_path.read_text(encoding="utf-8")
    return {
        "exit": proc.returncode,
        "stdout": (proc.stdout or "")[-2000:],
        "stderr": (proc.stderr or "")[-2000:],
        "final": final,
    }


def cycle(
    home: Path,
    task: str,
    think_file: Path | None = None,
    max_rounds: int = MAX_ROUNDS,
) -> dict:
    refuse_secrets(task)
    if max_rounds < 1:
        raise SystemExit("headlong stub: max rounds must be >= 1")
    if max_rounds > MAX_ROUNDS:
        max_rounds = MAX_ROUNDS

    observe(home, task, source="cycle")
    seen: list[str] = []
    last_run: dict | None = None

    for round_i in range(1, max_rounds + 1):
        bash = think_bash_for_task(task, think_file)
        fp = fingerprint(bash)
        think_rec = append_step(
            home,
            {
                "type": "think",
                "source": "stub",
                "round": round_i,
                "fingerprint": fp,
                "content": bash,
            },
        )
        if fp in seen:
            stop = append_step(
                home,
                {
                    "type": "stop",
                    "reason": "same_fingerprint",
                    "fingerprint": fp,
                    "round": round_i,
                    "content": f"same fingerprint twice: {fp}",
                },
            )
            return {
                "ok": False,
                "reason": "same_fingerprint",
                "rounds": round_i,
                "fingerprint": fp,
                "think": think_rec,
                "stop": stop,
                "final": None,
            }
        seen.append(fp)

        result = run_bash(home, bash)
        last_run = append_step(
            home,
            {
                "type": "run",
                "source": "sandbox",
                "round": round_i,
                "exit": result["exit"],
                "stdout": result["stdout"],
                "stderr": result["stderr"],
            },
        )
        if result["final"] != "":
            final_rec = append_step(
                home,
                {
                    "type": "final",
                    "source": "sandbox",
                    "round": round_i,
                    "content": result["final"],
                },
            )
            return {
                "ok": True,
                "reason": "final",
                "rounds": round_i,
                "fingerprint": fp,
                "think": think_rec,
                "run": last_run,
                "final": final_rec,
            }

        observe(
            home,
            f"round {round_i} produced no FINAL (exit={result['exit']})",
            source="run",
        )

    fail = append_step(
        home,
        {
            "type": "stop",
            "reason": "max_rounds",
            "round": max_rounds,
            "content": f"stopped after {max_rounds} rounds with no FINAL",
        },
    )
    return {
        "ok": False,
        "reason": "max_rounds",
        "rounds": max_rounds,
        "think": None,
        "run": last_run,
        "stop": fail,
        "final": None,
    }


def write_proof(path: Path, invoke: str, result: dict, home: Path) -> None:
    steps = load_steps(home)
    think_steps = [s for s in steps if s.get("type") == "think"]
    run_steps = [s for s in steps if s.get("type") == "run"]
    snippet = think_steps[-1:] + run_steps[-1:]
    final_text = ""
    if result.get("final"):
        final_text = result["final"].get("content", "")
    lines = [
        "# Headlong cycle proof",
        "",
        "## Invoke",
        "",
        "```bash",
        invoke,
        "```",
        "",
        "## Trajectory snippet (think + run)",
        "",
        "```jsonl",
    ]
    for step in snippet:
        lines.append(json.dumps(step, ensure_ascii=False))
    lines.extend(
        [
            "```",
            "",
            "## FINAL",
            "",
            "```",
            final_text if final_text != "" else "(none)",
            "```",
            "",
            f"result: {result.get('reason')} in {result.get('rounds')} round(s).",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Thin Headlong-shaped loop (think-run-FINAL). No AgentSky, no secrets."
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
    cy = sub.add_parser("cycle", help="Run one think-run-FINAL loop (max 3 rounds)")
    cy.add_argument("--task", default=TOY_TASK, help="Tiny task text")
    cy.add_argument(
        "--think-file",
        type=Path,
        default=None,
        help="Bash the think step should run (offline; no LLM)",
    )
    cy.add_argument(
        "--proof",
        type=Path,
        default=None,
        help="Write invoke + think/run snippet + FINAL to this markdown file",
    )
    return p


def _cycle_invoke(args: argparse.Namespace) -> str:
    parts = ["python3", "tools/headlong/loop.py", "cycle"]
    if args.task != TOY_TASK:
        parts.extend(["--task", json.dumps(args.task)])
    else:
        parts.extend(["--task", json.dumps(TOY_TASK)])
    if args.think_file is not None:
        parts.extend(["--think-file", str(args.think_file)])
    if args.proof is not None:
        parts.extend(["--proof", str(args.proof)])
    if args.home is not None:
        parts.extend(["--home", str(args.home)])
    return " ".join(parts)


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
    if args.cmd == "cycle":
        result = cycle(home, args.task, think_file=args.think_file)
        if args.proof is not None:
            write_proof(args.proof, _cycle_invoke(args), result, home)
        out = {
            "ok": result["ok"],
            "reason": result["reason"],
            "rounds": result["rounds"],
            "final": (result["final"] or {}).get("content") if result.get("final") else None,
            "fingerprint": result.get("fingerprint"),
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0 if result["ok"] else 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
