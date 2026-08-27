---
name: testing-for-json-web-token-vulnerabilities
description: Tests JWT implementations for algorithm confusion, "none" algorithm bypass,
  kid/jku parameter injection, and weak secret exploitation using jwt_tool and Burp Suite's
  JWT Editor extension, aiming to achieve authentication bypass and privilege escalation.
  Use when assessing JWT-based auth/session management, OAuth2/OIDC token handling, or
  SSO systems during a security engagement.
domain: cybersecurity
subdomain: web-application-security
tags:
- jwt
- json-web-token
- algorithm-confusion
- authentication-bypass
- token-forgery
- kid-injection
- jku-attack
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
Source: https://github.com/mukul975/Anthropic-Cybersecurity-Skills/blob/main/skills/testing-for-json-web-token-vulnerabilities/SKILL.md

LanBB copy: payloads, exploit PoCs, attack procedures, C2, phishing tradecraft,
nuclei/sqlmap/AFL/nikto, and live-program hunting steps were stripped.
Kept: when-to-use, checklist (what to look for), report shape.
Authorized CASE / local Juice Shop lab only. Fail-closed without programs/<slug>/scope.md.
-->

# Testing for JSON Web Token Vulnerabilities

Copied for LanBB CASE UX / report shape. Attack procedures and payloads removed.

## When to Use

- When testing applications using JWT for authentication and session management
- During API security assessments where JWTs are used for authorization
- When evaluating OAuth 2.0 or OpenID Connect implementations using JWT
- During penetration testing of single sign-on (SSO) systems
- When auditing JWT library configurations for known vulnerabilities

**LanBB:** authorized CASE and local Juice Shop lab only. Fail-closed without `programs/<slug>/scope.md`. Do not generate exploit payloads or PoCs. Do not hunt live programs or adult/porn programs.

## Key Concepts

| Concept | Description |
|---------|-------------|
| Algorithm confusion | Server accepts a different signing algorithm than it advertised |
| Unsigned token | Server accepts a token with no signature |
| Key identifier | `kid` / `jku` / `x5u` headers are trusted without an allowlist |
| Weak secret | HMAC secret is short or guessable |
| Token replay | Expired or reused tokens are still accepted |

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

- Decode and Analyze JWT Structure

- Record whether unsigned tokens are rejected

- Record whether advertised alg is enforced

- Obtain the public key

- Forge token using public key as HMAC secret

- Record whether kid/jku/x5u are allowlisted

- Record key-source header handling in the report

- Generate key pair

- Host JWKS on attacker server

- Modify JWT header to point to attacker JWKS

- Note secret policy in the report (do not crack secrets)
