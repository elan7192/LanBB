# Juice Shop lab wall

Local OWASP Juice Shop only. Hypothetical shop. Not a live bounty program.

Current wall: see `versions.json` (`wall`). Hunt that overlay, then harden a **new** overlay so the next hunt is strictly harder.

| Overlay | Role |
| --- | --- |
| `overlays/v0-stock/` | Unmodified `bkimminich/juice-shop` |
| `overlays/v1-hardened/` | Older wall: security headers, login rate limit, extra-file path closed |
| `overlays/v2-hardened/` | Older wall: v1 plus image pin, stronger headers, broader rate limits, WAF-ish query block, extra surfaces closed |
| `overlays/v3-hardened/` | Older wall: v2 plus method allowlist, URI WAF, cookie flags, COEP/HSTS, read-only edge, upload/PII/chatbot/B2B/snippets closed |
| `overlays/v4-hardened/` | Older wall: v3 plus app/edge caps, broader URI WAF, GraphQL/basket/reviews/captcha/data-export closed |
| `overlays/v5-hardened/` | Previous wall: v4 plus juice read-only, drop OPTIONS, login WAF, identity/Web3/catalog/search/info-leak closed |
| `overlays/v6-hardened/` | Current wall: working harden (no juice EROFS, no tmpfs over data/static) plus login closed, GET/HEAD only, SPA/static leak closed |

```bash
# stock
docker compose -f labs/juice-shop/overlays/v0-stock/docker-compose.yml up

# older walls
docker compose -f labs/juice-shop/overlays/v1-hardened/docker-compose.yml up
docker compose -f labs/juice-shop/overlays/v2-hardened/docker-compose.yml up
docker compose -f labs/juice-shop/overlays/v3-hardened/docker-compose.yml up
docker compose -f labs/juice-shop/overlays/v4-hardened/docker-compose.yml up
docker compose -f labs/juice-shop/overlays/v5-hardened/docker-compose.yml up

# current wall (v6)
docker compose -f labs/juice-shop/overlays/v6-hardened/docker-compose.yml up
```

In-scope URL stays `http://127.0.0.1:3000`. Fail-closed: no recon/score without `programs/juice-shop/scope.md`.

Do not auto-pwn. Score is GET `/api/Challenges` solved/total. 0/N is valid if the CASE report path still works.
