#!/usr/bin/env python3
"""LanBB thin wrapper around the MIT book-to-skill package.

Extraction is `book-to-skill` (git+https://github.com/virgiliojr94/book-to-skill).
Generation follows that project's SKILL.md spec via Claude Code / Codex /
OpenCode / Copilot CLI (or a command you pass). Output is a skill bundle:

    SKILL.md  chapters/  glossary.md  patterns.md  cheatsheet.md

Nothing here writes to wiki, second-brain, or semantica.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

TOOL_ROOT = Path(__file__).resolve().parent
REQUIREMENTS = TOOL_ROOT / "requirements.txt"
VENV_DIR = TOOL_ROOT / ".venv"
VENV_PY = VENV_DIR / "bin" / "python"
CACHE_DIR = TOOL_ROOT / ".cache"
UPSTREAM_REPO = "https://github.com/virgiliojr94/book-to-skill"
UPSTREAM_TAG = "v1.4.0"
SPEC_URLS = (
    f"https://raw.githubusercontent.com/virgiliojr94/book-to-skill/{UPSTREAM_TAG}/SKILL.md",
    "https://raw.githubusercontent.com/virgiliojr94/book-to-skill/master/SKILL.md",
)
FORBIDDEN_OUTPUT_MARKERS = (
    "/wiki/",
    "/second-brain/",
    "/semantica/",
    "/semantica-agi/",
    "/tools/semantica",
)
HOST_INSTALL_DIRS = {
    "local": None,  # resolved to <repo>/skills
    "claude": Path.home() / ".claude" / "skills",
    "codex": Path.home() / ".agents" / "skills",
    "opencode": Path.home() / ".agents" / "skills",
    "copilot": Path.home() / ".copilot" / "skills",
    "amp": Path.home() / ".agents" / "skills",
}
GENERATOR_CLIS = (
    ("claude", ("claude",)),
    ("codex", ("codex",)),
    ("opencode", ("opencode",)),
    ("copilot", ("copilot",)),
)

BUNDLE_FILES = ("SKILL.md", "glossary.md", "patterns.md", "cheatsheet.md")


def find_repo_root(start: Path | None = None) -> Path:
    here = start or TOOL_ROOT
    for candidate in [here, *here.parents]:
        if (candidate / ".git").exists() and (candidate / "tools").is_dir():
            return candidate
    return here.parent if here.name == "book-to-skill" else here


def default_skills_parent(repo_root: Path | None = None) -> Path:
    return (repo_root or find_repo_root()) / "skills"


def slugify(value: str) -> str:
    text = value.strip().lower()
    text = re.sub(r"\.[A-Za-z0-9]{1,8}$", "", text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text or "book-skill"


def assert_output_allowed(path: Path) -> Path:
    resolved = path.resolve()
    as_posix = f"{resolved.as_posix()}/"
    for marker in FORBIDDEN_OUTPUT_MARKERS:
        if marker in as_posix or as_posix.rstrip("/").endswith(marker.rstrip("/")):
            raise SystemExit(
                f"Refusing to write a skill bundle under {resolved}. "
                "book-to-skill output must not go into wiki, second-brain, or semantica."
            )
    return resolved


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="convert.py",
        description=(
            "Convert a technical PDF, folder, or glob of sources into an agent "
            "skill bundle using the MIT book-to-skill package."
        ),
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="PDF / EPUB / DOCX / Markdown / folder / glob. Last token may be a slug.",
    )
    parser.add_argument("--name", help="Skill slug (default: from the first filename).")
    parser.add_argument(
        "--output",
        type=Path,
        help="Parent directory for <slug>/ (default: <repo>/skills).",
    )
    parser.add_argument(
        "--install-to",
        choices=sorted(HOST_INSTALL_DIRS),
        default="local",
        help="Where to place the bundle. 'local' is ./skills in this repo.",
    )
    parser.add_argument(
        "--mode",
        choices=("technical", "text"),
        default="technical",
        help="Extraction mode. Technical tries Docling then falls back (upstream).",
    )
    parser.add_argument(
        "--install-missing",
        choices=("yes", "no", "ask"),
        default="no",
        help="Forwarded to book-to-skill. Default no so the wrapper stays non-interactive.",
    )
    parser.add_argument(
        "--generator",
        default="auto",
        help=(
            "auto | prompt-only | claude | codex | opencode | copilot | "
            "a shell command. auto tries agent CLIs; prompt-only writes GENERATE.md."
        ),
    )
    parser.add_argument(
        "--extract-only",
        action="store_true",
        help="Run the MIT extractor only; still writes GENERATE.md for the generator half.",
    )
    parser.add_argument(
        "--from-workdir",
        type=Path,
        help="Skip extraction; generate from an existing book-to-skill workdir.",
    )
    parser.add_argument(
        "--keep-workdir",
        action="store_true",
        help="Do not delete the extraction workdir after a successful bundle.",
    )
    parser.add_argument(
        "--require-bundle",
        action="store_true",
        help="Exit non-zero if SKILL.md + chapters/glossary/patterns/cheatsheet are missing.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Install the MIT package if needed, then run book-to-skill --check.",
    )
    parser.add_argument(
        "--skip-venv",
        action="store_true",
        help="Use the current Python instead of tools/book-to-skill/.venv.",
    )
    return parser.parse_args(argv)


def ensure_runtime(skip_venv: bool = False) -> Path:
    """Return the Python that has book-to-skill installed."""
    if skip_venv or os.environ.get("BOOK_TO_SKILL_SKIP_VENV") == "1":
        python = Path(sys.executable)
        _install_package(python)
        return python

    if not VENV_PY.exists():
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)
    _install_package(VENV_PY)
    return VENV_PY


def _install_package(python: Path) -> None:
    probe = subprocess.run(
        [str(python), "-c", "import book_to_skill"],
        capture_output=True,
        text=True,
    )
    if probe.returncode == 0:
        return
    print("Installing book-to-skill (MIT, from GitHub v1.4.0)…", file=sys.stderr)
    subprocess.run(
        [str(python), "-m", "pip", "install", "--upgrade", "pip"],
        check=True,
    )
    subprocess.run(
        [str(python), "-m", "pip", "install", "-r", str(REQUIREMENTS)],
        check=True,
    )


def resolve_inputs(paths: list[str]) -> tuple[list[str], str | None]:
    """Split trailing slug from input paths the way upstream SKILL.md does."""
    if not paths:
        return [], None
    last = paths[-1]
    looks_like_path = any(ch in last for ch in ("/", "\\", "*", "?", ".")) or Path(
        os.path.expanduser(last)
    ).exists()
    if len(paths) > 1 and not looks_like_path and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", last):
        return paths[:-1], last
    return paths, None


def run_extract(
    python: Path,
    inputs: list[str],
    mode: str,
    install_missing: str,
    workdir: Path,
) -> Path:
    workdir = workdir.resolve()
    workdir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["BOOK_SKILL_WORKDIR"] = str(workdir)
    cmd = [
        str(python),
        "-m",
        "book_to_skill",
        *inputs,
        "--mode",
        mode,
        "--install-missing",
        install_missing,
    ]
    print(f"+ {' '.join(cmd)}", file=sys.stderr)
    result = subprocess.run(cmd, env=env)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    meta = workdir / "metadata.json"
    text = workdir / "full_text.txt"
    if not meta.is_file() or not text.is_file():
        raise SystemExit(
            f"Extractor finished but {meta} or {text} is missing. "
            "See book-to-skill --check."
        )
    return workdir


def cache_generator_spec() -> Path | None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    dest = CACHE_DIR / f"SKILL.{UPSTREAM_TAG}.md"
    if dest.is_file() and dest.stat().st_size > 1000:
        return dest
    for url in SPEC_URLS:
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                body = response.read()
            if b"Book-to-Skill Converter" in body or b"name: book-to-skill" in body:
                dest.write_bytes(body)
                return dest
        except (urllib.error.URLError, TimeoutError, OSError):
            continue
    return None


def load_generator_spec() -> str:
    """Path or URL the generator prompt should follow."""
    override = os.environ.get("BOOK_TO_SKILL_SPEC")
    if override:
        path = Path(override).expanduser()
        if not path.is_file():
            raise SystemExit(f"BOOK_TO_SKILL_SPEC is not a file: {path}")
        return str(path.resolve())
    cached = cache_generator_spec()
    if cached is not None:
        return str(cached)
    return f"{UPSTREAM_REPO}/blob/{UPSTREAM_TAG}/SKILL.md"


def write_generate_prompt(
    workdir: Path,
    bundle_dir: Path,
    slug: str,
    mode: str,
    spec_path: str,
    metadata: dict,
) -> Path:
    sources = metadata.get("sources") or []
    source_lines = "\n".join(
        f"- {src.get('filename')} ({src.get('format')}, "
        f"{src.get('extraction_method')})"
        for src in sources
    ) or f"- {metadata.get('filename')}"
    prompt = f"""# LanBB book-to-skill generation request

