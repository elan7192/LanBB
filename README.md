# LanBB

LanBB is the product.

**semantica** is a tool/engine under LanBB, not the product itself. Do not rename the GitHub repository or the Python package.

- Canonical engine remote: https://github.com/semantica-agi/semantica
- Nesting: git submodule at `tools/semantica`

## Persistent RLM-style harness (note)

[Headlong](https://github.com/andyk/headlong) (and the [laude-institute/headlong](https://github.com/laude-institute/headlong) microharness) keep a mind running between human turns: messages land as observations on an append-only trajectory, and thinking is an RLM loop (model writes code against context, runs it, recurses). LanBB maps that idea here without vendoring the upstream trees, without AgentSky, and without secrets.

See [tools/headlong/README.md](tools/headlong/README.md). Optional offline stub:

```bash
python3 tools/headlong/loop.py observe "a ping"
python3 tools/headlong/loop.py tick
```
