# CASE report: juice-shop

- Date (Taipei): 2026-08-27
- UTC: 2026-08-27T03:02:48Z
- Kind: lab
- Lab score: 0/116
- Fill: live GET /api/Challenges/ on v13-hardened
- Fill GET: 200
- Fill 403: /, /login, /api
- Fill POST: see versions.json
- Last live fill: 0/116 on v13-hardened
- Last live GET: 200
- Last live 403: /, /login, /api
- Last live POST: see versions.json
- Score path: GET = /api/Challenges/
- Bind: 127.0.0.1:3000
- Edge floor: mem 6m / pids 6
- Edge floor reason: Fill on v11: compose mem 4m/pids 4 FAILED (daemon min 6MB, can't fork). Fill on v12 and v13: mem 6m/pids 6 held (no patch). Live floor is mem 6m pids 6. v14 keeps mem>=6m and pids>=6. Do not drop below that.
- Authorization: local-docker
- Hunted wall: v13-hardened
- Current wall: v14-hardened
- Applies: True (v13 Fill APPLIES: GET /api/Challenges/ 200, default-deny 403 on / /login /api; working harden EROFS_GONE, ReadonlyRootfs=false, tmpfs=/tmp only, data/static visible. Edge mem 6m pids 6 held (no patch). v14 keeps those apply constraints and the floor, plus leftover hop/session/token headers closed on the score path, leftover continue-code-findIt-apply/fixIt-apply/snippets-fixes/2FA-enter/web3-nft HTTP routes closed. Do not rediscover.)

## Judgment

Authorized CASE against the in-scope lab only. Fill live score 0/116 on v13-hardened. Report path completed without an exploit PoC.

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

Harden the lab overlay (auth, WAF-ish rules, close the extra surface). Next hunt uses `v14-hardened` in `labs/juice-shop` (this loop hunted `v13-hardened`). Do not attach payloads or reproduction scripts.