You are executing the **generator half** of [book-to-skill]({UPSTREAM_REPO})
({UPSTREAM_TAG}, MIT). Extraction already ran. Do **not** re-extract.

## Pre-answered choices (non-interactive)

- BOOK_TYPE = `{mode}`
- DEPTH = `study` (all of: apply frameworks, think with the models, reference chapters)
- SKILL_NAME / slug = `{slug}`
- SKILLS_HOME = `{bundle_dir.parent}`
- Write the skill at `{bundle_dir}`
- Skip Step 2 extraction. Skip Step 2.5 confirmation. Skip Step 4 questions.
- Skip Step 11 publish. Do not `gh repo create`.
- Do **not** write into wiki, second-brain, semantica, or tools/semantica.

## Spec

Follow the upstream generator spec literally:

`{spec_path}`

Quality rule #7: never copy raw book passages. Synthesize structure
(frameworks, principles, techniques, anti-patterns).

## Extraction outputs

- Text: `{workdir / "full_text.txt"}`
- Metadata: `{workdir / "metadata.json"}`
- Workdir: `{workdir}`

Sources:
{source_lines}

Pages/sections: {metadata.get("pages")} | Words: {metadata.get("words")} | Tokens: {metadata.get("estimated_tokens_human", metadata.get("estimated_tokens"))}
Chapters detected: {metadata.get("chapters_detected")} ({metadata.get("chapters_method")})
Headings sample: {json.dumps(metadata.get("chapter_headings_sample") or [])}

