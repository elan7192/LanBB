---
name: conducting-api-security-testing
description: 'Conducts security testing of REST, GraphQL, and gRPC APIs to identify
  vulnerabilities in authentication, authorization, rate limiting, input validation,
  and business logic. The tester uses the OWASP API Security Top 10 as the testing
  framework, combining Burp Suite interception with Postman collections and custom
  scripts to test endpoint security at every privilege level. Activates for requests
  involving API security testing, REST API pentest, GraphQL security assessment, or
  API vulnerability testing.

  '
domain: cybersecurity
subdomain: penetration-testing
tags:
- API-security
- OWASP-API-Top10
- REST
- GraphQL
- authorization-testing
version: 1.0.0
author: mahipal
license: Apache-2.0
nist_csf:
- ID.RA-01
- ID.RA-06
- GV.OV-02
- DE.AE-07
mitre_attack:
- T1190
- T1213
- T1552.001
- T1078
- T1071.001
---

<!--
Copyright 2026 mukul975 (and skill author in frontmatter)
Licensed under the Apache License, Version 2.0
http://www.apache.org/licenses/LICENSE-2.0
Source: https://github.com/mukul975/Anthropic-Cybersecurity-Skills/blob/main/skills/conducting-api-security-testing/SKILL.md

LanBB copy: payloads, exploit PoCs, attack procedures, C2, phishing tradecraft,
nuclei/sqlmap/AFL/nikto, and live-program hunting steps were stripped.
Kept: when-to-use, checklist (what to look for), report shape.
Authorized CASE / local Juice Shop lab only. Fail-closed without programs/<slug>/scope.md.
-->

# Conducting API Security Testing

Copied for LanBB CASE UX / report shape. Attack procedures and payloads removed.

## When to Use

- Testing API endpoints for authorization flaws, injection vulnerabilities, and business logic bypasses
- Assessing the security of microservices architecture where APIs are the primary communication method
- Validating that API gateway protections (rate limiting, authentication, input validation) are properly enforced
- Testing third-party API integrations for data exposure and insecure configurations
- Evaluating GraphQL APIs for introspection disclosure, query complexity attacks, and authorization bypasses

**Do not use** against APIs without written authorization, for load testing or denial-of-service testing unless explicitly scoped, or for testing production APIs that process real financial transactions without safeguards.

**LanBB:** authorized CASE and local Juice Shop lab only. Fail-closed without `programs/<slug>/scope.md`. Do not generate exploit payloads or PoCs. Do not hunt live programs or adult/porn programs.

## Key Concepts

| Term | Definition |
|------|------------|
| **BOLA** | Broken Object Level Authorization (OWASP API #1); failure to verify that the requesting user is authorized to access a specific object, enabling IDOR attacks |
| **BFLA** | Broken Function Level Authorization (OWASP API #5); failure to restrict administrative or privileged API functions from being accessed by lower-privilege users |
| **Mass Assignment** | A vulnerability where the API binds client-provided data to internal object properties without filtering, allowing attackers to modify fields they should not have access to |
| **GraphQL Introspection** | A built-in GraphQL feature that exposes the complete API schema including all types, fields, and relationships; should be disabled in production |
| **JWT** | JSON Web Token; a self-contained token format used for API authentication containing claims signed with a secret or key pair |
| **Rate Limiting** | Controls that restrict the number of API requests a client can make within a time window, preventing brute force, enumeration, and abuse |

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

- API Discovery and Documentation

- Authentication and Token Testing

- Authorization Testing (BOLA/BFLA)

- Input Validation and Injection Testing

- Data Exposure and Response Analysis
