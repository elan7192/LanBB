---
name: testing-api-security-with-owasp-top-10
description: Systematically assesses REST, GraphQL, and gRPC API endpoints against the OWASP
  API Security Top 10 (2023) using Burp Suite and Postman for automated and manual testing.
  Use during authorized API penetration tests, before deploying new endpoints to production,
  or when validating API gateway controls and rate limiting.
domain: cybersecurity
subdomain: web-application-security
tags:
- penetration-testing
- api-security
- owasp
- rest-api
- graphql
- burpsuite
- postman
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
---

<!--
Copyright 2026 mukul975 (and skill author in frontmatter)
Licensed under the Apache License, Version 2.0
http://www.apache.org/licenses/LICENSE-2.0
Source: https://github.com/mukul975/Anthropic-Cybersecurity-Skills/blob/main/skills/testing-api-security-with-owasp-top-10/SKILL.md

LanBB copy: payloads, exploit PoCs, attack procedures, C2, phishing tradecraft,
nuclei/sqlmap/AFL/nikto, and live-program hunting steps were stripped.
Kept: when-to-use, checklist (what to look for), report shape.
Authorized CASE / local Juice Shop lab only. Fail-closed without programs/<slug>/scope.md.
-->

# Testing API Security with OWASP Top 10

Copied for LanBB CASE UX / report shape. Attack procedures and payloads removed.

## When to Use

- During authorized API penetration testing engagements
- When assessing REST, GraphQL, or gRPC APIs for security vulnerabilities
- Before deploying new API endpoints to production environments
- When reviewing API security posture against the OWASP API Security Top 10 (2023)
- For validating API gateway security controls and rate limiting effectiveness

**LanBB:** authorized CASE and local Juice Shop lab only. Fail-closed without `programs/<slug>/scope.md`. Do not generate exploit payloads or PoCs. Do not hunt live programs or adult/porn programs.

## Key Concepts

| Concept | Description |
|---------|-------------|
| **BOLA (API1)** | Broken Object Level Authorization - accessing objects belonging to other users |
| **Broken Authentication (API2)** | Weak authentication mechanisms allowing credential stuffing or token manipulation |
| **BOPLA (API3)** | Broken Object Property Level Authorization - excessive data exposure or mass assignment |
| **Unrestricted Resource Consumption (API4)** | Missing rate limiting enabling DoS or brute-force attacks |
| **Broken Function Level Auth (API5)** | Regular users accessing admin-level API functions |
| **SSRF (API7)** | Server-Side Request Forgery through API parameters accepting URLs |
| **Security Misconfiguration (API8)** | Missing security headers, verbose errors, permissive CORS |
| **Improper Inventory (API9)** | Undocumented, deprecated, or shadow API endpoints left exposed |

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

- Discover and Map API Endpoints

- Test API1 - Broken Object Level Authorization (BOLA)

- Test API2 - Broken Authentication

- Test API3 - Broken Object Property Level Authorization

- Test API4/API6 - Rate Limiting and Unrestricted Access to Sensitive Flows

- Test API5 - Broken Function Level Authorization

- Test API7-API10 - SSRF, Misconfiguration, Inventory, and Unsafe Consumption
