---
name: teach
description: "Explain code while reading it so a person actually understands it. Use for 'teach me this', 'walk me through X', 'help me understand this change or subsystem'."
disable-model-invocation: true
---

# Teach

**Explain what a thing is, how it works, and why it's built that way — in plain language, at the person's pace. The goal is understanding, not changing code.**

Adapted from [cursor/plugins `pstack/skills/teach`](https://github.com/cursor/plugins/tree/main/pstack/skills/teach). LanBB does not ship the upstream `how`, `why`, or `unslop` skills; this skill is self-contained.

## When to use

- "Teach me this", "walk me through X", "help me understand this subsystem"
- Before or after a change, when the person needs a mental model
- Code review or onboarding where listing files is not enough

## How to explain while reading

1. **Orient first.** Read the relevant code (entry points, callers, data flow). Decide the few things they should walk away understanding. Choose depth from why they're asking and what they already know — skip what they plainly know.

2. **Read, then explain — don't narrate the read.** Use tools to explore; deliver the explanation, not a report of what you opened. Lead with the main point in one or two sentences, then build out.

3. **Cover what, how, why — in that order when it helps.**
   - *What:* name the thing and what role it plays here.
   - *How:* walk the mechanism — what triggers it, what happens step by step, where data goes. Reference files/functions so they can look; avoid dumping long code blocks unless a snippet is essential.
   - *Why:* the design reason or constraint, when it isn't obvious from the how.

4. **Teach mechanisms, not inventories.** Explain the problem each part solves and how it works. Listing functions and constants is reference, not teaching. Walk through what happens when the user does the thing (runs a command, hits an endpoint, scrolls a list) when that makes it land.

5. **Show when it helps.** Open the diff or cite code regions when that's faster than prose. For three or more moving parts, prefer a short series of small diagrams (each adds one piece) over one crowded figure. Use mermaid for flows; use images only when spatial layout matters.

6. **Keep it conversational.** Smallest complete answer first; add layers when they ask. No quizzes, no pacing theater ("pause here", "the key insight"), no stock headers ("TL;DR", "at its core"). One-shot with no live human: deliver cleanly and offer to go deeper at the end.

7. **Write plainly.** Tight prose, normal sentence case. One name per concept. Split long sentences. Cut filler; keep what makes it click. No em dashes. The explanation is the reply — not a meta-summary of what you did.
