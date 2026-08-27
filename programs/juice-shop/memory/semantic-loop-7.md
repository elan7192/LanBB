Loop 7 hunted the v6-hardened wall, not v5 and not stock. Fill on the box after that overlay scored live 0/116 (GET /api/Challenges/, docker_disabled=18). Do not rediscover. CASE tools did not auto-pwn.

Defense: v6 wall APPLIES (EROFS_GONE, ReadonlyRootfs=false, tmpfs=/tmp only, data/static visible: challenges.yml 1593, securityQuestions.yml 29). v7-hardened keeps those apply constraints (no juice EROFS, no tmpfs over data/static, nginx limit_req burst>=1), then default-denies unmatched GET/HEAD so juice is no longer the fallback, closes remaining /api and /rest namespaces except the score harness, closes leftover SPA routes and root JS/CSS, tightens caps, and adds X-Download-Options plus broader WAF-ish tokens.

UX: Flow Studio names whether the wall applies beside n/N, fill, hunted, next-hunt, and coding /snippets. Catalog rows carry applies. versions.json records hunted=v6-hardened, wall=v7-hardened, fill=live 0/116, applies=true with EROFS_GONE evidence.

Coverage honesty: the 13-skill pack still does not cover Cryptographic Issues, Miscellaneous, Security Misconfiguration, or Security through Obscurity. Docker-off: Insecure Deserialization and XXE were not exercised. Coding /snippets stay out of n/N.

Product metric this loop is the same: report and memory emit still run when the wall is higher and the live Fill score is 0/N. Next hunt must use v7, not v6.
