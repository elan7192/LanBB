# LanBB Flow Studio

Authorized bug-bounty CASE workflow. Local only. No production deploy.

## Open

```bash
python3 flows/serve.py
```

Then open http://127.0.0.1:8765/ (serves `flows/studio/index.html`).

## Graphs

Persisted as files in `flows/graphs/*.json`.

| File | Role |
| --- | --- |
| `graphs/case-bounty.json` | Default. Authorized CASE DAG: intake, scope, authorization, report, close. Scope and authorization gates fail closed. |
| `graphs/team-swimlanes.json` | Second saved graph. Team lanes (lead, lanbb, wiki freeze). Not the default. |
| `templates/case-bounty.json` | Documented template used when the catalog is empty. |

This is a CASE file (intake, scope, authorization, report, close). It does not include exploit, scan, payload, attack, or weaponized nodes.

## API

`GET /api/graphs` lists `flows/graphs/*.json`. It never creates a graph.

If that list is empty, Flow Studio `POST`s `/api/graphs` with `upsert_template`, which writes the documented CASE template, or the page shows that template in memory.

`GET /api/graphs/{id}` reads a file. 404 if missing. No seed.

## Tests

```bash
python3 flows/test_api.py
```
