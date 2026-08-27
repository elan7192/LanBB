# LanBB Flow Studio

Authorized CASE workflow. Local only.

## Open

```bash
python3 flows/serve.py
```

Then open http://127.0.0.1:8765/ (serves `flows/studio/index.html`).

## Graphs

Persisted as files in `flows/graphs/*.json`.

| File | Role |
| --- | --- |
| `graphs/case-bounty.json` | Default CASE DAG. CyberGym 10-task subset. Score is the PoC server n/N or its fail text. Scope, authorization, and recon gates fail closed. |
| `graphs/team-swimlanes.json` | Second saved graph. Team lanes. Not the default. |
| `templates/case-bounty.json` | Template used when the catalog is empty. |

## API

`GET /api/graphs` lists `flows/graphs/*.json`. It never creates a graph.

If that list is empty, Flow Studio `POST`s `/api/graphs` with `upsert_template`, which writes the documented CASE template, or the page shows that template in memory.

`GET /api/graphs/{id}` reads a file. 404 if missing. No seed.

## Tests

```bash
python3 flows/test_api.py flows/test_case_gates.py
```


CASE gates (leftover grok-bot-team 15/31 pass/fail cards): a graph fails if it has a coordinator node, wiki ingest True, a route that skips lead, merge-now, the semantica-agi org string, a specialist that asks the user, or `e:route:cursor` / `e:route:lanbb` / `e:route:search` that skip `approval:lead` (`e:social-wiki` AFTER_APPROVE without `approval:lead` is the same fail-closed rule). `graphs/case-bounty.json` and `graphs/team-swimlanes.json` must pass. Fixtures under `flows/fixtures/` fail one rule each.
