# Audited task contract

Harnesses keep native sessions. They share an audited task contract, not transcripts or KV cache (D4).

## Allowed fields

| Field | Purpose |
| --- | --- |
| `objective` | Concrete task goal (required) |
| `acceptance_checks` | Verifiable checks before state advances |
| `write_scope` | Paths or components executors may modify |
| `accepted_commit` | Git SHA accepted by the auditor |
| `decisions` | Locked choices with `decision` + `evidence` |
| `failed_approaches` | Rejected paths with `approach` + `reason` |
| `blockers` | External or unresolved impediments |
| `phase` | `plan`, `execute`, `audit`, `complete`, or `blocked` (required) |
| `state_version` | Monotonic revision; increment when the auditor advances state (required) |

## Forbidden content

Contracts must not contain full transcripts, secrets, raw tool dumps, or subjective adjectives.

The validator rejects forbidden field names, secret-like patterns, transcript markers, oversized strings, and a blocklist of evaluative wording.

## Usage

```bash
# Create a starter contract
python3 tools/audited-task-contract/atc.py create contract.json

# Validate structure and D4 policy
python3 tools/audited-task-contract/atc.py validate contract.json
```

`schema.json` is the canonical JSON Schema. `atc.py` mirrors it for offline validation without extra dependencies.

## Workflow

1. Executor updates candidate work in an isolated worktree.
2. Executor writes or updates the contract with facts, checks, and scope.
3. Auditor with fresh context runs `validate`, checks acceptance gates, then bumps `state_version` and `phase`.

Peer claims do not advance state until an objective gate passes outside the model.
