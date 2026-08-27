#!/usr/bin/python3
"""Write an authorized CASE report from the case file. No PoC generator."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

from scope import load_scope, repo_root


def _findings(case_dir: Path) -> list[str]:
    folder = case_dir / "findings"
    if not folder.is_dir():
        return []
    out = []
    for path in sorted(folder.glob("*.md")):
        if path.name.startswith("."):
            continue
        out.append(path.read_text(encoding="utf-8").strip())
    return out


def _wall_meta(root: Path) -> dict:
    versions = root / "labs" / "juice-shop" / "versions.json"
    if not versions.is_file():
        return {
            "wall": "unknown",
            "hunted": "unknown",
            "score": "0/N",
            "fill": "unknown",
            "fill_wall": "unknown",
            "last_live_fill": "",
            "last_live_score": "",
            "last_live_wall": "",
            "score_path": "GET /api/Challenges/",
            "bind": "",
            "applies": None,
            "applies_reason": "",
            "coverage": [],
            "docker_off": [],
        }
    import json

    data = json.loads(versions.read_text(encoding="utf-8"))
    hunted = str(data.get("hunted") or "unknown")
    return {
        "wall": str(data.get("wall") or "unknown"),
        "hunted": hunted,
        "score": str(data.get("last_score") or data.get("score") or "0/N"),
            "fill": str(data.get("fill") or "unknown"),
            "fill_wall": str(data.get("fill_wall") or hunted),
            "last_live_fill": str(data.get("last_live_fill") or ""),
            "last_live_score": str(data.get("last_live_score") or ""),
            "last_live_wall": str(data.get("last_live_wall") or ""),
            "score_path": str(data.get("score_path") or "GET /api/Challenges/"),
            "bind": str(data.get("bind") or ""),
            "applies": data.get("applies"),
            "applies_reason": str(data.get("applies_reason") or ""),
            "coverage": list(data.get("skill_pack_does_not_cover") or []),
        "docker_off": list(data.get("docker_off_not_exercised") or []),
    }


def _score_line(case_dir: Path, root: Optional[Path] = None) -> str:
    path = case_dir / "score.json"
    if path.is_file():
        import json

        data = json.loads(path.read_text(encoding="utf-8"))
        return str(data.get("score") or "n/N")
    return _wall_meta(root or repo_root())["score"]


def write_report(slug: str, root: Optional[Path] = None) -> Path:
    scope = load_scope(slug, root)
    case_dir = scope.path.parent
    wall_meta = _wall_meta(root or repo_root())
    score = _score_line(case_dir, root)
    findings = _findings(case_dir)
    when = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    taipei = datetime.now(ZoneInfo("Asia/Taipei")).strftime("%Y-%m-%d")
    finding_block = (
        "\n\n".join(findings)
        if findings
        else "None recorded. Empty findings are valid. This hunt did not auto-pwn the lab."
    )
    coverage = wall_meta["coverage"]
    docker_off = wall_meta["docker_off"]
    coverage_block = ""
    if coverage or docker_off:
        miss = ", ".join(coverage) if coverage else "(none listed)"
        off = ", ".join(docker_off) if docker_off else "(none listed)"
        coverage_block = f"""
## Coverage honesty

13-skill pack does not cover: {miss}.
Docker-off: {off}.
"""
    body = f"""# CASE report: {scope.slug}

- Date (Taipei): {taipei}
- UTC: {when}
- Kind: {scope.kind}
- Lab score: {score}
- Fill: {wall_meta["fill"]} GET /api/Challenges/ on {wall_meta["fill_wall"]}
- Last live fill: {wall_meta["last_live_score"] or "none"} on {wall_meta["last_live_wall"] or "none"}
- Score path: {wall_meta["score_path"]}
- Bind: {wall_meta["bind"] or "see overlay"}
- Authorization: {scope.authorization or "see scope.md"}
- Hunted wall: {wall_meta["hunted"]}
- Current wall: {wall_meta["wall"]}
- Applies: {wall_meta["applies"]} ({wall_meta["applies_reason"] or "see versions.json"})

## Judgment

Authorized CASE against the in-scope lab only. Fill {wall_meta["fill"]} score {score} on {wall_meta["fill_wall"]}. Report path completed without an exploit PoC.

## Scope

In scope:

{os_list(scope.in_scope)}

Out of scope:

{os_list(scope.out_of_scope)}

## Findings

{finding_block}
{coverage_block}
## Close path

Harden the lab overlay (auth, WAF-ish rules, close the extra surface). Next hunt uses `{wall_meta["wall"]}` in `labs/juice-shop` (this loop hunted `{wall_meta["hunted"]}`). Do not attach payloads or reproduction scripts.
"""
    dest = case_dir / "reports" / "draft.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(body, encoding="utf-8")
    return dest


def os_list(items: list[str]) -> str:
    lines = [i for i in items if i and not i.strip().startswith("#")]
    if not lines:
        return "- (none listed)"
    return "\n".join(f"- {i}" for i in lines)
