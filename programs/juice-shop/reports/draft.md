# CASE report: juice-shop

- Date (Taipei): 2026-08-27
- UTC: 2026-08-27T02:10:58Z
- Kind: lab
- Lab score: 0/116
- Fill: live GET /api/Challenges/ on v8-hardened
- Fill GET: 200
- Fill 403: /, /login, /api
- Fill POST: see versions.json
- Last live fill: 0/116 on v8-hardened
- Last live GET: 200
- Last live 403: /, /login, /api
- Last live POST: see versions.json
- Score path: GET = /api/Challenges/
- Bind: 127.0.0.1:3000
- Authorization: local-docker
- Hunted wall: v8-hardened
- Current wall: v9-hardened
- Applies: True (v8 Fill APPLIES: GET /api/Challenges/ 200, default-deny 403 on / /login /api; working harden EROFS_GONE, ReadonlyRootfs=false, tmpfs=/tmp only, data/static visible. v9 keeps those apply constraints plus exact-equals GET /api/Challenges/, host allowlist, leftover oauth/health/debug closed. Do not rediscover.)

## Judgment

Authorized CASE against the in-scope lab only. Fill live score 0/116 on v8-hardened. Report path completed without an exploit PoC.

## Scope

In scope:

- http://127.0.0.1:3000
- http://localhost:3000

Out of scope:

- Any host that is not this local lab
- Live bug-bounty programs
- Random internet
- Adult or porn programs

## Findings

None recorded. Empty findings are valid. This hunt did not auto-pwn the lab.

## Coverage honesty

13-skill pack does not cover: Cryptographic Issues, Miscellaneous, Security Misconfiguration, Security through Obscurity.
Docker-off: Insecure Deserialization, XXE.

## Close path

Harden the lab overlay (auth, WAF-ish rules, close the extra surface). Next hunt uses `v9-hardened` in `labs/juice-shop` (this loop hunted `v8-hardened`). Do not attach payloads or reproduction scripts.
