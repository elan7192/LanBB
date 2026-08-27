---
name: testing-for-broken-access-control
description: Systematically tests web applications and APIs for broken access control
  (OWASP A01:2021), including privilege escalation, missing function-level checks, insecure
  direct object references, and multi-tenant data leakage, using Burp Suite with the
  Authorize extension. Use during authorized penetration tests or RBAC/multi-tenant
  authorization audits.
domain: cybersecurity
subdomain: web-application-security
tags:
- penetration-testing
- access-control
- authorization
- owasp
- privilege-escalation
- web-security
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
- T1068
---

<!--
Copyright 2026 mukul975 (and skill author in frontmatter)
Licensed under the Apache License, Version 2.0
http://www.apache.org/licenses/LICENSE-2.0
Source: https://github.com/mukul975/Anthropic-Cybersecurity-Skills/blob/main/skills/testing-for-broken-access-control/SKILL.md

LanBB copy: payloads, exploit PoCs, attack procedures, C2, phishing tradecraft,
nuclei/sqlmap/AFL/nikto, and live-program hunting steps were stripped.
Kept: when-to-use, checklist (what to look for), report shape.
Authorized CASE / local Juice Shop lab only. Fail-closed without programs/<slug>/scope.md.
-->

# Testing for Broken Access Control

Copied for LanBB CASE UX / report shape. Attack procedures and payloads removed.

## When to Use

- During authorized penetration tests as the primary assessment for OWASP A01:2021 - Broken Access Control
- When evaluating role-based access control (RBAC) implementations across all application endpoints
- For testing multi-tenant applications where users in one organization should not access another's data
- When assessing API endpoints for missing or inconsistent authorization checks
- During security audits where privilege escalation and unauthorized access are primary concerns

**LanBB:** authorized CASE and local Juice Shop lab only. Fail-closed without `programs/<slug>/scope.md`. Do not generate exploit payloads or PoCs. Do not hunt live programs or adult/porn programs.

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Vertical Privilege Escalation** | Lower-privilege user accessing higher-privilege functionality (user -> admin) |
| **Horizontal Privilege Escalation** | User accessing another user's resources at the same privilege level |
| **Function-Level Access Control** | Authorization checks on specific features/functions regardless of URL |
| **RBAC** | Role-Based Access Control - permissions assigned to roles, roles assigned to users |
| **ABAC** | Attribute-Based Access Control - permissions based on user/resource/environment attributes |
| **Multi-Tenant Isolation** | Ensuring data and functionality separation between different organizations/tenants |
| **Insecure Direct Object Reference** | Accessing objects by manipulating identifiers without authorization checks |
| **Missing Function-Level Check** | Endpoint exists but does not verify the caller has permission to invoke it |

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

- Map All Endpoints and Create Access Control Matrix

- Configure Automated Access Control Testing

- Test Vertical Privilege Escalation

- Test Horizontal Privilege Escalation

- Test Function-Level Access Control

- Test Multi-Tenant Isolation
