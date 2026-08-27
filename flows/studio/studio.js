const TYPE_STYLE = {
  trigger: { stroke: "#5ee0b5", fill: "#10241c", bar: "#5ee0b5" },
  case_step: { stroke: "#3d8bfd", fill: "#101820", bar: "#3d8bfd" },
  decision_gate: { stroke: "#e4b84a", fill: "#241c10", bar: "#e4b84a" },
  hold: { stroke: "#f07167", fill: "#241414", bar: "#f07167" },
  close: { stroke: "#c4b5fd", fill: "#181424", bar: "#c4b5fd" },
};

const KNOWN_FILES = ["case-bounty", "team-swimlanes"];
const DEFAULT_ID = "case-bounty";
const NODE_W = 188;
const NODE_H = 72;

const DOCUMENTATED_DEFAULT = {
  id: "case-bounty",
  name: "Authorized bug-bounty CASE",
  description:
    "Documented default. Shown in memory when the catalog is empty and upsert is unavailable.",
  version: "1.0.0",
  nodes: [],
  edges: [],
  metadata: {
    product: "LanBB",
    kind: "case_dag",
    layout: "dag",
    default: true,
    fail_closed: true,
    source: "documented-default",
  },
};

const state = {
  graphs: [],
  current: null,
  selected: null,
  pan: { x: 24, y: 28 },
  scale: 1,
  drag: null,
};

function $(id) {
  return document.getElementById(id);
}

async function getJson(url) {
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error(String(res.status));
  return res.json();
}

async function listGraphs() {
  try {
    const data = await getJson("/api/graphs");
    return Array.isArray(data.graphs) ? data.graphs : [];
  } catch {
    return null;
  }
}

async function loadGraphFile(id) {
  const tries = [
    `/api/graphs/${encodeURIComponent(id)}`,
    `/graphs/${encodeURIComponent(id)}.json`,
    `../graphs/${encodeURIComponent(id)}.json`,
    `/templates/${encodeURIComponent(id)}.json`,
    `../templates/${encodeURIComponent(id)}.json`,
  ];
  for (const url of tries) {
    try {
      return await getJson(url);
    } catch {
      /* try next */
    }
  }
  return null;
}

async function upsertTemplate() {
  const res = await fetch("/api/graphs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ upsert_template: true }),
  });
  if (!res.ok) throw new Error("upsert failed");
  return res.json();
}

function pickDefault(list) {
  return (
    list.find((g) => g.default && g.id === DEFAULT_ID) ||
    list.find((g) => g.id === DEFAULT_ID) ||
    list.find((g) => g.default) ||
    list[0]
  );
}

function setHint(text) {
  $("loadHint").textContent = text;
}

function setEmptyVisible(visible) {
  const el = $("emptyState");
  if (!el) return;
  el.classList.toggle("hidden", !visible);
  el.hidden = !visible;
}

