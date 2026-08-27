# Skill Recorder → SKILL.md

Thin LanBB note on turning a screen recording into a reusable agent `SKILL.md`, based on [Microsoft Skill Recorder](https://github.com/microsoft/skill-recorder).

This folder is documentation only. It does not vendor the Skill Recorder app or require extra SaaS beyond what Microsoft’s tool already needs (GitHub Copilot for the Analyze/Build steps).

## What it is

[Microsoft Skill Recorder](https://github.com/microsoft/skill-recorder) is an MIT-licensed Electron desktop app. It records a real work session (clicks, app/window switches, browser URLs, optional narration) **locally**, then uses the **GitHub Copilot CLI** to reconstruct an **intent** and **ordered steps**, and finally generalizes that into:

- a **Skill** — a `SKILL.md` procedure an agent runs on demand, or
- an **Automation** — the same procedure on a schedule or trigger (`automation.json` for Microsoft Scout).

The output favors an agent’s **native tools** (for example `gh`, file APIs, CLIs) over brittle UI click replay. See the upstream README: [How it works](https://github.com/microsoft/skill-recorder#how-it-works).

## Workflow (Record → Analyze → Create)

| Stage | You do | Skill Recorder does | Output |
| --- | --- | --- | --- |
| **Record** | Perform the task once (`⌘⇧R` / `Ctrl+Shift+R` or in-app). Keep secrets out of frame, clipboard, and narration. | Captures screen/activity on-device (`events.jsonl`, `video.webm`, optional narration). | Local session files |
| **Analyze** | Review and edit the reconstructed intent + steps. Requires GitHub Copilot sign-in. | Sends timeline, screen images, and narration to GitHub’s cloud; Copilot CLI **Describer** returns structured analysis. | Approved analysis |
| **Create** | Approve the Skill Builder plan, then export. | **Skill Builder** proposes a generalized plan (`propose_plan`), then writes `SKILL.md` (`submit_skill`) after approval. | `SKILL.md` (and/or `automation.json`) |

Upstream references:

- [README — How it works](https://github.com/microsoft/skill-recorder#how-it-works)
- [README — What gets captured](https://github.com/microsoft/skill-recorder#what-gets-captured)
- [INSTALL.md](https://github.com/microsoft/skill-recorder/blob/main/INSTALL.md) — source install (commit-pinned; no prebuilt app in source channel)
- [Skill Builder instructions](https://github.com/microsoft/skill-recorder/blob/main/electron/skillbuilder/instructions.ts) — how `SKILL.md` is authored

## Prerequisites

- **GitHub account with Copilot access** — required for Analyze and Create ([README — Get started](https://github.com/microsoft/skill-recorder#get-started)).
- **Supported OS** — macOS primary; Windows 11 x64/ARM64 supported ([WINDOWS-VALIDATION.md](https://github.com/microsoft/skill-recorder/blob/main/WINDOWS-VALIDATION.md)).
- **Install** — source release only: copy the commit-pinned one-liner from [latest release](https://github.com/microsoft/skill-recorder/releases/latest) ([INSTALL.md](https://github.com/microsoft/skill-recorder/blob/main/INSTALL.md)).

## Security (read before recording)

- Recording stays local until you click **Analyze**; then event timeline, URLs/window titles, clipboard previews, screen images, and narration go to **GitHub’s cloud** ([README — What gets captured](https://github.com/microsoft/skill-recorder#what-gets-captured)).
- **Do not** record, type, paste, or narrate passwords, tokens, or API keys.
- Use synthetic data in an isolated environment for sensitive workflows.

## What a good `SKILL.md` contains

Per Microsoft’s Skill Builder ([instructions.ts](https://github.com/microsoft/skill-recorder/blob/main/electron/skillbuilder/instructions.ts)):

1. **YAML frontmatter** — `name`, `description` (the trigger: when to use this skill), optional `allowed-tools`.
2. **Generalized procedure** — imperative steps derived from one example run, not a transcript of that run.
3. **Fixed values as tokens** — literals that never change (canonical URLs, repo slugs) as `{{id}}` placeholders, not hardcoded in step text.
4. **Native tools first** — map actions to CLI/API/file tools; avoid UI replay unless unavoidable.
5. **Calculation vs action steps** — reads/decisions vs side effects (submit, delete, post).
6. **Edge cases** — empty input, missing files, per-item failures.

## Using the result in LanBB / Cursor

Skill Recorder targets Microsoft Scout, Copilot Cowork, and (eventually) Copilot Studio. For **Cursor** and LanBB agents:

1. Export or copy the generated `SKILL.md`.
2. Place it where your agent loads skills (for example `.cursor/skills/` or a path referenced in agent configuration).
3. **Edit for your runtime** — replace Scout/Cowork tool names with Cursor MCP tools, shell commands, or repo-specific paths.
4. Keep the **description** field rich with trigger phrases so the agent selects the skill reliably.

See [`SKILL.md`](./SKILL.md) in this folder for agent-oriented step-by-step guidance.

## Sources

| Source | URL |
| --- | --- |
| Microsoft Skill Recorder (repo) | https://github.com/microsoft/skill-recorder |
| README | https://github.com/microsoft/skill-recorder/blob/main/README.md |
| INSTALL.md | https://github.com/microsoft/skill-recorder/blob/main/INSTALL.md |
| Skill Builder instructions | https://github.com/microsoft/skill-recorder/blob/main/electron/skillbuilder/instructions.ts |
| Windows validation notes | https://github.com/microsoft/skill-recorder/blob/main/WINDOWS-VALIDATION.md |
| Releases (install commands) | https://github.com/microsoft/skill-recorder/releases/latest |
