# Teach skill

Agent instructions for **explaining code while reading it** — plain explanations of what something is, how it works, and why it's built that way.

## Upstream

This skill is a thin, self-contained adaptation of Cursor's **teach** skill:

- **Repository:** [cursor/plugins](https://github.com/cursor/plugins)
- **Path:** [`pstack/skills/teach`](https://github.com/cursor/plugins/tree/main/pstack/skills/teach)
- **Upstream file:** [`SKILL.md`](https://github.com/cursor/plugins/blob/main/pstack/skills/teach/SKILL.md)

Upstream teach orchestrates separate `how` and `why` skills and applies an `unslop` writing style. LanBB does not include those dependencies; `tools/teach/SKILL.md` keeps the core teaching contract in one file.

## Layout

| File | Audience |
|------|----------|
| `SKILL.md` | Cursor agents — load when the user asks to be taught or to understand a subsystem |
| `README.md` | Humans — what the skill is and where it came from |

## What "explain while reading" means

1. **Read first** — trace entry points, call chains, and data flow with normal codebase tools.
2. **Explain second** — deliver understanding, not a log of files opened.
3. **Lead with the point** — shortest complete answer, then depth on request.
4. **Mechanism over inventory** — how behavior unfolds, not a symbol list.
5. **Show when useful** — citations, diffs, or stepwise diagrams for multi-part flows.

## Example triggers

- "Teach me how the semantica integration works"
- "Walk me through this PR"
- "Help me understand why this module is structured this way"

## Installing for agents

Point your agent's skill path at `tools/teach/SKILL.md`, or copy/symlink into your Cursor skills directory. The skill sets `disable-model-invocation: true` so it is used only when the user explicitly asks for teaching, not auto-invoked on every task.
