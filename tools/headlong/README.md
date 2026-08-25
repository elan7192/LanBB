# Headlong (LanBB note)

LanBB is the product. This directory is a **thin note** (plus an optional
offline stub) about a persistent RLM-style agent harness. It is **not** a
checkout of Headlong, not a hosted agent, and not the engine.

**semantica**, second-brain, and wiki ingest are out of scope. Do not nest or
rename those projects from here.

## Upstream (cite; do not vendor)

| Project | What it is |
| --- | --- |
| [andyk/headlong](https://github.com/andyk/headlong) | Research harness: a persistent thought stream. Humans and the agent co-edit thoughts; an environment daemon turns `action:` thoughts into observations. Thinking uses an RLM-style REPL (`FINAL()`), not a fresh chat session per message. |
| [laude-institute/headlong](https://github.com/laude-institute/headlong) | Open-source **microharness** (Apache 2.0): persistent agency in Bash. A dispatcher keeps generating thoughts between human turns. `shellm` is the RLM core: the model writes bash, the harness runs it, output returns as the next observation, nested `shellm` calls recurse. |
| [Recursive LMs (Zhang)](https://alexzhang13.github.io/blog/2025/rlm/) | Inference pattern: treat context as data in an environment (REPL), peek/partition/recurse instead of stuffing the whole prompt into one call. |

LanBB does **not** vendor those trees. Clone them yourself if you want the
real harness. This repo only maps the idea onto LanBB’s product/tool split.

## How the harness maps to LanBB

A typical coding-agent session is turn-taking: the human starts a run, the
model answers, the run ends. Headlong’s claim is the opposite: **the mind is
already running**. A human message is one more **observation** in an
append-only trajectory. The loop decides whether to think, act, reply, or
stay quiet.

```
                    ┌─────────────────────────────────────┐
  human / tools ──► │  trajectory (jsonl DAG / thought log)│
                    └─────────────────┬───────────────────┘
                                      │ project (context)
                                      ▼
                    ┌─────────────────────────────────────┐
                    │  persistent loop (thinkers)         │
                    │    think → (optional) act → sleep   │
                    └─────────────────┬───────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │  RLM step (shellm-shaped)           │
                    │    LLM writes code against context  │
                    │    run → observe → recurse or FINAL │
                    └─────────────────────────────────────┘
```

| Headlong piece | Meaning here |
| --- | --- |
| Persistent agency / thinkers | LanBB product loop: keep a mind between UI turns. Do not spawn a new “session” per ping. |
| Thought stream + `traj` | Append-only log local to this tool (`loop.py` writes jsonl). Not semantica storage, not second-brain. |
| Human chat / Slack / Telegram | Inject `observation` (or `human`) steps into that log. The loop notices them on the next tick. |
| `shellm` RLM | One tick may *reason by acting on context* (nested sub-query with an isolated `CONTEXT`) instead of one giant prompt. The stub fakes this without an LLM. |
| `context` compaction | The next model call is a **projection** of the log (tail + summaries). The stub only keeps a tail; real Headlong does tiered resolution. |
| Identity / persona / dashboard | Product UX, not this note. |
| Docker sandbox / `llm` CLI | Real Headlong. Not installed here. |

## What this directory will not do

- **No AgentSky** (or any other hosted-agent signup). Do not install, register,
  or phone home.
- **No secrets.** Do not put API keys, tokens, or `.env` files here. The stub
  refuses observation text that looks like a credential.
- **No `curl …/install.sh`**. Do not run Headlong’s installer from LanBB.
- **No Origin / extra GitHub repo.** This `tools/headlong/` note is the
  allowed fallback when a separate harness repo is blocked.

## Optional stub (offline)

Stdlib only. No network, no model, no keys:

```bash
python3 tools/headlong/loop.py observe "ship the headlong note"
python3 tools/headlong/loop.py tick --ticks 2
python3 tools/headlong/loop.py status
```

Human text is recorded as `observation`. `tick` appends a `thought` (and, for
messages that start with `sub:`, a nested RLM tick whose isolated context is
that query). Default state: `tools/headlong/.run/` (gitignored). Override with
`--home`.

```bash
python3 -m unittest discover -s tools/headlong/tests -v
```

Use the real Headlong repos when you want a live mind. This stub only proves
the **shape** of the loop inside LanBB.
