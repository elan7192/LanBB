---
name: resolving-merge-conflicts
description: "Use when you need to resolve an in-progress git merge/rebase conflict."
---

Adapted for LanBB from [mattpocock/skills — resolving-merge-conflicts](https://github.com/mattpocock/skills/tree/main/skills/engineering/resolving-merge-conflicts).

1. **See the current state** of the merge/rebase. Run `git status`, inspect conflicted paths, and read recent history on both sides (`git log --oneline --graph --left-right HEAD...MERGE_HEAD` during a merge, or the rebase todo / upstream branch during a rebase).

2. **Find the primary sources** for each conflict. Understand deeply why each change was made and what the original intent was. Read commit messages, linked PRs, and issues/tickets. For submodule pointer conflicts (`tools/semantica`), treat the canonical remote ([semantica-agi/semantica](https://github.com/semantica-agi/semantica)) as the source of truth — update the gitlink only; do not edit files inside the submodule checkout.

3. **Resolve each hunk.** Preserve both intents where possible. Where incompatible, pick the side that matches the merge's stated goal and note the trade-off. Do **not** invent new behaviour. Always resolve; never `git merge --abort` or `git rebase --abort` unless the user explicitly asks to stop.

4. Discover the project's **automated checks** and run them (typecheck, tests, format/lint — whatever this repo defines). Fix anything the merge broke. If no checks are configured yet, at minimum confirm the tree is clean (`git diff --check`) and conflict markers are gone.

5. **Finish the merge/rebase.** Stage everything (`git add` including resolved submodules if needed) and commit. If rebasing, run `git rebase --continue` until the rebase completes.

## LanBB guardrails

- **Do not** modify content under `tools/semantica` — only resolve which commit the submodule should point at.
- **Do not** ingest or rewrite paths reserved for wiki, second-brain, or semantica workflows unless the merge explicitly requires it.
- Prefer minimal diffs: resolve conflicts, do not refactor adjacent code in the same commit.
