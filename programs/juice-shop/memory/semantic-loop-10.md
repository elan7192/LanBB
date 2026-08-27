# Semantic memory — loop 10

Loop 10 hunted the v9-hardened wall, not v8 and not stock. Fill on this Cloud VM was unavailable (GET /api/Challenges/ connection refused; docker not installed). Honest score 0/116. Last live Fill remains 0/116 on v8 (GET 200, default-deny 403 on /, /login, /api APPLIES). Do not invent n. Do not rediscover. CASE tools did not auto-pwn.

Defense: v10-hardened keeps the working-harden apply constraints (no juice EROFS, no tmpfs over data/static, nginx limit_req burst>=1, GET /api/Challenges/ stays open for n/N, juice 128m). It raises the wall with exact trailing-slash score location only (v9 also proxied /api/Challenges), empty-query and inbound Cookie closed on the score path, leftover privacy/identity/hidden/data HTTP routes closed (HTTP /data deny, not tmpfs over juice data/static), broader static deny, tighter edge caps, and extra headers/WAF signatures.

UX: Flow Studio names this hunt fill as unavailable beside last live fill (still 0/116 on v8), plus score path, bind, GET 200 / 403 default-deny on last-live, inspector, and score API. Report draft carries the same Fill evidence so 0/N is not mistaken for a missed wall or a forged live n.

Coverage honesty: the 13-skill pack still does not cover Cryptographic Issues, Miscellaneous, Security Misconfiguration, or Security through Obscurity. Docker-off: Insecure Deserialization and XXE were not exercised. Coding /snippets stay out of n/N.

Product metric this loop is the same: report and memory emit still run when the wall is higher and the live Fill score is 0/N. Next hunt must use v10, not v9.
