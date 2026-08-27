# v8-hardened

Stricter than `v7-hardened`. Previous wall. Next hunt must use `v9-hardened`, not v8.

This overlay is a **working harden** that actually applies. Fill on v8 scored live 0/116 (GET `/api/Challenges/` HTTP 200). Wall APPLIES: default-deny 403 on `/`, `/login`, `/api`. Fill on v7 had already scored live 0/116 (GET 200, default-deny 403, POST 405). v8 keeps those apply constraints (no juice EROFS, no tmpfs over data/static, burst>=1, GET `/api/Challenges/` stays open). v5 juice `read_only` EROFS-skipped `.well-known/csaf` and `tmpfs /juice-shop/data` hid `data/static`. v8 does not copy those skipped locks.

Keeps from v7 what actually applied:

- Image pin `bkimminich/juice-shop@sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e`
- Juice root writable; tmpfs only `/tmp` (not `data/static`); read-only **edge**
- Default-deny unmatched GET; URI WAF; cookie flags; COEP/HSTS; Trusted Types; Origin-Agent-Cluster
- App/edge caps, `NODE_ENV=production`, `limit_req` burst>=1 (never burst=0)
- Closed ftp/admin/upload/PII/chatbot/B2B/snippets/continue-code/GraphQL/basket/reviews/captcha/data-export/identity/Web3/catalog/search/info-leak/login/SPA-assets/remaining /api /rest

Raises the wall (and keeps a working juice/edge):

- Score harness is exact `^/api/Challenges/?$` (v7 prefix `/api/Challenges` could still match suffixes)
- Host bind `127.0.0.1:3000` only (not `0.0.0.0`)
- GET only (HEAD dropped); `limit_except GET` on the score path
- Closed leftover SPA/Web3/payment routes v7 left to the catch-all
- Broader static deny (html/svg/fonts/images/json/xml/wasm)
- Broader WAF-ish tokens (still signatures only; no PoC)
- `X-XSS-Protection 0`; extra Permissions-Policy features; gzip/ssi/autoindex off
- Tighter mem/pids/cpu/ulimits, body/rate (`30r/m`, burst>=1)/connection/timeouts

GET `/api/Challenges/` stays the only proxied path so the CASE score harness still works. No exploit PoC. Coding `/snippets` stay out of n/N.
