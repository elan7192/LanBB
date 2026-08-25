# book-to-skill (LanBB)

Turn a technical PDF — or a folder of sources — into an agent skill bundle you
can query in Claude Code, Codex, OpenCode, or Copilot CLI.

This is a **thin wrapper**. Extraction is the MIT package
[`virgiliojr94/book-to-skill`](https://github.com/virgiliojr94/book-to-skill)
(v1.4.0). Generation follows that repo's `SKILL.md` spec. LanBB does **not**
vendor a rewrite, and it does **not** ingest the result into the wiki,
second-brain, or semantica.

Tweet that called for this wiring: https://x.com/0x_sakata/status/2091761448414478357

## One command

From the LanBB repo root:

```bash
python3 tools/book-to-skill/convert.py path/to/book.pdf
```

That is the in-repo equivalent of the upstream CLI (`pip install` from git,
then `book-to-skill path/to/book.pdf`). The wrapper:

1. Creates `tools/book-to-skill/.venv` and installs
   `book-to-skill[pdf]` from GitHub (`v1.4.0`). The project is not on PyPI yet.
2. Extracts with `--mode technical` (Docling if installed, otherwise pypdf /
   pdftotext / pdfminer — same fallback as upstream).
3. Writes a generator prompt and, if `claude` / `codex` / `opencode` /
   `copilot` is on `PATH`, runs it so you get the bundle upstream produces:

   ```
   skills/<slug>/
     SKILL.md          # core frameworks + chapter/topic index
     chapters/         # one file per chapter, loaded on demand
     glossary.md
     patterns.md
     cheatsheet.md
   ```

If no agent CLI is installed, extraction still finishes. Open the printed
`GENERATE.md` in Claude Code, Codex, OpenCode, or Copilot CLI and the agent
writes those files.

### Folder / several sources / slug

```bash
python3 tools/book-to-skill/convert.py path/to/sources/
python3 tools/book-to-skill/convert.py paper1.pdf notes.md unified-research
python3 tools/book-to-skill/convert.py --name designing-data-intensive-apps book.pdf
```

### Drop the bundle into a host skills directory

```bash
python3 tools/book-to-skill/convert.py --install-to claude path/to/book.pdf
# claude   → ~/.claude/skills/<slug>/
# copilot  → ~/.copilot/skills/<slug>/
# codex / opencode / amp → ~/.agents/skills/<slug>/
# local (default) → ./skills/<slug>/
```

## Setup

First run only needs network (git install of the MIT package):

```bash
python3 tools/book-to-skill/convert.py --check
```

PDF extractors (install any one; more is better):

| Need | Install |
|------|---------|
| Fast text PDFs | `sudo apt install poppler-utils` and/or the wrapper venv already has `pypdf` |
| Technical PDFs (tables, code, formulas) | `tools/book-to-skill/.venv/bin/pip install 'book-to-skill[technical] @ git+https://github.com/virgiliojr94/book-to-skill.git@v1.4.0'` |
| Scanned / image-only PDFs | OCR first: `ocrmypdf input.pdf output.pdf` |

## Direct MIT CLI (extractor only)

The pip CLI is the **extractor**, not the full skill generator. Upstream is
explicit about that. Use it when you only want `full_text.txt` + `metadata.json`:

```bash
python3 tools/book-to-skill/convert.py --extract-only path/to/book.pdf
# or, after the venv exists:
tools/book-to-skill/.venv/bin/book-to-skill path/to/book.pdf --mode technical --install-missing no
```

Full conversion (SKILL.md + chapters/glossary/patterns/cheatsheet) still needs
an agent following upstream `SKILL.md`. That is what `convert.py` orchestrates.

## Resume generation

```bash
python3 tools/book-to-skill/convert.py --from-workdir /path/to/book_skill_work --name my-slug
```

## Tests

```bash
python3 -m unittest discover -s tools/book-to-skill/tests -v
```

## Scan a generated bundle (NVIDIA SkillSpector)

After `convert.py` writes `skills/<slug>/`, you can run a **static** security
pass with [NVIDIA SkillSpector](https://github.com/NVIDIA/SkillSpector)
(Apache-2.0). SkillSpector is **not** vendored or installed by this wrapper.

Install (see upstream [Quick Start](https://github.com/NVIDIA/SkillSpector#quick-start)):

```bash
# CLI-only (recommended)
uv tool install git+https://github.com/NVIDIA/skillspector.git

# or from source
git clone https://github.com/NVIDIA/SkillSpector.git
cd SkillSpector
python3 -m venv .venv && source .venv/bin/activate
make install
```

Scan the bundle — static checks only, no LLM calls:

```bash
skillspector scan ./skills/my-slug/ --no-llm
```

LanBB thin wrapper (same flags; requires `skillspector` on `PATH`):

```bash
tools/book-to-skill/scan-skill.sh ./skills/my-slug/
```

Repeatable end-to-end smoke (fixture → bundle → static scan):

```bash
tools/book-to-skill/smoke.sh
```

Uses the synthetic public-domain-style fixture
`tests/fixtures/widget-protocol.md` and the test double generator so the
bundle is complete without an agent CLI. On first run, installs SkillSpector
into `tools/book-to-skill/.cache/skillspector-venv/` (gitignored, not vendored).

Hosted guide: [Scan agent skills before installation](https://docs.nvidia.com/skills/scanning-agent-skills).
Exit codes and report formats: `skillspector scan --help`.

## Out of scope

- Wiki / second-brain ingest
- `tools/semantica` / [semantica-agi/semantica](https://github.com/semantica-agi/semantica)
- Publishing generated skills of third-party books (keep them private)
