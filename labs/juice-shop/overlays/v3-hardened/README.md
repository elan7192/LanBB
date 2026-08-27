# v3-hardened

Stricter than `v2-hardened`. Previous wall. Next hunt must use `v4-hardened`, not v3.

Keeps v2:

- Image pin `bkimminich/juice-shop@sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e`
- Security headers, login rate limit, WAF-ish block
- Closed `/ftp`, `/encryptionkeys`, `/metrics`, `/support`, `/redirect`, `/rest/admin`, GET `/api/Users`

Raises the wall:

- Method allowlist (GET/HEAD/POST/OPTIONS only); TRACE/TRACK/CONNECT stay 405
- WAF-ish match on `$request_uri` (path + query), not query-string only
- Tighter CSP (no `unsafe-inline`), COEP, HSTS, cookie flags
- Connection limit, smaller upload cap, lower login/API/search bursts
- Edge container: read-only root, tmpfs, `no-new-privileges`, `cap_drop ALL`
- Closed another class v2 left open: upload/profile/video, B2B, `/snippets`, chatbot/socket, order/PII/wallet/2FA, continue-code mutation

GET `/api/Challenges/` stays open so the CASE score harness still works. No exploit PoC. Coding `/snippets` stay out of n/N.
