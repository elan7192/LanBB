# Semantic memory — loop 17

Loop 17 hunted the v16-hardened wall, not v15 and not stock. Fill on the box after that overlay scored live 0/116 (GET /api/Challenges/ HTTP 200). Wall APPLIES: default-deny 403 on /, /login, /api. Edge mem 6m/pids 6 held. worker_processes 1 is source (no Fill patch). OOM=false. Do not rediscover. CASE tools did not auto-pwn.

Defense: v17-hardened keeps the working-harden apply constraints (no juice EROFS, no tmpfs over data/static, nginx limit_req burst>=1, GET /api/Challenges/ stays open for n/N, juice 128m) and the locked edge floor mem>=6m pids>=6. It keeps worker_processes 1 (not auto) after Fill proved the v16 source held, and raises the wall with leftover B3 sampled/flags/parent, Datadog parent/sampling/origin, Sentry-Trace, OpenTracing, Envoy, Azure Easy Auth principal, remaining GAE user-id/admin, CF-Access user-id, oauth2-proxy preferred-username, and TLS client-cert headers closed on the score path, leftover chatbot-respond/2FA-verify/codefixes HTTP routes closed, broader static deny, and extra headers/WAF signatures.

UX: Flow Studio now names that Fill on v16 also held nginx worker_processes 1 as source (OOM=false) beside the workers pill so a later overlay cannot copy auto or treat the v16 hold as a Fill patch. Catalog, inspector, and score API still carry worker_processes_oom and worker_processes_source. Report draft still carries Fill evidence so 0/N is not mistaken for a missed wall.

Coverage honesty: the 13-skill pack still does not cover Cryptographic Issues, Miscellaneous, Security Misconfiguration, or Security through Obscurity. Docker-off: Insecure Deserialization and XXE were not exercised. Coding /snippets stay out of n/N.

Product metric this loop is the same: report and memory emit still run when the wall is higher and the live Fill score is 0/N. Next hunt must use v17, not v16.
