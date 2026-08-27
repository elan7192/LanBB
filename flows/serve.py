#!/usr/bin/python3
"""LanBB Flow Studio local server.

GET /api/graphs lists files. It never creates a graph.
POST /api/graphs with an empty catalog (or upsert_template) writes the
documented CASE template. PUT writes a named graph.

Local only. No production deploy.
"""

from __future__ import annotations

import json
import os
import re
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

ROOT = Path(os.environ.get("LANBB_FLOWS_ROOT", Path(__file__).resolve().parent))
GRAPHS = ROOT / "graphs"
TEMPLATES = ROOT / "templates"
STUDIO = ROOT / "studio"
REPO_ROOT = Path(os.environ.get("LANBB_REPO_ROOT", ROOT.parent))
DEFAULT_ID = "case-bounty"
HOST = os.environ.get("LANBB_FLOW_HOST", "127.0.0.1")
PORT = int(os.environ.get("LANBB_FLOW_PORT", "8765"))

BANNED_RE = re.compile(
    r"\b(exploit|scan|payload|attack|weaponized)s?\b", re.IGNORECASE
)
SAFE_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,80}$")


def _json_bytes(payload: Any, status: int = 200) -> Tuple[int, bytes, str]:
    body = json.dumps(payload, indent=2).encode("utf-8")
    return status, body, "application/json; charset=utf-8"


def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def list_graphs() -> List[Dict[str, Any]]:
    """Return catalog. Do not create files or directories."""
    if not GRAPHS.is_dir():
        return []
    out: List[Dict[str, Any]] = []
    for path in sorted(GRAPHS.glob("*.json")):
        data = _read_json(path)
        if not data:
            continue
        meta = data.get("metadata") or {}
        gid = str(data.get("id") or path.stem)
        lab = meta.get("lab") if isinstance(meta.get("lab"), dict) else {}
        out.append(
            {
                "id": gid,
                "name": str(data.get("name") or gid),
                "file": path.name,
                "default": bool(meta.get("default")),
                "kind": meta.get("kind"),
                "layout": meta.get("layout"),
                "last_score": lab.get("last_score") or meta.get("score"),
                "score": meta.get("score") or lab.get("last_score"),
                "wall": lab.get("wall"),
                "hunted": lab.get("hunted"),
                "fill": lab.get("fill"),
                "fill_wall": lab.get("fill_wall"),
                "fill_reason": lab.get("fill_reason"),
                "next_hunt": lab.get("next_hunt") or lab.get("wall"),
                "coding_challenges": lab.get("coding_challenges"),
                "docker_disabled_env": lab.get("docker_disabled_env"),
            }
        )
    return out


def graph_path(graph_id: str) -> Optional[Path]:
    if not SAFE_ID.match(graph_id):
        return None
    return GRAPHS / f"{graph_id}.json"


def forbidden_tokens(graph: Dict[str, Any]) -> List[str]:
    """Scan node and edge fields only. Policy docs may name forbidden kinds."""
    parts: List[str] = []
    for node in graph.get("nodes") or []:
        if not isinstance(node, dict):
            continue
        cfg = node.get("config")
        if isinstance(cfg, dict):
            # Allowlist may name catalogue skills (e.g. prompt-injection-attacks).
            # Forbidden kinds are node type/label, not the 13-skill pick list.
            cfg_scan = {k: v for k, v in cfg.items() if k != "allowlist"}
        else:
            cfg_scan = cfg
        parts.append(
            json.dumps(
                {
                    "id": node.get("id"),
                    "type": node.get("type"),
                    "label": node.get("label"),
                    "description": node.get("description"),
                    "category": node.get("category"),
                    "config": cfg_scan,
                }
            )
        )
    for edge in graph.get("edges") or []:
        if isinstance(edge, dict):
            parts.append(json.dumps({"id": edge.get("id"), "label": edge.get("label")}))
    blob = "\n".join(parts)
    return sorted({m.group(1).lower() for m in BANNED_RE.finditer(blob)})


