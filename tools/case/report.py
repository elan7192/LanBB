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


def _score_line(case_dir: Path) -> str:
    path = case_dir / "score.json"
    if path.is_file():
        import json

        data = json.loads(path.read_text(encoding="utf-8"))
        return str(data.get("score") or "n/N")
    versions = repo_root() / "labs" / "juice-shop" / "versions.json"
    if versions.is_file():
        import json

        data = json.loads(versions.read_text(encoding="utf-8"))
        return str(data.get("last_score") or "0/N")
    return "0/N"


def write_report(slug: str, root: Optional[Path] = None) -> Path:
    scope = load_scope(slug, root)
    case_dir = scope.path.parent
    score = _score_line(case_dir)
    findings = _findings(case_dir)
    when = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    taipei = datetime.now(ZoneInfo("Asia/Taipei")).strftime("%Y-%m-%d")
    finding_block = (
        "\n\n".join(findings)
        if findings
        else "None recorded. Empty findings are valid. This hunt did not auto-pwn the lab."
    )
    body = f"""# CASE report: {scope.slug}

- Date (Taipei): {taipei}
- UTC: {when}
- Kind: {scope.kind}
- Lab score: {score}
- Authorization: {scope.authorization or "see scope.md"}

## Judgment

Authorized CASE against the in-scope lab only. Score {score}. Report path completed without an exploit PoC.

## Scope

In scope:

{os_list(scope.in_scope)}

Out of scope:

{os_list(scope.out_of_scope)}

## Findings

{finding_block}

## Close path

Harden the lab overlay (auth, WAF-ish rules, close the extra surface). Next hunt uses the harder wall in `labs/juice-shop`. Do not attach payloads or reproduction scripts.
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
