# v15-hardened

Stricter than `v14-hardened`. Next hunt must use this wall, not v14.

This overlay is a **working harden** that actually applies. Fill on v14 scored live 0/116 (GET `/api/Challenges/` HTTP 200). Wall APPLIES: default-deny 403 on `/`, `/login`, `/api`. v15 keeps those apply constraints (no juice EROFS, no tmpfs over data/static, burst>=1, exact GET `/api/Challenges/` stays open). v5 juice `read_only` EROFS-skipped `.well-known/csaf` and `tmpfs /juice-shop/data` hid `data/static`. v15 does not copy those skipped locks. Juice stays at 128m so the score harness can still apply.

Fill on v14 also held the edge floor: compose `mem 6m` / `pids 6`. v11 `mem 4m` / `pids 4` FAILED (daemon min 6MB, can't fork). v14 `worker_processes auto` OOM-killed nginx (exit 137); Fill patched `worker_processes 1` so the edge still listens. v15 bakes `worker_processes 1`. Do not use `worker_processes auto`. Keep `mem>=6m` and `pids>=6`.

Keeps from v14 what actually applied:

- Image pin `bkimminich/juice-shop@sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e`
- Juice root writable; tmpfs only `/tmp` (not `data/static`); read-only **edge**
- Host bind `127.0.0.1:3000` only; GET only; host allowlist `127.0.0.1|localhost`
- Default-deny unmatched GET; URI WAF; cookie flags; COEP/HSTS; Trusted Types; Origin-Agent-Cluster; CSP sandbox
- App/edge caps, `NODE_ENV=production`, `limit_req` burst>=1 (never burst=0)
- Edge floor mem 6m / pids 6
- Closed ftp/admin/upload/PII/chatbot/B2B/snippets/continue-code/GraphQL/basket/reviews/captcha/data-export/identity/Web3/catalog/search/info-leak/login/SPA-assets/remaining /api /rest / leftover SPA/Web3/payment/oauth/health/debug/privacy/hidden/data/continue-code/login/search/Baskets/hacking-instructor/juicy-nft/continue-code-xss/products-queries/continue-code-apply/tutorial/access_token/ftp-backup/continue-code-findIt-apply/fixIt-apply/snippets-fixes/2FA-enter/web3-nft HTTP

Raises the wall (and keeps a working juice/edge):

- Score harness still exact `= /api/Challenges/`; inbound X-Remote-User, Remote-User, X-Forwarded-User, X-Forwarded-Email, X-Auth-Request-User, X-Auth-Request-Email, X-Original-Forwarded-For, WL-Proxy-Client-IP, X-Appengine-Remote-Addr, X-Amzn-Trace-Id, Traceparent, X-Request-Id, X-Correlation-Id, CF-Ray, X-Goog-Authenticated-User-Email now closed (v14 closed hop/session/token headers)
- Closed leftover web3 walletExploitAddress, two-factor-authentication SPA, ftp/quarantine, solve/challenges/server-side, coupon HTTP routes v14 left to the catch-all (HTTP deny only — not tmpfs over juice `data/static`). Do not forge continue-code.
- Broader leak deny (netdata/cadvisor/minio/pgadmin/sonarqube/argocd/vault/harbor/nexus/airflow)
- Broader WAF-ish tokens (still signatures only; no PoC)
- Extra Permissions-Policy; `worker_processes 1` (not auto)
- Edge floor mem 6m / pids 6 held (do not copy v11's failed 4m/4)

GET `/api/Challenges/` stays the only proxied path so the CASE score harness still works. No exploit PoC. Coding `/snippets` stay out of n/N.
