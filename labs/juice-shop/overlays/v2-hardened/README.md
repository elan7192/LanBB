# v2-hardened

Stricter than `v1-hardened`. Next hunt must use this wall, not v1.

Keeps v1:

- Security headers
- Login rate limit
- Extra-file path `/ftp` closed

Raises the wall:

- Image pin `bkimminich/juice-shop@sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e`
- Stronger headers (Permissions-Policy, COOP, CORP, tighter CSP)
- Broader rate limits (API, search, register, reset-password) and lower login burst
- WAF-ish query-string block on search and the default location
- Closed another class v1 left open: `/encryptionkeys`, `/metrics`, `/support`, `/redirect`, `/rest/admin`, GET `/api/Users`
- TRACE off, `server_tokens off`, smaller upload cap

GET `/api/Challenges/` stays open so the CASE score harness still works. No exploit PoC.
