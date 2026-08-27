# v7-hardened

Stricter than `v6-hardened`. Previous wall. Next hunt must use `v8-hardened`, not v7.

This overlay is a **working harden** that actually applies. Fill on v7 scored live 0/116 (GET `/api/Challenges/` HTTP 200). Wall APPLIES: default-deny 403 on `/`, `/ftp`, `/api`, `/rest`, `/login`, `/assets`, `/snippets`, `/graphql`; POST on the score path 405. Fill on v6 had already confirmed EROFS_GONE, ReadonlyRootfs=false, tmpfs=/tmp only, data/static visible. v7 keeps those apply constraints. v5 juice `read_only` EROFS-skipped `.well-known/csaf` and `tmpfs /juice-shop/data` hid `data/static`. v7 does not copy those skipped locks.

Keeps from v6 what actually applied:

- Image pin `bkimminich/juice-shop@sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e`
- Juice root writable; tmpfs only `/tmp` (not `data/static`); read-only **edge**
- Method allowlist GET/HEAD only; URI WAF; cookie flags; COEP/HSTS; Trusted Types; Origin-Agent-Cluster
- App/edge caps, `NODE_ENV=production`, `limit_req` burst>=1 (never burst=0)
- Closed ftp/admin/upload/PII/chatbot/B2B/snippets/continue-code/GraphQL/basket/reviews/captcha/data-export/identity/Web3/catalog/search/info-leak/login/SPA-assets

Raises the wall (and keeps a working juice/edge):

- Default-deny unmatched GET/HEAD: `location /` no longer `proxy_pass`es to juice
- Remaining `/api` and `/rest` namespaces closed except GET `/api/Challenges/`
- Closed leftover SPA shell (`location = /`) plus leftover frontend routes v6 left open
- Closed root JS/CSS/ico leak (v6 closed `/assets` only)
- Broader WAF-ish tokens (still signatures only; no PoC)
- `X-Download-Options`; explicit PUT/PATCH/DELETE 405
- Tighter mem/pids/cpu, body/rate/connection/timeouts
- Score harness also rate-limited (`burst>=1`)

GET `/api/Challenges/` stays the only proxied path so the CASE score harness still works. No exploit PoC. Coding `/snippets` stay out of n/N.
