# Real Headlong cycle fail

Harness: https://github.com/laude-institute/headlong
Clone: `/tmp/headlong-sandbox`
Headlong SHA: `15f20b4b991ec36ae88039058c765ef526fe14da`
LanBB PR: https://github.com/elan7192/LanBB/pull/29

## Invoke

```bash
git clone --depth 1 https://github.com/laude-institute/headlong.git /tmp/headlong-sandbox
export HEADLONG_HOME=/tmp/headlong-state
export PATH="/tmp/headlong-sandbox/bin:$PATH"
cd /tmp/headlong-sandbox
shellm --env local --max-iterations 1 --here "Print the word ping."
```

Also: `echo print ping | llm -m claude-opus-4-7` (exit 1).

Skipped `install.sh`. Skipped AgentSky. No keys in the environment. `docker` not found.

## Fail log (shellm stderr, ANSI stripped)

```
▶ Trajectory: 6e0074c7-9841-47bb-8c83-ac290cd402eb (dir: /tmp/headlong-state/trajectories)
▶ Workdir: /tmp/headlong-sandbox
▶ Starting shellm loop (model: claude-opus-4-7, max iterations: 1)

▶ Iteration 1/1 — calling claude-opus-4-7...
llm: error: ANTHROPIC_API_KEY is not set
shellm: error: llm failed (exit 1): llm: error: ANTHROPIC_API_KEY is not set
```

## llm stderr

```
llm: error: ANTHROPIC_API_KEY is not set
```

Exits: llm=1, shellm=1. stdout empty.

## Trajectory jsonl

Path: `/tmp/headlong-state/trajectories/6e0074c7-print-the-word-ping./trajectory.jsonl`

The harness wrote a trajectory header, a `shellm-run` step, the prompt, and a failed `run-summary`. It stopped before a think bash step and before a run step.

```jsonl
{"type":"trajectory","step_id":"6e0074c7-9841-47bb-8c83-ac290cd402eb","ts":"2026-08-27T11:54:18.914Z"}
{"type":"shellm-run","command":"shellm --env local --max-iterations 1 --here Print the word ping.","workdir":"/tmp/headlong-sandbox","model":"claude-opus-4-7","effort":"high","max_iterations":"1","max_tokens":"","inactivity_timeout":"30","context_files":[],"env":{"name":"local","type":"local"},"resumed":false,"step_id":"a6b720ae-6d61-4b4b-9507-ef6e0152dc7b","ts":"2026-08-27T11:54:18.969Z"}
{"type":"prompt","content":"Print the word ping.","run_id":"a6b720ae-6d61-4b4b-9507-ef6e0152dc7b","step_id":"5b7342a8-e5e7-4a79-b2c3-709ff4f4d72e","ts":"2026-08-27T11:54:19.009Z"}
{"type":"run-summary","tldr":"(summary generation failed)","full_summary":"","run_id":"a6b720ae-6d61-4b4b-9507-ef6e0152dc7b","model":"claude-haiku-4-5-20251001","step_id":"ee0e0e1f-ef5b-4ec1-8f1c-c427f42445b7","ts":"2026-08-27T11:54:19.022Z"}
```

## FINAL

Empty. `llm` exited before the model wrote bash.

STOP.
