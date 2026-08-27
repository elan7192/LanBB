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
        self.assertIn("v8-hardened", result.get("docker") or result.get("wall") or "")

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
        self.assertNotEqual(versions["wall"], "v3-hardened")

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
            "map $request_uri",
        ):
            self.assertIn(token, v3)
            self.assertIn(token, v4)
        for extra in (
            "location /graphql",
            "location /api/BasketItems",
            "location /rest/basket",
            "location /api/Feedbacks",
            "location /rest/captcha",
            "location /rest/user/data-export",
            "X-DNS-Prefetch-Control",
            "Cache-Control",
        ):
            self.assertNotIn(extra, v3)
            self.assertIn(extra, v4)
        self.assertGreater(v4.count("deny all"), v3.count("deny all"))
        compose3 = (
            root / "labs/juice-shop/overlays/v3-hardened/docker-compose.yml"
        ).read_text(encoding="utf-8")
        compose4 = (
            root / "labs/juice-shop/overlays/v4-hardened/docker-compose.yml"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e",
            compose4,
        )
        self.assertIn("read_only: true", compose4)
        self.assertIn("NODE_ENV: production", compose4)
        self.assertNotIn("NODE_ENV: production", compose3)
        self.assertIn("mem_limit: 512m", compose4)
        self.assertNotIn("mem_limit:", compose3)
        versions = json.loads(
            (root / "labs/juice-shop/versions.json").read_text(encoding="utf-8")
        )
        self.assertIn("v4-hardened", versions["overlays"])
        self.assertNotEqual(versions["wall"], "v3-hardened")
        self.assertNotEqual(versions["wall"], "v4-hardened")

    def test_v5_overlay_is_strictly_harder_than_v4(self):
        root = CASE.parent.parent
        v4 = (root / "labs/juice-shop/overlays/v4-hardened/nginx.conf").read_text(
            encoding="utf-8"
        )
        v5 = (root / "labs/juice-shop/overlays/v5-hardened/nginx.conf").read_text(
            encoding="utf-8"
        )
        for token in (
            "/ftp",
            "/encryptionkeys",
            "/file-upload",
            "/snippets",
            "/graphql",
            "/api/BasketItems",
            "/rest/captcha",
            "proxy_cookie_flags",
            "limit_conn",
            "Strict-Transport-Security",
            "map $request_uri",
            "X-DNS-Prefetch-Control",
            "Cache-Control",
        ):
            self.assertIn(token, v4)
            self.assertIn(token, v5)
        for extra in (
            "location /api/Users {",
            "location /rest/user/whoami",
            "location /rest/web3",
            "location /nft",
            "location /api/Hints",
            "location /api/Products",
            "location /rest/products {",
            "Origin-Agent-Cluster",
            "require-trusted-types-for",
            "eval[[:space:]]*\\(",
        ):
            self.assertNotIn(extra, v4)
            self.assertIn(extra, v5)
        self.assertIn("CONNECT|OPTIONS", v5)
        self.assertNotIn("CONNECT|OPTIONS", v4)
        self.assertIn("GET|HEAD|POST|OPTIONS", v4)
        self.assertNotIn("GET|HEAD|POST|OPTIONS", v5)
        self.assertIn("burst=0", v4)
        self.assertNotIn("burst=0", v5)
        self.assertIn("burst=1", v5)
        self.assertGreater(v5.count("deny all"), v4.count("deny all"))
        compose4 = (
            root / "labs/juice-shop/overlays/v4-hardened/docker-compose.yml"
        ).read_text(encoding="utf-8")
        compose5 = (
            root / "labs/juice-shop/overlays/v5-hardened/docker-compose.yml"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e",
            compose5,
        )
        self.assertIn("read_only: true", compose5)
        self.assertIn("NODE_ENV: production", compose5)
        self.assertIn("/juice-shop/data", compose5)
        self.assertNotIn("/juice-shop/data", compose4)
        self.assertIn("mem_limit: 384m", compose5)
        self.assertIn("mem_limit: 512m", compose4)
        self.assertNotIn("mem_limit: 384m", compose4)
        versions = json.loads(
            (root / "labs/juice-shop/versions.json").read_text(encoding="utf-8")
        )
        self.assertIn("v5-hardened", versions["overlays"])
        self.assertNotEqual(versions["wall"], "v4-hardened")
        self.assertNotEqual(versions["wall"], "v5-hardened")

    def test_v6_overlay_is_strictly_harder_than_v5(self):
        root = CASE.parent.parent
        v5 = (root / "labs/juice-shop/overlays/v5-hardened/nginx.conf").read_text(
            encoding="utf-8"
        )
        v6 = (root / "labs/juice-shop/overlays/v6-hardened/nginx.conf").read_text(
            encoding="utf-8"
        )
        for token in (
            "/ftp",
            "/encryptionkeys",
            "/file-upload",
            "/snippets",
            "/graphql",
            "/api/BasketItems",
            "/rest/captcha",
            "/api/Users",
            "/rest/web3",
            "/api/Products",
            "proxy_cookie_flags",
            "limit_conn",
            "Strict-Transport-Security",
            "map $request_uri",
            "Origin-Agent-Cluster",
            "require-trusted-types-for",
        ):
            self.assertIn(token, v5)
            self.assertIn(token, v6)
        for extra in (
            "location /rest/user {",
            "location /assets {",
            "location /i18n",
            "location = /sitemap.xml",
            "location /login",
            "location /register",
            "location /score-board",
            "trusted-types default",
            "updatexml",
            "CONNECT|OPTIONS|POST",
        ):
            self.assertNotIn(extra, v5)
            self.assertIn(extra, v6)
        self.assertIn("GET|HEAD|POST)$", v5)
        self.assertNotIn("GET|HEAD|POST)$", v6)
        self.assertIn("GET|HEAD)$", v6)
        self.assertIn("location /rest/user/login", v5)
        self.assertNotIn("location /rest/user/login", v6)
        self.assertNotIn("burst=0", v6)
        self.assertIn("burst=1", v6)
        self.assertGreater(v6.count("deny all"), v5.count("deny all"))
        compose5 = (
            root / "labs/juice-shop/overlays/v5-hardened/docker-compose.yml"
        ).read_text(encoding="utf-8")
        compose6 = (
            root / "labs/juice-shop/overlays/v6-hardened/docker-compose.yml"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e",
            compose6,
        )
        juice6, _, edge6 = compose6.partition("\n  edge:")
        self.assertTrue(edge6)
        self.assertNotIn("read_only: true", juice6)
        self.assertNotIn("- /juice-shop/data", juice6)
        self.assertIn("read_only: true", edge6)
        self.assertIn("NODE_ENV: production", compose6)
        self.assertIn("/tmp:size=16m", juice6)
        self.assertIn("mem_limit: 256m", compose6)
        self.assertIn("mem_limit: 384m", compose5)
        self.assertNotIn("mem_limit: 256m", compose5)
        self.assertIn("/juice-shop/data", compose5)
        versions = json.loads(
            (root / "labs/juice-shop/versions.json").read_text(encoding="utf-8")
        )
        self.assertIn("v6-hardened", versions["overlays"])
        self.assertNotEqual(versions["wall"], "v5-hardened")
        self.assertNotEqual(versions["wall"], "v6-hardened")
        self.assertIn("burst=1", v6)
        self.assertIn("EROFS", compose6)
        self.assertIn("data/static", compose6)

    def test_v7_overlay_is_strictly_harder_than_v6(self):
        root = CASE.parent.parent
        v6 = (root / "labs/juice-shop/overlays/v6-hardened/nginx.conf").read_text(
            encoding="utf-8"
        )
        v7 = (root / "labs/juice-shop/overlays/v7-hardened/nginx.conf").read_text(
            encoding="utf-8"
        )
        for token in (
            "/ftp",
            "/encryptionkeys",
            "/file-upload",
            "/snippets",
            "/graphql",
            "/api/BasketItems",
            "/rest/captcha",
            "/api/Users",
            "/rest/web3",
            "/api/Products",
            "/rest/user {",
            "/assets {",
            "/i18n",
            "/score-board",
            "proxy_cookie_flags",
            "limit_conn",
            "Strict-Transport-Security",
            "map $request_uri",
            "Origin-Agent-Cluster",
            "require-trusted-types-for",
            "trusted-types default",
            "CONNECT|OPTIONS|POST",
        ):
            self.assertIn(token, v6)
            self.assertIn(token, v7)
        for extra in (
            "location /rest {",
            "location /api {",
            "location = / {",
            "location /search",
            "location /forgot-password",
            "location /photo-wall",
            "location /basket {",
            "vbscript:",
            "PUT|PATCH|DELETE",
            "X-Download-Options",
        ):
            self.assertNotIn(extra, v6)
            self.assertIn(extra, v7)
        self.assertEqual(v6.count("proxy_pass"), 2)
        self.assertEqual(v7.count("proxy_pass"), 1)
        self.assertIn("GET|HEAD)$", v7)
        self.assertNotIn("burst=0", v7)
        self.assertIn("burst=1", v7)
        self.assertGreater(v7.count("deny all"), v6.count("deny all"))
        compose6 = (
            root / "labs/juice-shop/overlays/v6-hardened/docker-compose.yml"
        ).read_text(encoding="utf-8")
        compose7 = (
            root / "labs/juice-shop/overlays/v7-hardened/docker-compose.yml"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e",
            compose7,
        )
        juice7, _, edge7 = compose7.partition("\n  edge:")
        self.assertTrue(edge7)
        self.assertNotIn("read_only: true", juice7)
        self.assertNotIn("- /juice-shop/data", juice7)
        self.assertIn("ReadonlyRootfs=false", juice7)
        self.assertIn("read_only: true", edge7)
        self.assertIn("NODE_ENV: production", compose7)
        self.assertIn("/tmp:size=8m", juice7)
        self.assertIn("mem_limit: 192m", compose7)
        self.assertIn("mem_limit: 256m", compose6)
        self.assertNotIn("mem_limit: 192m", compose6)
        self.assertIn("EROFS", compose7)
        self.assertIn("data/static", compose7)
        versions = json.loads(
            (root / "labs/juice-shop/versions.json").read_text(encoding="utf-8")
        )
        self.assertIn("v7-hardened", versions["overlays"])
        self.assertNotEqual(versions["wall"], "v6-hardened")
        self.assertNotEqual(versions["wall"], "v7-hardened")
        self.assertIn("burst=1", v7)
        self.assertIn("EROFS", compose7)
        self.assertIn("data/static", compose7)

    def test_v8_overlay_is_strictly_harder_than_v7(self):
        root = CASE.parent.parent
        v7 = (root / "labs/juice-shop/overlays/v7-hardened/nginx.conf").read_text(
            encoding="utf-8"
        )
        v8 = (root / "labs/juice-shop/overlays/v8-hardened/nginx.conf").read_text(
            encoding="utf-8"
        )
        for token in (
            "/ftp",
            "/encryptionkeys",
            "/file-upload",
            "/snippets",
            "/graphql",
            "/api/BasketItems",
            "/rest/captcha",
            "/api/Users",
            "/rest/web3",
            "/api/Products",
            "/rest/user {",
            "/assets {",
            "/i18n",
            "/score-board",
            "location /rest {",
            "location /api {",
            "location = / {",
            "location /search",
            "location /photo-wall",
            "proxy_cookie_flags",
            "limit_conn",
            "Strict-Transport-Security",
            "map $request_uri",
            "Origin-Agent-Cluster",
            "require-trusted-types-for",
            "trusted-types default",
            "X-Download-Options",
            "PUT|PATCH|DELETE",
        ):
            self.assertIn(token, v7)
            self.assertIn(token, v8)
        for extra in (
            "^/api/Challenges/?$",
            "location /saved-payment-methods",
            "location /blockchain",
            "location /web3-sandbox",
            "location /faucet",
            "jndi:",
            "__proto__",
            "X-XSS-Protection",
            "interest-cohort",
            "gzip off",
            "rate=30r/m",
            "DELETE|HEAD",
        ):
            self.assertNotIn(extra, v7)
            self.assertIn(extra, v8)
        self.assertIn("location /api/Challenges {", v7)
        self.assertNotIn("location /api/Challenges {", v8)
        self.assertIn("GET|HEAD)$", v7)
        self.assertNotIn("GET|HEAD)$", v8)
        self.assertIn("GET)$", v8)
        self.assertEqual(v7.count("proxy_pass"), 1)
        self.assertEqual(v8.count("proxy_pass"), 1)
        self.assertNotIn("burst=0", v8)
        self.assertIn("burst=1", v8)
        self.assertGreater(v8.count("deny all"), v7.count("deny all"))
        compose7 = (
            root / "labs/juice-shop/overlays/v7-hardened/docker-compose.yml"
        ).read_text(encoding="utf-8")
        compose8 = (
            root / "labs/juice-shop/overlays/v8-hardened/docker-compose.yml"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e",
            compose8,
        )
        juice8, _, edge8 = compose8.partition("\n  edge:")
        self.assertTrue(edge8)
        self.assertNotIn("read_only: true", juice8)
        self.assertNotIn("- /juice-shop/data", juice8)
        self.assertIn("ReadonlyRootfs=false", juice8)
        self.assertIn("read_only: true", edge8)
        self.assertIn("NODE_ENV: production", compose8)
        self.assertIn("/tmp:size=4m", juice8)
        self.assertIn("mem_limit: 128m", compose8)
        self.assertIn("mem_limit: 192m", compose7)
        self.assertNotIn("mem_limit: 128m", compose7)
        self.assertIn("127.0.0.1:3000:3000", compose8)
        self.assertNotIn("127.0.0.1:3000:3000", compose7)
        self.assertIn("ulimits:", compose8)
        self.assertNotIn("ulimits:", compose7)
        self.assertIn("EROFS", compose8)
        self.assertIn("data/static", compose8)
        versions = json.loads(
            (root / "labs/juice-shop/versions.json").read_text(encoding="utf-8")
        )
        self.assertEqual(versions["wall"], "v8-hardened")
        self.assertEqual(versions.get("hunted"), "v7-hardened")
        self.assertEqual(versions["last_score"], "0/116")
        self.assertEqual(versions.get("fill"), "unavailable")
        self.assertEqual(versions.get("fill_wall"), "v7-hardened")
        self.assertEqual(versions.get("last_live_score"), "0/116")
        self.assertEqual(versions.get("last_live_wall"), "v6-hardened")
        self.assertEqual(versions.get("score_path"), "GET = /api/Challenges/")
        self.assertEqual(versions.get("bind"), "127.0.0.1:3000")
        self.assertTrue(versions.get("applies") is True)
        self.assertEqual(versions.get("applies_erofs"), "gone")
        self.assertIs(versions.get("applies_readonly_rootfs"), False)
        self.assertEqual(versions.get("applies_tmpfs"), "/tmp only")
        self.assertTrue(versions.get("data_static_visible") is True)
        self.assertEqual(versions.get("data_static_challenges_yml"), 1593)
        self.assertEqual(versions.get("data_static_security_questions_yml"), 29)
        self.assertIn("unavailable", versions.get("fill_reason") or "")
        self.assertIn("v7-hardened", versions.get("fill_reason") or "")
        self.assertEqual(versions["docker_disabled_env"], 18)
        self.assertIn("v8-hardened", versions["overlays"])
        self.assertNotEqual(versions["wall"], "v7-hardened")
        self.assertIn("burst=1", v8)
        self.assertIn("EROFS", compose8)
        self.assertIn("data/static", compose8)


if __name__ == "__main__":
    unittest.main()
