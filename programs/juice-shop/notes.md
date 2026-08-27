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

Coverage honesty: the 13-skill pack does not cover Cryptographic Issues, Miscellaneous, Security Misconfiguration, Security through Obscurity. Docker-off: Insecure Deserialization, XXE.
