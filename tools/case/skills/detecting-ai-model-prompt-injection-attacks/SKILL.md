---
name: detecting-ai-model-prompt-injection-attacks
description: Detects prompt injection using regex signature matching, heuristic scoring for structural anomalies, and DeBERTa-based transformer classification, flagging direct injections (system-prompt overrides, role-play escapes) and indirect injections (encoded payloads, obfuscation) per OWASP LLM Top 10 (LLM01:2025). Use for input validation layers in chatbots/agents/RAG pipelines, or for retrospectively classifying injection attempts in logs or incident investigations.
domain: cybersecurity
subdomain: ai-security
tags:
- prompt-injection
- LLM-security
- OWASP-LLM-Top10
- NLP-classification
- input-validation
version: 1.0.0
author: mukul975
license: Apache-2.0
atlas_techniques:
- AML.T0051
- AML.T0054
- AML.T0056
- AML.T0068
- AML.T0067
nist_ai_rmf:
- GOVERN-1.1
- GOVERN-6.1
- MEASURE-2.7
- MEASURE-2.5
- MANAGE-2.4
d3fend_techniques:
- Content Validation
- Content Filtering
- Application Hardening
- Inbound Traffic Filtering
- User Behavior Analysis
nist_csf:
- GV.OC-03
- ID.RA-01
- PR.PS-01
- DE.AE-02
mitre_attack:
- T1659
- T1566
- T1204
- T1588.007
- T1565
---

<!--
Copyright 2026 mukul975 (and skill author in frontmatter)
Licensed under the Apache License, Version 2.0
http://www.apache.org/licenses/LICENSE-2.0
Source: https://github.com/mukul975/Anthropic-Cybersecurity-Skills/blob/main/skills/detecting-ai-model-prompt-injection-attacks/SKILL.md

LanBB copy: payloads, exploit PoCs, attack procedures, C2, phishing tradecraft,
nuclei/sqlmap/AFL/nikto, and live-program hunting steps were stripped.
Kept: when-to-use, checklist (what to look for), report shape.
Authorized CASE / local Juice Shop lab only. Fail-closed without programs/<slug>/scope.md.
-->

# Detecting AI Model Prompt Injection Attacks

Copied for LanBB CASE UX / report shape. Attack procedures and payloads removed.

## When to Use

- Scanning user inputs to LLM-powered applications before they are forwarded to the model
- Building an input validation layer for chatbots, AI agents, or retrieval-augmented generation (RAG) pipelines
- Monitoring logs of LLM interactions to retrospectively identify prompt injection attempts
- Evaluating the effectiveness of existing prompt injection defenses through red-team testing
- Classifying prompt injection payloads during security incident investigations involving AI systems

**Do not use** as the sole defense mechanism against prompt injection -- always combine with output validation, privilege separation, and least-privilege tool access. Not suitable for detecting jailbreaks that do not involve injection of adversarial instructions.

**LanBB:** authorized CASE and local Juice Shop lab only. Fail-closed without `programs/<slug>/scope.md`. Do not generate exploit payloads or PoCs. Do not hunt live programs or adult/porn programs.

## Key Concepts

| Term | Definition |
|------|------------|
| **Direct Prompt Injection** | An attack where the user directly includes adversarial instructions in their input to override the system prompt or manipulate LLM behavior |
| **Indirect Prompt Injection** | An attack where malicious instructions are embedded in external data sources (documents, web pages, emails) consumed by the LLM during processing |
| **Heuristic Scoring** | A rule-based analysis method that computes anomaly scores from structural features of the input text without using machine learning |
| **DeBERTa Classifier** | A transformer-based sequence classification model fine-tuned on prompt injection datasets to distinguish adversarial from benign inputs |
| **Canary Token** | A unique marker inserted into system prompts to detect if the LLM has been tricked into leaking its instructions |
| **OWASP LLM01** | The top risk in the OWASP Top 10 for LLM Applications (2025), covering both direct and indirect prompt injection vulnerabilities |

## Checklist (what to look for — no payloads)

Use only on in-scope lab hosts after `scope.md` parses. Record findings in `programs/<slug>/findings/`. Do not attach exploit steps.

- Install Detection Dependencies

- Run the Prompt Injection Detector

- Interpret Detection Results

- Integrate into an LLM Application

- Batch Audit Historical Prompts
