# v12-hardened

Stricter than `v11-hardened`. Next hunt must use this wall, not v11.

This overlay is a **working harden** that actually applies. Fill on v11 scored live 0/116 (GET `/api/Challenges/` HTTP 200). Wall APPLIES: default-deny 403 on `/`, `/login`, `/api`. v12 keeps those apply constraints (no juice EROFS, no tmpfs over data/static, burst>=1, exact GET `/api/Challenges/` stays open). v5 juice `read_only` EROFS-skipped `.well-known/csaf` and `tmpfs /juice-shop/data` hid `data/static`. v12 does not copy those skipped locks. Juice stays at 128m so the score harness can still apply.

Fill on v11 also showed the edge floor: compose `mem 4m` / `pids 4` FAILED (daemon min 6MB, can't fork). Live floor is **mem 6m pids 6**. v12 bakes `mem>=6m` and `pids>=6`. Do not drop below that.

Keeps from v11 what actually applied:

- Image pin `bkimminich/juice-shop@sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e`
- Juice root writable; tmpfs only `/tmp` (not `data/static`); read-only **edge**
- Host bind `127.0.0.1:3000` only; GET only; host allowlist `127.0.0.1|localhost`
- Default-deny unmatched GET; URI WAF; cookie flags; COEP/HSTS; Trusted Types; Origin-Agent-Cluster; CSP sandbox
- App/edge caps, `NODE_ENV=production`, `limit_req` burst>=1 (never burst=0)
- Closed ftp/admin/upload/PII/chatbot/B2B/snippets/continue-code/GraphQL/basket/reviews/captcha/data-export/identity/Web3/catalog/search/info-leak/login/SPA-assets/remaining /api /rest / leftover SPA/Web3/payment/oauth/health/debug/privacy/hidden/data/continue-code/login/search/Baskets HTTP

Raises the wall (and keeps a working juice/edge):

- Score harness still exact `= /api/Challenges/`; inbound X-Forwarded-Host/Proto, Forwarded, X-Original-URL, X-Http-Method-Override, Proxy-Authorization now closed (v11 closed Authorization/Origin/Referer/X-Forwarded-For/X-Real-IP)
- Closed leftover hacking-instructor/juicy-nft/wallet-web3, continue-code-xss, products/queries, admin application, b2b v2, data/static HTTP routes v11 left to the catch-all (`location /data/static` is HTTP deny, not tmpfs over juice `data/static`)
- Broader static deny (jar/war/ear/class/so/dll)
- Broader WAF-ish tokens (still signatures only; no PoC)
- CSP `navigate-to 'none'`; extra Permissions-Policy; tighter `3r/m` (burst>=1)
- Edge floor mem 6m / pids 6 (do not copy v11's failed 4m/4)

GET `/api/Challenges/` stays the only proxied path so the CASE score harness still works. No exploit PoC. Coding `/snippets` stay out of n/N.
