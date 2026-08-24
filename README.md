LanBB is the product.

**semantica** is a tool/engine under LanBB, not the product itself. Do not rename the GitHub repository or the Python package.

- Canonical engine remote: https://github.com/semantica-agi/semantica
- Nesting: git submodule at `tools/semantica`

## Convert a technical PDF into an agent skill

Drop a technical PDF (or a folder of sources) and get a skill bundle —
`SKILL.md`, `chapters/`, `glossary.md`, `patterns.md`, `cheatsheet.md` — for
Claude Code, Codex, OpenCode, or Copilot CLI.

```bash
python3 tools/book-to-skill/convert.py path/to/book.pdf
```

Output lands in `skills/<slug>/` (gitignored). This path does **not** ingest
into the wiki, second-brain, or semantica.

The converter depends on the MIT package
[book-to-skill](https://github.com/virgiliojr94/book-to-skill) rather than a
vendored rewrite. Usage, host install dirs, and extractor extras:
[tools/book-to-skill/README.md](tools/book-to-skill/README.md).