def _fill_reason(wall: Dict[str, Any]) -> str:
    fill = wall.get("fill")
    if fill == "live":
        return "Fill live n/N from GET /api/Challenges/ on hunted wall; wall is the next overlay"
    if fill in {"unavailable", "unknown"}:
        return (
            "Fill unavailable: GET /api/Challenges/ did not arrive; "
            "0/N is honest; wall is the next overlay"
        )
    return "live lab not scored; last_score is the hunt result; wall is the next overlay"


def case_score(program: str) -> Tuple[int, Dict[str, Any]]:
    """Fail-closed lab score. Missing programs/<slug>/scope.md is 400."""
    slug = (program or "").strip().lower()
    if not SAFE_ID.match(slug):
        return 400, {"error": "invalid program", "fail_closed": True}
    scope = REPO_ROOT / "programs" / slug / "scope.md"
    if not scope.is_file():
        return 400, {
            "error": "missing program scope file",
            "fail_closed": True,
            "path": str(scope),
        }
    saved = REPO_ROOT / "programs" / slug / "score.json"
    versions = REPO_ROOT / "labs" / "juice-shop" / "versions.json"
    wall = _read_json(versions) if versions.is_file() else {}
    if saved.is_file():
        data = _read_json(saved) or {}
        data["fail_closed"] = False
        if "available" not in data:
            data["available"] = data.get("status") == "ok"
        data["last_score"] = data.get("score") or data.get("last_score") or (
            wall or {}
        ).get("last_score")
        if wall:
            # Current wall is versions.json; hunted is the overlay this loop scored.
            data["wall"] = wall.get("wall") or data.get("wall")
            data["hunted"] = wall.get("hunted") or data.get("hunted")
            data["fill"] = wall.get("fill") or data.get("fill")
            data["fill_wall"] = wall.get("fill_wall") or data.get("fill_wall")
            data["fill_reason"] = wall.get("fill_reason") or _fill_reason(wall)
            data["next_hunt"] = wall.get("wall") or data.get("next_hunt")
            data["coding_challenges"] = wall.get("coding_challenges") or data.get(
                "coding_challenges"
            )
            data["docker_disabled_env"] = wall.get("docker_disabled_env") or data.get(
                "docker_disabled_env"
            )
            data["last_score"] = wall.get("last_score") or data.get("last_score")
            data["score"] = data.get("last_score") or data.get("score")
            data["n"] = wall.get("n") if wall.get("n") is not None else data.get("n")
            data["N"] = wall.get("N") or wall.get("challenges") or data.get("N")
            data["reason"] = data["fill_reason"]
            if not data.get("available"):
                data["docker"] = (
                    "docker compose -f labs/juice-shop/overlays/"
                    f"{wall.get('wall')}/docker-compose.yml up"
                )
        return 200, data
    last = (wall or {}).get("last_score") or (wall or {}).get("score")
    return 200, {
        "program": slug,
        "available": False,
        "fail_closed": False,
        "score": last,
        "last_score": last,
        "n": (wall or {}).get("n"),
        "N": (wall or {}).get("N") or (wall or {}).get("challenges"),
        "wall": (wall or {}).get("wall"),
        "hunted": (wall or {}).get("hunted"),
        "fill": (wall or {}).get("fill"),
        "fill_wall": (wall or {}).get("fill_wall"),
        "fill_reason": (wall or {}).get("fill_reason") or _fill_reason(wall or {}),
        "next_hunt": (wall or {}).get("wall"),
        "coding_challenges": (wall or {}).get("coding_challenges"),
        "docker_disabled_env": (wall or {}).get("docker_disabled_env"),
        "reason": (wall or {}).get("fill_reason") or _fill_reason(wall or {}),
    }


def load_template() -> Dict[str, Any]:
    path = TEMPLATES / f"{DEFAULT_ID}.json"
    data = _read_json(path)
    if not data:
        raise FileNotFoundError(f"missing documented template: {path}")
    return data


def upsert_template() -> Dict[str, Any]:
    graph = load_template()
    GRAPHS.mkdir(parents=True, exist_ok=True)
    dest = GRAPHS / f"{DEFAULT_ID}.json"
    dest.write_text(json.dumps(graph, indent=2) + "\n", encoding="utf-8")
    return graph


