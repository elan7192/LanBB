---
name: conducting-external-reconnaissance-with-osint
description: Conduct external recon using OSINT techniques to map an organization's external attack surface without touching target systems, gathering DNS records, certificate transparency logs, search results, social media, code repositories, and breach databases into a target profile. Use for the passive info-gathering phase of a pentest, external footprinting, or collecting employee/email intel for a social engineering campaign.
domain: cybersecurity
subdomain: penetration-testing
tags:
- OSINT
- reconnaissance
- attack-surface
- footprinting
- passive-recon
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
- T1592
- T1589
- T1590
---

<!--
Copyright 2026 mukul975 (and skill author in frontmatter)
Licensed under the Apache License, Version 2.0
http://www.apache.org/licenses/LICENSE-2.0
Source: https://github.com/mukul975/Anthropic-Cybersecurity-Skills/blob/main/skills/conducting-external-reconnaissance-with-osint/SKILL.md

LanBB copy: payloads, exploit PoCs, attack procedures, C2, phishing tradecraft,
nuclei/sqlmap/AFL/nikto, and live-program hunting steps were stripped.
Kept: when-to-use, checklist (what to look for), report shape.
Authorized CASE / local Juice Shop lab only. Fail-closed without programs/<slug>/scope.md.
-->

# Conducting External Reconnaissance with OSINT

Copied for LanBB CASE UX / report shape. Attack procedures and payloads removed.

## When to Use

- Performing the initial reconnaissance phase of a penetration test to gather intelligence before active scanning
- Mapping an organization's external attack surface to identify unknown or shadow IT assets
- Identifying exposed credentials, leaked data, or sensitive documents published on the internet
- Scoping the breadth of an organization's digital footprint prior to a red team engagement

**Do not use** for stalking, harassment, or unauthorized surveillance of individuals. OSINT gathering must be conducted within the scope of an authorized engagement and comply with applicable privacy laws (GDPR, CCPA).

**LanBB:** authorized CASE and local Juice Shop lab only. Fail-closed without `programs/<slug>/scope.md`. Do not generate exploit payloads or PoCs. Do not hunt live programs or adult/porn programs.

## Key Concepts

| Term | Definition |
|------|------------|
| **OSINT** | Open Source Intelligence; intelligence collected from publicly available sources including websites, social media, public records, and government data |
| **Passive Reconnaissance** | Information gathering without directly interacting with target systems, leaving no footprint in target logs |
| **Active Reconnaissance** | Information gathering that involves direct interaction with target systems (scanning, probing) and may be logged |
| **Certificate Transparency** | Public logs of TLS certificates issued by certificate authorities, queryable to discover subdomains and infrastructure |
| **Attack Surface** | The sum of all points where an unauthorized user can attempt to enter or extract data from an environment |
| **Google Dorking** | Using advanced Google search operators to find sensitive information indexed by search engines that was not intended to be public |
| **Shadow IT** | Technology systems and services deployed by employees or departments without the knowledge or approval of the IT department |

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

- Domain and DNS Enumeration

- Infrastructure and Service Discovery

- Email and Personnel Intelligence

- Credential and Data Leak Analysis

- Technology Stack Profiling
