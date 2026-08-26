---
name: testing-for-xss-vulnerabilities
description: Tests web applications for reflected, stored, and DOM-based Cross-Site
  Scripting by injecting JavaScript payloads with Burp Suite (XSS extensions, Active
  Scan++) and browser tools, then bypassing sanitization and CSP to demonstrate session
  hijacking and user impersonation. Use for OWASP WSTG client-side injection testing or
  when evaluating input sanitization and output encoding coverage.
domain: cybersecurity
subdomain: penetration-testing
tags:
- XSS
- cross-site-scripting
- client-side-security
- OWASP-A03
- JavaScript-injection
version: 1.0.0
author: mahipal
license: Apache-2.0
nist_csf:
- ID.RA-01
- ID.RA-06
- GV.OV-02
- DE.AE-07
mitre_attack:
- T1595
- T1190
- T1059
- T1078
- T1055
---

<!--
Copyright 2026 mukul975 (and skill author in frontmatter)
Licensed under the Apache License, Version 2.0
http://www.apache.org/licenses/LICENSE-2.0
Source: https://github.com/mukul975/Anthropic-Cybersecurity-Skills/blob/main/skills/testing-for-xss-vulnerabilities/SKILL.md

LanBB copy: payloads, exploit PoCs, attack procedures, C2, phishing tradecraft,
nuclei/sqlmap/AFL/nikto, and live-program hunting steps were stripped.
Kept: when-to-use, checklist (what to look for), report shape.
Authorized CASE / local Juice Shop lab only. Fail-closed without programs/<slug>/scope.md.
-->

# Testing for XSS Vulnerabilities

Copied for LanBB CASE UX / report shape. Attack procedures and payloads removed.

## When to Use

- Testing web applications for client-side injection vulnerabilities as part of OWASP WSTG testing
- Evaluating the effectiveness of input sanitization and output encoding across all application features
- Assessing the protection provided by Content Security Policy (CSP) headers against XSS exploitation
- Testing single-page applications (React, Angular, Vue) for DOM-based XSS in client-side routing and rendering


**LanBB:** authorized CASE and local Juice Shop lab only. Fail-closed without `programs/<slug>/scope.md`. Do not generate exploit payloads or PoCs. Do not hunt live programs or adult/porn programs.

## Key Concepts

| Term | Definition |
|------|------------|
| **DOM-Based XSS** | XSS that occurs entirely in the browser when client-side JavaScript reads attacker-controlled data and writes it to a dangerous DOM sink |
| **Content Security Policy** | HTTP response header that restricts which sources the browser can load scripts, styles, and other resources from, providing defense-in-depth against XSS |
| **Output Encoding** | Converting special characters to their HTML entity equivalents (e.g., `<` to `&lt;`) to prevent the browser from interpreting user input as code |
| **Sink** | A JavaScript function or DOM property that can cause code execution or HTML rendering if attacker-controlled data reaches it unsanitized |

## Output Format

Write `programs/<slug>/reports/draft.md` (and a finding note under `findings/` if anything is in-scope). No exploit PoC, no payload, no reproduction script.

```
## CASE finding
- Program / wall:
- In-scope surface:
- Class (OWASP / CWE if known):
- Evidence pointer (path in the case file only):
- Impact in plain language:
- Close path (how the lab overlay should get harder):
```

## Checklist (what to look for — no payloads)

Use only on in-scope lab hosts after `scope.md` parses. Record findings in `programs/<slug>/findings/`. Do not attach exploit steps.

- Input and Output Mapping

- Reflected XSS Testing

- Stored XSS Testing

- DOM-Based XSS Testing

- CSP Bypass and Advanced Exploitation
