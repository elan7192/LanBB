Loop 8 hunted the v7-hardened wall, not v6 and not stock. Fill on the box after that overlay scored live 0/116 (GET /api/Challenges/ HTTP 200). Wall APPLIES: default-deny 403 on /, /ftp, /api, /rest, /login, /assets, /snippets, /graphql; POST on the score path 405. Do not rediscover. CASE tools did not auto-pwn.

Defense: v8-hardened keeps the working-harden apply constraints (no juice EROFS, no tmpfs over data/static, nginx limit_req burst>=1, GET /api/Challenges/ stays open for n/N). It raises the wall with an exact GET /api/Challenges/ score path (not the v7 prefix), localhost bind 127.0.0.1:3000, GET-only (HEAD dropped), leftover SPA/Web3/payment routes closed, broader static deny, tighter caps/ulimits, and extra headers/WAF signatures.

UX: Flow Studio names last live fill beside this hunt's fill (now live 0/116 on v7), plus score path, bind, GET 200 / 403 default-deny / POST 405 on catalog, inspector, and score API. Report draft carries the same Fill evidence so 0/N is not mistaken for a missed wall.

Coverage honesty: the 13-skill pack still does not cover Cryptographic Issues, Miscellaneous, Security Misconfiguration, or Security through Obscurity. Docker-off: Insecure Deserialization and XXE were not exercised. Coding /snippets stay out of n/N.

Product metric this loop is the same: report and memory emit still run when the wall is higher and the live Fill score is 0/N. Next hunt must use v8, not v7.
