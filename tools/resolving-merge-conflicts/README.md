# resolving-merge-conflicts (LanBB)

Agent skill for working through an in-progress **git merge or rebase** conflict
hunk by hunk: trace each side's intent to primary sources, resolve, verify, and
finish the operation — never `--abort` unless the user explicitly stops.

Pattern and workflow are adapted from Matt Pocock's engineering skills (not
vendored wholesale):

**Upstream:** https://github.com/mattpocock/skills/tree/main/skills/engineering/resolving-merge-conflicts

## For agents

When a merge or rebase stops with conflicts, **read
[`SKILL.md`](./SKILL.md) first** and follow its steps before editing conflicted
files.

Trigger phrases: merge conflict, rebase conflict, `<<<<<<<`, unmerged paths,
`git status` showing *both modified*.

## For humans

| Install where | Path |
|---------------|------|
| Cursor (project) | Already at `tools/resolving-merge-conflicts/SKILL.md` — add to agent rules or symlink into `.cursor/skills/` if your setup expects skills there |
| Cursor / Claude (user) | `ln -s "$(pwd)/tools/resolving-merge-conflicts" ~/.cursor/skills/resolving-merge-conflicts` |
| Codex / OpenCode / Amp | `ln -s "$(pwd)/tools/resolving-merge-conflicts" ~/.agents/skills/resolving-merge-conflicts` |

Or copy `SKILL.md` into your host's skills directory and keep the upstream link
in the header for updates.

## Out of scope

- `tools/semantica` file edits (submodule pointer only)
- Wiki / second-brain ingest
- Replacing human judgment on product direction — the skill resolves *git*
  conflicts by intent, not business prioritization
