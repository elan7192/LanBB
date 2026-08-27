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
IMAGE_DIGEST = (
    "sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e"
)
DOCKER_IMAGE = f"bkimminich/juice-shop@{IMAGE_DIGEST}"
DOCKER_NAME = "lanbb-juice-shop"
# Juice Shop master hacking challenges (not coding /snippets).
HACKING_TOTAL = 116
DOCKER_SOLVABLE = 98
DOCKER_DISABLED_ENV = 18


def load_versions(root: Optional[Path] = None) -> Dict[str, Any]:
    path = (root or repo_root()) / "labs" / "juice-shop" / "versions.json"
    if not path.is_file():
        return {"wall": "v5-hardened", "hunted": "v4-hardened", "last_score": "0/116"}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"wall": "v5-hardened", "hunted": "v4-hardened", "last_score": "0/116"}
    return data if isinstance(data, dict) else {"wall": "v5-hardened"}


def current_wall(root: Optional[Path] = None) -> str:
    wall = str(load_versions(root).get("wall") or "v5-hardened").strip()
    return wall or "v5-hardened"


def compose_file(root: Optional[Path] = None) -> Path:
    root = root or repo_root()
    return root / "labs" / "juice-shop" / "overlays" / current_wall(root) / "docker-compose.yml"


def documented_start(root: Optional[Path] = None) -> str:
    path = compose_file(root)
    return f"docker compose -f {path} up"


# Back-compat name used in older error text; always the current wall, never stock.
DOCKER_RUN = documented_start()


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
            f"Start the current wall: {documented_start()}"
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


def start_lab_docker(root: Optional[Path] = None) -> str:
    """Bring up the current wall overlay. Never falls back to stock v0."""
    root = root or repo_root()
    start = documented_start(root)
    docker = shutil.which("docker")
    if not docker:
        raise ScoreError(
            "docker not installed. Documented start (current wall, not stock):\n"
            f"  {start}\n"
            "Then: python3 tools/case/lanbb.py case score juice-shop"
        )
    compose = compose_file(root)
    if not compose.is_file():
        raise ScoreError(f"missing current wall compose file: {compose}")
    inspect = subprocess.run(
        [docker, "inspect", "-f", "{{.State.Running}}", DOCKER_NAME],
        capture_output=True,
        text=True,
    )
    if inspect.returncode == 0 and inspect.stdout.strip() == "true":
        return "already-running"
    proc = subprocess.run(
        [docker, "compose", "-f", str(compose), "up", "-d"],
        capture_output=True,
        text=True,
        cwd=str(compose.parent),
    )
    if proc.returncode != 0:
        raise ScoreError(
            "docker compose failed:\n"
            f"{proc.stderr or proc.stdout}\n"
            f"Documented start: {start}"
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
    versions = load_versions(root)
    wall = current_wall(root)
    meta = {
        "program": scope.slug,
        "base": base,
        "fail_closed": False,
        "kind": scope.kind,
        "image": DOCKER_IMAGE,
        "wall": wall,
        "hunted": versions.get("hunted") or "",
        "hacking_total_master": HACKING_TOTAL,
        "docker_solvable": DOCKER_SOLVABLE,
        "docker_disabled_env": DOCKER_DISABLED_ENV,
        "continue_code": "GET /rest/continue-code is a token only — do not forge",
        "note": "Authorized CASE tools only. This harness does not auto-pwn.",
        "last_score": versions.get("last_score") or "0/116",
    }
    if payload is None:
        try:
            if start:
                start_lab_docker(root)
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
                "docker": documented_start(root),
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
