# v9-hardened

Stricter than `v8-hardened`. Next hunt must use this wall, not v8.

This overlay is a **working harden** that actually applies. This hunt's Fill on v8 was unavailable (GET `/api/Challenges/` connection refused; docker not installed). Honest score 0/116. Last live Fill remains 0/116 on v7-hardened (GET 200, default-deny 403, POST 405). v9 keeps the apply constraints (no juice EROFS, no tmpfs over data/static, burst>=1, exact GET `/api/Challenges/` stays open). v5 juice `read_only` EROFS-skipped `.well-known/csaf` and `tmpfs /juice-shop/data` hid `data/static`. v9 does not copy those skipped locks. Juice stays at 128m so the score harness can still apply.

Keeps from v8 what actually applied:

- Image pin `bkimminich/juice-shop@sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e`
- Juice root writable; tmpfs only `/tmp` (not `data/static`); read-only **edge**
- Host bind `127.0.0.1:3000` only; GET only (HEAD dropped)
- Default-deny unmatched GET; URI WAF; cookie flags; COEP/HSTS; Trusted Types; Origin-Agent-Cluster
- App/edge caps, `NODE_ENV=production`, `limit_req` burst>=1 (never burst=0)
- Closed ftp/admin/upload/PII/chatbot/B2B/snippets/continue-code/GraphQL/basket/reviews/captcha/data-export/identity/Web3/catalog/search/info-leak/login/SPA-assets/remaining /api /rest / leftover SPA/Web3/payment

Raises the wall (and keeps a working juice/edge):

- Score harness is two exact locations (`= /api/Challenges` and `= /api/Challenges/`), not the v8 regex
- Host allowlist `127.0.0.1|localhost` (444 otherwise); inbound cookies stripped on the score path; no `X-Forwarded-For`
- Closed leftover oauth/logout/error/health/debug/config routes v8 left to the catch-all
- Broader static deny (md/yml/env/bak/sql/zip/log)
- Broader WAF-ish tokens (still signatures only; no PoC)
- CSP sandbox + `base-uri 'none'` + `form-action 'none'`; `etag off`
- Tighter edge caps, juice pids/tmpfs/ulimits, body/rate (`10r/m`, burst>=1)

GET `/api/Challenges/` stays the only proxied path so the CASE score harness still works. No exploit PoC. Coding `/snippets` stay out of n/N.
