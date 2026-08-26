#!/usr/bin/python3
"""Juice Shop lab score harness.

Reads the app's own GET /api/Challenges (solved/total). Does not auto-pwn.
Lab-only. Fail-closed without programs/<slug>/scope.md.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional

from scope import ScopeError, load_scope, repo_root

DEFAULT_BASE = os.environ.get("LANBB_JUICE_BASE", "http://127.0.0.1:3000")
DOCKER_IMAGE = "bkimminich/juice-shop"
DOCKER_NAME = "lanbb-juice-shop"
DOCKER_RUN = (
    f"docker run --rm -d --name {DOCKER_NAME} -p 3000:3000 {DOCKER_IMAGE}"
)
# Juice Shop master hacking challenges (not coding /snippets).
HACKING_TOTAL = 116
DOCKER_SOLVABLE = 98
DOCKER_DISABLED_ENV = 18


class ScoreError(ScopeError):
    """Score harness refused or could not read the lab."""


def _challenges_url(base: str) -> str:
    return base.rstrip("/") + "/api/Challenges/"


def fetch_challenges(base: str, timeout: float = 4.0) -> Dict[str, Any]:
    req = urllib.request.Request(
        _challenges_url(base),
        headers={"Accept": "application/json", "User-Agent": "lanbb-case-score"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            body = res.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise ScoreError(
            f"Juice Shop not reachable at {base} ({exc}). "
            f"Start the local lab: {DOCKER_RUN}"
        ) from exc
    try:
        data = json.loads(body)
    except json.JSONDecodeError as exc:
        raise ScoreError("Juice Shop /api/Challenges was not JSON") from exc
    if not isinstance(data, dict):
        raise ScoreError("Juice Shop /api/Challenges must be an object")
    return data


def tally(payload: Dict[str, Any]) -> Dict[str, Any]:
    rows = payload.get("data")
    if not isinstance(rows, list):
        raise ScoreError("Juice Shop /api/Challenges missing data[]")
    total = len(rows)
    solved = 0
    for row in rows:
        if isinstance(row, dict) and row.get("solved") is True:
            solved += 1
    return {
        "solved": solved,
        "total": total,
        "score": f"{solved}/{total}",
        "ratio": (solved / total) if total else 0.0,
        "docker_solvable": DOCKER_SOLVABLE,
        "docker_disabled_env": DOCKER_DISABLED_ENV,
        "coding_challenges": "separate /snippets — not mixed into n/N",
    }


def wait_for_lab(base: str, tries: int = 30, delay: float = 2.0) -> Dict[str, Any]:
    last: Optional[Exception] = None
    for _ in range(tries):
        try:
            return fetch_challenges(base)
        except ScoreError as exc:
            last = exc
            time.sleep(delay)
    raise ScoreError(str(last) if last else "lab did not become ready")


def start_lab_docker() -> str:
    docker = shutil.which("docker")
    if not docker:
        raise ScoreError(
            "docker not installed. Documented start:\n"
            f"  {DOCKER_RUN}\n"
            "Then: python3 tools/case/lanbb.py case score juice-shop"
        )
    inspect = subprocess.run(
        [docker, "inspect", "-f", "{{.State.Running}}", DOCKER_NAME],
        capture_output=True,
        text=True,
    )
    if inspect.returncode == 0 and inspect.stdout.strip() == "true":
        return "already-running"
    subprocess.run([docker, "rm", "-f", DOCKER_NAME], capture_output=True)
    proc = subprocess.run(
        [
            docker,
            "run",
            "--rm",
            "-d",
            "--name",
            DOCKER_NAME,
            "-p",
            "3000:3000",
            DOCKER_IMAGE,
        ],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise ScoreError(
            "docker run failed:\n"
            f"{proc.stderr or proc.stdout}\n"
            f"Documented start: {DOCKER_RUN}"
        )
    return "started"


def score_program(
    slug: str,
    root: Optional[Path] = None,
    base: str = DEFAULT_BASE,
    start: bool = False,
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    root = root or repo_root()
    scope = load_scope(slug, root)
    if not scope.is_lab and slug != "juice-shop":
        raise ScoreError(
            f"fail-closed: score loop is lab-only; {slug!r} is kind={scope.kind!r}"
        )
    meta = {
        "program": scope.slug,
        "base": base,
        "fail_closed": False,
        "kind": scope.kind,
        "image": DOCKER_IMAGE,
        "hacking_total_master": HACKING_TOTAL,
        "docker_solvable": DOCKER_SOLVABLE,
        "docker_disabled_env": DOCKER_DISABLED_ENV,
        "continue_code": "GET /rest/continue-code is a token only — do not forge",
        "note": "Authorized CASE tools only. This harness does not auto-pwn.",
    }
    if payload is None:
        try:
            if start:
                start_lab_docker()
                payload = wait_for_lab(base)
            else:
                payload = fetch_challenges(base)
        except ScoreError as exc:
            result = {
                "solved": 0,
                "total": HACKING_TOTAL,
                "score": "0/116",
                "status": "unknown",
                "available": False,
                "reason": str(exc),
                "docker": DOCKER_RUN,
            }
            result.update(meta)
            dest = scope.path.parent / "score.json"
            dest.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
            result["wrote"] = str(dest)
            return result
    result = tally(payload)
    result.update(meta)
    result["available"] = True
    result["status"] = "ok"
    dest = scope.path.parent / "score.json"
    dest.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    result["wrote"] = str(dest)
    return result
