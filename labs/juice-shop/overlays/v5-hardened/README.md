# v5-hardened

Stricter than `v4-hardened`. Previous wall. Next hunt must use `v6-hardened`, not v5.

Fill on this overlay: juice `read_only` SKIPPED (EROFS on `.well-known/csaf`). `tmpfs /juice-shop/data` hides `data/static`, so those container locks did not apply. nginx `limit_req` burst>=1 did apply. v6 does not copy the skipped juice locks.

Keeps v4:

- Image pin `bkimminich/juice-shop@sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e`
- Method allowlist, URI WAF, cookie flags, COEP/HSTS, tight CSP, Cache-Control, DNS prefetch off
- App/edge caps, `NODE_ENV=production`, read-only edge
- Closed ftp/admin/upload/PII/chatbot/B2B/snippets/continue-code/GraphQL/basket/reviews/captcha/data-export

Raises the wall:

- Juice app container: read-only root, tmpfs for data/tmp, tighter mem/pids/cpu, log caps
- Edge mem/pids/cpu tighter
- Drop OPTIONS from the method allowlist (GET/HEAD/POST only)
- Broader WAF-ish tokens; WAF now also on login (still signatures only; no PoC)
- `limit_req` burst>=1 (v4 used burst=0, which nginx rejects; Fill patched v4 to burst=1 so the edge listens)
- Tighter body/rate/connection/timeouts
- Trusted Types + Origin-Agent-Cluster
- Closed another class v4 left open: registration, password-reset, whoami/session, OAuth, Web3/NFT, catalog/search, hints/swagger/robots, remaining info-leak APIs

GET `/api/Challenges/` stays open so the CASE score harness still works. Login remains the remaining auth door. No exploit PoC. Coding `/snippets` stay out of n/N.