def save_graph(graph_id: str, graph: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    path = graph_path(graph_id)
    if path is None:
        return None, "invalid graph id"
    banned = forbidden_tokens(graph)
    if banned:
        return None, "forbidden node kinds: " + ", ".join(banned)
    graph = dict(graph)
    graph["id"] = graph_id
    GRAPHS.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(graph, indent=2) + "\n", encoding="utf-8")
    return graph, None


class FlowHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _read_body(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        if not raw:
            return {}
        try:
            data = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return {"_error": "invalid json"}
        return data if isinstance(data, dict) else {"_error": "json object required"}

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        if path in ("/", "/studio", "/studio/"):
            loc = b"/studio/index.html"
            self.send_response(302)
            self.send_header("Location", "/studio/index.html")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if path == "/api/case/score":
            qs = parse_qs(parsed.query)
            program = (qs.get("program") or ["juice-shop"])[0]
            status, payload = case_score(program)
            self._send(*_json_bytes(payload, status))
            return
        if path == "/api/graphs":
            # GET must not seed. Empty catalog is a valid response.
            status, body, ctype = _json_bytes({"graphs": list_graphs()})
            self._send(status, body, ctype)
            return
        if path.startswith("/api/graphs/"):
            graph_id = path[len("/api/graphs/") :].strip("/")
            dest = graph_path(graph_id)
            if dest is None:
                status, body, ctype = _json_bytes({"error": "invalid graph id"}, 400)
                self._send(status, body, ctype)
                return
            data = _read_json(dest) if dest.is_file() else None
            if data is None:
                status, body, ctype = _json_bytes({"error": "not found"}, 404)
                self._send(status, body, ctype)
                return
            status, body, ctype = _json_bytes(data)
            self._send(status, body, ctype)
            return
        super().do_GET()

    def do_HEAD(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/"):
            self.do_GET()
            return
        super().do_HEAD()

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path != "/api/graphs":
            self._send(*_json_bytes({"error": "not found"}, 404))
            return
        body = self._read_body()
        if body.get("_error"):
            self._send(*_json_bytes({"error": body["_error"]}, 400))
            return
        existing = list_graphs()
        upsert = bool(body.get("upsert_template")) or not existing
        if upsert:
            try:
                graph = upsert_template()
            except FileNotFoundError as exc:
                self._send(*_json_bytes({"error": str(exc)}, 500))
                return
            payload = {
                "ok": True,
                "upserted": True,
                "id": graph.get("id", DEFAULT_ID),
                "graph": graph,
                "graphs": list_graphs(),
            }
            self._send(*_json_bytes(payload, 201 if not existing else 200))
            return
        graph = body.get("graph") if isinstance(body.get("graph"), dict) else body
        graph_id = str(body.get("id") or graph.get("id") or "").strip()
        if not graph_id:
            self._send(*_json_bytes({"error": "id required"}, 400))
            return
        saved, err = save_graph(graph_id, graph)
        if err:
            self._send(*_json_bytes({"error": err}, 400))
            return
        self._send(*_json_bytes({"ok": True, "id": graph_id, "graph": saved}, 201))

    def do_PUT(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if not parsed.path.startswith("/api/graphs/"):
            self._send(*_json_bytes({"error": "not found"}, 404))
            return
        graph_id = parsed.path[len("/api/graphs/") :].strip("/")
        body = self._read_body()
        if body.get("_error"):
            self._send(*_json_bytes({"error": body["_error"]}, 400))
            return
        graph = body.get("graph") if isinstance(body.get("graph"), dict) else body
        saved, err = save_graph(graph_id, graph)
        if err:
            self._send(*_json_bytes({"error": err}, 400))
            return
        self._send(*_json_bytes({"ok": True, "id": graph_id, "graph": saved}))


def main() -> None:
    if not STUDIO.joinpath("index.html").is_file():
        sys.stderr.write(f"missing studio page: {STUDIO / 'index.html'}\n")
        sys.exit(1)
    httpd = ThreadingHTTPServer((HOST, PORT), FlowHandler)
    sys.stderr.write(
        f"LanBB Flow Studio  http://{HOST}:{PORT}/\n"
        "GET /api/graphs does not seed. Empty list POST upserts the CASE template.\n"
        "Local only. No production deploy.\n"
    )
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        sys.stderr.write("\nstop\n")
        httpd.server_close()


if __name__ == "__main__":
    main()
