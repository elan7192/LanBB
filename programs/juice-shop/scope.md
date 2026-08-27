---
program: juice-shop
kind: lab
authorization: local-docker
wall: v4-hardened
hunted: v3-hardened
---

# OWASP Juice Shop (local lab)

Hypothetical in-scope shop. Not a live bounty program. Not random internet.

Current wall: `labs/juice-shop/overlays/v4-hardened/` (see `labs/juice-shop/versions.json`). Loop 4 hunted v3, then raised this wall.

## In scope

- http://127.0.0.1:3000
- http://localhost:3000

## Out of scope

- Any host that is not this local lab
- Live bug-bounty programs
- Random internet
- Adult or porn programs
