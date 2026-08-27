# v10-hardened

Stricter than `v9-hardened`. Previous wall. Next hunt must use `v11-hardened`, not v10.

This overlay is a **working harden** that actually applies. Fill on v9 scored live 0/116 (GET `/api/Challenges/` HTTP 200). Wall APPLIES: default-deny 403 on `/`, `/login`, `/api`. v10 keeps those apply constraints (no juice EROFS, no tmpfs over data/static, burst>=1, exact GET `/api/Challenges/` stays open). v5 juice `read_only` EROFS-skipped `.well-known/csaf` and `tmpfs /juice-shop/data` hid `data/static`. v10 does not copy those skipped locks. Juice stays at 128m so the score harness can still apply.

Keeps from v9 what actually applied:

- Image pin `bkimminich/juice-shop@sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e`
- Juice root writable; tmpfs only `/tmp` (not `data/static`); read-only **edge**
- Host bind `127.0.0.1:3000` only; GET only; host allowlist `127.0.0.1|localhost`
- Default-deny unmatched GET; URI WAF; cookie flags; COEP/HSTS; Trusted Types; Origin-Agent-Cluster; CSP sandbox
- App/edge caps, `NODE_ENV=production`, `limit_req` burst>=1 (never burst=0)
- Closed ftp/admin/upload/PII/chatbot/B2B/snippets/continue-code/GraphQL/basket/reviews/captcha/data-export/identity/Web3/catalog/search/info-leak/login/SPA-assets/remaining /api /rest / leftover SPA/Web3/payment/oauth/health/debug

Raises the wall (and keeps a working juice/edge):

- Score harness is only exact `= /api/Challenges/` (v9 also proxied `/api/Challenges` without slash)
- Empty query and inbound Cookie closed on the score path; `Authorization` stripped
- Closed leftover privacy/identity/hidden/data HTTP routes v9 left to the catch-all (`location /data` is HTTP deny, not tmpfs over juice `data/static`)
- Broader static deny (php/asp/jsp/cgi/sh/py)
- Broader WAF-ish tokens (still signatures only; no PoC)
- CSP `script-src 'none'` / `connect-src 'none'`; extra Permissions-Policy; `limit_req_status 429`
- Tighter edge caps, juice pids/tmpfs/ulimits, body/rate (`5r/m`, burst>=1)

GET `/api/Challenges/` stays the only proxied path so the CASE score harness still works. No exploit PoC. Coding `/snippets` stay out of n/N.
