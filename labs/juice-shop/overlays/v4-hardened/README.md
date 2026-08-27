# v4-hardened

Stricter than `v3-hardened`. Next hunt must use this wall, not v3.

Keeps v3:

- Image pin `bkimminich/juice-shop@sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e`
- Method allowlist, URI WAF, cookie flags, COEP/HSTS, tight CSP
- Read-only edge, connection limit, closed ftp/admin/upload/PII/chatbot/B2B/snippets/continue-code

Raises the wall:

- App container: `cap_drop ALL`, memory/pids caps, `NODE_ENV=production`
- Edge memory/pids caps
- Broader WAF-ish tokens on `$request_uri` (still signatures only; no PoC)
- Tighter body/rate/connection caps
- Cache-Control no-store, DNS prefetch off
- Closed another class v3 left open: GraphQL, basket/commerce, reviews/feedback, captcha, remaining data-export

GET `/api/Challenges/` stays open so the CASE score harness still works. No exploit PoC. Coding `/snippets` stay out of n/N.
