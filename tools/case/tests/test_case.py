#!/usr/bin/python3
"""Scaffold, report path, score tally, and memory emit."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASE = HERE.parent
if str(CASE) not in sys.path:
    sys.path.insert(0, str(CASE))

import lanbb as cli  # noqa: E402
import memory as memory_mod  # noqa: E402
import report as report_mod  # noqa: E402
import score as score_mod  # noqa: E402
import scope as scope_mod  # noqa: E402


class JuiceShopCaseTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="lanbb-case-"))
        (self.tmp / "flows" / "graphs").mkdir(parents=True)
        (self.tmp / "flows" / "graphs" / "case-bounty.json").write_text("{}\n")
        (self.tmp / "README.md").write_text("LanBB\n")
        (self.tmp / ".gitmodules").write_text("")

    def test_case_new_juice_shop_layout(self):
        dest = cli.case_new("juice-shop", self.tmp)
        for rel in (
            "scope.md",
            "notes.md",
            "recon/subdomains",
            "findings",
            "reports",
            "memory",
        ):
            self.assertTrue((dest / rel).exists(), rel)
        text = (dest / "scope.md").read_text(encoding="utf-8")
        self.assertIn("127.0.0.1:3000", text)
        self.assertIn("kind: lab", text)

    def test_score_without_scope_fails(self):
        with self.assertRaises(scope_mod.ScopeError):
            score_mod.score_program("nope", root=self.tmp, payload={"data": []})

    def test_score_fixture_is_zero_of_n(self):
        cli.case_new("juice-shop", self.tmp)
        payload = json.loads(
            (HERE / "fixtures" / "challenges-fresh.json").read_text(encoding="utf-8")
        )
        result = score_mod.score_program(
            "juice-shop", root=self.tmp, payload=payload
        )
        self.assertEqual(result["score"], "0/3")
        self.assertEqual(result["solved"], 0)
        self.assertEqual(result["total"], 3)

    def test_report_path_works_at_zero(self):
        cli.case_new("juice-shop", self.tmp)
        dest = report_mod.write_report("juice-shop", self.tmp)
        self.assertTrue(dest.is_file())
        body = dest.read_text(encoding="utf-8")
        self.assertIn("0/", body)
        self.assertNotIn("PoC payload", body)

    def test_memory_emit_semantic_and_episodic_not_working(self):
        cli.case_new("juice-shop", self.tmp)
        note = "\n".join(
            [
                "Loop method note one.",
                "Defense got a higher wall.",
                "UX kept fail-closed scope.",
                "Score stayed 0/N without auto-pwn.",
                "Report path still wrote a draft.",
            ]
        )
        result = memory_mod.emit(
            "juice-shop",
            semantic=note,
            score="0/3",
            hardened="v1-hardened headers",
            sha_pr="test",
            loop=1,
            root=self.tmp,
        )
        dest = self.tmp / "programs" / "juice-shop" / "memory"
        self.assertTrue((dest / "semantic-loop-1.md").is_file())
        epi = (dest / "episodic.csv").read_text(encoding="utf-8")
        self.assertIn("0/3", epi)
        self.assertGreaterEqual(epi.count("\n"), 2)
        self.assertFalse((dest / "working.md").exists())
        self.assertEqual(result["working"], "not-written")

    def test_memory_rejects_short_semantic(self):
        cli.case_new("juice-shop", self.tmp)
        with self.assertRaises(memory_mod.MemoryError):
            memory_mod.emit(
                "juice-shop",
                semantic="too short",
                score="0/1",
                hardened="none",
                root=self.tmp,
            )

    def test_cli_refuses_missing_scope(self):
        code = cli.main(["--root", str(self.tmp), "scope", "parse", "missing"])
        self.assertEqual(code, 2)

    def test_lab_down_score_is_unknown_zero_of_116(self):
        cli.case_new("juice-shop", self.tmp)
        result = score_mod.score_program(
            "juice-shop",
            root=self.tmp,
            base="http://127.0.0.1:1",
        )
        self.assertEqual(result["score"], "0/116")
        self.assertEqual(result["status"], "unknown")
        self.assertEqual(result["hacking_total_master"], 116)
        self.assertEqual(result["docker_solvable"], 98)
        self.assertIn("v4-hardened", result.get("docker") or result.get("wall") or "")
        self.assertEqual(result.get("fill"), "unknown")

    def test_copied_skills_exist_without_payloads(self):
        skills = CASE / "skills"
        names = [
            "conducting-external-reconnaissance-with-osint",
            "performing-web-application-vulnerability-triage",
            "prioritizing-vulnerabilities-with-cvss-scoring",
            "testing-api-security-with-owasp-top-10",
            "testing-for-xss-vulnerabilities",
            "testing-for-json-web-token-vulnerabilities",
            "testing-for-broken-access-control",
            "testing-for-business-logic-vulnerabilities",
            "testing-oauth2-implementation-flaws",
            "conducting-api-security-testing",
            "testing-cors-misconfiguration",
            "testing-for-open-redirect-vulnerabilities",
            "detecting-ai-model-prompt-injection-attacks",
        ]
        for name in names:
            path = skills / name / "SKILL.md"
            self.assertTrue(path.is_file(), name)
            text = path.read_text(encoding="utf-8")
            self.assertIn("Apache License", text)
            self.assertNotIn("<script>alert", text)
            self.assertNotIn("WAITFOR DELAY", text)
            self.assertNotIn("169.254.169.254", text)
        forbidden = [
            "exploiting-sql-injection-vulnerabilities",
            "exploiting-idor-vulnerabilities",
            "performing-ssrf-vulnerability-exploitation",
        ]
        for name in forbidden:
            self.assertFalse((skills / name).exists(), name)
        self.assertEqual(len(names), 13)

    def test_v2_overlay_is_strictly_harder_than_v1(self):
        root = CASE.parent.parent
        v1 = (root / "labs/juice-shop/overlays/v1-hardened/nginx.conf").read_text(
            encoding="utf-8"
        )
        v2 = (root / "labs/juice-shop/overlays/v2-hardened/nginx.conf").read_text(
            encoding="utf-8"
        )
        for token in (
            "/ftp",
            "limit_req",
            "X-Content-Type-Options",
            "Content-Security-Policy",
        ):
            self.assertIn(token, v1)
            self.assertIn(token, v2)
        for extra in (
            "/encryptionkeys",
            "/redirect",
            "/rest/admin",
            "Permissions-Policy",
            "lab_waf_block",
        ):
            self.assertNotIn(extra, v1)
            self.assertIn(extra, v2)
        self.assertGreater(v2.count("deny all"), v1.count("deny all"))
        compose = (
            root / "labs/juice-shop/overlays/v2-hardened/docker-compose.yml"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e",
            compose,
        )
        versions = json.loads(
            (root / "labs/juice-shop/versions.json").read_text(encoding="utf-8")
        )
        self.assertIn("v2-hardened", versions["overlays"])
        self.assertNotEqual(versions["wall"], "v1-hardened")

    def test_v3_overlay_is_strictly_harder_than_v2(self):
        root = CASE.parent.parent
        v2 = (root / "labs/juice-shop/overlays/v2-hardened/nginx.conf").read_text(
            encoding="utf-8"
        )
        v3 = (root / "labs/juice-shop/overlays/v3-hardened/nginx.conf").read_text(
            encoding="utf-8"
        )
        for token in (
            "/ftp",
            "/encryptionkeys",
            "/redirect",
            "/rest/admin",
            "limit_req",
            "Permissions-Policy",
            "lab_waf_block",
            "Content-Security-Policy",
        ):
            self.assertIn(token, v2)
            self.assertIn(token, v3)
        for extra in (
            "location /file-upload",
            "location /b2b",
            "location /snippets",
            "location /socket.io",
            "location /rest/continue-code",
            "proxy_cookie_flags",
            "limit_conn",
            "Strict-Transport-Security",
            "Cross-Origin-Embedder-Policy",
            "map $request_uri",
        ):
            self.assertNotIn(extra, v2)
            self.assertIn(extra, v3)
        self.assertIn("unsafe-inline", v2)
        self.assertNotIn("unsafe-inline", v3)
        self.assertGreater(v3.count("deny all"), v2.count("deny all"))
        compose = (
            root / "labs/juice-shop/overlays/v3-hardened/docker-compose.yml"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e",
            compose,
        )
        self.assertIn("read_only: true", compose)
        self.assertIn("no-new-privileges:true", compose)
        versions = json.loads(
            (root / "labs/juice-shop/versions.json").read_text(encoding="utf-8")
        )
        self.assertIn("v3-hardened", versions["overlays"])
        self.assertNotEqual(versions["wall"], "v2-hardened")

    def test_v4_overlay_is_strictly_harder_than_v3(self):
        root = CASE.parent.parent
        v3 = (root / "labs/juice-shop/overlays/v3-hardened/nginx.conf").read_text(
            encoding="utf-8"
        )
        v4 = (root / "labs/juice-shop/overlays/v4-hardened/nginx.conf").read_text(
            encoding="utf-8"
        )
        for token in (
            "/ftp",
            "/encryptionkeys",
            "/file-upload",
            "/snippets",
            "/rest/continue-code",
            "proxy_cookie_flags",
            "limit_conn",
            "Strict-Transport-Security",
            "Cross-Origin-Embedder-Policy",
            "map $request_uri",
        ):
            self.assertIn(token, v3)
            self.assertIn(token, v4)
        for extra in (
            "location /api/Feedbacks",
            "location /api/BasketItems",
            "location /rest/user/whoami",
            "location /api/PrivacyRequests",
            "lab_bad_origin",
            "lab_bad_ua",
            "Access-Control-Allow-Origin",
            "fromcharcode",
        ):
            self.assertNotIn(extra, v3)
            self.assertIn(extra, v4)
        self.assertIn("location /rest/products/search", v3)
        self.assertIn("location /rest/products/search", v4)
        self.assertIn("limit_except POST", v3)
        self.assertNotIn("limit_except POST", v4)
        self.assertGreater(v4.count("deny all"), v3.count("deny all"))
        compose_v3 = (
            root / "labs/juice-shop/overlays/v3-hardened/docker-compose.yml"
        ).read_text(encoding="utf-8")
        compose_v4 = (
            root / "labs/juice-shop/overlays/v4-hardened/docker-compose.yml"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e",
            compose_v4,
        )
        self.assertIn("pids_limit", compose_v4)
        self.assertNotIn("pids_limit", compose_v3)
        self.assertGreater(compose_v4.count("cap_drop"), compose_v3.count("cap_drop"))
        versions = json.loads(
            (root / "labs/juice-shop/versions.json").read_text(encoding="utf-8")
        )
        self.assertEqual(versions["wall"], "v4-hardened")
        self.assertEqual(versions.get("hunted"), "v3-hardened")
        self.assertEqual(versions["last_score"], "0/116")
        self.assertEqual(versions.get("fill"), "unknown")
        self.assertEqual(versions["docker_disabled_env"], 18)
        self.assertIn("v4-hardened", versions["overlays"])
        self.assertNotEqual(versions["wall"], "v3-hardened")


if __name__ == "__main__":
    unittest.main()
