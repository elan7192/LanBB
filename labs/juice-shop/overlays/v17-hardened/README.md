# v17-hardened

Stricter than `v16-hardened`. Next hunt must use this wall, not v16.

This overlay is a **working harden** that actually applies. Fill on v16 scored live 0/116 (GET `/api/Challenges/` HTTP 200). Wall APPLIES: default-deny 403 on `/`, `/login`, `/api`. v17 keeps those apply constraints (no juice EROFS, no tmpfs over data/static, burst>=1, exact GET `/api/Challenges/` stays open). v5 juice `read_only` EROFS-skipped `.well-known/csaf` and `tmpfs /juice-shop/data` hid `data/static`. v17 does not copy those skipped locks. Juice stays at 128m so the score harness can still apply.

Fill on v16 also held the edge floor: compose `mem 6m` / `pids 6`. v11 `mem 4m` / `pids 4` FAILED (daemon min 6MB, can't fork). v14 `worker_processes auto` OOM-killed nginx (exit 137). v15 baked `worker_processes 1`. Fill on v15 and v16: source `worker_processes 1` held (OOM=false, no Fill patch). v17 keeps `worker_processes 1`. Do not use `worker_processes auto`. Keep `mem>=6m` and `pids>=6`.

Keeps from v16 what actually applied:

- Image pin `bkimminich/juice-shop@sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e`
- Juice root writable; tmpfs only `/tmp` (not `data/static`); read-only **edge**
- Host bind `127.0.0.1:3000` only; GET only; host allowlist `127.0.0.1|localhost`
- Default-deny unmatched GET; URI WAF; cookie flags; COEP/HSTS; Trusted Types; Origin-Agent-Cluster; CSP sandbox
- App/edge caps, `NODE_ENV=production`, `limit_req` burst>=1 (never burst=0)
- Edge floor mem 6m / pids 6
- `worker_processes 1` (not auto)
- Closed ftp/admin/upload/PII/chatbot/B2B/snippets/continue-code/GraphQL/basket/reviews/captcha/data-export/identity/Web3/catalog/search/info-leak/login/SPA-assets/remaining /api /rest / leftover SPA/Web3/payment/oauth/health/debug/privacy/hidden/data/continue-code/login/search/Baskets/hacking-instructor/juicy-nft/continue-code-xss/products-queries/continue-code-apply/tutorial/access_token/ftp-backup/continue-code-findIt-apply/fixIt-apply/snippets-fixes/2FA-enter/web3-nft/web3-walletExploitAddress/2FA-SPA/ftp-quarantine/solve-server-side/coupon/CSAF/product-image/coupon-apply HTTP

Raises the wall (and keeps a working juice/edge):

- Score harness still exact `= /api/Challenges/`; inbound X-B3-Sampled, X-B3-Flags, X-B3-ParentSpanId, X-Datadog-Parent-Id, X-Datadog-Sampling-Priority, X-Datadog-Origin, Sentry-Trace, X-Ot-Span-Context, X-Envoy-Internal, X-Envoy-External-Address, X-Envoy-Original-Path, X-MS-Client-Principal, X-MS-Client-Principal-Id, X-MS-Client-Principal-Name, X-Appengine-User-Id, X-Appengine-User-Is-Admin, Cf-Access-Authenticated-User-Id, X-Auth-Request-Preferred-Username, X-Forwarded-Tls-Client-Cert now closed (v16 closed W3C/B3 trace/span, Datadog trace-id, ALB OIDC/IAP/CF-Access jwt/email, oauth2-proxy token-groups, Istio client-cert, GAE user-email)
- Closed leftover chatbot-respond, 2FA-verify, data/static/codefixes HTTP routes v16 left to the catch-all (HTTP deny only — not tmpfs over juice `data/static`). Do not forge continue-code. Coding `/snippets` stay out of n/N.
- Broader leak deny (keycloak/authentik/kong/apisix/istio/linkerd/envoy/gitea/gitlab/spinnaker)
- Broader WAF-ish tokens (still signatures only; no PoC)
- Extra Permissions-Policy (remaining Client Hints / private-state-token-redemption); `worker_processes 1` (source, OOM=false)
- Edge floor mem 6m / pids 6 held (do not copy v11's failed 4m/4)

GET `/api/Challenges/` stays the only proxied path so the CASE score harness still works. No exploit PoC. Coding `/snippets` stay out of n/N.
