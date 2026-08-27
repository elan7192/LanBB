Loop 3 hunted the v2-hardened wall, not v1 and not stock. Fill on the box after that overlay scored live 0/116 (GET /api/Challenges/, docker_disabled=18). CASE tools did not auto-pwn and did not rediscover.

Defense: v3-hardened is now the wall. It keeps the v2 pin, headers, rate-limits, query WAF, and closed surfaces, then raises method allowlist, URI-wide WAF-ish matching, cookie flags, COEP/HSTS, a tighter CSP, connection limits, a read-only edge container, and closes upload/PII/chatbot/B2B/snippets/continue-code surfaces v2 left open.

UX: Flow Studio now shows hunt vs current wall — a wall pill next to n/N, catalog rows carry wall, and the lab node inspector lists hunted / current / score. versions.json records hunted=v2-hardened, wall=v3-hardened, fill=live 0/116.

Coverage honesty: the 13-skill pack still does not cover Cryptographic Issues, Miscellaneous, Security Misconfiguration, or Security through Obscurity. Docker-off: Insecure Deserialization and XXE were not exercised. Coding /snippets stay out of n/N.

Product metric this loop is the same: report and memory emit still run when the wall is higher and the live Fill score is 0/N. Next hunt must use v3, not v2.
