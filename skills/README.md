# Generated skill bundles

`python3 tools/book-to-skill/convert.py <pdf-or-folder>` writes each bundle here:

```
skills/<slug>/
  SKILL.md
  chapters/
  glossary.md
  patterns.md
  cheatsheet.md
```

These directories are gitignored. They may derive from third-party books — keep
them private. This is **not** a wiki, second-brain, or semantica ingest path.

How to run the converter: [tools/book-to-skill/README.md](../tools/book-to-skill/README.md).
