# juice-shop case notes

Authorized CASE file. Evidence dumps, screenshots, and HTTP traffic stay gitignored.

1. Parse `scope.md` (fail-closed).
2. Passive recon only on in-scope domains. Local labs skip subfaster.
3. Record findings, then write a report. No exploit PoC generator.
4. After hunt→harden, emit memory (`lanbb case memory emit`). Not working memory. Not a wiki.

Loop 2 hunted `v1-hardened`. Score 0/116 (lab docker was not running in this agent VM). Report path still wrote. Wall became `v2-hardened`.

Loop 3 hunted `v2-hardened`. Fill live score **0/116** (GET `/api/Challenges/`, docker_disabled=18). Report path still wrote. Wall became `v3-hardened`.

Loop 4 hunted `v3-hardened`. Fill **unavailable** (GET `/api/Challenges/` connection refused; docker not installed). Honest score **0/116**. Report path still wrote. Wall is now `v4-hardened`.

Loop 5 hunted `v4-hardened`. Fill live score **0/116** (GET `/api/Challenges/`, docker_disabled=18). Report path still wrote. Wall is now `v5-hardened` (nginx `limit_req` burst>=1).

Loop 6 hunted `v5-hardened`. Fill live score **0/116** (GET `/api/Challenges/`, docker_disabled=18). v5 juice read-only SKIPPED (EROFS on `.well-known/csaf`); tmpfs `/juice-shop/data` hid `data/static`. Report path still wrote. Wall is now `v6-hardened` (working harden: no juice EROFS, no tmpfs over data/static; login closed; GET/HEAD only; SPA/static leak closed; nginx `limit_req` burst>=1).

Loop 7 hunted `v6-hardened`. Fill live score **0/116** (GET `/api/Challenges/`, docker_disabled=18). Wall APPLIES: EROFS_GONE, ReadonlyRootfs=false, tmpfs=/tmp only, data/static visible (challenges.yml 1593, securityQuestions.yml 29). Do not rediscover. Report path still wrote. Wall became `v7-hardened` (working harden with the same apply constraints; default-deny unmatched GET/HEAD except the score harness; leftover SPA/JS and remaining `/api` `/rest` closed; nginx `limit_req` burst>=1).

Loop 8 hunted `v7-hardened`. Fill live score **0/116** (GET `/api/Challenges/` HTTP 200, docker_disabled=18). Wall APPLIES: default-deny 403 on `/`, `/ftp`, `/api`, `/rest`, `/login`, `/assets`, `/snippets`, `/graphql`; POST on score path 405. Do not rediscover. Report path still wrote. Wall became `v8-hardened` (working harden: no juice EROFS, no tmpfs over data/static, burst>=1, GET `/api/Challenges/` stays open; exact score path; localhost bind; leftover SPA/Web3/payment closed).

Loop 9 hunted `v8-hardened`. Fill live score **0/116** (GET `/api/Challenges/` HTTP 200, docker_disabled=18). Wall APPLIES: default-deny 403 on `/`, `/login`, `/api`. Do not rediscover. Report path still wrote. Wall is now `v9-hardened` (working harden: no juice EROFS, no tmpfs over data/static, burst>=1, exact-equals GET `/api/Challenges/`; host allowlist; leftover oauth/health/debug closed).

Loop 10 hunted `v9-hardened`. Fill live score **0/116** (GET `/api/Challenges/` HTTP 200, docker_disabled=18). Wall APPLIES: default-deny 403 on `/`, `/login`, `/api`. Do not rediscover. Report path still wrote. Wall is now `v10-hardened` (working harden: no juice EROFS, no tmpfs over data/static, burst>=1, exact trailing-slash GET `/api/Challenges/` only; empty-query/cookie-closed score path; leftover privacy/hidden/data HTTP routes closed).

Loop 11 hunted `v10-hardened`. Fill **unavailable** (GET `/api/Challenges/` connection refused; docker not installed). Honest score **0/116**. Last live Fill remains **0/116** on v9-hardened (GET 200, default-deny 403 on `/`, `/login`, `/api`) APPLIES. Do not invent n. Report path still wrote. Wall is now `v11-hardened` (working harden: no juice EROFS, no tmpfs over data/static, burst>=1, exact GET `/api/Challenges/` stays open; Authorization/Origin/Referer/X-Forwarded-For closed on the score path; leftover continue-code/login/search/Baskets/nested privacy-security SPA HTTP routes closed).

Coverage honesty: the 13-skill pack does not cover Cryptographic Issues, Miscellaneous, Security Misconfiguration, Security through Obscurity. Docker-off: Insecure Deserialization, XXE.
