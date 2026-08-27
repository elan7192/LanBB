# Semantic memory — loop 14

Loop 14 hunted the v13-hardened wall, not v12 and not stock. Fill on the box after that overlay scored live 0/116 (GET /api/Challenges/ HTTP 200). Wall APPLIES: default-deny 403 on /, /login, /api. Edge mem 6m/pids 6 held (no compose patch). Do not rediscover. CASE tools did not auto-pwn.

Defense: v14-hardened keeps the working-harden apply constraints (no juice EROFS, no tmpfs over data/static, nginx limit_req burst>=1, GET /api/Challenges/ stays open for n/N, juice 128m) and the locked edge floor mem>=6m pids>=6. It raises the wall with leftover hop/session/token headers closed on the score path, leftover continue-code-findIt-apply/fixIt-apply/snippets-fixes/2FA-enter/web3-nft HTTP routes closed, broader static deny, and extra headers/WAF signatures.

UX: Flow Studio still names the edge floor (mem 6m / pids 6) beside last live fill so a later overlay cannot copy v11's failed 4m/4 or drop the floor that v12 and v13 Fill held. Catalog, inspector, and score API carry edge_floor_mem / edge_floor_pids. Report draft still carries Fill evidence so 0/N is not mistaken for a missed wall.

Coverage honesty: the 13-skill pack still does not cover Cryptographic Issues, Miscellaneous, Security Misconfiguration, or Security through Obscurity. Docker-off: Insecure Deserialization and XXE were not exercised. Coding /snippets stay out of n/N.

Product metric this loop is the same: report and memory emit still run when the wall is higher and the live Fill score is 0/N. Next hunt must use v14, not v13.
