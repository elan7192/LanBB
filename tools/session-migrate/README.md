# session-migrate

Thin LanBB wrapper around [xhluca/session-migrate](https://github.com/xhluca/session-migrate).

Use this when a coding-agent **quota dies** and you want the same conversation in another harness (Claude Code, Codex, OpenCode, GitHub Copilot CLI, Cursor, plus Pi / Antigravity / Mistral Vibe). LanBB does not vendor the converter: install the upstream CLI and call it through `tools/session-migrate/session-migrate`.

Python 3.11+ and Linux are what upstream currently supports.

## Install

From this directory:

```bash
./session-migrate install
```

That prefers `uv tool install session-migrate`, then `pipx install session-migrate`, then the standalone installer:

```bash
curl -LsSf https://session-migrate.github.io/install.sh | sh
```

You can also install upstream yourself:

```bash
uv tool install session-migrate
# already installed?
uv tool upgrade session-migrate
```

The published command is `session-migrate`; `smigrate` is the same binary. Point the wrapper at a specific binary with `SESSION_MIGRATE_BIN`.

## One-command convert

Write a standalone target artifact (does **not** install into an agent home):

```bash
./session-migrate convert SOURCE --to TARGET --output PATH
```

Examples when Claude / Codex / Copilot quota is exhausted:

```bash
# Claude Code jsonl → Cursor store (experimental, text-only)
./session-migrate convert ~/.claude/projects/-work/SESSION.jsonl \
  --to cursor --output ./migrated-cursor.db

# Codex rollout → Copilot CLI
./session-migrate convert ~/.codex/sessions/2026/08/20/rollout-….jsonl \
  --to copilot --output ./migrated-copilot.jsonl

# OpenCode export → Claude Code
./session-migrate convert ./opencode-session.json \
  --to claude --output ./migrated-claude.jsonl
```

`TARGET` is one of: `claude`, `codex`, `opencode`, `copilot`, `cursor`, `pi`, `antigravity`, `vibe`.

A sidecar manifest is written next to the output as `PATH.session-migrate.json`. Source files are never modified.

## Resume in the other agent

To install into the target's native store instead of a standalone file:

```bash
./session-migrate transfer SESSION_UUID --from claude --to codex --cwd "$PWD"
codex resume NEW_SESSION_UUID
```

`--from` / `--to` use the same format names as `convert`. Cursor is experimental and pinned; it moves ordered user/assistant text only.

Search by title if you do not have the UUID:

```bash
./session-migrate catalog refresh
./session-migrate catalog search "oauth refresh" --format claude
./session-migrate transfer --title "oauth refresh" --from claude --to cursor
```

## Quota-death cheat sheet

| From (quota dead) | `--from` / source | `--to` |
| --- | --- | --- |
| Claude Code | `claude` | `codex`, `opencode`, `copilot`, `cursor`, … |
| Codex | `codex` | `claude`, `opencode`, `copilot`, `cursor`, … |
| OpenCode | `opencode` | `claude`, `codex`, `copilot`, `cursor`, … |
| GitHub Copilot CLI | `copilot` | `claude`, `codex`, `opencode`, `cursor`, … |
| Cursor Agent | `cursor` | `claude`, `codex`, `opencode`, `copilot`, … |

`inspect SOURCE` reports structure without printing conversation text.

## Pass-through

Any other arguments go to upstream (`inspect`, `import`, `catalog`, `convert`, `transfer`). Wrapper-only:

```text
./session-migrate            # this README-style usage
./session-migrate --help
./session-migrate install
```

Full CLI: [upstream CLI reference](https://github.com/xhluca/session-migrate/blob/main/docs/cli-reference.md).
