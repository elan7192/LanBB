---
name: lanbb-book-to-skill
description: >
  LanBB wrapper around the MIT book-to-skill package. Convert a technical PDF,
  folder, or glob of sources into an agent skill bundle (SKILL.md, chapters/,
  glossary.md, patterns.md, cheatsheet.md) for Claude Code, Codex, OpenCode, or
  Copilot CLI. Use when the user wants to drop a book or docs folder and get a
  queryable skill. Does not ingest into the wiki, second-brain, or semantica.
---

# LanBB book-to-skill

This is a **thin wrapper**, not a fork. Extraction is the upstream
[`book-to-skill`](https://github.com/virgiliojr94/book-to-skill) MIT package.
Generation follows that repo's `SKILL.md` spec.

## One command

From the LanBB repo root (non-interactive; technical PDF mode by default):

```bash
python3 tools/book-to-skill/convert.py path/to/book.pdf
```

Folder or several sources:

```bash
python3 tools/book-to-skill/convert.py path/to/sources/
python3 tools/book-to-skill/convert.py paper1.pdf notes.md unified-research
```

Output is `skills/<slug>/` in this repo unless `--output` or `--install-to` is set.

## Hard limits

- Do **not** write into wiki, second-brain, semantica, or `tools/semantica`.
- Do **not** vendor or rewrite the extractor. Depend on the MIT package.
- Do **not** copy raw book text into the bundle (upstream quality rule #7).

## If convert.py already extracted

Read `GENERATE.md` in the printed workdir (or `skills/<slug>/GENERATE.md` if copied)
and execute that prompt: write `SKILL.md`, `chapters/`, `glossary.md`, `patterns.md`,
and `cheatsheet.md` under the stated `SKILLS_HOME/<slug>/`. Skip extraction. Skip
publish. Skip wiki ingest.

Full usage: `tools/book-to-skill/README.md`.
