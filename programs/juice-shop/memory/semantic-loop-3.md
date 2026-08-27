Loop 3 hunted the v2-hardened wall, not v1 and not stock. Score stayed 0/116: this VM has no Docker and nothing listens on :3000. CASE tools still do not auto-pwn.

Defense: v3-hardened is now the wall. It keeps the v2 pin, headers, rate-limits, query WAF, and closed surfaces, then raises method allowlist, URI-wide WAF-ish matching, cookie flags, COEP/HSTS, a tighter CSP, connection limits, a read-only edge container, and closes upload/PII/chatbot/B2B/snippets/continue-code surfaces v2 left open.

UX: Flow Studio now shows hunt vs current wall — a wall pill next to n/N, catalog rows carry wall, and the lab node inspector lists hunted / current / score. versions.json records hunted=v2-hardened and wall=v3-hardened so a 0/N fill still names the overlay the next hunt must use.

Coverage honesty: the 13-skill pack still does not cover Cryptographic Issues, Miscellaneous, Security Misconfiguration, or Security through Obscurity. Docker-off: Insecure Deserialization and XXE were not exercised. Coding /snippets stay out of n/N.

Product metric this loop is the same: report and memory emit still run when the wall is higher and the score is 0/N. Next hunt must use v3, not v2.
