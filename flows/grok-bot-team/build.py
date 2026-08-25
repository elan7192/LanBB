#!/usr/bin/env python3
"""Build the LanBB Grok Bot team workflow (n8n-style FlowGraph + case graph).

Reuses the semantica.flow graph schema (FlowNode / FlowEdge / FlowGraph) and
the sites/bug-bounty-flow artifact pattern (flow/graph JSON + PNG + HTML).

Case/graph orchestration only. No exploit, scan, or payload node types.

Run from repo root or this directory:

    python3 flows/grok-bot-team/build.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DIR = Path(__file__).resolve().parent
if str(DIR) not in sys.path:
    sys.path.insert(0, str(DIR))

from flow_models import FlowEdge, FlowGraph, FlowNode

LANES = [
    "lead",
    "wiki",
    "arxiv",
    "search",
    "lanbb",
    "cursor",
    "design huddle",
]

LANE_H = 168.0
COL_W = 250.0
ORIGIN_X = 210.0
ORIGIN_Y = 52.0

LANE_COLOR = {
    "lead": "#2d72d2",
    "wiki": "#9179f2",
    "arxiv": "#d9822b",
    "search": "#32a467",
    "lanbb": "#48aff0",
    "cursor": "#c8763a",
    "design huddle": "#db6bcf",
}

TYPE_COLOR = {
    "trigger": "#32a467",
    "agent": "#2d72d2",
    "merge": "#8fa8c6",
    "decision_gate": "#d9822b",
    "graph_export": "#56d364",
    "policy": "#9179f2",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _pos(col: float, lane: str, dy: float = 0.0) -> Dict[str, float]:
    return {
        "x": ORIGIN_X + col * COL_W,
        "y": ORIGIN_Y + LANES.index(lane) * LANE_H + dy,
    }


def _node(
    nid: str,
    ntype: str,
    label: str,
    lane: str,
    col: float,
    *,
    dy: float = 0.0,
    config: Optional[Dict[str, Any]] = None,
    description: str = "",
    badge: str = "",
) -> FlowNode:
    cfg = dict(config or {})
    cfg.setdefault("lane", lane)
    if badge:
        cfg.setdefault("badge", badge)
    return FlowNode(
        id=nid,
        type=ntype,
        label=label,
        config=cfg,
        position=_pos(col, lane, dy),
        category=lane,
        description=description,
    )


def _edge(source: str, target: str, label: str = "") -> FlowEdge:
    return FlowEdge(
        id=f"e_{source}_{target}_{label.replace(' ', '_')}"[:80] if label else f"e_{source}_{target}",
        source=source,
        target=target,
        label=label,
    )


def build_flow() -> FlowGraph:
    """n8n-style DAG of the Grok Bot team. Split lead into intake + approvals to stay acyclic."""
    nodes = [
        # ── lead ──────────────────────────────────────────────────────────
        _node(
            "n_user_request",
            "trigger",
            "New user request",
            "lead",
            0,
            description="anyone/user → lead. All new requests enter the front door.",
            badge="ANYONE → LEAD",
        ),
        _node(
            "n_lead_intake",
            "agent",
            "lead · front door",
            "lead",
            2,
            description="Front door. All new requests + routing. Approvals (merge/push/pay/auth) are a later lead node.",
            badge="FRONT DOOR",
            config={"role": "lead", "owns": ["intake", "routing", "approvals"]},
        ),
        _node(
            "n_route",
            "merge",
            "Route to specialist",
            "lead",
            3,
            description="lead → specialist. New user requests are handed to the matching lane.",
        ),
        _node(
            "n_lead_approve",
            "decision_gate",
            "lead · approvals",
            "lead",
            5,
            description="specialist → lead. merge/push/pay/auth. Never ask the user to click.",
            badge="NEVER ASK USER",
            config={"field": "ready", "fail_closed": True, "actions": ["merge", "push", "pay", "auth"]},
        ),
        _node(
            "n_export",
            "graph_export",
            "Export team graph",
            "lead",
            6,
            description="Export the LanBB team case graph (semantica_case_graph).",
            config={"format": "semantica_case_graph"},
        ),
        # ── wiki ──────────────────────────────────────────────────────────
        _node(
            "n_wiki_gate",
            "decision_gate",
            "Approve wiki ingest",
            "wiki",
            3,
            description="Social finds: search → lead → wiki after approve. Gate is CLOSED — wiki is FULL FREEZE.",
            badge="CLOSED",
            config={"field": "wiki_thawed", "fail_closed": True, "wiki_thawed": False},
        ),
        _node(
            "n_wiki",
            "agent",
            "wiki",
            "wiki",
            4,
            description="second-brain vault elan7192/second-brain. Currently FULL FREEZE (no ingest/push).",
            badge="FULL FREEZE",
            config={
                "role": "wiki",
                "vault": "elan7192/second-brain",
                "status": "FULL_FREEZE",
                "ingest": False,
                "push": False,
            },
        ),
        # ── arxiv ─────────────────────────────────────────────────────────
        _node(
            "n_arxiv",
            "agent",
            "arxiv",
            "arxiv",
            4,
            description="Paper corpus. Harvest dead, digests paused for quota. Paper hits: search → lead → arxiv.",
            badge="PAUSED",
            config={
                "role": "arxiv",
                "harvest": "dead",
                "digests": "paused_quota",
            },
        ),
        # ── search ────────────────────────────────────────────────────────
        _node(
            "n_search_scout",
            "agent",
            "search · scout",
            "search",
            0,
            description="Only scout. Google/Reddit/X/FB/IG/Threads. NO scheduled scout unless lan E asks.",
            badge="ON-DEMAND",
            config={
                "role": "search",
                "mode": "scout",
                "sources": ["Google", "Reddit", "X", "FB", "IG", "Threads"],
                "scheduled_scout": False,
            },
        ),
        _node(
            "n_paper_hit",
            "trigger",
            "Paper hit",
            "search",
            1,
            dy=-36,
            description="Paper hits: search → lead → arxiv.",
            badge="SEARCH → LEAD → ARXIV",
        ),
        _node(
            "n_social_find",
            "trigger",
            "Social find",
            "search",
            1,
            dy=36,
            description="Social finds: search → lead → wiki after approve.",
            badge="SEARCH → LEAD → WIKI",
        ),
        _node(
            "n_search_ondemand",
            "agent",
            "search · on-demand",
            "search",
            4,
            description="Specialist work only when lan E asks via lead. Not a scheduled scout.",
            badge="NO SCHEDULE",
            config={"role": "search", "mode": "on_demand", "scheduled_scout": False},
        ),
        # ── lanbb ─────────────────────────────────────────────────────────
        _node(
            "n_lanbb",
            "agent",
            "lanbb",
            "lanbb",
            4,
            description="LanBB product.",
            badge="PRODUCT",
            config={"role": "lanbb", "product": "LanBB"},
        ),
        # ── cursor ────────────────────────────────────────────────────────
        _node(
            "n_cursor",
            "agent",
            "cursor",
            "cursor",
            4,
            description="CloudAgents on owned repos.",
            badge="OWNED REPOS",
            config={"role": "cursor", "scope": "owned_repos_only"},
        ),
        # ── design huddle ─────────────────────────────────────────────────
        _node(
            "n_design",
            "agent",
            "design huddle",
            "design huddle",
            4,
            description="figma, motion, experiments, devbot.",
            badge="CREATIVE",
            config={
                "role": "design huddle",
                "surfaces": ["figma", "motion", "experiments", "devbot"],
            },
        ),
    ]

    specialists = [
        "n_wiki",
        "n_arxiv",
        "n_search_ondemand",
        "n_lanbb",
        "n_cursor",
        "n_design",
    ]

    edges = [
        # New user requests: anyone/user → lead → specialist
        _edge("n_user_request", "n_lead_intake", "new request"),
        _edge("n_lead_intake", "n_route", "route"),
        # Paper hits: search → lead → arxiv
        _edge("n_search_scout", "n_paper_hit", "scout"),
        _edge("n_paper_hit", "n_lead_intake", "paper hits"),
        _edge("n_lead_intake", "n_arxiv", "paper hits"),
        # Social finds: search → lead → wiki after approve
        _edge("n_search_scout", "n_social_find", "scout"),
        _edge("n_social_find", "n_lead_intake", "social finds"),
        _edge("n_lead_intake", "n_wiki_gate", "social finds"),
        _edge("n_wiki_gate", "n_wiki", "after approve"),
        # User-request fan-out to specialists (wiki still hits the freeze gate)
        _edge("n_route", "n_wiki_gate", "specialist"),
        _edge("n_route", "n_arxiv", "specialist"),
        _edge("n_route", "n_search_ondemand", "specialist"),
        _edge("n_route", "n_lanbb", "specialist"),
        _edge("n_route", "n_cursor", "specialist"),
        _edge("n_route", "n_design", "specialist"),
        # Approvals: specialist → lead (never ask user to click)
        *[ _edge(sid, "n_lead_approve", "approval") for sid in specialists ],
        _edge("n_lead_approve", "n_export", "signed off"),
    ]

    return FlowGraph(
        id="flow_grok_bot_team",
        name="LanBB Grok Bot team",
        description=(
            "LanBB Grok Bot team routing, n8n-style. lead is the front door and the "
            "only approval hop (merge/push/pay/auth) — specialists never ask the user "
            "to click. wiki is FULL FREEZE. arxiv harvest is dead and digests are "
            "paused for quota. search scouts only on demand (Google/Reddit/X/FB/IG/Threads)."
        ),
        nodes=nodes,
        edges=edges,
        metadata={
            "template": "grok_bot_team",
            "product": "LanBB",
            "domain": "team_routing",
            "style": "n8n_graph",
            "lanes": LANES,
            "wiki_status": "FULL_FREEZE",
            "wiki_vault": "elan7192/second-brain",
            "arxiv_harvest": "dead",
            "arxiv_digests": "paused_quota",
            "search_scheduled_scout": False,
            "search_sources": ["Google", "Reddit", "X", "FB", "IG", "Threads"],
            "approval_actions": ["merge", "push", "pay", "auth"],
            "approval_never_asks_user": True,
            "authorized_only": True,
        },
        version="1.0.0",
    )


def build_case_graph(flow: FlowGraph) -> Dict[str, Any]:
    """Case graph of the team (semantica_case_graph format). Not an attack surface."""
    agents = {
        "lead": {
            "label": "lead",
            "duty": "front door. All new requests + approvals (merge/push/pay/auth).",
            "status": "active",
        },
        "wiki": {
            "label": "wiki",
            "duty": "second-brain vault elan7192/second-brain.",
            "status": "FULL_FREEZE",
            "ingest": False,
            "push": False,
            "vault": "elan7192/second-brain",
        },
        "arxiv": {
            "label": "arxiv",
            "duty": "paper corpus.",
            "status": "paused",
            "harvest": "dead",
            "digests": "paused_quota",
        },
        "search": {
            "label": "search",
            "duty": "only scout. Google/Reddit/X/FB/IG/Threads.",
            "status": "on_demand",
            "scheduled_scout": False,
            "sources": ["Google", "Reddit", "X", "FB", "IG", "Threads"],
        },
        "lanbb": {
            "label": "lanbb",
            "duty": "LanBB product.",
            "status": "active",
            "product": "LanBB",
        },
        "cursor": {
            "label": "cursor",
            "duty": "CloudAgents on owned repos.",
            "status": "active",
            "scope": "owned_repos_only",
        },
        "design huddle": {
            "label": "design huddle",
            "duty": "figma, motion, experiments, devbot.",
            "status": "active",
            "surfaces": ["figma", "motion", "experiments", "devbot"],
        },
    }

    nodes: List[Dict[str, Any]] = [
        {
            "id": "team:grok-bot",
            "type": "Team",
            "label": "LanBB Grok Bot team",
            "properties": {
                "product": "LanBB",
                "lanes": LANES,
                "front_door": "lead",
            },
        },
        {
            "id": "intake:user-request",
            "type": "Intake",
            "label": "New user request",
            "properties": {"from": "anyone/user", "route": "lead → specialist"},
        },
        {
            "id": "intake:paper-hit",
            "type": "Intake",
            "label": "Paper hit",
            "properties": {"from": "search", "route": "search → lead → arxiv"},
        },
        {
            "id": "intake:social-find",
            "type": "Intake",
            "label": "Social find",
            "properties": {"from": "search", "route": "search → lead → wiki after approve"},
        },
        {
            "id": "approval:lead",
            "type": "Approval",
            "label": "lead approvals",
            "properties": {
                "actions": ["merge", "push", "pay", "auth"],
                "never_ask_user": True,
            },
        },
        {
            "id": "policy:wiki-freeze",
            "type": "Policy",
            "label": "wiki FULL FREEZE",
            "properties": {"ingest": False, "push": False, "vault": "elan7192/second-brain"},
        },
        {
            "id": "policy:arxiv-pause",
            "type": "Policy",
            "label": "arxiv paused",
            "properties": {"harvest": "dead", "digests": "paused_quota"},
        },
        {
            "id": "policy:search-on-demand",
            "type": "Policy",
            "label": "search on-demand only",
            "properties": {
                "scheduled_scout": False,
                "unless": "lan E asks",
                "sources": ["Google", "Reddit", "X", "FB", "IG", "Threads"],
            },
        },
    ]
    for name, props in agents.items():
        nodes.append(
            {
                "id": f"agent:{name}",
                "type": "Agent",
                "label": name,
                "properties": props,
            }
        )

    edges: List[Dict[str, Any]] = [
        *[
            {"id": f"e:member:{name}", "source": "team:grok-bot", "target": f"agent:{name}", "type": "HAS_LANE"}
            for name in LANES
        ],
        {"id": "e:intake-user", "source": "intake:user-request", "target": "agent:lead", "type": "ENTERS"},
        {"id": "e:paper-search", "source": "agent:search", "target": "intake:paper-hit", "type": "SCOUTS"},
        {"id": "e:paper-lead", "source": "intake:paper-hit", "target": "agent:lead", "type": "PAPER_HITS"},
        {"id": "e:paper-arxiv", "source": "agent:lead", "target": "agent:arxiv", "type": "PAPER_HITS"},
        {"id": "e:social-search", "source": "agent:search", "target": "intake:social-find", "type": "SCOUTS"},
        {"id": "e:social-lead", "source": "intake:social-find", "target": "agent:lead", "type": "SOCIAL_FINDS"},
        {"id": "e:social-wiki", "source": "agent:lead", "target": "agent:wiki", "type": "SOCIAL_FINDS_AFTER_APPROVE"},
        {"id": "e:user-route", "source": "agent:lead", "target": "intake:user-request", "type": "ROUTES"},
        *[
            {"id": f"e:route:{name}", "source": "agent:lead", "target": f"agent:{name}", "type": "ROUTES_TO"}
            for name in LANES
            if name != "lead"
        ],
        *[
            {"id": f"e:approve:{name}", "source": f"agent:{name}", "target": "approval:lead", "type": "ASKS_APPROVAL"}
            for name in LANES
            if name != "lead"
        ],
        {"id": "e:approval-owned", "source": "agent:lead", "target": "approval:lead", "type": "OWNS"},
        {"id": "e:wiki-policy", "source": "policy:wiki-freeze", "target": "agent:wiki", "type": "BINDS"},
        {"id": "e:arxiv-policy", "source": "policy:arxiv-pause", "target": "agent:arxiv", "type": "BINDS"},
        {"id": "e:search-policy", "source": "policy:search-on-demand", "target": "agent:search", "type": "BINDS"},
    ]

    return {
        "nodes": nodes,
        "edges": edges,
        "exported_at": _now(),
        "format": "semantica_case_graph",
        "product": "LanBB",
        "flow_id": flow.id,
        "flow_name": flow.name,
    }


def render_png(flow: FlowGraph, dest: Path) -> None:
    """Swimlane PNG from the same FlowGraph positions (matplotlib)."""
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, Rectangle

    node_w, node_h = 208.0, 78.0
    pad_l, pad_r, pad_t, pad_b = 24.0, 48.0, 88.0, 36.0
    max_x = max(n.position["x"] for n in flow.nodes) + node_w + pad_r
    max_y = ORIGIN_Y + len(LANES) * LANE_H + pad_b
    width = max_x + pad_l
    height = max_y + pad_t

    fig, ax = plt.subplots(figsize=(width / 90.0, height / 90.0), dpi=140)
    fig.patch.set_facecolor("#0f1419")
    ax.set_facecolor("#0f1419")
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    ax.axis("off")
    ax.set_aspect("equal")

    # Title
    ax.text(
        pad_l,
        28,
        "LanBB  ·  Grok Bot team",
        color="#e8eef5",
        fontsize=16,
        fontweight="bold",
        fontfamily="DejaVu Sans",
        va="center",
    )
    ax.text(
        pad_l + 420,
        28,
        "n8n-style routing  ·  lead is the only approval hop  ·  wiki FROZEN  ·  arxiv paused  ·  search on-demand",
        color="#8fa8c0",
        fontsize=8.5,
        fontfamily="DejaVu Sans",
        va="center",
    )

    # Lane bands + labels
    for i, lane in enumerate(LANES):
        y0 = ORIGIN_Y + i * LANE_H - 18
        color = LANE_COLOR[lane]
        band = Rectangle(
            (8, y0),
            width - 16,
            LANE_H - 8,
            facecolor=color,
            edgecolor="none",
            alpha=0.07,
            zorder=0,
        )
        ax.add_patch(band)
        rail = Rectangle((8, y0), 8, LANE_H - 8, facecolor=color, edgecolor="none", zorder=1, alpha=0.9)
        ax.add_patch(rail)
        ax.text(
            28,
            y0 + (LANE_H - 8) / 2,
            lane,
            color=color,
            fontsize=9.5,
            fontweight="bold",
            fontfamily="DejaVu Sans",
            va="center",
            ha="left",
            rotation=90,
            zorder=2,
        )

    node_map = {n.id: n for n in flow.nodes}

    def center(n: FlowNode) -> Tuple[float, float]:
        return n.position["x"] + node_w / 2, n.position["y"] + node_h / 2

    def port(n: FlowNode, side: str) -> Tuple[float, float]:
        cx, cy = center(n)
        if side == "right":
            return n.position["x"] + node_w, cy
        if side == "left":
            return n.position["x"], cy
        if side == "bottom":
            return cx, n.position["y"] + node_h
        return cx, n.position["y"]

    frozen_edges = {("n_wiki_gate", "n_wiki"), ("n_route", "n_wiki_gate")}
    paused_edges = {("n_lead_intake", "n_arxiv"), ("n_route", "n_arxiv")}

    for edge in flow.edges:
        src, tgt = node_map[edge.source], node_map[edge.target]
        x1, y1 = port(src, "right")
        x2, y2 = port(tgt, "left")
        key = (edge.source, edge.target)
        if key in frozen_edges or (edge.source == "n_wiki_gate"):
            color = "#cd4246"
            ls = (0, (5, 3))
        elif key in paused_edges:
            color = "#d9822b"
            ls = (0, (4, 3))
        elif edge.label == "approval":
            color = "#8fa8c0"
            ls = "solid"
        else:
            color = "#5f7388"
            ls = "solid"
        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops=dict(
                arrowstyle="-|>",
                color=color,
                lw=1.15,
                linestyle=ls,
                connectionstyle="arc3,rad=0.08",
                mutation_scale=9,
            ),
            zorder=2,
        )
        if edge.label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2 - 6
            ax.text(
                mx,
                my,
                edge.label,
                color="#8fa8c0",
                fontsize=5.8,
                fontfamily="DejaVu Sans",
                ha="center",
                va="bottom",
                zorder=4,
                alpha=0.95,
            )

    for n in flow.nodes:
        x, y = n.position["x"], n.position["y"]
        lane = n.config.get("lane") or n.category
        accent = LANE_COLOR.get(lane, TYPE_COLOR.get(n.type, "#4aa3ff"))
        box = FancyBboxPatch(
            (x, y),
            node_w,
            node_h,
            boxstyle="round,pad=0.02,rounding_size=8",
            facecolor="#161d24",
            edgecolor=accent,
            linewidth=1.4,
            zorder=3,
        )
        ax.add_patch(box)
        bar = Rectangle((x, y + 6), 5, node_h - 12, facecolor=accent, edgecolor="none", zorder=4)
        ax.add_patch(bar)
        ax.text(
            x + 16,
            y + 16,
            n.type,
            color="#5f7388",
            fontsize=6.2,
            fontfamily="DejaVu Sans",
            fontweight="normal",
            zorder=5,
        )
        ax.text(
            x + 16,
            y + 36,
            n.label,
            color="#e8eef5",
            fontsize=9.2,
            fontfamily="DejaVu Sans",
            fontweight="bold",
            zorder=5,
        )
        badge = n.config.get("badge")
        if badge:
            ax.text(
                x + 16,
                y + 58,
                badge,
                color=accent,
                fontsize=6.6,
                fontfamily="DejaVu Sans",
                fontweight="bold",
                zorder=5,
            )
        else:
            desc = (n.description or "")[:42]
            ax.text(x + 16, y + 58, desc, color="#8fa8c0", fontsize=6.0, fontfamily="DejaVu Sans", zorder=5)

    plt.tight_layout(pad=0.4)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(dest, dpi=140, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)


def render_html(flow: FlowGraph, case: Dict[str, Any], dest: Path) -> None:
    flow_json = json.dumps(flow.to_dict(), indent=2)
    case_json = json.dumps(case, indent=2)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>LanBB — Grok Bot team</title>
  <meta name="description" content="LanBB Grok Bot team routing: n8n-style flow graph. lead is the front door and the only approval hop." />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet" />
  <script src="https://unpkg.com/vis-network@9.1.9/standalone/umd/vis-network.min.js"></script>
  <style>
    :root {{
      --bg: #0f1419;
      --bg-elev: #161d24;
      --bg-panel: #1b2430;
      --line: rgba(143, 176, 209, 0.14);
      --text: #e8eef5;
      --muted: #8fa8c0;
      --dim: #5f7388;
      --blue: #2d72d2;
      --font: "IBM Plex Sans", sans-serif;
      --mono: "IBM Plex Mono", monospace;
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ height: 100%; margin: 0; }}
    body {{ font-family: var(--font); background: var(--bg); color: var(--text); overflow: hidden; }}
    .app {{ height: 100%; display: grid; grid-template-rows: 48px 1fr; }}
    .topbar {{
      display: flex; align-items: center; gap: 14px; padding: 0 14px;
      border-bottom: 1px solid var(--line);
      background: linear-gradient(180deg, #141b22, #10161c);
    }}
    .mark {{ display: flex; align-items: center; gap: 10px; font-weight: 700; }}
    .mark-badge {{
      width: 22px; height: 22px; border-radius: 4px;
      background: linear-gradient(135deg, var(--blue), #1f4b8f);
      display: grid; place-items: center; font-size: 11px;
    }}
    .mark small {{ color: var(--muted); font-weight: 500; margin-left: 6px; }}
    .top-tabs {{ display: flex; gap: 2px; margin-left: 8px; }}
    .top-tab {{
      border: 0; background: transparent; color: var(--muted);
      font: 500 13px/1 var(--font); padding: 8px 12px; border-radius: 6px; cursor: pointer;
    }}
    .top-tab[data-active="true"] {{ background: rgba(45,114,210,0.16); color: #9ec3f5; }}
    .pill {{
      margin-left: auto; border: 1px solid var(--line); border-radius: 999px;
      padding: 5px 10px; font-family: var(--mono); font-size: 11px; color: var(--muted);
    }}
    .body {{ min-height: 0; display: grid; grid-template-columns: 240px 1fr 300px; }}
    .sidebar, .right {{
      background: var(--bg-elev); overflow: auto; padding: 12px 10px;
    }}
    .sidebar {{ border-right: 1px solid var(--line); }}
    .right {{ border-left: 1px solid var(--line); }}
    .side-label {{
      font-size: 10px; letter-spacing: 0.08em; text-transform: uppercase;
      color: var(--dim); padding: 8px 8px 6px;
    }}
    .lane {{
      display: flex; align-items: center; gap: 8px;
      padding: 8px 10px; border-radius: 6px; color: var(--muted); font-size: 13px;
    }}
    .dot {{ width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }}
    .rule {{
      padding: 8px 10px; margin: 0 0 6px; border: 1px solid var(--line);
      border-radius: 6px; font-size: 12px; color: var(--muted); line-height: 1.4;
    }}
    .rule b {{ color: var(--text); font-weight: 600; }}
    #canvas {{ min-height: 0; }}
    .hidden {{ display: none !important; }}
    h2 {{ font-size: 13px; margin: 0 0 10px; }}
    pre {{
      white-space: pre-wrap; word-break: break-word; font: 11px/1.45 var(--mono);
      color: var(--muted); background: #10161c; border: 1px solid var(--line);
      border-radius: 6px; padding: 10px; max-height: 55vh; overflow: auto;
    }}
    .kv {{ display: grid; grid-template-columns: 88px 1fr; gap: 6px 8px; font-size: 12px; margin-bottom: 12px; }}
    .kv b {{ color: var(--dim); font-weight: 500; }}
    .warn {{ color: #e8a598; }}
  </style>
</head>
<body>
  <div class="app">
    <header class="topbar">
      <div class="mark">
        <div class="mark-badge">L</div>
        LanBB <small>Grok Bot team · Flow Studio</small>
      </div>
      <div class="top-tabs">
        <button class="top-tab" data-view="flow" data-active="true">Flow</button>
        <button class="top-tab" data-view="case">Case graph</button>
      </div>
      <div class="pill">wiki FULL FREEZE · arxiv paused · search on-demand</div>
    </header>
    <div class="body">
      <aside class="sidebar">
        <div class="side-label">Team lanes</div>
        <div id="laneList"></div>
        <div class="side-label">Routing</div>
        <div class="rule"><b>Paper hits</b><br/>search → lead → arxiv</div>
        <div class="rule"><b>Social finds</b><br/>search → lead → wiki after approve</div>
        <div class="rule"><b>New user requests</b><br/>anyone/user → lead → specialist</div>
        <div class="rule"><b>Approvals</b><br/>specialist → lead (never ask user to click)</div>
        <div class="side-label">Holds</div>
        <div class="rule warn"><b>wiki</b> — elan7192/second-brain FULL FREEZE (no ingest/push)</div>
        <div class="rule warn"><b>arxiv</b> — harvest dead, digests paused for quota</div>
        <div class="rule warn"><b>search</b> — no scheduled scout unless lan E asks</div>
      </aside>
      <div id="canvas"></div>
      <aside class="right">
        <h2 id="inspTitle">Node inspector</h2>
        <div class="kv" id="inspKv"></div>
        <pre id="inspPre">Click a node.</pre>
      </aside>
    </div>
  </div>
  <script>
    const FLOW = {flow_json};
    const GRAPH = {case_json};
    const LANE_COLOR = {{
      lead: "#2d72d2", wiki: "#9179f2", arxiv: "#d9822b", search: "#32a467",
      lanbb: "#48aff0", cursor: "#c8763a", "design huddle": "#db6bcf"
    }};
    const TYPE_COLOR = {{
      Team: "#2d72d2", Agent: "#48aff0", Intake: "#32a467", Approval: "#d9822b", Policy: "#9179f2"
    }};

    document.getElementById("laneList").innerHTML = (FLOW.metadata.lanes || []).map((lane) => `
      <div class="lane"><span class="dot" style="background:${{LANE_COLOR[lane] || "#8fa8c0"}}"></span>${{lane}}</div>
    `).join("");

    let network;
    let view = "flow";

    function inspect(obj) {{
      const kv = document.getElementById("inspKv");
      document.getElementById("inspTitle").textContent = obj.label || obj.id || "Node";
      kv.innerHTML = `
        <b>id</b><span>${{obj.id || ""}}</span>
        <b>type</b><span>${{obj.type || ""}}</span>
        <b>lane</b><span>${{obj.category || obj.config?.lane || "—"}}</span>
      `;
      document.getElementById("inspPre").textContent = JSON.stringify(obj, null, 2);
    }}

    function drawFlow() {{
      const nodes = new vis.DataSet(FLOW.nodes.map((n) => ({{
        id: n.id,
        label: n.label + (n.config?.badge ? "\\n" + n.config.badge : ""),
        x: n.position?.x || 0,
        y: n.position?.y || 0,
        physics: false,
        color: {{
          background: "#161d24",
          border: LANE_COLOR[n.category] || "#8fa8c0",
          highlight: {{ background: "#1b2430", border: "#9ec3f5" }}
        }},
        font: {{ color: "#e8eef5", face: "IBM Plex Sans", size: 13, multi: true }},
        shape: "box",
        margin: 12,
        widthConstraint: {{ minimum: 160, maximum: 200 }},
        borderWidth: 2,
        raw: n
      }})));
      const edges = new vis.DataSet(FLOW.edges.map((e) => ({{
        id: e.id, from: e.source, to: e.target, label: e.label || "",
        arrows: {{ to: {{ enabled: true, scaleFactor: 0.7 }} }},
        color: {{ color: "rgba(143,168,192,0.45)", highlight: "#2d72d2" }},
        font: {{ color: "#8fa8c0", size: 10, strokeWidth: 0, face: "IBM Plex Mono" }},
        dashes: e.label === "after approve" || e.source === "n_wiki_gate",
        smooth: {{ type: "cubicBezier", forceDirection: "horizontal", roundness: 0.25 }}
      }})));
      return {{ nodes, edges }};
    }}

    function drawCase() {{
      const nodes = new vis.DataSet(GRAPH.nodes.map((n) => ({{
        id: n.id,
        label: n.label,
        color: {{
          background: TYPE_COLOR[n.type] || "#738694",
          border: "rgba(255,255,255,0.18)",
          highlight: {{ background: "#f5f8fa", border: "#2d72d2" }}
        }},
        font: {{ color: "#0f1419", face: "IBM Plex Sans", size: 12, bold: true }},
        shape: "box",
        margin: 12,
        raw: n
      }})));
      const edges = new vis.DataSet(GRAPH.edges.map((e) => ({{
        id: e.id, from: e.source, to: e.target, label: e.type,
        arrows: {{ to: {{ enabled: true, scaleFactor: 0.65 }} }},
        color: {{ color: "rgba(143,168,192,0.45)", highlight: "#2d72d2" }},
        font: {{ color: "#8fa8c0", size: 9, strokeWidth: 0, face: "IBM Plex Mono" }},
        smooth: {{ type: "cubicBezier", forceDirection: "horizontal", roundness: 0.35 }}
      }})));
      return {{ nodes, edges }};
    }}

    function mount(kind) {{
      view = kind;
      document.querySelectorAll(".top-tab").forEach((t) => {{
        t.dataset.active = String(t.dataset.view === kind);
      }});
      const data = kind === "flow" ? drawFlow() : drawCase();
      const options = kind === "flow"
        ? {{ physics: false, interaction: {{ hover: true, dragNodes: true }}, edges: {{ font: {{ align: "middle" }} }} }}
        : {{ physics: {{ barnesHut: {{ gravitationalConstant: -14000, springLength: 130 }}, stabilization: {{ iterations: 120 }} }}, interaction: {{ hover: true }} }};
      if (network) network.destroy();
      network = new vis.Network(document.getElementById("canvas"), data, options);
      network.on("click", (params) => {{
        if (!params.nodes.length) return;
        inspect(data.nodes.get(params.nodes[0]).raw);
      }});
      if (kind === "case") {{
        network.once("stabilizationIterationsDone", () => network.setOptions({{ physics: false }}));
      }} else {{
        setTimeout(() => network.fit({{ animation: true }}), 50);
      }}
    }}

    document.querySelectorAll(".top-tab").forEach((el) => {{
      el.addEventListener("click", () => mount(el.dataset.view));
    }});
    inspect({{ id: FLOW.id, type: "FlowGraph", label: FLOW.name, category: "LanBB", ...FLOW.metadata }});
    mount("flow");
  </script>
</body>
</html>
"""
    dest.write_text(html, encoding="utf-8")


def main() -> int:
    flow = build_flow()
    case = build_case_graph(flow)

    flow_path = DIR / "flow.json"
    graph_path = DIR / "graph.json"
    png_path = DIR / "graph.png"
    html_path = DIR / "index.html"

    flow_path.write_text(json.dumps(flow.to_dict(), indent=2) + "\n", encoding="utf-8")
    graph_path.write_text(json.dumps(case, indent=2) + "\n", encoding="utf-8")
    render_png(flow, png_path)
    render_html(flow, case, html_path)

    print(f"Flow: {flow.name} ({flow.id})")
    print(f"  nodes={len(flow.nodes)} edges={len(flow.edges)}")
    print(f"  {flow_path}")
    print(f"  {graph_path}")
    print(f"  {png_path}")
    print(f"  {html_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
