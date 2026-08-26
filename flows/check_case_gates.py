#!/usr/bin/python3
"""CASE DAG pass/fail gates for leftover grok-bot-team cards (15 nodes / 31 edges).

A graph fails this slice if any of:
  coordinator_node, wiki_ingest_true, route_skips_lead,
  merge_now, semantica_agi, specialist_asks_user.

CASE workflow only. No exploit, scan, or payload checks here.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, Iterable, List, Tuple

RULES = (
    "coordinator_node",
    "wiki_ingest_true",
    "route_skips_lead",
    "merge_now",
    "semantica_agi",
    "specialist_asks_user",
)

SPECIALIST_LANES = {
    "wiki",
    "arxiv",
    "search",
    "lanbb",
    "cursor",
    "design huddle",
    "design",
    "specialist",
}

COORD_RE = re.compile(r"\bcoordinators?\b", re.I)
MERGE_NOW_RE = re.compile(r"merge[\s_-]*now", re.I)
SEMANTICA_AGI_RE = re.compile(r"semantica-agi", re.I)
ASK_USER_RE = re.compile(
    r"\basks? the user\b|\bask user\b|\bspecialist asks user\b",
    re.I,
)
ARROW_RE = re.compile(r"\s*(?:→|->|=>)\s*")

Violation = Dict[str, str]


def check_graph(graph: Dict[str, Any]) -> List[Violation]:
    """Return violations. Empty list means the graph passes every gate."""
    nodes = [n for n in (graph.get("nodes") or []) if isinstance(n, dict)]
    edges = [e for e in (graph.get("edges") or []) if isinstance(e, dict)]
    by_id = {str(n.get("id")): n for n in nodes}
    found: List[Violation] = []
    found.extend(_coordinator_nodes(nodes))
    found.extend(_wiki_ingest_true(graph, nodes))
    found.extend(_route_skips_lead(nodes, edges, by_id))
    found.extend(_merge_now(graph, nodes, edges))
    found.extend(_semantica_agi(graph))
    found.extend(_specialist_asks_user(nodes, edges, by_id))
    return found


def passes(graph: Dict[str, Any]) -> bool:
    return not check_graph(graph)


def _blob(parts: Iterable[Any]) -> str:
    return " ".join("" if p is None else str(p) for p in parts)


def _lane(node: Dict[str, Any]) -> str:
    cfg = node.get("config") if isinstance(node.get("config"), dict) else {}
    props = node.get("properties") if isinstance(node.get("properties"), dict) else {}
    raw = cfg.get("lane") or props.get("lane") or node.get("category") or ""
    return str(raw).strip().lower()


def _is_lead(node: Dict[str, Any]) -> bool:
    text = _blob(
        [node.get("id"), node.get("label"), node.get("type"), _lane(node)]
    ).lower()
    return "lead" in text


def _is_intake(node: Dict[str, Any]) -> bool:
    kind = str(node.get("type") or "").lower()
    ident = str(node.get("id") or "").lower()
    lane = _lane(node)
    return kind in {"trigger", "intake"} or ident.startswith("intake:") or lane == "intake"


def _is_user(node: Dict[str, Any]) -> bool:
    text = _blob([node.get("id"), node.get("label"), _lane(node)]).lower()
    return any(tok in text for tok in ("user", "anyone", "requester"))


def _is_specialist(node: Dict[str, Any]) -> bool:
    if _is_lead(node):
        return False
    lane = _lane(node)
    if lane in SPECIALIST_LANES:
        return True
    ident = str(node.get("id") or "").lower()
    label = str(node.get("label") or "").lower()
    if ident.startswith("agent:") and "lead" not in ident:
        return True
    return any(lane_name == label or lane_name in ident for lane_name in SPECIALIST_LANES)


def _walk_truthy_ingest(obj: Any, path: str, hits: List[str]) -> None:
    if isinstance(obj, dict):
        for key, val in obj.items():
            here = f"{path}.{key}" if path else str(key)
            if str(key).lower() in {"ingest", "wiki_ingest"} and val is True:
                hits.append(here)
            else:
                _walk_truthy_ingest(val, here, hits)
    elif isinstance(obj, list):
        for i, val in enumerate(obj):
            _walk_truthy_ingest(val, f"{path}[{i}]", hits)


def _coordinator_nodes(nodes: List[Dict[str, Any]]) -> List[Violation]:
    out: List[Violation] = []
    for node in nodes:
        text = _blob(
            [
                node.get("id"),
                node.get("type"),
                node.get("label"),
                node.get("category"),
                (node.get("config") or {}).get("role") if isinstance(node.get("config"), dict) else "",
                (node.get("properties") or {}).get("role")
                if isinstance(node.get("properties"), dict)
                else "",
            ]
        )
        if COORD_RE.search(text):
            out.append(
                {
                    "rule": "coordinator_node",
                    "where": str(node.get("id") or node.get("label") or "node"),
                }
            )
    return out


def _wiki_ingest_true(graph: Dict[str, Any], nodes: List[Dict[str, Any]]) -> List[Violation]:
    hits: List[str] = []
    _walk_truthy_ingest(graph, "", hits)
    return [{"rule": "wiki_ingest_true", "where": path} for path in hits]


def _route_text_skips_lead(text: str) -> bool:
    if not ARROW_RE.search(text):
        return False
    hops = [h.strip().lower() for h in ARROW_RE.split(text) if h.strip()]
    if len(hops) < 2:
        return False
    mentions_specialist = any(
        hop in SPECIALIST_LANES or hop in {"anyone", "user", "specialist"} for hop in hops
    )
    if not mentions_specialist:
        return False
    return "lead" not in hops


def _route_skips_lead(
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    by_id: Dict[str, Dict[str, Any]],
) -> List[Violation]:
    out: List[Violation] = []
    for node in nodes:
        for holder in (node, node.get("config"), node.get("properties")):
            if not isinstance(holder, dict):
                continue
            route = holder.get("route")
            if isinstance(route, str) and _route_text_skips_lead(route):
                out.append(
                    {
                        "rule": "route_skips_lead",
                        "where": f"{node.get('id')}.route",
                    }
                )
    for edge in edges:
        src = by_id.get(str(edge.get("source")))
        dst = by_id.get(str(edge.get("target")))
        if not src or not dst:
            continue
        if _is_lead(src) or _is_lead(dst):
            continue
        if not _is_specialist(dst):
            continue
        skipped = False
        if _is_intake(src) or _is_user(src):
            skipped = True
        elif _is_specialist(src) and _lane(src) != _lane(dst):
            skipped = True
        if skipped:
            out.append(
                {
                    "rule": "route_skips_lead",
                    "where": str(edge.get("id") or f"{src.get('id')}->{dst.get('id')}"),
                }
            )
        label = str(edge.get("label") or "")
        if _route_text_skips_lead(label):
            out.append({"rule": "route_skips_lead", "where": str(edge.get("id") or label)})
    return out


def _merge_now(
    graph: Dict[str, Any],
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
) -> List[Violation]:
    out: List[Violation] = []
    for node in nodes:
        text = json.dumps({"id": node.get("id"), "type": node.get("type"), "label": node.get("label"), "config": node.get("config"), "properties": node.get("properties")})
        if MERGE_NOW_RE.search(text):
            out.append({"rule": "merge_now", "where": str(node.get("id") or node.get("label"))})
    for edge in edges:
        text = json.dumps({"id": edge.get("id"), "label": edge.get("label"), "type": edge.get("type")})
        if MERGE_NOW_RE.search(text):
            out.append({"rule": "merge_now", "where": str(edge.get("id") or edge.get("label"))})
    meta = graph.get("metadata") if isinstance(graph.get("metadata"), dict) else {}
    if MERGE_NOW_RE.search(json.dumps(meta)):
        out.append({"rule": "merge_now", "where": "metadata"})
    return out


def _semantica_agi(graph: Dict[str, Any]) -> List[Violation]:
    blob = json.dumps(graph)
    if SEMANTICA_AGI_RE.search(blob):
        return [{"rule": "semantica_agi", "where": "graph"}]
    return []


def _node_asks_user(node: Dict[str, Any]) -> bool:
    cfg = node.get("config") if isinstance(node.get("config"), dict) else {}
    props = node.get("properties") if isinstance(node.get("properties"), dict) else {}
    for holder in (cfg, props, node):
        if holder.get("ask_user") is True or holder.get("asks_user") is True:
            return True
        if holder.get("never_ask_user") is False:
            return True
    text = _blob([node.get("label"), node.get("description"), cfg.get("badge"), props.get("duty")])
    return bool(ASK_USER_RE.search(text))


def _specialist_asks_user(
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    by_id: Dict[str, Dict[str, Any]],
) -> List[Violation]:
    out: List[Violation] = []
    for node in nodes:
        if _is_lead(node) or _is_intake(node):
            continue
        if not (_is_specialist(node) or _lane(node) in SPECIALIST_LANES):
            continue
        if _node_asks_user(node):
            out.append(
                {
                    "rule": "specialist_asks_user",
                    "where": str(node.get("id") or node.get("label")),
                }
            )
    for edge in edges:
        src = by_id.get(str(edge.get("source")))
        dst = by_id.get(str(edge.get("target")))
        if not src or not dst:
            continue
        if _is_lead(src) or not _is_specialist(src):
            continue
        if _is_user(dst) or ASK_USER_RE.search(str(edge.get("label") or "")):
            out.append(
                {
                    "rule": "specialist_asks_user",
                    "where": str(edge.get("id") or f"{src.get('id')}->{dst.get('id')}"),
                }
            )
    return out


def load_json(path: Any) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"graph must be an object: {path}")
    return data


def summarize(violations: List[Violation]) -> Tuple[bool, List[str]]:
    rules = sorted({v["rule"] for v in violations})
    return (not violations, rules)
