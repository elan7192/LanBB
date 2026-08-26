---
name: prioritizing-vulnerabilities-with-cvss-scoring
description: The Common Vulnerability Scoring System (CVSS) is the industry standard
  framework maintained by FIRST (Forum of Incident Response and Security Teams) for
  assessing vulnerability severity. CVSS v4.0 (r
domain: cybersecurity
subdomain: vulnerability-management
tags:
- vulnerability-management
- cve
- cvss
- risk
- prioritization
- nist
version: '1.0'
author: mahipal
license: Apache-2.0
nist_csf:
- ID.RA-01
- ID.RA-02
- ID.IM-02
- ID.RA-06
mitre_attack:
- T1190
- T1203
- T1068
---

<!--
Copyright 2026 mukul975 (and skill author in frontmatter)
Licensed under the Apache License, Version 2.0
http://www.apache.org/licenses/LICENSE-2.0
Source: https://github.com/mukul975/Anthropic-Cybersecurity-Skills/blob/main/skills/prioritizing-vulnerabilities-with-cvss-scoring/SKILL.md

LanBB copy: payloads, exploit PoCs, attack procedures, C2, phishing tradecraft,
nuclei/sqlmap/AFL/nikto, and live-program hunting steps were stripped.
Kept: when-to-use, checklist (what to look for), report shape.
Authorized CASE / local Juice Shop lab only. Fail-closed without programs/<slug>/scope.md.
-->

# Prioritizing Vulnerabilities with CVSS Scoring

Copied for LanBB CASE UX / report shape. Attack procedures and payloads removed.

## Overview

The Common Vulnerability Scoring System (CVSS) is the industry standard framework maintained by FIRST (Forum of Incident Response and Security Teams) for assessing vulnerability severity. CVSS v4.0 (released November 2023) introduces refined metrics for more accurate scoring. This skill covers calculating CVSS scores, interpreting vector strings, and using CVSS alongside contextual factors like EPSS and CISA KEV for effective vulnerability prioritization.

## When to Use

- When managing security operations that require prioritizing vulnerabilities with cvss scoring
- When improving security program maturity and operational processes
- When establishing standardized procedures for security team workflows
- When integrating threat intelligence or vulnerability data into operations

**LanBB:** authorized CASE and local Juice Shop lab only. Fail-closed without `programs/<slug>/scope.md`. Do not generate exploit payloads or PoCs. Do not hunt live programs or adult/porn programs.

## Core Concepts

## Best Practices

1. Never rely solely on CVSS base score for prioritization
2. Always incorporate threat intelligence (EPSS, KEV, exploit databases)
3. Maintain accurate asset criticality ratings in your CMDB
4. Adjust environmental metrics for your specific deployment context
5. Use CVSS v4.0 vector strings for precise communication between teams
6. Document scoring rationale for audit trail and consistency
7. Re-evaluate scores when new threat intelligence becomes available
8. Train remediation teams on interpreting CVSS metrics and vector strings

## Common Pitfalls

- Treating CVSS base score as the sole prioritization factor
- Ignoring environmental metrics that reflect organizational risk
- Not updating threat metrics when exploit maturity changes
- Confusing CVSS severity with actual organizational risk
- Using outdated CVSS v2.0 scores instead of v3.1/v4.0
- Over-relying on scanner-provided scores without validation

## Related Skills

- prioritizing-patches-with-exploit-prediction-scoring
- implementing-risk-based-vulnerability-management
- implementing-vulnerability-remediation-sla

## Checklist (what to look for — no payloads)

Use only on in-scope lab hosts after `scope.md` parses. Record findings in `programs/<slug>/findings/`. Do not attach exploit steps.

- Assess Base Metrics

- Apply Threat Intelligence Context

- Calculate Environmental Score

- Multi-Factor Prioritization Matrix

- Define Remediation SLAs
