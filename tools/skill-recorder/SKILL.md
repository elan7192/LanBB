---
name: skill-recorder-to-skill-md
description: Turn a screen recording of a work session into a reusable SKILL.md using Microsoft Skill Recorder. Use when the user wants to capture a procedure by demonstration, author agent skills from recordings, or adapt Skill Recorder output for Cursor/LanBB.
---

# Screen recording → SKILL.md (Microsoft Skill Recorder)

Use this skill when the user wants to **demonstrate a task once** and produce a **reusable `SKILL.md`** for an AI agent. The canonical upstream tool is [Microsoft Skill Recorder](https://github.com/microsoft/skill-recorder) (MIT, source install).

## When to use this skill

- User asks to record a workflow and turn it into a skill.
- User mentions Microsoft Skill Recorder, Scout Skills, or “record → analyze → skill”.
- User has a recording session and needs help reviewing analysis or adapting exported `SKILL.md` for Cursor.

## Upstream workflow

Follow Microsoft’s **Record → Analyze → Create** pipeline ([README](https://github.com/microsoft/skill-recorder#how-it-works)):

### 1. Record (local only)

1. Install from the [latest release](https://github.com/microsoft/skill-recorder/releases/latest) using the commit-pinned command in [INSTALL.md](https://github.com/microsoft/skill-recorder/blob/main/INSTALL.md).
2. Grant screen-recording permission on first launch.
3. Start recording: `⌘⇧R` (macOS) or `Ctrl+Shift+R` (Windows), or use the in-app control bar.
4. Perform the task **once**, clearly and at a steady pace. Optionally narrate intent.
5. **Never** include passwords, tokens, API keys, or real customer data ([security warning](https://github.com/microsoft/skill-recorder#what-gets-captured)).

Captured locally: window switches, browser URLs (macOS), screen video/snapshots, clipboard previews, optional on-device narration transcription.

### 2. Analyze (requires GitHub Copilot)

1. Click **Analyze** and sign in to GitHub Copilot if prompted.
2. Copilot reconstructs **one intent** and an **ordered list of steps** from the session.
3. Edit the analysis until it accurately describes what should be repeated — not incidental details from the single run.

Data sent to GitHub’s cloud on Analyze: event timeline, extracted screen images, narration text ([what gets captured](https://github.com/microsoft/skill-recorder#what-gets-captured)).

### 3. Create → SKILL.md

1. Choose output target (Scout Skill, Cowork Skill, etc.).
2. **Skill Builder** runs in two phases ([instructions.ts](https://github.com/microsoft/skill-recorder/blob/main/electron/skillbuilder/instructions.ts)):
   - **propose_plan** — generalized values (`{{id}}` tokens), calculation/action steps, native tools.
   - **submit_skill** — final `SKILL.md` **only after user approves** the plan.
3. Export or install the generated `SKILL.md`.

## Authoring principles (from Skill Builder)

When reviewing or hand-editing the exported file, enforce these rules from Microsoft’s Skill Builder:

| Principle | Do | Avoid |
| --- | --- | --- |
| **Trigger** | Put “when to use” cues in YAML `description` | Burying triggers only in the body |
| **Generalize** | Procedure for N items / any matching input | Hardcoding the 3 rows from the demo |
| **Tools** | Native CLI/API/file tools (`gh`, HTTP, shell) | Simulated clicks unless no alternative |
| **Values** | Fixed literals as `{{token}}` in steps | Inlining URLs/paths that should be editable |
| **Steps** | Separate calculations (read/decide) from actions (side effects) | One vague paragraph |
| **Tone** | Imperative, concise, edge cases noted | Transcript of the recording |

## Adapting output for Cursor / LanBB

Skill Recorder optimizes for Microsoft Scout and Copilot Cowork. For this repository:

1. Copy `SKILL.md` into the agent’s skill path (for example `.cursor/skills/<name>/SKILL.md`).
2. Replace upstream tool names with **Cursor-available** tools (MCP servers, shell, repo scripts).
3. Align `allowed-tools` / body instructions with what the runtime actually exposes.
4. Test by prompting with phrases from the skill’s `description`.

## Agent checklist

When helping the user through this process:

- [ ] Confirm Copilot access and supported OS before suggesting install.
- [ ] Warn about secrets and cloud upload before Analyze.
- [ ] After Analyze, verify intent/steps match the user’s goal before Create.
- [ ] After export, review generalization (not overfit to one example).
- [ ] Adapt tool references for the target agent (Cursor vs Scout/Cowork).

## References

- Repo: https://github.com/microsoft/skill-recorder
- Install: https://github.com/microsoft/skill-recorder/blob/main/INSTALL.md
- Skill Builder source: https://github.com/microsoft/skill-recorder/blob/main/electron/skillbuilder/instructions.ts
- LanBB note: [README.md](./README.md)