function renderGraphList(activeId) {
  const box = $("graphList");
  box.innerHTML = "";
  state.graphs.forEach((g) => {
    const btn = document.createElement("button");
    btn.className = "graph-btn";
    btn.type = "button";
    btn.setAttribute("aria-current", String(g.id === activeId));
    btn.innerHTML = `${escapeHtml(g.name)}<small>${escapeHtml(g.id)}${
      g.default ? " · default" : ""
    }${g.last_score ? " · " + escapeHtml(g.last_score) : ""}${
      g.wall ? " · " + escapeHtml(g.wall) : ""
    }${g.hunted ? " · hunted " + escapeHtml(g.hunted) : ""}${
      g.fill ? " · fill " + escapeHtml(g.fill) : ""
    }${g.fill_wall ? " · fill-wall " + escapeHtml(g.fill_wall) : ""}${
      g.next_hunt ? " · next " + escapeHtml(g.next_hunt) : ""
    }</small>`;
    btn.addEventListener("click", () => openGraph(g.id));
    box.appendChild(btn);
  });
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function graphLastScore(graph) {
  const meta = (graph && graph.metadata) || {};
  const lab = meta.lab || {};
  return lab.last_score || meta.score || null;
}

function graphWall(graph) {
  const meta = (graph && graph.metadata) || {};
  const lab = meta.lab || {};
  return lab.wall || null;
}

function graphHunted(graph) {
  const meta = (graph && graph.metadata) || {};
  const lab = meta.lab || {};
  return lab.hunted || null;
}

function graphFill(graph) {
  const meta = (graph && graph.metadata) || {};
  const lab = meta.lab || {};
  return lab.fill || null;
}

function graphFillWall(graph) {
  const meta = (graph && graph.metadata) || {};
  const lab = meta.lab || {};
  return lab.fill_wall || null;
}

function graphFillReason(graph) {
  const meta = (graph && graph.metadata) || {};
  const lab = meta.lab || {};
  return lab.fill_reason || null;
}

function graphNextHunt(graph) {
  const meta = (graph && graph.metadata) || {};
  const lab = meta.lab || {};
  return lab.next_hunt || lab.wall || null;
}

function showScorePill(text, live) {
  const el = $("labScore");
  if (!el) return;
  if (!text) {
    el.textContent = "score —";
    el.classList.add("dim");
    return;
  }
  const nN = String(text).replace(/^score\s+/i, "");
  el.textContent = nN;
  el.classList.toggle("dim", !live);
}

function showHuntedPill(text) {
  const el = $("labHunted");
  if (!el) return;
  if (!text) {
    el.textContent = "hunted —";
    el.classList.add("dim");
    return;
  }
  el.textContent = "hunted " + String(text);
  el.classList.remove("dim");
}

function showFillPill(text, reason) {
  const el = $("labFill");
  if (!el) return;
  const value = text ? String(text) : "";
  if (!value) {
    el.textContent = "fill —";
    el.classList.add("dim");
    el.classList.remove("live", "miss");
    el.removeAttribute("title");
    return;
  }
  el.textContent = "fill " + value;
  el.classList.remove("dim");
  const live = value === "live";
  el.classList.toggle("live", live);
  el.classList.toggle("miss", !live);
  if (reason) el.setAttribute("title", String(reason));
  else el.removeAttribute("title");
}

function showNextPill(text) {
  const el = $("labNext");
  if (!el) return;
  if (!text) {
    el.textContent = "next hunt —";
    el.classList.add("dim");
    return;
  }
  el.textContent = "next hunt " + String(text);
  el.classList.remove("dim");
}

function showWallPill(text, live) {
  const el = $("labWall");
  if (!el) return;
  if (!text) {
    el.textContent = "wall —";
    el.classList.add("dim");
    return;
  }
  el.textContent = String(text);
  el.classList.toggle("dim", !live);
}

function renderStages(graph) {
  const meta = graph.metadata || {};
  const stages =
    meta.layout === "swimlanes" && Array.isArray(meta.lanes)
      ? meta.lanes.map((lane) => ({ id: lane.id, label: lane.label }))
      : meta.stages || [
          { id: "intake", label: "Intake" },
          { id: "scope", label: "Scope" },
          { id: "authorization", label: "Authorization" },
          { id: "recon", label: "Recon" },
          { id: "report", label: "Report" },
          { id: "close", label: "Close" },
        ];
  $("stageNav").innerHTML = stages
    .map((s) => `<span class="stage-chip on">${escapeHtml(s.label)}</span>`)
    .join("");
}

async function loadLabScore(
  fallback,
  wallFallback,
  huntedFallback,
  fillFallback,
  nextFallback,
  fillReasonFallback
) {
  const el = $("labScore");
  if (!el) return;
  if (fallback) showScorePill(fallback, false);
  if (wallFallback) showWallPill(wallFallback, false);
  if (huntedFallback) showHuntedPill(huntedFallback);
  if (fillFallback) showFillPill(fillFallback, fillReasonFallback);
  if (nextFallback) showNextPill(nextFallback);
  try {
    const data = await getJson("/api/case/score?program=juice-shop");
    const live = data && (data.score || data.last_score);
    if (live) {
      showScorePill(live, Boolean(data.available));
    } else if (!fallback) {
      showScorePill(null, false);
    }
    const wall = data && data.wall;
    if (wall) {
      showWallPill(wall, Boolean(data.available));
    } else if (!wallFallback) {
      showWallPill(null, false);
    }
    const hunted = data && data.hunted;
    if (hunted) {
      showHuntedPill(hunted);
    } else if (!huntedFallback) {
      showHuntedPill(null);
    }
    const fill = data && data.fill;
    const reason = data && (data.fill_reason || data.reason);
    if (fill) {
      showFillPill(fill, reason);
    } else if (!fillFallback) {
      showFillPill(null);
    }
    const nextHunt = data && (data.next_hunt || data.wall);
    if (nextHunt) {
      showNextPill(nextHunt);
    } else if (!nextFallback) {
      showNextPill(null);
    }
  } catch {
    if (!fallback) showScorePill(null, false);
    if (!wallFallback) showWallPill(null, false);
    if (!huntedFallback) showHuntedPill(null);
    if (!fillFallback) showFillPill(null);
    if (!nextFallback) showNextPill(null);
  }
}

function inspect(node) {
  state.selected = node ? node.id : null;
  if (!node) {
    $("inspTitle").textContent = "Select a node";
    $("inspMeta").innerHTML = "";
    $("inspBody").textContent =
      "Click a node on the CASE DAG. Gates fail closed: missing scope or authorization holds the case.";
    $("inspJson").classList.add("hidden");
    draw(state.current);
    return;
  }
  const cfg = node.config || {};
  const lab = ((state.current && state.current.metadata) || {}).lab || {};
  const rows = [
    ["Type", node.type],
    ["Stage", cfg.stage || node.category || "-"],
    ["Gate", cfg.fail_closed ? "fail-closed" : node.type === "decision_gate" ? "review" : "-"],
    ["Badge", cfg.badge || "-"],
  ];
  if (node.id === "n_lab" || cfg.stage === "lab") {
    rows.push(["Wall", lab.wall || graphWall(state.current) || "-"]);
    rows.push(["Hunted", lab.hunted || graphHunted(state.current) || "-"]);
    rows.push(["Score", lab.last_score || graphLastScore(state.current) || "-"]);
    rows.push(["Fill", lab.fill || graphFill(state.current) || "-"]);
    rows.push(["Fill wall", lab.fill_wall || graphFillWall(state.current) || "-"]);
    rows.push(["Fill reason", lab.fill_reason || graphFillReason(state.current) || "-"]);
    rows.push(["Next hunt", lab.next_hunt || graphNextHunt(state.current) || "-"]);
  }
  if (node.id === "n_harden" || cfg.stage === "harden") {
    rows.push(["Next wall", lab.wall || graphWall(state.current) || "-"]);
    rows.push(["Hunted", lab.hunted || graphHunted(state.current) || "-"]);
    rows.push(["Next hunt", lab.next_hunt || graphNextHunt(state.current) || "-"]);
    rows.push(["Fill wall", lab.fill_wall || graphFillWall(state.current) || "-"]);
  }
  $("inspTitle").textContent = node.label;
  $("inspMeta").innerHTML = rows
    .map(([k, v]) => `<b>${escapeHtml(k)}</b><span>${escapeHtml(v)}</span>`)
    .join("");
  $("inspBody").textContent = node.description || "";
  $("inspJson").textContent = JSON.stringify(node, null, 2);
  $("inspJson").classList.remove("hidden");
  draw(state.current);
}

function nodeCenter(node) {
  return { x: node.position.x + NODE_W / 2, y: node.position.y + NODE_H / 2 };
}

function edgePath(a, b) {
  const x1 = a.position.x + NODE_W;
  const y1 = a.position.y + NODE_H / 2;
  const x2 = b.position.x;
  const y2 = b.position.y + NODE_H / 2;
  const dx = Math.max(48, (x2 - x1) / 2);
  return `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`;
}

function drawLanes(svg, graph) {
  const lanes = (graph.metadata && graph.metadata.lanes) || [];
  if ((graph.metadata && graph.metadata.layout) !== "swimlanes" || !lanes.length) return;
  const byLane = {};
  graph.nodes.forEach((n) => {
    const lane = (n.config && n.config.lane) || n.category;
    if (!byLane[lane]) byLane[lane] = [];
    byLane[lane].push(n);
  });
  lanes.forEach((lane) => {
    const nodes = byLane[lane.id] || [];
    if (!nodes.length) return;
    const ys = nodes.map((n) => n.position.y);
    const xs = nodes.map((n) => n.position.x);
    const y = Math.min(...ys) - 28;
    const h = Math.max(...ys) - Math.min(...ys) + NODE_H + 56;
    const x = Math.min(...xs) - 36;
    const w = Math.max(...xs) - Math.min(...xs) + NODE_W + 72;
    const g = el("g", {});
    g.appendChild(
      el("rect", {
        x,
        y,
        width: w,
        height: h,
        rx: 18,
        fill: "rgba(16,22,31,0.35)",
        stroke: lane.color || "#3d8bfd",
        "stroke-opacity": 0.35,
      })
    );
    g.appendChild(
      el("text", {
        x: x + 16,
        y: y + 20,
        fill: lane.color || "#8aa0b8",
        "font-size": 11,
        "font-family": "IBM Plex Mono, monospace",
        "letter-spacing": "0.14em",
      }, lane.label.toUpperCase())
    );
    svg.appendChild(g);
  });
}

function el(name, attrs, text) {
  const node = document.createElementNS("http://www.w3.org/2000/svg", name);
  Object.entries(attrs).forEach(([k, v]) => node.setAttribute(k, String(v)));
  if (text) node.textContent = text;
  return node;
}

function draw(graph) {
  const svg = $("canvas");
  svg.innerHTML = "";
  if (!graph) return;
  const world = el("g", {
    transform: `translate(${state.pan.x} ${state.pan.y}) scale(${state.scale})`,
  });
  svg.appendChild(world);
  drawLanes(world, graph);

  const byId = Object.fromEntries(graph.nodes.map((n) => [n.id, n]));
  graph.edges.forEach((edge) => {
    const a = byId[edge.source];
    const b = byId[edge.target];
    if (!a || !b) return;
    const kind = edge.kind || "";
    const path = el("path", {
      d: edgePath(a, b),
      fill: "none",
      stroke: kind === "fail" ? "#f07167" : kind === "pass" ? "#5ee0b5" : "rgba(138,160,184,0.7)",
      "stroke-width": 1.8,
      "stroke-dasharray": kind === "fail" ? "6 5" : "none",
      "stroke-linecap": "round",
    });
    world.appendChild(path);
    if (edge.label) {
      const c1 = nodeCenter(a);
      const c2 = nodeCenter(b);
      world.appendChild(
        el(
          "text",
          {
            x: (c1.x + c2.x) / 2,
            y: (c1.y + c2.y) / 2 - 8,
            fill: "#8aa0b8",
            "font-size": 10,
            "text-anchor": "middle",
            "font-family": "IBM Plex Sans, sans-serif",
          },
          edge.label
        )
      );
    }
  });

  graph.nodes.forEach((node) => {
    const style = TYPE_STYLE[node.type] || TYPE_STYLE.case_step;
    const g = el("g", {
      class: `node-hit node-card${state.selected === node.id ? " on" : ""}`,
      transform: `translate(${node.position.x} ${node.position.y})`,
    });
    g.appendChild(
      el("rect", {
        class: "node-body",
        width: NODE_W,
        height: NODE_H,
        rx: 12,
        fill: style.fill,
        stroke: style.stroke,
        "stroke-opacity": 0.7,
      })
    );
    g.appendChild(el("rect", { width: 5, height: NODE_H, rx: 2, fill: style.bar }));
    g.appendChild(
      el(
        "text",
        {
          x: 18,
          y: 28,
          fill: "#e9eef6",
          "font-size": 13,
          "font-weight": 600,
          "font-family": "IBM Plex Sans, sans-serif",
        },
        node.label
      )
    );
    const badge = (node.config && node.config.badge) || node.type;
    g.appendChild(
      el(
        "text",
        {
          x: 18,
          y: 50,
          fill: "#8aa0b8",
          "font-size": 10,
          "letter-spacing": "0.08em",
          "font-family": "IBM Plex Mono, monospace",
        },
        badge
      )
    );
    g.addEventListener("click", (ev) => {
      ev.stopPropagation();
      inspect(node);
    });
    world.appendChild(g);
  });
}

function bindPan() {
  const svg = $("canvas");
  svg.addEventListener("pointerdown", (ev) => {
    if (ev.target.closest(".node-hit")) return;
    state.drag = { x: ev.clientX - state.pan.x, y: ev.clientY - state.pan.y };
    svg.setPointerCapture(ev.pointerId);
  });
  svg.addEventListener("pointermove", (ev) => {
    if (!state.drag) return;
    state.pan.x = ev.clientX - state.drag.x;
    state.pan.y = ev.clientY - state.drag.y;
    draw(state.current);
  });
  svg.addEventListener("pointerup", () => {
    state.drag = null;
  });
  svg.addEventListener(
    "wheel",
    (ev) => {
      ev.preventDefault();
      const next = state.scale * (ev.deltaY > 0 ? 0.94 : 1.06);
      state.scale = Math.min(1.8, Math.max(0.55, next));
      draw(state.current);
    },
    { passive: false }
  );
  svg.addEventListener("click", (ev) => {
    if (ev.target === svg) inspect(null);
  });
  svg.addEventListener("dblclick", () => {
    if (state.current) {
      fitGraph(state.current);
      draw(state.current);
    }
  });
}

function fitGraph(graph) {
  const vp = $("viewport");
  const vw = vp.clientWidth || 960;
  const vh = vp.clientHeight || 520;
  if (!graph || !graph.nodes.length) {
    state.scale = 1;
    state.pan = { x: 24, y: 28 };
    return;
  }
  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  graph.nodes.forEach((n) => {
    minX = Math.min(minX, n.position.x);
    minY = Math.min(minY, n.position.y);
    maxX = Math.max(maxX, n.position.x + NODE_W);
    maxY = Math.max(maxY, n.position.y + NODE_H);
  });
  const pad = 80;
  const w = maxX - minX + pad * 2;
  const h = maxY - minY + pad * 2;
  state.scale = Math.min((vw - 8) / w, (vh - 8) / h, 1);
  state.scale = Math.max(0.42, state.scale);
  state.pan.x = (vw - w * state.scale) / 2 - minX * state.scale + pad * state.scale;
  state.pan.y = (vh - h * state.scale) / 2 - minY * state.scale + pad * state.scale;
}

function showGraph(graph, hint) {
  state.current = graph;
  state.selected = null;
  setEmptyVisible(false);
  $("graphTitle").textContent = graph.name;
  $("graphDesc").textContent = graph.description || "";
  renderStages(graph);
  renderGraphList(graph.id);
  fitGraph(graph);
  inspect(null);
  if (hint) setHint(hint);
  const cached = graphLastScore(graph);
  if (cached) showScorePill(cached, false);
  const wall = graphWall(graph);
  if (wall) showWallPill(wall, false);
  const hunted = graphHunted(graph);
  if (hunted) showHuntedPill(hunted);
  const fill = graphFill(graph);
  if (fill) showFillPill(fill, graphFillReason(graph));
  const nextHunt = graphNextHunt(graph);
  if (nextHunt) showNextPill(nextHunt);
  loadLabScore(cached, wall, hunted, fill, nextHunt, graphFillReason(graph));
}

async function openGraph(id) {
  const graph = await loadGraphFile(id);
  if (!graph) {
    setHint(`Could not load ${id}.`);
    return;
  }
  showGraph(graph, `Loaded ${graph.id} from repo files.`);
}

async function showDocumentedDefault() {
  const file = await loadGraphFile(DEFAULT_ID);
  const graph = file || DOCUMENTATED_DEFAULT;
  if (!file) {
    graph.description =
      "Documented default CASE DAG shown in memory. GET did not seed. Save via POST upsert to persist.";
  }
  showGraph(graph, file ? "Loaded documented default from repo files." : "Showing documented default in memory. GET did not seed.");
}

async function boot() {
  bindPan();
  $("btnUpsert").addEventListener("click", async () => {
    try {
      const data = await upsertTemplate();
      state.graphs = data.graphs || [{ id: DEFAULT_ID, name: data.graph.name, default: true }];
      showGraph(data.graph, "POST upserted the documented CASE template.");
    } catch (err) {
      setHint("Upsert needs the local server (python3 flows/serve.py). Showing documented default instead.");
      showDocumentedDefault();
    }
  });
  $("btnDefault").addEventListener("click", showDocumentedDefault);

  const listed = await listGraphs();
  if (listed && listed.length) {
    state.graphs = listed;
    const pick = pickDefault(listed);
    await openGraph(pick.id);
    setHint("GET /api/graphs listed repo files. GET did not seed.");
    return;
  }
  if (listed && listed.length === 0) {
    state.graphs = [];
    renderGraphList(null);
    setEmptyVisible(true);
    setHint("GET /api/graphs was empty and did not seed.");
    try {
      const data = await upsertTemplate();
      state.graphs = data.graphs || [];
      showGraph(data.graph, "Empty list: POST upserted the documented CASE template.");
      return;
    } catch {
      return;
    }
  }

  const fallback = [];
  for (const id of KNOWN_FILES) {
    const graph = await loadGraphFile(id);
    if (graph) {
      fallback.push({
        id: graph.id,
        name: graph.name,
        default: Boolean(graph.metadata && graph.metadata.default),
      });
    }
  }
  if (fallback.length) {
    state.graphs = fallback;
    const pick = pickDefault(fallback);
    await openGraph(pick.id);
    setHint("API catalog unavailable. Loaded known repo graph files.");
    return;
  }
  setEmptyVisible(true);
  setHint("No catalog and no graph files. Show the documented default or POST upsert.");
}

boot();
