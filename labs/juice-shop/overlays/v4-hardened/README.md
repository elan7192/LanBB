# v4-hardened

Stricter than `v3-hardened`. Next hunt must use this wall, not v3.

Keeps v3:

- Image pin `bkimminich/juice-shop@sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e`
- Method allowlist, URI WAF, cookie flags, COEP/HSTS, read-only edge
- Closed `/ftp`, `/encryptionkeys`, `/metrics`, `/support`, `/redirect`, `/rest/admin`
- Closed upload/profile/video, B2B, `/snippets`, chatbot/socket, order/PII/wallet/2FA, continue-code

Raises the wall:

- Juice process: `cap_drop ALL`, `pids_limit`, `mem_limit` (v3 only locked the edge)
- Origin allowlist (loopback shop only) and scanner User-Agent deny
- Strip backend CORS headers
- Stronger WAF-ish signatures on `$request_uri` (concat/sleep/benchmark/fromCharCode/base64_decode)
- Smaller body cap, lower connection and API rates, login burst 0
- Closed another class v3 left open: registration POST `/api/Users`, reset/change-password, whoami/export, search, reviews/feedback/complaints, baskets/quantity, captcha, privacy/recycles/deliveries, promotions

GET `/api/Challenges/` stays open so the CASE score harness still works. No exploit PoC. Coding `/snippets` stay out of n/N.
