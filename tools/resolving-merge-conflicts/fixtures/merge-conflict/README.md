# merge-conflict fixture

Tiny two-branch repo used by `dry-run.sh`. Both branches diverge from the same
base commit, so merging `feature` into `main` produces a real conflict (not a
fast-forward).

| Branch | Change | Intent (commit message) |
|--------|--------|-------------------------|
| `main` | `greeting.txt` → "Hello from main." | `main: rename greeting for trunk` |
| `feature` | `greeting.txt` → "Hello from feature." | `feature: rename greeting for branch work` |

Merging `feature` into `main` conflicts on `greeting.txt`. The dry-run resolves by
combining both intents → `expected/greeting.txt`.
