#!/usr/bin/python3
"""Fail-closed scope tests: missing file, OOS rejected, in-scope allowed."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASE = HERE.parent
if str(CASE) not in sys.path:
    sys.path.insert(0, str(CASE))

import lanbb as cli  # noqa: E402
import scope as scope_mod  # noqa: E402


class FailClosedScopeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="lanbb-scope-"))
        (self.tmp / "flows" / "graphs").mkdir(parents=True)
        (self.tmp / "flows" / "graphs" / "case-bounty.json").write_text("{}\n")
        (self.tmp / "README.md").write_text("LanBB\n")
        (self.tmp / ".gitmodules").write_text("")

    def test_missing_scope_file_fails(self):
        with self.assertRaises(scope_mod.ScopeError) as ctx:
            scope_mod.load_scope("ghost-lab", self.tmp)
        self.assertIn("no program scope file", str(ctx.exception).lower())

    def test_oos_domain_is_rejected(self):
        cli.case_new("juice-shop", self.tmp)
        with self.assertRaises(scope_mod.ScopeError) as ctx:
            scope_mod.require_in_scope("juice-shop", "evil.example", self.tmp)
        self.assertIn("not listed in-scope", str(ctx.exception).lower())

    def test_in_scope_domain_is_allowed(self):
        cli.case_new("juice-shop", self.tmp)
        parsed = scope_mod.require_in_scope(
            "juice-shop", "http://127.0.0.1:3000", self.tmp
        )
        self.assertEqual(parsed.slug, "juice-shop")
        self.assertTrue(parsed.is_lab)

    def test_localhost_alias_is_in_scope(self):
        cli.case_new("juice-shop", self.tmp)
        scope_mod.require_in_scope("juice-shop", "localhost:3000", self.tmp)

    def test_adult_program_slug_is_refused(self):
        with self.assertRaises(scope_mod.ScopeError) as ctx:
            scope_mod.validate_slug("pornhub-bounty")
        self.assertIn("adult", str(ctx.exception).lower())

    def test_recon_without_scope_fails(self):
        import recon as recon_mod

        with self.assertRaises(scope_mod.ScopeError):
            recon_mod.run_passive_recon("missing-lab", root=self.tmp)

    def test_recon_rejects_oos_domain(self):
        import recon as recon_mod

        cli.case_new("juice-shop", self.tmp)
        with self.assertRaises(scope_mod.ScopeError):
            recon_mod.run_passive_recon(
                "juice-shop", domain="not-in-scope.test", root=self.tmp
            )

    def test_recon_allows_in_scope_and_skips_local_lab(self):
        import recon as recon_mod

        cli.case_new("juice-shop", self.tmp)
        result = recon_mod.run_passive_recon(
            "juice-shop", domain="127.0.0.1:3000", root=self.tmp
        )
        self.assertTrue(result["ok"])
        self.assertTrue(result.get("skipped") or not result.get("ran_subfaster"))


if __name__ == "__main__":
    unittest.main()
