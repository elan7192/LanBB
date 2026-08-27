# Semantic memory — loop 15

Loop 15 hunted the v14-hardened wall, not v13 and not stock. Fill on the box after that overlay scored live 0/116 (GET /api/Challenges/ HTTP 200). Wall APPLIES: default-deny 403 on /, /login, /api. Edge mem 6m/pids 6 held. worker_processes auto OOM-killed nginx (exit 137); Fill patched worker_processes 1 so the edge still listens. Do not rediscover. CASE tools did not auto-pwn.

Defense: v15-hardened keeps the working-harden apply constraints (no juice EROFS, no tmpfs over data/static, nginx limit_req burst>=1, GET /api/Challenges/ stays open for n/N, juice 128m) and the locked edge floor mem>=6m pids>=6. It bakes worker_processes 1 (not auto) so the 6m edge still listens, and raises the wall with leftover remote-user/oauth-proxy/tracing/cloud-auth headers closed on the score path, leftover web3-walletExploitAddress/2FA-SPA/ftp-quarantine/solve-server-side/coupon HTTP routes closed, broader static deny, and extra headers/WAF signatures.

UX: Flow Studio now names nginx worker_processes 1 (not auto) beside the edge floor so a later overlay cannot copy v14's auto OOM. Catalog, inspector, and score API carry worker_processes. Report draft still carries Fill evidence so 0/N is not mistaken for a missed wall.

Coverage honesty: the 13-skill pack still does not cover Cryptographic Issues, Miscellaneous, Security Misconfiguration, or Security through Obscurity. Docker-off: Insecure Deserialization and XXE were not exercised. Coding /snippets stay out of n/N.

Product metric this loop is the same: report and memory emit still run when the wall is higher and the live Fill score is 0/N. Next hunt must use v15, not v14.
