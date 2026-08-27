Loop 2 hunted the v1-hardened wall, not stock. Score stayed 0/116: the lab docker was not running in this VM, and CASE tools still do not auto-pwn.

Defense: v2-hardened is now the wall. It keeps v1 headers, login rate-limit, and /ftp closed, then raises auth/WAF-ish/headers/rate-limit and closes extra surfaces v1 left open (encryptionkeys, metrics, redirect, admin, GET /api/Users). Image is pinned. GET /api/Challenges stays open for n/N.

UX: Juice Shop lab node, first-class last_score n/N on the CASE graph plus the studio pill, skill-pick limited to the 13 copied testing/UX skills, harden node after report (lab overlay, not a LanBB merge), and fail-closed skip-approval so e:route:cursor/lanbb/search visit approval:lead first.

Coverage honesty: the 13-skill pack does not cover Cryptographic Issues, Miscellaneous, Security Misconfiguration, or Security through Obscurity. Docker-off: Insecure Deserialization and XXE were not exercised.

Product metric this loop is the same: report and memory emit still run when the wall is higher and the score is 0/N. Next hunt must use v2, not v1.
