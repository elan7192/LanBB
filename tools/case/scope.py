#!/usr/bin/python3
"""Fail-closed program scope parser for authorized LanBB CASE work.

Refuse any target that has no programs/<slug>/scope.md.
Refuse out-of-scope domains. Refuse adult/porn program slugs.
Lab-only scoring never uses live bounty programs.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple
from urllib.parse import urlparse

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
ADULT_RE = re.compile(
    r"(?:^|[-_])(porn|pornhub|onlyfans|xxx|nsfw|adult(?:-?film|-?video|-?cam)?|xnxx|xvideos)(?:[-_]|$)",
    re.I,
)
HEADING_RE = re.compile(r"^#{1,6}\s+(.*)$")
LIST_RE = re.compile(r"^\s*[-*+]\s+(.+)$")
FRONT_KV_RE = re.compile(r"^([A-Za-z][\w-]*)\s*:\s*(.+)$")

IN_SCOPE_HEADINGS = {
    "in scope",
    "in-scope",
    "inscope",
    "scope",
    "assets",
    "in-scope assets",
}
OOS_HEADINGS = {
    "out of scope",
    "out-of-scope",
    "oos",
    "not in scope",
    "excluded",
}

LOOPBACK_HOSTS = {"localhost", "127.0.0.1", "::1", "0.0.0.0"}


class ScopeError(Exception):
    """Fail-closed scope refusal."""


@dataclass
class ProgramScope:
    slug: str
    path: Path
    kind: str = "unknown"
    authorization: str = ""
    in_scope: List[str] = field(default_factory=list)
    out_of_scope: List[str] = field(default_factory=list)
    raw: str = ""

    @property
    def is_lab(self) -> bool:
        return self.kind.lower() in {"lab", "hypothetical", "local"}

    def in_scope_hosts(self) -> List[str]:
        hosts = []
        seen = set()
        for item in self.in_scope:
            host = normalize_host(item)
            if host and host not in seen:
                seen.add(host)
                hosts.append(host)
        return hosts


def repo_root(start: Optional[Path] = None) -> Path:
    here = (start or Path(__file__)).resolve()
    for parent in [here] + list(here.parents):
        if (parent / "flows" / "graphs" / "case-bounty.json").is_file():
            return parent
        if (parent / ".gitmodules").is_file() and (parent / "README.md").is_file():
            return parent
    return Path(__file__).resolve().parents[2]


def programs_dir(root: Optional[Path] = None) -> Path:
    return (root or repo_root()) / "programs"


def program_dir(slug: str, root: Optional[Path] = None) -> Path:
    return programs_dir(root) / slug


def scope_path(slug: str, root: Optional[Path] = None) -> Path:
    return program_dir(slug, root) / "scope.md"


def validate_slug(slug: str) -> str:
    value = (slug or "").strip().lower()
    if not SLUG_RE.match(value):
        raise ScopeError(
            f"invalid program slug {slug!r}: use lowercase kebab-case "
            "(letters, digits, hyphens)"
        )
    if ADULT_RE.search(value):
        raise ScopeError(
            f"refused program {value!r}: adult/porn programs are noise and out of LanBB"
        )
    return value


def normalize_host(value: str) -> str:
    text = (value or "").strip()
    if not text or text.startswith("#"):
        return ""
    if any(ord(char) < 0x20 or ord(char) == 0x7F for char in text):
        raise ScopeError(
            f"fail-closed: control characters in target {value!r} are rejected"
        )
    text = text.split()[0].strip(" `.,;\"'")
    if text.startswith("<") and text.endswith(">"):
        text = text[1:-1]
    if "://" not in text and text.startswith("//"):
        text = "http:" + text
    if "://" in text:
        parsed = urlparse(text)
        if parsed.username or parsed.password:
            raise ScopeError(
                f"fail-closed: userinfo in target {value!r} is rejected"
            )
        host = parsed.hostname or ""
        port = parsed.port
    else:
        host = text
        port = None
        if host.count(":") == 1 and not host.startswith("["):
            name, maybe_port = host.rsplit(":", 1)
            if maybe_port.isdigit():
                host, port = name, int(maybe_port)
        if "/" in host:
            host = host.split("/", 1)[0]
    host = host.strip(".").lower()
    if host.startswith("[") and host.endswith("]"):
        host = host[1:-1]
    if not host:
        return ""
    if port and port not in (80, 443):
        return f"{host}:{port}"
    return host


def _heading_key(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def parse_scope_text(text: str, slug: str, path: Path) -> ProgramScope:
    kind = "unknown"
    authorization = ""
    in_scope: List[str] = []
    oos: List[str] = []
    section = ""
    in_front = False
    front_lines: List[str] = []
    lines = text.splitlines()
    i = 0
    if lines and lines[0].strip() == "---":
        in_front = True
        i = 1
        while i < len(lines):
            if lines[i].strip() == "---":
                i += 1
                break
            front_lines.append(lines[i])
            i += 1
        in_front = False
    for raw in front_lines:
        match = FRONT_KV_RE.match(raw.strip())
        if not match:
            continue
        key, val = match.group(1).lower(), match.group(2).strip().strip("\"'")
        if key in {"kind", "type"}:
            kind = val
        elif key in {"authorization", "auth"}:
            authorization = val
        elif key in {"program", "slug"} and val:
            slug = val
    body_lines = lines[i:]
    for line in body_lines:
        heading = HEADING_RE.match(line)
        if heading:
            section = _heading_key(heading.group(1))
            continue
        item = LIST_RE.match(line)
        if not item:
            continue
        entry = item.group(1).strip()
        if section in IN_SCOPE_HEADINGS:
            in_scope.append(entry)
        elif section in OOS_HEADINGS:
            oos.append(entry)
    return ProgramScope(
        slug=slug,
        path=path,
        kind=kind,
        authorization=authorization,
        in_scope=in_scope,
        out_of_scope=oos,
        raw=text,
    )


def load_scope(slug: str, root: Optional[Path] = None) -> ProgramScope:
    slug = validate_slug(slug)
    path = scope_path(slug, root)
    if not path.is_file():
        raise ScopeError(
            f"fail-closed: no program scope file at {path}. "
            "Refusing target without programs/<slug>/scope.md"
        )
    text = path.read_text(encoding="utf-8")
    scope = parse_scope_text(text, slug, path)
    if not scope.in_scope_hosts() and not any(
        normalize_host(x) for x in scope.in_scope
    ):
        # Allow non-host in-scope notes (URLs already parsed). Empty host list
        # still fail-closes any concrete domain check.
        pass
    return scope


def _host_parts(host: str) -> Tuple[str, Optional[int]]:
    if host.count(":") == 1 and not host.startswith("["):
        name, port = host.rsplit(":", 1)
        if port.isdigit():
            return name, int(port)
    return host, None


def _matches(candidate: str, pattern: str) -> bool:
    cand_host, cand_port = _host_parts(candidate)
    pat_host, pat_port = _host_parts(pattern)
    if cand_host in LOOPBACK_HOSTS and pat_host in LOOPBACK_HOSTS:
        if pat_port is None or cand_port == pat_port:
            return True
        if cand_port is None and pat_port is not None:
            return True
    if cand_host == pat_host:
        if pat_port is None or cand_port == pat_port:
            return True
        return False
    if cand_host.endswith("." + pat_host):
        if pat_port is None or cand_port == pat_port:
            return True
    return False


def classify_target(scope: ProgramScope, target: str) -> str:
    host = normalize_host(target)
    if not host:
        raise ScopeError(f"fail-closed: empty or unparseable target {target!r}")
    oos_hosts = [normalize_host(x) for x in scope.out_of_scope]
    oos_hosts = [h for h in oos_hosts if h]
    for pattern in oos_hosts:
        if _matches(host, pattern):
            return "oos"
    in_hosts = scope.in_scope_hosts()
    for pattern in in_hosts:
        if _matches(host, pattern):
            return "in-scope"
    return "unknown"


def require_in_scope(slug: str, target: str, root: Optional[Path] = None) -> ProgramScope:
    """Fail-closed: missing scope file, unknown, or OOS raises ScopeError."""
    scope = load_scope(slug, root)
    status = classify_target(scope, target)
    if status == "oos":
        raise ScopeError(
            f"fail-closed: {target!r} is out of scope for program {scope.slug}"
        )
    if status != "in-scope":
        raise ScopeError(
            f"fail-closed: {target!r} is not listed in-scope for program {scope.slug}"
        )
    return scope


def require_scope_file(slug: str, root: Optional[Path] = None) -> ProgramScope:
    return load_scope(slug, root)


def is_loopback(target: str) -> bool:
    host, _port = _host_parts(normalize_host(target))
    return host in LOOPBACK_HOSTS


def public_in_scope_domains(scope: ProgramScope) -> List[str]:
    """Apex hosts that are in-scope and not loopback (eligible for optional subfaster)."""
    out = []
    for host in scope.in_scope_hosts():
        name, _port = _host_parts(host)
        if name in LOOPBACK_HOSTS:
            continue
        if name.endswith(".local") or name.endswith(".internal"):
            continue
        out.append(name)
    return out
