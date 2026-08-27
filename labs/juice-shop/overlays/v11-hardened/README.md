# v11-hardened

Stricter than `v10-hardened`. Previous wall. Next hunt must use `v12-hardened`, not v11.

This overlay is a **working harden** that actually applies. Fill on v10 scored live 0/116 (GET `/api/Challenges/` HTTP 200). Wall APPLIES: default-deny 403 on `/`, `/login`, `/api`. v11 keeps those apply constraints (no juice EROFS, no tmpfs over data/static, burst>=1, exact GET `/api/Challenges/` stays open). v5 juice `read_only` EROFS-skipped `.well-known/csaf` and `tmpfs /juice-shop/data` hid `data/static`. v11 does not copy those skipped locks. Juice stays at 128m so the score harness can still apply.

Keeps from v10 what actually applied:

- Image pin `bkimminich/juice-shop@sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e`
- Juice root writable; tmpfs only `/tmp` (not `data/static`); read-only **edge**
- Host bind `127.0.0.1:3000` only; GET only; host allowlist `127.0.0.1|localhost`
- Default-deny unmatched GET; URI WAF; cookie flags; COEP/HSTS; Trusted Types; Origin-Agent-Cluster; CSP sandbox
- App/edge caps, `NODE_ENV=production`, `limit_req` burst>=1 (never burst=0)
- Closed ftp/admin/upload/PII/chatbot/B2B/snippets/continue-code/GraphQL/basket/reviews/captcha/data-export/identity/Web3/catalog/search/info-leak/login/SPA-assets/remaining /api /rest / leftover SPA/Web3/payment/oauth/health/debug/privacy/hidden/data HTTP

Raises the wall (and keeps a working juice/edge):

- Score harness still exact `= /api/Challenges/`; inbound Authorization/Origin/Referer/X-Forwarded-For/X-Real-IP now closed (v10 only closed query + Cookie)
- Closed leftover continue-code-findIt/fixIt, login/search/Baskets, nested privacy-security SPA, address/payment, support/logs HTTP routes v10 left to the catch-all
- Broader static deny (ini/toml/pem/key/crt)
- Broader WAF-ish tokens (still signatures only; no PoC)
- CSP `worker-src 'none'` / `manifest-src 'none'`; extra Permissions-Policy; tighter `4r/m` (burst>=1)
- Tighter edge caps, juice pids/ulimits

GET `/api/Challenges/` stays the only proxied path so the CASE score harness still works. No exploit PoC. Coding `/snippets` stay out of n/N.
