---
name: passive-recon
description: "Passive subdomain recon for an authorized CASE, only on in-scope domains. Optional subfaster/crt.name. Local Juice Shop skips public lookup. Not a probe, not nuclei."
---

# Passive subdomain recon

**Look up names already in public CT data for in-scope apexes. Never run this on an out-of-scope host. Local labs skip it.**

Portions adapted from [auditing-tls-certificate-transparency-logs](https://github.com/mukul975/Anthropic-Cybersecurity-Skills/blob/main/skills/auditing-tls-certificate-transparency-logs/SKILL.md) in [mukul975/Anthropic-Cybersecurity-Skills](https://github.com/mukul975/Anthropic-Cybersecurity-Skills) (Apache-2.0). Copyright 2026 mukul975.

This file is a reduced CASE skill. Deleted: phishing/typosquat hunting, CA disruption, nuclei, httpx probe chains, live-program hunting, and every non-CT step. Remaining idea: query public certificate data for **in-scope** names only.

Optional CLI (not vendored): [melvinsh/subfaster](https://github.com/melvinsh/subfaster) (homepage [crt.name](https://crt.name)).

```
go install -v github.com/melvinsh/subfaster/v2/cmd/subfaster@latest
subfaster -d <in-scope-apex>
```

## When to use

- After scope parse passes
- When the program lists a **public** in-scope apex
- Juice Shop / loopback / `.local`: skip public lookup; record the skip

Do not use for C2, phishing, nuclei, exploit packs, OOS domains, or random internet.

## Steps

1. **Load scope.** `lanbb recon` fails closed without `programs/<slug>/scope.md`. Pass `--domain` only if that host is in-scope.

2. **Skip local labs.** If in-scope is only `localhost` / `127.0.0.1` (Juice Shop docker), do not call subfaster. Write `recon/subdomains/skipped.txt`.

3. **Optional subfaster.** If a public in-scope apex exists and `subfaster` is installed, run it on that apex only. Do not add extra hosts from search engines.

4. **Keep evidence out of git.** Raw dumps stay under `programs/<slug>/recon/subdomains/` (gitignored). Notes in `notes.md` may list counts, not packet captures.

```bash
python3 tools/case/lanbb.py recon juice-shop
# Juice Shop is local — subfaster is skipped unless in-scope public domains exist
```

Licensed under the Apache License, Version 2.0. http://www.apache.org/licenses/LICENSE-2.0
