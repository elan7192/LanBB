from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

TOOL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = TOOL_ROOT.parent.parent
sys.path.insert(0, str(TOOL_ROOT))

import convert  # noqa: E402

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "widget-protocol.md"
FAKE_GENERATOR = Path(__file__).resolve().parent / "fake_generator.py"
STUB_SPEC = Path(__file__).resolve().parent / "fixtures" / "stub-skill.md"


class SlugAndPathTests(unittest.TestCase):
    def test_slugify_strips_extension(self) -> None:
        self.assertEqual(
            convert.slugify("Designing Data-Intensive Apps.pdf"),
            "designing-data-intensive-apps",
        )

    def test_trailing_slug_is_not_an_input_path(self) -> None:
        paths, slug = convert.resolve_inputs(["notes.md", "unified-research"])
        self.assertEqual(paths, ["notes.md"])
        self.assertEqual(slug, "unified-research")

    def test_existing_file_is_not_treated_as_slug(self) -> None:
        paths, slug = convert.resolve_inputs([str(FIXTURE)])
        self.assertEqual(paths, [str(FIXTURE)])
        self.assertIsNone(slug)

    def test_refuses_wiki_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "wiki" / "skills"
            wiki.mkdir(parents=True)
            with self.assertRaises(SystemExit) as ctx:
                convert.assert_output_allowed(wiki)
            self.assertIn("wiki", str(ctx.exception))

    def test_refuses_semantica_output(self) -> None:
        with self.assertRaises(SystemExit):
            convert.assert_output_allowed(REPO_ROOT / "tools" / "semantica")


class ExtractAndBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        convert.ensure_runtime()

    def _run_convert(self, extra_env: dict[str, str], argv: list[str]) -> int:
        old = os.environ.copy()
        os.environ.update(extra_env)
        try:
            return convert.main(argv)
        finally:
            os.environ.clear()
            os.environ.update(old)

    def test_extract_only_writes_full_text_and_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            workdir = tmp_path / "work"
            skills = tmp_path / "skills"
            code = self._run_convert(
                {
                    "BOOK_TO_SKILL_SPEC": str(STUB_SPEC),
                    "BOOK_SKILL_WORKDIR": str(workdir),
                },
                [
                    "--extract-only",
                    "--output",
                    str(skills),
                    "--name",
                    "widget-protocol",
                    str(FIXTURE),
                ],
            )
            self.assertEqual(code, 0)
            self.assertTrue((workdir / "full_text.txt").is_file())
            self.assertTrue((workdir / "metadata.json").is_file())
            text = (workdir / "full_text.txt").read_text(encoding="utf-8")
            self.assertIn("Chapter 1: Handshake", text)
            self.assertIn("credit-based flow control", text.lower())
            bundle = skills / "widget-protocol"
            generate = (bundle / "GENERATE.md").read_text(encoding="utf-8")
            self.assertIn("glossary.md", generate)
            self.assertIn("cheatsheet.md", generate)
            self.assertIn("Do **not** write into wiki", generate)
            self.assertEqual(
                convert.validate_bundle(bundle),
                ["SKILL.md", "glossary.md", "patterns.md", "cheatsheet.md", "chapters/*.md"],
            )

    def test_fake_generator_writes_upstream_layout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            workdir = tmp_path / "work"
            skills = tmp_path / "skills"
            code = self._run_convert(
                {
                    "BOOK_TO_SKILL_SPEC": str(STUB_SPEC),
                    "BOOK_TO_SKILL_GENERATOR": f"{sys.executable} {FAKE_GENERATOR}",
                    "BOOK_SKILL_WORKDIR": str(workdir),
                },
                [
                    "--require-bundle",
                    "--keep-workdir",
                    "--output",
                    str(skills),
                    "--name",
                    "widget-protocol",
                    str(FIXTURE),
                ],
            )
            self.assertEqual(code, 0)
            bundle = skills / "widget-protocol"
            self.assertEqual(convert.validate_bundle(bundle), [])
            skill = (bundle / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("name: widget-protocol", skill)
            self.assertTrue((bundle / "chapters" / "ch01-handshake.md").is_file())
            self.assertTrue((bundle / "glossary.md").is_file())
            self.assertTrue((bundle / "patterns.md").is_file())
            self.assertTrue((bundle / "cheatsheet.md").is_file())
            self.assertTrue((workdir / "full_text.txt").is_file())


if __name__ == "__main__":
    unittest.main()
