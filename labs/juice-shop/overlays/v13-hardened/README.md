# v13-hardened

Stricter than `v12-hardened`. Previous wall. Next hunt must use `v14-hardened`, not v13.

This overlay is a **working harden** that actually applies. Fill on v12 scored live 0/116 (GET `/api/Challenges/` HTTP 200). Wall APPLIES: default-deny 403 on `/`, `/login`, `/api`. v13 keeps those apply constraints (no juice EROFS, no tmpfs over data/static, burst>=1, exact GET `/api/Challenges/` stays open). v5 juice `read_only` EROFS-skipped `.well-known/csaf` and `tmpfs /juice-shop/data` hid `data/static`. v13 does not copy those skipped locks. Juice stays at 128m so the score harness can still apply.

Fill on v12 also held the edge floor: compose `mem 6m` / `pids 6` (no patch). v11 `mem 4m` / `pids 4` FAILED (daemon min 6MB, can't fork). v13 keeps `mem>=6m` and `pids>=6`. Do not drop below that.

Keeps from v12 what actually applied:

- Image pin `bkimminich/juice-shop@sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e`
- Juice root writable; tmpfs only `/tmp` (not `data/static`); read-only **edge**
- Host bind `127.0.0.1:3000` only; GET only; host allowlist `127.0.0.1|localhost`
- Default-deny unmatched GET; URI WAF; cookie flags; COEP/HSTS; Trusted Types; Origin-Agent-Cluster; CSP sandbox
- App/edge caps, `NODE_ENV=production`, `limit_req` burst>=1 (never burst=0)
- Edge floor mem 6m / pids 6
- Closed ftp/admin/upload/PII/chatbot/B2B/snippets/continue-code/GraphQL/basket/reviews/captcha/data-export/identity/Web3/catalog/search/info-leak/login/SPA-assets/remaining /api /rest / leftover SPA/Web3/payment/oauth/health/debug/privacy/hidden/data/continue-code/login/search/Baskets/hacking-instructor/juicy-nft/continue-code-xss/products-queries HTTP

Raises the wall (and keeps a working juice/edge):

- Score harness still exact `= /api/Challenges/`; inbound X-Rewrite-URL, X-Original-URI, X-Forwarded-Prefix/Port, X-Host, True-Client-IP, CF-Connecting-IP, X-Client-IP, X-Requested-With, X-Csrf-Token, X-Api-Key, X-Auth-Token now closed (v12 closed X-Forwarded-Host/Proto, Forwarded, X-Original-URL, X-Http-Method-Override, Proxy-Authorization)
- Closed leftover continue-code-apply, tutorial/error SPA, oauth access_token, ftp/encryptionkeys backup-file HTTP routes v12 left to the catch-all (HTTP deny only — not tmpfs over juice `data/static`). Do not forge continue-code.
- Broader leak deny (prometheus/phpmyadmin/wp-admin/cgi-bin/nginx_status/solr/jenkins/.svn/.hg/webdav/.aws/jwks.json/.env)
- Broader WAF-ish tokens (still signatures only; no PoC)
- CSP `prefetch-src 'none'` / `block-all-mixed-content`; extra Permissions-Policy; tighter `2r/m` (burst>=1)
- Edge floor mem 6m / pids 6 held (do not copy v11's failed 4m/4)

GET `/api/Challenges/` stays the only proxied path so the CASE score harness still works. No exploit PoC. Coding `/snippets` stay out of n/N.
