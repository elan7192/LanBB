# Semantic memory — loop 16

Loop 16 hunted the v15-hardened wall, not v14 and not stock. Fill on the box after that overlay scored live 0/116 (GET /api/Challenges/ HTTP 200). Wall APPLIES: default-deny 403 on /, /login, /api. Edge mem 6m/pids 6 held. worker_processes 1 is source (no Fill patch). OOM=false. Do not rediscover. CASE tools did not auto-pwn.

Defense: v16-hardened keeps the working-harden apply constraints (no juice EROFS, no tmpfs over data/static, nginx limit_req burst>=1, GET /api/Challenges/ stays open for n/N, juice 128m) and the locked edge floor mem>=6m pids>=6. It keeps worker_processes 1 (not auto) after Fill proved the v15 source held, and raises the wall with leftover W3C/B3/GCP/Datadog tracing plus ALB OIDC/IAP/Cloudflare Access/oauth2-proxy token-groups/Istio client-cert/GAE user identity headers closed on the score path, leftover CSAF/product-image/coupon-apply HTTP routes closed, broader static deny, and extra headers/WAF signatures.

UX: Flow Studio now names that nginx worker_processes 1 is source and OOM=false beside the workers pill so a later overlay cannot copy auto or assume a Fill patch is required. Catalog, inspector, and score API carry worker_processes_oom and worker_processes_source. Report draft still carries Fill evidence so 0/N is not mistaken for a missed wall.

Coverage honesty: the 13-skill pack still does not cover Cryptographic Issues, Miscellaneous, Security Misconfiguration, or Security through Obscurity. Docker-off: Insecure Deserialization and XXE were not exercised. Coding /snippets stay out of n/N.

Product metric this loop is the same: report and memory emit still run when the wall is higher and the live Fill score is 0/N. Next hunt must use v16, not v15.
