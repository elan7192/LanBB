# CASE report: juice-shop

- Date (Taipei): 2026-08-27
- UTC: 2026-08-27T01:09:51Z
- Kind: lab
- Lab score: 0/116
- Fill: unavailable GET /api/Challenges/ on v6-hardened
- Authorization: local-docker
- Hunted wall: v6-hardened
- Current wall: v7-hardened
- Applies: True (working harden: no juice EROFS, no tmpfs over data/static; edge default-deny except GET /api/Challenges/)

## Judgment

Authorized CASE against the in-scope lab only. Fill unavailable score 0/116 on v6-hardened. Report path completed without an exploit PoC.

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

Harden the lab overlay (auth, WAF-ish rules, close the extra surface). Next hunt uses `v7-hardened` in `labs/juice-shop` (this loop hunted `v6-hardened`). Do not attach payloads or reproduction scripts.
