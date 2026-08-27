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
| `overlays/v5-hardened/` | Older wall: v4 plus juice read-only, drop OPTIONS, login WAF, identity/Web3/catalog/search/info-leak closed |
| `overlays/v6-hardened/` | Older wall: working harden (no juice EROFS, no tmpfs over data/static) plus login closed, GET/HEAD only, SPA/static leak closed |
| `overlays/v7-hardened/` | Older wall: working harden plus default-deny unmatched GET/HEAD, leftover SPA/JS, remaining /api /rest closed except Challenges |
| `overlays/v8-hardened/` | Older wall: working harden plus exact GET /api/Challenges/, localhost bind, leftover SPA/Web3/payment closed |
| `overlays/v9-hardened/` | Older wall: working harden plus exact-equals score locations, host allowlist, leftover oauth/health/debug closed |
| `overlays/v10-hardened/` | Older wall: working harden plus exact trailing-slash GET /api/Challenges/ only, empty-query/cookie-closed score path, leftover privacy/hidden/data HTTP routes closed |
| `overlays/v11-hardened/` | Older wall: working harden plus Authorization/Origin/Referer closed on the score path, leftover continue-code/login/search/Baskets/nested privacy-security SPA HTTP routes closed. Edge 4m/4 failed on Fill (daemon min 6MB). |
| `overlays/v12-hardened/` | Previous wall: working harden plus extra hop/auth headers closed on the score path, leftover hacking-instructor/juicy-nft/continue-code-xss/products-queries HTTP routes closed, edge floor mem>=6m pids>=6 |
| `overlays/v13-hardened/` | Current wall: working harden plus leftover rewrite/identity headers closed on the score path, leftover continue-code-apply/tutorial/access_token/ftp-backup HTTP routes closed, edge floor mem>=6m pids>=6 held |

```bash
# stock
docker compose -f labs/juice-shop/overlays/v0-stock/docker-compose.yml up

# older walls
docker compose -f labs/juice-shop/overlays/v1-hardened/docker-compose.yml up
docker compose -f labs/juice-shop/overlays/v2-hardened/docker-compose.yml up
docker compose -f labs/juice-shop/overlays/v3-hardened/docker-compose.yml up
docker compose -f labs/juice-shop/overlays/v4-hardened/docker-compose.yml up
docker compose -f labs/juice-shop/overlays/v5-hardened/docker-compose.yml up
docker compose -f labs/juice-shop/overlays/v6-hardened/docker-compose.yml up
docker compose -f labs/juice-shop/overlays/v7-hardened/docker-compose.yml up
docker compose -f labs/juice-shop/overlays/v8-hardened/docker-compose.yml up
docker compose -f labs/juice-shop/overlays/v9-hardened/docker-compose.yml up
docker compose -f labs/juice-shop/overlays/v10-hardened/docker-compose.yml up
docker compose -f labs/juice-shop/overlays/v11-hardened/docker-compose.yml up
docker compose -f labs/juice-shop/overlays/v12-hardened/docker-compose.yml up

# current wall (v13)
docker compose -f labs/juice-shop/overlays/v13-hardened/docker-compose.yml up
```

In-scope URL stays `http://127.0.0.1:3000`. Fail-closed: no recon/score without `programs/juice-shop/scope.md`.

Do not auto-pwn. Score is GET `/api/Challenges` solved/total. 0/N is valid if the CASE report path still works.
