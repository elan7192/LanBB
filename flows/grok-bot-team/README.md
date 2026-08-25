# LanBB — Grok Bot team workflow

n8n-style routing graph for the Grok Bot team, generated from the same
FlowGraph model as `semantica.flow` (Flow Studio / sites/bug-bounty-flow
pattern). This is a **LanBB** product artifact, not a semantica submodule
change.

## Open the diagram

- **PNG (GitHub):** open `graph.png` on this branch.
- **HTML Flow Studio:** open `index.html` in a browser (needs network for vis-network CDN).

  ```bash
  python3 -m http.server 8765 --directory flows/grok-bot-team
  ```

  Then visit http://127.0.0.1:8765/

- **JSON:** `flow.json` is the n8n-style FlowGraph (node positions + edges).
  `graph.json` is the team case graph (`semantica_case_graph`).
- **Explorer Flow Studio:** if you run Knowledge Explorer with FlowWorkspace,
  load `flow.json` as a Flow payload (nodes/edges/positions).

## Rebuild

```bash
python3 flows/grok-bot-team/build.py
```

Requires matplotlib (PNG). HTML/JSON need only the stdlib.

## Lanes

| lane | role |
|---|---|
| lead | front door. All new requests + approvals (merge/push/pay/auth). |
| wiki | second-brain vault `elan7192/second-brain`. FULL FREEZE (no ingest/push). |
| arxiv | paper corpus. Harvest dead, digests paused for quota. |
| search | only scout. Google/Reddit/X/FB/IG/Threads. No scheduled scout unless lan E asks. |
| lanbb | LanBB product. |
| cursor | CloudAgents on owned repos. |
| design huddle | figma, motion, experiments, devbot. |

Routing: paper hits `search → lead → arxiv`; social finds `search → lead → wiki after approve`;
new user requests `anyone/user → lead → specialist`; approvals `specialist → lead` (never ask the user to click).
