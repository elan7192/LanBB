---
name: testing-for-open-redirect-vulnerabilities
description: Identifies and exploits open redirect vulnerabilities by analyzing URL
  redirection parameters (next, url, redirect, return, goto), applying bypass techniques,
  and chaining findings into phishing or token-theft exploits, using Burp Suite/OWASP ZAP
  and Burp Collaborator. Use when testing login/logout flows, OAuth redirect_uri handling,
  or SSO redirect validation.
domain: cybersecurity
subdomain: web-application-security
tags:
- open-redirect
- url-redirect
- phishing
- owasp
- url-validation
- redirect-bypass
- unvalidated-redirect
version: '1.0'
author: mahipal
license: Apache-2.0
nist_csf:
- PR.PS-01
- ID.RA-01
- PR.DS-10
- DE.CM-01
mitre_attack:
- T1190
- T1059.007
- T1505.003
- T1083
- T1566
---

<!--
Copyright 2026 mukul975 (and skill author in frontmatter)
Licensed under the Apache License, Version 2.0
http://www.apache.org/licenses/LICENSE-2.0
Source: https://github.com/mukul975/Anthropic-Cybersecurity-Skills/blob/main/skills/testing-for-open-redirect-vulnerabilities/SKILL.md

LanBB copy: payloads, exploit PoCs, attack procedures, C2, phishing tradecraft,
nuclei/sqlmap/AFL/nikto, and live-program hunting steps were stripped.
Kept: when-to-use, checklist (what to look for), report shape.
Authorized CASE / local Juice Shop lab only. Fail-closed without programs/<slug>/scope.md.
-->

# Testing for Open Redirect Vulnerabilities

Copied for LanBB CASE UX / report shape. Attack procedures and payloads removed.

## When to Use

- When testing login/logout flows that redirect users to specified URLs
- During assessment of OAuth authorization endpoints with redirect_uri parameters
- When auditing applications with URL parameters (next, url, redirect, return, goto, target)
- When testing SSO implementations for redirect validation weaknesses

**LanBB:** authorized CASE and local Juice Shop lab only. Fail-closed without `programs/<slug>/scope.md`. Do not generate exploit payloads or PoCs. Do not hunt live programs or adult/porn programs.

## Key Concepts

| Concept | Description |
|---------|-------------|
| Unvalidated Redirect | Application redirects to user-supplied URL without checking destination |
| URL Parsing Inconsistency | Different libraries parse URLs differently, enabling bypass |
| Protocol-Relative URL | Using // prefix to redirect while inheriting current protocol |
| Userinfo Abuse | Using @ symbol to make URL appear to belong to trusted domain |
| Open Redirect Chain | Combining multiple open redirects or chaining with other vulnerabilities |
| DOM-Based Redirect | Client-side JavaScript performing redirect using attacker-controlled input |
| Meta Refresh Redirect | HTML meta tag performing redirect without server-side 302 |

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

- Identify Redirect Parameters

- Test Basic Open Redirect Payloads

- Apply Validation Bypass Techniques

- Test Path-Based Redirects

- Chain with Other Vulnerabilities

- Find open redirect on target.com

- Use it as redirect_uri in OAuth flow

- Automate Open Redirect Testing
