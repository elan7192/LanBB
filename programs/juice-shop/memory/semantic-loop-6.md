Loop 6 hunted the v5-hardened wall, not v4 and not stock. Fill on the box after that overlay scored live 0/116 (GET /api/Challenges/, docker_disabled=18). CASE tools did not auto-pwn and did not rediscover.

Defense: v6-hardened is now a working wall that actually applies. Fill found v5 juice read-only SKIPPED (EROFS on .well-known/csaf) and tmpfs /juice-shop/data hiding data/static, so those container locks did not apply. v6 keeps the v5 pin, dropped OPTIONS, identity/Web3/catalog closures, and nginx limit_req burst>=1, leaves juice root writable, tmpfs only /tmp (not data/static), keeps a read-only edge, then closes the remaining auth door, drops POST (GET/HEAD only), broadens WAF-ish signatures, tightens caps, and closes the SPA/static leak class.

UX: Flow Studio names coding /snippets as out of n/N beside n/N, fill, hunted, and next-hunt. Catalog rows carry coding_challenges and docker_disabled_env. versions.json records hunted=v5-hardened, wall=v6-hardened, fill=live 0/116.

Coverage honesty: the 13-skill pack still does not cover Cryptographic Issues, Miscellaneous, Security Misconfiguration, or Security through Obscurity. Docker-off: Insecure Deserialization and XXE were not exercised. Coding /snippets stay out of n/N.

Product metric this loop is the same: report and memory emit still run when the wall is higher and the live Fill score is 0/N. Next hunt must use v6, not v5.
