# v5-hardened

Stricter than `v4-hardened`. Next hunt must use this wall, not v4.

Keeps v4:

- Image pin `bkimminich/juice-shop@sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e`
- Method allowlist, URI WAF, cookie/COEP/HSTS, read-only edge, GraphQL/basket/reviews/captcha/data-export closed

Raises the wall:

- App container: read-only root + tmpfs, lower memory/pids
- Edge: pinned `nginx:1.27-alpine`, lower memory/pids
- Score path GET/HEAD only (`limit_except` on `/api/Challenges`)
- Tighter body/rate/connection caps
- Closed another class v4 left open: registration, password-reset, whoami, product-search

GET `/api/Challenges/` stays open so the CASE score harness still works. No exploit PoC. Coding `/snippets` stay out of n/N.
