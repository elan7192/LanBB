---
name: testing-oauth2-implementation-flaws
description: Tests OAuth 2.0 and OpenID Connect implementations for authorization code
  interception, redirect URI manipulation, CSRF in OAuth flows, token leakage, scope
  escalation, and PKCE bypass, using Burp Suite Professional and the EsPReSSO extension
  to probe the authorization server, client, and token handling. Use when assessing OAuth2/OIDC
  flows or SSO systems for misconfigurations enabling account takeover.
domain: cybersecurity
subdomain: api-security
tags:
- api-security
- oauth2
- oidc
- authentication
- redirect-uri
- token-security
version: 1.0.0
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
- T1552.001
- T1027
- T1070
---

<!--
Copyright 2026 mukul975 (and skill author in frontmatter)
Licensed under the Apache License, Version 2.0
http://www.apache.org/licenses/LICENSE-2.0
Source: https://github.com/mukul975/Anthropic-Cybersecurity-Skills/blob/main/skills/testing-oauth2-implementation-flaws/SKILL.md

LanBB copy: payloads, exploit PoCs, attack procedures, C2, phishing tradecraft,
nuclei/sqlmap/AFL/nikto, and live-program hunting steps were stripped.
Kept: when-to-use, checklist (what to look for), report shape.
Authorized CASE / local Juice Shop lab only. Fail-closed without programs/<slug>/scope.md.
-->

# Testing OAuth2 Implementation Flaws

Copied for LanBB CASE UX / report shape. Attack procedures and payloads removed.

## When to Use

- Assessing OAuth 2.0 authorization code flow for redirect URI validation weaknesses
- Testing OAuth client applications for CSRF protection (state parameter usage) and PKCE enforcement
- Evaluating token storage, transmission, and lifecycle management in OAuth implementations
- Testing scope escalation where clients request more permissions than authorized
- Assessing OpenID Connect implementations for ID token validation and nonce usage

**Do not use** without written authorization. OAuth testing may result in token theft or unauthorized access.

**LanBB:** authorized CASE and local Juice Shop lab only. Fail-closed without `programs/<slug>/scope.md`. Do not generate exploit payloads or PoCs. Do not hunt live programs or adult/porn programs.

## Key Concepts

| Term | Definition |
|------|------------|
| **Authorization Code Flow** | OAuth 2.0 flow where the client receives an authorization code via redirect, then exchanges it for tokens at the token endpoint |
| **PKCE** | Proof Key for Code Exchange - extension that binds the authorization request to the token request using a code verifier/challenge, preventing authorization code interception |
| **Redirect URI Validation** | Authorization server verification that the redirect_uri matches the registered value exactly, preventing code/token theft via open redirect |
| **State Parameter** | Random value passed in the authorization request and verified in the callback to prevent CSRF attacks on the OAuth flow |
| **Scope Escalation** | Requesting or obtaining more permissions (scopes) than the client is authorized for, enabling unauthorized access |
| **Implicit Flow** | Deprecated OAuth flow that returns tokens directly in the URL fragment, vulnerable to token leakage and replay attacks |

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

- OAuth Flow Reconnaissance

- Redirect URI Validation Testing

- State Parameter (CSRF) Testing

- PKCE Bypass Testing

- Scope Escalation and Token Testing

- Implicit Flow and Token Leakage Testing
