# CASE report: juice-shop

- Date (Taipei): 2026-08-27
- UTC: 2026-08-27T00:48:41Z
- Kind: lab
- Lab score: 0/116
- Fill: live GET /api/Challenges/ on v4-hardened
- Authorization: local-docker
- Hunted wall: v4-hardened
- Current wall: v5-hardened

## Judgment

Authorized CASE against the in-scope lab only. Fill live score 0/116 on v4-hardened. Report path completed without an exploit PoC.

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

Harden the lab overlay (auth, WAF-ish rules, close the extra surface). Next hunt uses `v5-hardened` in `labs/juice-shop` (this loop hunted `v4-hardened`). Do not attach payloads or reproduction scripts.
