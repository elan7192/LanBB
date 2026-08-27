# Headlong stub

Cites [laude-institute/headlong](https://github.com/laude-institute/headlong)
and [andyk/headlong](https://github.com/andyk/headlong).
Keeps a thin think-run-FINAL loop inside LanBB.
Leaves those trees out of this repo.

A human message lands as an observation on one jsonl trajectory.
`cycle` writes bash, runs it in `.run/sandbox`, and reads `FINAL`.
Stops on FINAL, on a repeated think fingerprint, or after three rounds.

## One cycle

```bash
python3 tools/headlong/loop.py cycle \
  --task "Print 6 times 7 as a single integer." \
  --proof tools/headlong/proof/cycle-1.md
```

The default toy prints `42`. Pass `--think-file` to supply the bash yourself.
The stub has no LLM.

## Observe / tick

```bash
python3 tools/headlong/loop.py observe "a ping"
python3 tools/headlong/loop.py tick
python3 tools/headlong/loop.py status
```

State lives in `tools/headlong/.run/` (gitignored). Override with `--home`.

## Guardrails

Refuse secret-looking text.
Skip AgentSky signup.
Skip Headlong `install.sh`.
Leave semantica and wiki ingest alone.

## Tests

```bash
python3 -m unittest discover -s tools/headlong/tests -v
```
