Loop 5 hunted the v4-hardened wall, not v3 and not stock. Fill on the box after that overlay scored live 0/116 (GET /api/Challenges/, docker_disabled=18). CASE tools did not auto-pwn and did not rediscover.

Defense: v5-hardened is now the wall. It keeps the v4 pin, method allowlist, URI WAF, cookie/COEP/HSTS, app/edge caps, and closed GraphQL/basket/reviews/captcha/data-export surfaces, then raises juice read-only plus tmpfs, drops OPTIONS, applies WAF-ish signatures on login, bakes nginx limit_req burst>=1 (v4 burst=0 is invalid and Fill had to patch it so the edge listens), tightens body/rate/connection, and closes registration, password-reset, whoami/session, OAuth, Web3/NFT, catalog/search, hints/swagger/robots, and leftover info-leak APIs v4 left open.

UX: Flow Studio now names the next hunt. A next-hunt pill sits beside n/N, fill, and hunted so a live 0/N fill still points at the overlay that must be hunted next (v5, not v4). Catalog rows carry fill_wall, fill_reason, and next_hunt. Lab and harden inspectors list Fill wall, Fill reason, and Next hunt. versions.json records hunted=v4-hardened, wall=v5-hardened, fill=live 0/116.

Coverage honesty: the 13-skill pack still does not cover Cryptographic Issues, Miscellaneous, Security Misconfiguration, or Security through Obscurity. Docker-off: Insecure Deserialization and XXE were not exercised. Coding /snippets stay out of n/N.

Product metric this loop is the same: report and memory emit still run when the wall is higher and the live Fill score is 0/N. Next hunt must use v5, not v4.
