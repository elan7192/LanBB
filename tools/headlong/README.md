# Headlong note

Cites [laude-institute/headlong](https://github.com/laude-institute/headlong)
and [andyk/headlong](https://github.com/andyk/headlong).
Keeps a thin observe/tick helper and a cycle fail log.
The harness clone stays outside this repo (`/tmp/headlong-sandbox` on the agent VM).

## Real cycle (2026-08-27)

Ran `bin/shellm` from a throwaway clone. Tiny task: print the word ping.

```bash
git clone --depth 1 https://github.com/laude-institute/headlong.git /tmp/headlong-sandbox
export HEADLONG_HOME=/tmp/headlong-state
export PATH="/tmp/headlong-sandbox/bin:$PATH"
cd /tmp/headlong-sandbox
shellm --env local --max-iterations 1 --here "Print the word ping."
```

`llm` exited 1: `ANTHROPIC_API_KEY is not set`.
`shellm` exited 1 with the same error. No think bash. No run. No FINAL.
Log: [proof/shellm-fail.md](proof/shellm-fail.md).

## Observe / tick helper

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