For books over ~50k tokens, probe `full_text.txt` with grep/sed (spec Step 2.6).
Do not dump the whole file into context.

## Required output (must all exist when you finish)

```
{bundle_dir}/SKILL.md
{bundle_dir}/chapters/ch01-*.md   # one file per chapter/section
{bundle_dir}/glossary.md
{bundle_dir}/patterns.md
{bundle_dir}/cheatsheet.md
```

Create `{bundle_dir}/chapters` first. When done, print the file list and stop.
"""
    prompt_path = workdir / "GENERATE.md"
    prompt_path.write_text(prompt, encoding="utf-8")
    return prompt_path


def build_generator_command(generator: str, prompt_path: Path, prompt: str) -> list[str] | None:
    env_cmd = os.environ.get("BOOK_TO_SKILL_GENERATOR")
    if env_cmd:
        return shlex.split(env_cmd) + [str(prompt_path)]

    kind = generator.strip()
    if kind in {"prompt-only", "none", "off"}:
        return None
    if kind != "auto" and not any(kind == name for name, _ in GENERATOR_CLIS):
        return shlex.split(kind) + [str(prompt_path)]

    wanted = None if kind == "auto" else kind
    for name, binaries in GENERATOR_CLIS:
        if wanted and name != wanted:
            continue
        binary = next((b for b in binaries if shutil.which(b)), None)
        if not binary:
            continue
        if name == "claude":
            return [binary, "-p", prompt, "--permission-mode", "acceptEdits"]
        if name == "codex":
            return [binary, "exec", prompt]
        if name == "opencode":
            return [binary, "run", prompt]
        if name == "copilot":
            return [binary, "-p", prompt]
    return None


def run_generator(generator: str, prompt_path: Path, bundle_dir: Path) -> bool:
    prompt = prompt_path.read_text(encoding="utf-8")
    cmd = build_generator_command(generator, prompt_path, prompt)
    if cmd is None:
        print(
            "No agent CLI found (claude / codex / opencode / copilot).\n"
            f"Extraction is done. Open this prompt in Claude Code, Codex, "
            f"OpenCode, or Copilot CLI to finish the bundle:\n  {prompt_path}",
            file=sys.stderr,
        )
        return False
    env = os.environ.copy()
    env["BOOK_TO_SKILL_BUNDLE_DIR"] = str(bundle_dir)
    env["BOOK_TO_SKILL_PROMPT"] = str(prompt_path)
    print(f"+ {cmd[0]} …  (generator={generator})", file=sys.stderr)
    result = subprocess.run(cmd, env=env)
    if result.returncode != 0:
        print(
            f"Generator command exited {result.returncode}. "
            f"You can retry from {prompt_path}",
            file=sys.stderr,
        )
        return False
    return True


def validate_bundle(bundle_dir: Path) -> list[str]:
    missing: list[str] = []
    for name in BUNDLE_FILES:
        if not (bundle_dir / name).is_file():
            missing.append(name)
    chapters = bundle_dir / "chapters"
    if not chapters.is_dir() or not any(chapters.glob("*.md")):
        missing.append("chapters/*.md")
    return missing


def resolve_output_parent(args: argparse.Namespace, repo_root: Path) -> Path:
    if args.output:
        return assert_output_allowed(Path(args.output).expanduser())
    mapped = HOST_INSTALL_DIRS[args.install_to]
    if mapped is None:
        return assert_output_allowed(default_skills_parent(repo_root))
    return assert_output_allowed(mapped)


def load_metadata(workdir: Path) -> dict:
    meta_path = workdir / "metadata.json"
    return json.loads(meta_path.read_text(encoding="utf-8"))


def print_bundle_report(bundle_dir: Path, workdir: Path, prompt_path: Path) -> None:
    missing = validate_bundle(bundle_dir)
    print()
    if missing:
        print("Skill bundle is not complete yet.")
        print(f"  Missing: {', '.join(missing)}")
        print(f"  Finish by running the generator prompt:\n    {prompt_path}")
        print(f"  Extraction workdir: {workdir}")
        return
    print(f"Skill bundle: {bundle_dir}")
    print("  SKILL.md")
    print("  chapters/")
    for path in sorted((bundle_dir / "chapters").glob("*.md")):
        print(f"    {path.name}")
    print("  glossary.md")
    print("  patterns.md")
    print("  cheatsheet.md")
    print()
    print("Install / use:")
    print("  Claude Code : copy or symlink this folder into ~/.claude/skills/")
    print("  Codex/OpenCode/Amp : ~/.agents/skills/")
    print("  Copilot CLI : ~/.copilot/skills/")
    print("  or re-run with --install-to claude|codex|opencode|copilot")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = find_repo_root()
    python = ensure_runtime(skip_venv=args.skip_venv)

    if args.check:
        return subprocess.run([str(python), "-m", "book_to_skill", "--check"]).returncode

    inputs, trailing_slug = resolve_inputs(args.paths)
    if args.from_workdir is None and not inputs:
        print(
            "convert.py requires a document path, folder, or glob.\n"
            "Example: python3 tools/book-to-skill/convert.py path/to/book.pdf",
            file=sys.stderr,
        )
        return 2

    output_parent = resolve_output_parent(args, repo_root)
    output_parent.mkdir(parents=True, exist_ok=True)

    if args.from_workdir:
        workdir = Path(args.from_workdir).expanduser().resolve()
        if not (workdir / "metadata.json").is_file():
            raise SystemExit(f"No metadata.json in {workdir}")
    else:
        workdir = Path(
            os.environ.get("BOOK_SKILL_WORKDIR")
            or (TOOL_ROOT / ".cache" / "work" / str(os.getpid()))
        )
        workdir = run_extract(
            python, inputs, args.mode, args.install_missing, workdir
        )

    metadata = load_metadata(workdir)
    slug = args.name or trailing_slug or slugify(str(metadata.get("filename") or "book"))
    bundle_dir = assert_output_allowed(output_parent / slug)
    bundle_dir.mkdir(parents=True, exist_ok=True)

    spec_path = load_generator_spec()
    prompt_path = write_generate_prompt(
        workdir, bundle_dir, slug, args.mode, spec_path, metadata
    )
    (bundle_dir / "GENERATE.md").write_text(
        prompt_path.read_text(encoding="utf-8"), encoding="utf-8"
    )

    generated = False
    if not args.extract_only:
        generated = run_generator(args.generator, prompt_path, bundle_dir)

    missing = validate_bundle(bundle_dir)
    print_bundle_report(bundle_dir, workdir, prompt_path)

    if generated and not missing and not args.keep_workdir and args.from_workdir is None:
        # Keep GENERATE.md copy on the bundle; drop the temp extraction dir.
        shutil.rmtree(workdir, ignore_errors=True)

    if args.require_bundle and missing:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
