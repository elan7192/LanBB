---
name: testing-for-business-logic-vulnerabilities
description: Manually identifies flaws in application business logic - price manipulation,
  multi-step workflow bypass, and privilege escalation - by intercepting and modifying
  requests with Burp Suite, going beyond what automated vulnerability scanners detect.
  Use for e-commerce checkout/cart flows, voucher and rewards systems, or any assessment
  where scanners find little but business rules need scrutiny.
domain: cybersecurity
subdomain: web-application-security
tags:
- penetration-testing
- business-logic
- owasp
- web-security
- burpsuite
- manual-testing
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
Source: https://github.com/mukul975/Anthropic-Cybersecurity-Skills/blob/main/skills/testing-for-business-logic-vulnerabilities/SKILL.md

LanBB copy: payloads, exploit PoCs, attack procedures, C2, phishing tradecraft,
nuclei/sqlmap/AFL/nikto, and live-program hunting steps were stripped.
Kept: when-to-use, checklist (what to look for), report shape.
Authorized CASE / local Juice Shop lab only. Fail-closed without programs/<slug>/scope.md.
-->

# Testing for Business Logic Vulnerabilities

Copied for LanBB CASE UX / report shape. Attack procedures and payloads removed.

## When to Use

- During authorized penetration tests when automated scanners have found few technical vulnerabilities
- When assessing e-commerce platforms for pricing, cart, and payment flow manipulations
- For testing multi-step workflows (registration, checkout, approval processes) for bypass opportunities
- When evaluating rate-limited features like vouchers, coupons, referrals, and rewards systems
- During security assessments of financial applications, voting systems, or any application with critical business rules

**LanBB:** authorized CASE and local Juice Shop lab only. Fail-closed without `programs/<slug>/scope.md`. Do not generate exploit payloads or PoCs. Do not hunt live programs or adult/porn programs.

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Business Logic Flaw** | A vulnerability in the application's workflow or rules that allows unintended actions |
| **Price Manipulation** | Modifying price, quantity, or total values in client-side requests |
| **Workflow Bypass** | Skipping required steps in a multi-step business process |
| **Race Condition** | Exploiting concurrent request processing to violate business constraints |
| **Privilege Escalation** | Gaining higher permissions through business process manipulation |
| **Negative Testing** | Testing with unexpected values (negative, zero, null, extreme) |
| **State Manipulation** | Changing application state in an order not intended by the business logic |

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

- Map Business Workflows and Rules

- Test Price and Quantity Manipulation

- Test Workflow Step Bypass

- Test Race Conditions in Business Logic

- Test Referral and Reward System Abuse

- Test Role and Permission Logic
