# v16-hardened

Stricter than `v15-hardened`. Next hunt must use this wall, not v15.

This overlay is a **working harden** that actually applies. Fill on v15 scored live 0/116 (GET `/api/Challenges/` HTTP 200). Wall APPLIES: default-deny 403 on `/`, `/login`, `/api`. v16 keeps those apply constraints (no juice EROFS, no tmpfs over data/static, burst>=1, exact GET `/api/Challenges/` stays open). v5 juice `read_only` EROFS-skipped `.well-known/csaf` and `tmpfs /juice-shop/data` hid `data/static`. v16 does not copy those skipped locks. Juice stays at 128m so the score harness can still apply.

Fill on v15 also held the edge floor: compose `mem 6m` / `pids 6`. v11 `mem 4m` / `pids 4` FAILED (daemon min 6MB, can't fork). v14 `worker_processes auto` OOM-killed nginx (exit 137). v15 baked `worker_processes 1`. Fill on v15: source `worker_processes 1` held (OOM=false, no Fill patch). v16 keeps `worker_processes 1`. Do not use `worker_processes auto`. Keep `mem>=6m` and `pids>=6`.

Keeps from v15 what actually applied:

- Image pin `bkimminich/juice-shop@sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e`
- Juice root writable; tmpfs only `/tmp` (not `data/static`); read-only **edge**
- Host bind `127.0.0.1:3000` only; GET only; host allowlist `127.0.0.1|localhost`
- Default-deny unmatched GET; URI WAF; cookie flags; COEP/HSTS; Trusted Types; Origin-Agent-Cluster; CSP sandbox
- App/edge caps, `NODE_ENV=production`, `limit_req` burst>=1 (never burst=0)
- Edge floor mem 6m / pids 6
- `worker_processes 1` (not auto)
- Closed ftp/admin/upload/PII/chatbot/B2B/snippets/continue-code/GraphQL/basket/reviews/captcha/data-export/identity/Web3/catalog/search/info-leak/login/SPA-assets/remaining /api /rest / leftover SPA/Web3/payment/oauth/health/debug/privacy/hidden/data/continue-code/login/search/Baskets/hacking-instructor/juicy-nft/continue-code-xss/products-queries/continue-code-apply/tutorial/access_token/ftp-backup/continue-code-findIt-apply/fixIt-apply/snippets-fixes/2FA-enter/web3-nft/web3-walletExploitAddress/2FA-SPA/ftp-quarantine/solve-server-side/coupon HTTP

Raises the wall (and keeps a working juice/edge):

- Score harness still exact `= /api/Challenges/`; inbound Tracestate, Baggage, X-B3-TraceId, X-B3-SpanId, X-Cloud-Trace-Context, X-Datadog-Trace-Id, X-Amzn-Oidc-Identity, X-Amzn-Oidc-Data, X-Amzn-Oidc-Accesstoken, X-Goog-Authenticated-User-Id, X-Goog-Iap-Jwt-Assertion, Cf-Access-Authenticated-User-Email, Cf-Access-Jwt-Assertion, X-Auth-Request-Access-Token, X-Auth-Request-Groups, X-Forwarded-Client-Cert, X-Appengine-User-Email now closed (v15 closed remote-user/oauth-proxy user-email/tracing/cloud-auth headers)
- Closed leftover CSAF, product-image, coupon-apply HTTP routes v15 left to the catch-all (HTTP deny only — not tmpfs over juice `data/static`). Do not forge continue-code.
- Broader leak deny (adminer/mongo-express/rabbitmq/consul/jaeger/zipkin/kiali/rancher/cockpit/longhorn)
- Broader WAF-ish tokens (still signatures only; no PoC)
- Extra Permissions-Policy (Client Hints / deferred-fetch / digital-credentials / keyboard-map); `worker_processes 1` (source, OOM=false)
- Edge floor mem 6m / pids 6 held (do not copy v11's failed 4m/4)

GET `/api/Challenges/` stays the only proxied path so the CASE score harness still works. No exploit PoC. Coding `/snippets` stay out of n/N.
