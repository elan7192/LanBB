# Semantic memory — loop 11

Loop 11 hunted the v10-hardened wall, not v9 and not stock. Fill on the box after that overlay scored live 0/116 (GET /api/Challenges/ HTTP 200). Wall APPLIES: default-deny 403 on /, /login, /api. Do not rediscover. CASE tools did not auto-pwn.

Defense: v11-hardened keeps the working-harden apply constraints (no juice EROFS, no tmpfs over data/static, nginx limit_req burst>=1, GET /api/Challenges/ stays open for n/N, juice 128m). It raises the wall with Authorization/Origin/Referer/X-Forwarded-For closed on the score path, leftover continue-code-findIt/fixIt plus login/search/Baskets/nested privacy-security SPA HTTP routes closed, broader static deny, tighter edge caps, and extra headers/WAF signatures.

UX: Flow Studio names last live fill beside this hunt's fill (now live 0/116 on v10), plus score path, bind, GET 200 / 403 default-deny on catalog, inspector, and score API. Report draft carries the same Fill evidence so 0/N is not mistaken for a missed wall.

Coverage honesty: the 13-skill pack still does not cover Cryptographic Issues, Miscellaneous, Security Misconfiguration, or Security through Obscurity. Docker-off: Insecure Deserialization and XXE were not exercised. Coding /snippets stay out of n/N.

Product metric this loop is the same: report and memory emit still run when the wall is higher and the live Fill score is 0/N. Next hunt must use v11, not v10.
