---
name: parse-scope
description: "Parse a program scope file into in-scope and out-of-scope hosts. Use before any CASE recon or report. Fail-closed: no programs/<slug>/scope.md means no target."
---

# Parse program scope

**Read `programs/<slug>/scope.md` first. Missing file, empty in-scope, or an out-of-scope host stops the case.**

LanBB-authored. Catalogue skills for pentest recon were not copied (they mix OOS, social engineering, and live-program hunting). This skill is the CASE gate only.

## When to use

- Opening a case (`lanbb case new <slug>`)
- Before passive recon or a report draft
- When a host might be out of scope

Do not use for live-program attacks, adult/porn programs, or any target without a scope file.

## Steps

1. **Refuse without a file.** `programs/<slug>/scope.md` must exist. If it does not, stop. Do not guess scope from the internet.

2. **Parse lists.** Read YAML frontmatter (`kind`, `authorization`) and the `## In scope` / `## Out of scope` lists. Hosts may be URLs or host[:port]. Loopback (`localhost`, `127.0.0.1`) is valid for the Juice Shop lab.

3. **Classify the target.** A host is allowed only when it matches an in-scope entry (exact host, or subdomain of an in-scope apex) and does not match out-of-scope. Unknown is a fail, not a pass.

4. **Drop noise.** Adult/porn slugs are refused. Score loops are lab-only (`kind: lab`). Never treat random internet as in-scope.

5. **Record the parse.** Write a short note in `programs/<slug>/notes.md` listing in-scope hosts. Do not store raw HTTP dumps in git.

```bash
python3 tools/case/lanbb.py scope parse juice-shop
```
