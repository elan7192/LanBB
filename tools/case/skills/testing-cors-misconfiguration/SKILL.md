---
name: testing-cors-misconfiguration
description: Identifying and exploiting Cross-Origin Resource Sharing misconfigurations
  that allow unauthorized cross-domain data access and credential theft during security
  assessments.
domain: cybersecurity
subdomain: web-application-security
tags:
- penetration-testing
- cors
- web-security
- owasp
- same-origin-policy
- burpsuite
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
- T1003
---

<!--
Copyright 2026 mukul975 (and skill author in frontmatter)
Licensed under the Apache License, Version 2.0
http://www.apache.org/licenses/LICENSE-2.0
Source: https://github.com/mukul975/Anthropic-Cybersecurity-Skills/blob/main/skills/testing-cors-misconfiguration/SKILL.md

LanBB copy: payloads, exploit PoCs, attack procedures, C2, phishing tradecraft,
nuclei/sqlmap/AFL/nikto, and live-program hunting steps were stripped.
Kept: when-to-use, checklist (what to look for), report shape.
Authorized CASE / local Juice Shop lab only. Fail-closed without programs/<slug>/scope.md.
-->

# Testing CORS Misconfiguration

Copied for LanBB CASE UX / report shape. Attack procedures and payloads removed.

## When to Use

- During authorized penetration tests when assessing API endpoints for cross-origin access controls
- When testing single-page applications that make cross-origin API requests
- When assessing microservice architectures with multiple domains sharing data
- During security audits of applications using CORS headers for cross-domain communication

**LanBB:** authorized CASE and local Juice Shop lab only. Fail-closed without `programs/<slug>/scope.md`. Do not generate exploit payloads or PoCs. Do not hunt live programs or adult/porn programs.

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Same-Origin Policy** | Browser security model preventing scripts from one origin accessing data from another |
| **CORS** | Mechanism allowing servers to specify which origins can access their resources |
| **Origin Reflection** | Server mirrors the request Origin header in the ACAO response header (dangerous) |
| **Null Origin** | Special origin value from sandboxed iframes, data URIs, and redirects |
| **Preflight Request** | OPTIONS request sent before certain cross-origin requests to check permissions |
| **Credentialed Requests** | Cross-origin requests that include cookies, requiring explicit ACAO + ACAC headers |
| **Wildcard CORS** | `Access-Control-Allow-Origin: *` allows any origin but prohibits credentials |

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

- Identify CORS Configuration on Target Endpoints

- Test Origin Reflection and Validation Bypass

- Test Preflight Request Handling

- Craft CORS Exploitation Proof of Concept

- Exploit Null Origin Vulnerability

- Test for Internal Network Access via CORS
