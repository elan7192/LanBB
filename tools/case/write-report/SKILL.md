---
name: write-report
description: "Write an authorized CASE disclosure report from the case file. Find + report. No exploit PoC generator. Report path must still work at 0/N."
---

# Write a report

**Turn in-scope notes into a program report. Attach only evidence already in the case file. Do not generate exploit PoCs, payloads, or attack procedures.**

Portions adapted from [generating-threat-intelligence-reports](https://github.com/mukul975/Anthropic-Cybersecurity-Skills/blob/main/skills/generating-threat-intelligence-reports/SKILL.md) in [mukul975/Anthropic-Cybersecurity-Skills](https://github.com/mukul975/Anthropic-Cybersecurity-Skills) (Apache-2.0). Copyright 2026 mukul975 / team-cybersecurity.

This file is a reduced CASE skill. Deleted: IOC/YARA dumps, flash campaign products, live-program tasking. Remaining idea: lead with the finding, cite evidence, recommend a close path.

## When to use

- After scope and authorization gates
- When closing a Juice Shop hunt, including **0/N**
- When the lab wall is higher and nothing new was solved — still write the report

Do not use to generate PoCs, nuclei templates, C2, or phishing.

## Steps

1. **Confirm the case folder.** Need `scope.md`. If missing, stop (fail-closed).

2. **Lead with the judgment.** One sentence: what is in-scope, what was found (or not found), current lab score `n/N`.

3. **Scope block.** Quote in-scope / out-of-scope from `scope.md`. Name the wall version (`labs/juice-shop` overlay), not a live company.

4. **Findings.** For each item in `findings/`, write: title, affected in-scope surface, impact in plain language, evidence pointer (path in the case file). If findings is empty, say so. Empty is valid.

5. **No PoC section.** Do not include payloads, exploit steps, or reproduction scripts. The program already has the lab.

6. **Close path.** What the lab owner should harden next (auth, WAF-ish rule, that class of bug) — not how to weaponize it.

```bash
python3 tools/case/lanbb.py case report juice-shop
```

Writes `programs/juice-shop/reports/draft.md`. Product metric: the report path works even when score is 0/N.

Licensed under the Apache License, Version 2.0. http://www.apache.org/licenses/LICENSE-2.0
