# LanBB

LanBB is the product.

**Flow Studio** is the local CASE workflow page. Open path: `flows/studio/index.html`. Serve with `python3 flows/serve.py`. See `flows/README.md`. Local only. No production deploy.

**semantica** is a tool/engine under LanBB, not the product itself. Do not rename the GitHub repository or the Python package.

- Canonical engine remote: https://github.com/semantica-agi/semantica
- Nesting: git submodule at `tools/semantica`

## How to run a case (OWASP Juice Shop lab)

Lab only. Hypothetical shop. Not a live bounty program. Not random internet. Not adult/porn programs.

```bash
# 1. Scaffold (idempotent)
python3 tools/case/lanbb.py case new juice-shop
# or: ./lanbb case new juice-shop

# 2. Fail-closed scope
python3 tools/case/lanbb.py scope parse juice-shop

# 3. Flow Studio CASE graph (see score pill)
python3 flows/serve.py
# http://127.0.0.1:8765/  → pick case-bounty

# 4. Optional: start the current wall (v5-hardened). Do not hunt stock/v1/v2/v3/v4 forever.
docker compose -f labs/juice-shop/overlays/v5-hardened/docker-compose.yml up
# previous wall: labs/juice-shop/overlays/v4-hardened/docker-compose.yml
# older wall: labs/juice-shop/overlays/v3-hardened/docker-compose.yml
# stock pin: docker compose -f labs/juice-shop/overlays/v0-stock/docker-compose.yml up

# 5. Hunt is CASE-only (scope → in-scope recon skip on loopback → report). No auto-pwn.
python3 tools/case/lanbb.py recon juice-shop
python3 tools/case/lanbb.py case report juice-shop

# 6. Score = GET http://localhost:3000/api/Challenges/
#    n = count(solved==true), N = len(data). Hacking challenges only (N=116 on master).
#    docker-solvable=98 (18 disabledEnv on Docker). Coding /snippets are separate — do not mix.
#    GET /rest/continue-code is a token only — do not forge.
python3 tools/case/lanbb.py case score juice-shop
# Fill unavailable on v4 overlay this loop: 0/116 honest. Do not invent n.

# 7. After hunt→harden, emit Pawel memories (no working dump, no wiki)
python3 tools/case/lanbb.py case memory emit juice-shop \
  --score 0/116 \
  --hardened "v5-hardened: read-only app + pinned nginx + GET-only score path + registration/reset/whoami/search closed" \
  --semantic-file programs/juice-shop/memory/semantic-loop-5.md \
  --loop 5
```

Folder:

```
programs/juice-shop/
  scope.md
  recon/subdomains/   # dumps gitignored
  findings/
  reports/
  notes.md
  memory/             # semantic-loop-N.md + episodic.csv
```

Each later loop: hunt the current wall → harden the lab (strictly harder overlay) → LanBB UX fix → next hunt against that overlay. Memory emit after every loop.

Tests:

```bash
python3 tools/case/tests/test_scope.py
python3 tools/case/tests/test_case.py
python3 flows/test_api.py
python3 flows/test_case_gates.py
```
