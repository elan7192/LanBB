# Headlong cycle proof

## Invoke

```bash
python3 tools/headlong/loop.py cycle --task "Print 6 times 7 as a single integer." --proof tools/headlong/proof/cycle-1.md
```

## Trajectory snippet (think + run)

```jsonl
{"step_id": 2, "ts": "2026-08-27T11:52:05+00:00", "type": "think", "source": "stub", "round": 1, "fingerprint": "9f2ed287d4bb391e", "content": "FINAL=\"$(python3 -c 'print(6 * 7)')\"\n"}
{"step_id": 3, "ts": "2026-08-27T11:52:05+00:00", "type": "run", "source": "sandbox", "round": 1, "exit": 0, "stdout": "", "stderr": ""}
```

## FINAL

```
42
```

result: final in 1 round(s).
