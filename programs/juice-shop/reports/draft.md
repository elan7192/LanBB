# CASE report: juice-shop

- Date (Taipei): 2026-08-27
- UTC: 2026-08-27T02:18:54Z
- Kind: lab
- Lab score: 0/116
- Fill: unavailable GET /api/Challenges/ on v9-hardened
- Fill GET: unavailable
- Fill 403: unavailable
- Fill POST: unavailable
- Last live fill: 0/116 on v8-hardened
- Last live GET: 200
- Last live 403: /, /login, /api
- Last live POST: see versions.json
- Score path: GET = /api/Challenges/
- Bind: 127.0.0.1:3000
- Authorization: local-docker
- Hunted wall: v9-hardened
- Current wall: v10-hardened
- Applies: True (Last live Fill on v8 APPLIES: GET /api/Challenges/ 200, default-deny 403 on / /login /api; working harden EROFS_GONE, ReadonlyRootfs=false, tmpfs=/tmp only, data/static visible. This hunt Fill on v9 was unavailable (no docker). v10 keeps those apply constraints plus exact trailing-slash GET /api/Challenges/ only, empty-query/cookie-closed score path, leftover privacy/hidden/data HTTP routes closed. Do not rediscover.)

## Judgment

Authorized CASE against the in-scope lab only. Fill unavailable score 0/116 on v9-hardened. Report path completed without an exploit PoC.

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

Harden the lab overlay (auth, WAF-ish rules, close the extra surface). Next hunt uses `v10-hardened` in `labs/juice-shop` (this loop hunted `v9-hardened`). Do not attach payloads or reproduction scripts.
