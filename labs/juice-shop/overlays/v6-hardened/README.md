# v6-hardened

Stricter than `v5-hardened`. Next hunt must use this wall, not v5.

Keeps v5:

- Image pin `bkimminich/juice-shop@sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e`
- Method allowlist, URI WAF, cookie flags, COEP/HSTS, Trusted Types, Origin-Agent-Cluster
- Juice read-only + tmpfs, app/edge caps, `NODE_ENV=production`, read-only edge
- Drop OPTIONS; `limit_req` burst>=1 (never burst=0)
- Closed ftp/admin/upload/PII/chatbot/B2B/snippets/continue-code/GraphQL/basket/reviews/captcha/data-export/identity/Web3/catalog/search/info-leak

Raises the wall:

- Closes the remaining auth door v5 left open (`/rest/user/login` and the rest of `/rest/user`)
- Drops POST from the method allowlist (GET/HEAD only)
- Broader WAF-ish tokens (still signatures only; no PoC)
- Tighter mem/pids/cpu, tmpfs size caps, body/rate/connection/timeouts
- CSP `trusted-types default`
- Closed another class v5 left open: SPA/static leak (assets, i18n, source maps, sitemap) plus leftover frontend routes (login/register/score-board/admin/accounting)

GET `/api/Challenges/` stays open so the CASE score harness still works. No exploit PoC. Coding `/snippets` stay out of n/N.
