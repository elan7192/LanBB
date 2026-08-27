# v14-hardened

Stricter than `v13-hardened`. Next hunt must use this wall, not v13.

This overlay is a **working harden** that actually applies. Fill on v13 scored live 0/116 (GET `/api/Challenges/` HTTP 200). Wall APPLIES: default-deny 403 on `/`, `/login`, `/api`. v14 keeps those apply constraints (no juice EROFS, no tmpfs over data/static, burst>=1, exact GET `/api/Challenges/` stays open). v5 juice `read_only` EROFS-skipped `.well-known/csaf` and `tmpfs /juice-shop/data` hid `data/static`. v14 does not copy those skipped locks. Juice stays at 128m so the score harness can still apply.

Fill on v13 also held the edge floor: compose `mem 6m` / `pids 6` (no patch). v11 `mem 4m` / `pids 4` FAILED (daemon min 6MB, can't fork). v14 keeps `mem>=6m` and `pids>=6`. Do not drop below that.

Keeps from v13 what actually applied:

- Image pin `bkimminich/juice-shop@sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e`
- Juice root writable; tmpfs only `/tmp` (not `data/static`); read-only **edge**
- Host bind `127.0.0.1:3000` only; GET only; host allowlist `127.0.0.1|localhost`
- Default-deny unmatched GET; URI WAF; cookie flags; COEP/HSTS; Trusted Types; Origin-Agent-Cluster; CSP sandbox
- App/edge caps, `NODE_ENV=production`, `limit_req` burst>=1 (never burst=0)
- Edge floor mem 6m / pids 6
- Closed ftp/admin/upload/PII/chatbot/B2B/snippets/continue-code/GraphQL/basket/reviews/captcha/data-export/identity/Web3/catalog/search/info-leak/login/SPA-assets/remaining /api /rest / leftover SPA/Web3/payment/oauth/health/debug/privacy/hidden/data/continue-code/login/search/Baskets/hacking-instructor/juicy-nft/continue-code-xss/products-queries/continue-code-apply/tutorial/access_token/ftp-backup HTTP

Raises the wall (and keeps a working juice/edge):

- Score harness still exact `= /api/Challenges/`; inbound X-Forwarded-Scheme, X-Original-Host, X-Forwarded-Server, X-Cluster-Client-IP, Fastly-Client-IP, Client-IP, X-Originating-IP, X-Remote-IP, X-Id-Token, X-Access-Token, X-Refresh-Token, X-Session-Token, X-Xsrf-Token, Api-Key, Auth-Token, Via now closed (v13 closed rewrite/identity headers)
- Closed leftover continue-code-findIt-apply/fixIt-apply, snippets/fixes, two-factor-authentication-enter SPA, web3 nft mint/unlock HTTP routes v13 left to the catch-all (HTTP deny only — not tmpfs over juice `data/static`). Do not forge continue-code.
- Broader leak deny (grafana/kibana/traefik/portainer/healthz/readyz/livez/_profiler/debug/pprof/telescope/graphiql/wp-login.php/phpinfo/.DS_Store)
- Broader WAF-ish tokens (still signatures only; no PoC)
- Extra Permissions-Policy; tighter `1r/m` (burst>=1)
- Edge floor mem 6m / pids 6 held (do not copy v11's failed 4m/4)

GET `/api/Challenges/` stays the only proxied path so the CASE score harness still works. No exploit PoC. Coding `/snippets` stay out of n/N.
