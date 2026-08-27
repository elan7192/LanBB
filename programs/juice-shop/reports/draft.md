# CASE report: juice-shop

- Date (Taipei): 2026-08-27
- UTC: 2026-08-27T02:43:23Z
- Kind: lab
- Lab score: 0/116
- Fill: live GET /api/Challenges/ on v11-hardened
- Fill GET: 200
- Fill 403: /, /login, /api
- Fill POST: see versions.json
- Last live fill: 0/116 on v11-hardened
- Last live GET: 200
- Last live 403: /, /login, /api
- Last live POST: see versions.json
- Score path: GET = /api/Challenges/
- Bind: 127.0.0.1:3000
- Edge floor: mem 6m / pids 6
- Edge floor reason: Fill on v11: compose mem 4m/pids 4 FAILED (daemon min 6MB, can't fork). Live floor is mem 6m pids 6. v12 bakes mem>=6m and pids>=6. Do not drop below that.
- Authorization: local-docker
- Hunted wall: v11-hardened
- Current wall: v12-hardened
- Applies: True (v11 Fill APPLIES: GET /api/Challenges/ 200, default-deny 403 on / /login /api; working harden EROFS_GONE, ReadonlyRootfs=false, tmpfs=/tmp only, data/static visible. v11 edge 4m/4 FAILED (daemon min 6MB). v12 keeps those apply constraints, bakes edge mem>=6m pids>=6, plus extra hop/auth headers closed on the score path, leftover hacking-instructor/juicy-nft/continue-code-xss/products-queries HTTP routes closed. Do not rediscover.)

## Judgment

Authorized CASE against the in-scope lab only. Fill live score 0/116 on v11-hardened. Report path completed without an exploit PoC.

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

Harden the lab overlay (auth, WAF-ish rules, close the extra surface). Next hunt uses `v12-hardened` in `labs/juice-shop` (this loop hunted `v11-hardened`). Do not attach payloads or reproduction scripts.
