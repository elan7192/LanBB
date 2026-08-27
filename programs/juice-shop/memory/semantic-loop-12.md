# Semantic memory — loop 12

Loop 12 hunted the v11-hardened wall, not v10 and not stock. Fill on the box after that overlay scored live 0/116 (GET /api/Challenges/ HTTP 200). Wall APPLIES: default-deny 403 on /, /login, /api. Do not rediscover. CASE tools did not auto-pwn.

Defense: v12-hardened keeps the working-harden apply constraints (no juice EROFS, no tmpfs over data/static, nginx limit_req burst>=1, GET /api/Challenges/ stays open for n/N, juice 128m). Fill also showed v11 edge mem 4m/pids 4 FAILED (daemon min 6MB, can't fork); live floor is mem 6m pids 6, so v12 bakes mem>=6m and pids>=6. It raises the wall with extra hop/auth headers closed on the score path, leftover hacking-instructor/juicy-nft/continue-code-xss/products-queries HTTP routes closed, broader static deny, and extra headers/WAF signatures.

UX: Flow Studio names the edge floor (mem 6m / pids 6) beside last live fill so a later overlay cannot copy v11's failed 4m/4. Catalog, inspector, and score API carry edge_floor_mem / edge_floor_pids. Report draft still carries Fill evidence so 0/N is not mistaken for a missed wall.

Coverage honesty: the 13-skill pack still does not cover Cryptographic Issues, Miscellaneous, Security Misconfiguration, or Security through Obscurity. Docker-off: Insecure Deserialization and XXE were not exercised. Coding /snippets stay out of n/N.

Product metric this loop is the same: report and memory emit still run when the wall is higher and the live Fill score is 0/N. Next hunt must use v12, not v11.
