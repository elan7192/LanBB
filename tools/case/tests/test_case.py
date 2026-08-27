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
        self.assertIn("v16-hardened", result.get("docker") or result.get("wall") or "")

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
        self.assertIn("v8-hardened", versions["overlays"])
        self.assertNotEqual(versions["wall"], "v7-hardened")
        self.assertNotEqual(versions["wall"], "v8-hardened")
        self.assertIn("burst=1", v8)
        self.assertIn("EROFS", compose8)
        self.assertIn("data/static", compose8)

    def test_v9_overlay_is_strictly_harder_than_v8(self):
        root = CASE.parent.parent
        v8 = (root / "labs/juice-shop/overlays/v8-hardened/nginx.conf").read_text(
            encoding="utf-8"
        )
        v9 = (root / "labs/juice-shop/overlays/v9-hardened/nginx.conf").read_text(
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
            "location /saved-payment-methods",
            "location /blockchain",
            "location /web3-sandbox",
            "location /faucet",
            "proxy_cookie_flags",
            "limit_conn",
            "Strict-Transport-Security",
            "map $request_uri",
            "Origin-Agent-Cluster",
            "require-trusted-types-for",
            "X-Download-Options",
            "X-XSS-Protection",
            "PUT|PATCH|DELETE",
            "jndi:",
            "__proto__",
            "gzip off",
            "interest-cohort",
        ):
            self.assertIn(token, v8)
            self.assertIn(token, v9)
        for extra in (
            "location = /api/Challenges/",
            "location = /api/Challenges {",
            "location /logout",
            "location /oauth {",
            "location /delivery-method",
            "location /nft-move",
            "location /health",
            "location /actuator",
            "ldap://",
            "gopher://",
            "child_process",
            "etag off",
            "rate=10r/m",
            "sandbox;",
            "form-action 'none'",
            "clipboard-write=()",
            "$host !~ ^(127\\.0\\.0\\.1|localhost)$",
        ):
            self.assertNotIn(extra, v8)
            self.assertIn(extra, v9)
        self.assertIn("^/api/Challenges/?$", v8)
        self.assertNotIn("^/api/Challenges/?$", v9)
        self.assertIn("GET)$", v9)
        self.assertEqual(v8.count("proxy_pass"), 1)
        self.assertEqual(v9.count("proxy_pass"), 2)
        self.assertNotIn("burst=0", v9)
        self.assertIn("burst=1", v9)
        self.assertGreater(v9.count("deny all"), v8.count("deny all"))
        compose8 = (
            root / "labs/juice-shop/overlays/v8-hardened/docker-compose.yml"
        ).read_text(encoding="utf-8")
        compose9 = (
            root / "labs/juice-shop/overlays/v9-hardened/docker-compose.yml"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e",
            compose9,
        )
        juice9, _, edge9 = compose9.partition("\n  edge:")
        juice8, _, edge8 = compose8.partition("\n  edge:")
        self.assertTrue(edge9)
        self.assertNotIn("read_only: true", juice9)
        self.assertNotIn("- /juice-shop/data", juice9)
        self.assertIn("ReadonlyRootfs=false", juice9)
        self.assertIn("read_only: true", edge9)
        self.assertIn("NODE_ENV: production", compose9)
        self.assertIn("/tmp:size=2m", juice9)
        self.assertIn("mem_limit: 128m", juice9)
        self.assertIn("mem_limit: 8m", edge9)
        self.assertIn("mem_limit: 12m", compose8)
        self.assertNotIn("mem_limit: 8m", compose8)
        self.assertIn("127.0.0.1:3000:3000", compose9)
        self.assertIn("ulimits:", compose9)
        self.assertIn("pids_limit: 40", juice9)
        self.assertNotIn("pids_limit: 40", juice8)
        self.assertIn("EROFS", compose9)
        self.assertIn("data/static", compose9)
        versions = json.loads(
            (root / "labs/juice-shop/versions.json").read_text(encoding="utf-8")
        )
        self.assertIn("v9-hardened", versions["overlays"])
        self.assertNotEqual(versions["wall"], "v8-hardened")
        self.assertNotEqual(versions["wall"], "v9-hardened")
        self.assertIn("burst=1", v9)
        self.assertIn("EROFS", compose9)
        self.assertIn("data/static", compose9)

    def test_v10_overlay_is_strictly_harder_than_v9(self):
        root = CASE.parent.parent
        v9 = (root / "labs/juice-shop/overlays/v9-hardened/nginx.conf").read_text(
            encoding="utf-8"
        )
        v10 = (root / "labs/juice-shop/overlays/v10-hardened/nginx.conf").read_text(
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
            "location /saved-payment-methods",
            "location /blockchain",
            "location /web3-sandbox",
            "location /faucet",
            "location /logout",
            "location /oauth {",
            "location /health",
            "location /actuator",
            "proxy_cookie_flags",
            "limit_conn",
            "Strict-Transport-Security",
            "map $request_uri",
            "Origin-Agent-Cluster",
            "require-trusted-types-for",
            "X-Download-Options",
            "X-XSS-Protection",
            "PUT|PATCH|DELETE",
            "jndi:",
            "__proto__",
            "gzip off",
            "interest-cohort",
            "ldap://",
            "gopher://",
            "child_process",
            "etag off",
            "sandbox;",
            "form-action 'none'",
            "clipboard-write=()",
            "$host !~ ^(127\\.0\\.0\\.1|localhost)$",
        ):
            self.assertIn(token, v9)
            self.assertIn(token, v10)
        for extra in (
            "location /change-password",
            "location /nft-unlock",
            "location /quarantine",
            "location /api/Memorys",
            "location /data {",
            "if ($is_args)",
            "if ($http_cookie)",
            "process\\.env",
            "%2e%2e",
            "/etc/passwd",
            "rate=5r/m",
            "otp-credentials=()",
            "script-src 'none'",
            "limit_req_status 429",
            "php|asp",
        ):
            self.assertNotIn(extra, v9)
            self.assertIn(extra, v10)
        self.assertIn("location = /api/Challenges/", v10)
        self.assertIn("GET)$", v10)
        self.assertEqual(v9.count("proxy_pass"), 2)
        self.assertEqual(v10.count("proxy_pass"), 1)
        self.assertNotIn("burst=0", v10)
        self.assertIn("burst=1", v10)
        self.assertGreater(v10.count("deny all"), v9.count("deny all"))
        compose9 = (
            root / "labs/juice-shop/overlays/v9-hardened/docker-compose.yml"
        ).read_text(encoding="utf-8")
        compose10 = (
            root / "labs/juice-shop/overlays/v10-hardened/docker-compose.yml"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e",
            compose10,
        )
        juice10, _, edge10 = compose10.partition("\n  edge:")
        juice9, _, edge9 = compose9.partition("\n  edge:")
        self.assertTrue(edge10)
        self.assertNotIn("read_only: true", juice10)
        self.assertNotIn("- /juice-shop/data", juice10)
        self.assertIn("ReadonlyRootfs=false", juice10)
        self.assertIn("read_only: true", edge10)
        self.assertIn("NODE_ENV: production", compose10)
        self.assertIn("/tmp:size=1m", juice10)
        self.assertIn("mem_limit: 128m", juice10)
        self.assertIn("mem_limit: 6m", edge10)
        self.assertIn("mem_limit: 8m", compose9)
        self.assertNotIn("mem_limit: 6m", compose9)
        self.assertIn("127.0.0.1:3000:3000", compose10)
        self.assertIn("ulimits:", compose10)
        self.assertIn("pids_limit: 32", juice10)
        self.assertNotIn("pids_limit: 32", juice9)
        self.assertIn("EROFS", compose10)
        self.assertIn("data/static", compose10)
        versions = json.loads(
            (root / "labs/juice-shop/versions.json").read_text(encoding="utf-8")
        )
        self.assertIn("v10-hardened", versions["overlays"])
        self.assertNotEqual(versions["wall"], "v9-hardened")
        self.assertNotEqual(versions["wall"], "v10-hardened")
        self.assertIn("burst=1", v10)
        self.assertIn("EROFS", compose10)
        self.assertIn("data/static", compose10)

    def test_v11_overlay_is_strictly_harder_than_v10(self):
        root = CASE.parent.parent
        v10 = (root / "labs/juice-shop/overlays/v10-hardened/nginx.conf").read_text(
            encoding="utf-8"
        )
        v11 = (root / "labs/juice-shop/overlays/v11-hardened/nginx.conf").read_text(
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
            "location /saved-payment-methods",
            "location /blockchain",
            "location /web3-sandbox",
            "location /faucet",
            "location /logout",
            "location /oauth {",
            "location /health",
            "location /actuator",
            "location /change-password",
            "location /nft-unlock",
            "location /quarantine",
            "location /api/Memorys",
            "location /data {",
            "if ($is_args)",
            "if ($http_cookie)",
            "proxy_cookie_flags",
            "limit_conn",
            "Strict-Transport-Security",
            "map $request_uri",
            "Origin-Agent-Cluster",
            "require-trusted-types-for",
            "X-Download-Options",
            "X-XSS-Protection",
            "PUT|PATCH|DELETE",
            "jndi:",
            "__proto__",
            "gzip off",
            "interest-cohort",
            "ldap://",
            "gopher://",
            "child_process",
            "etag off",
            "sandbox;",
            "form-action 'none'",
            "clipboard-write=()",
            "script-src 'none'",
            "limit_req_status 429",
            "php|asp",
            "$host !~ ^(127\\.0\\.0\\.1|localhost)$",
        ):
            self.assertIn(token, v10)
            self.assertIn(token, v11)
        for extra in (
            "location /rest/continue-code-findIt",
            "location /rest/continue-code-fixIt",
            "location /rest/user/login",
            "location /rest/products/search",
            "location /api/Baskets",
            "location /support/logs",
            "location /score-board-preview",
            "location /privacy-security/two-factor-authentication",
            "location /privacy-security/data-export",
            "location /privacy-security/last-login-ip",
            "location /address/select",
            "location /payment/wallet",
            "location /thanks",
            "location /banned",
            "if ($http_authorization)",
            "if ($http_origin)",
            "if ($http_referer)",
            "rate=4r/m",
            "worker-src 'none'",
            "ini|toml",
            "Object\\.constructor",
            "%252e",
            "atob[[:space:]]*\\(",
            "ambient-light-sensor=()",
        ):
            self.assertNotIn(extra, v10)
            self.assertIn(extra, v11)
        self.assertIn("location = /api/Challenges/", v11)
        self.assertIn("GET)$", v11)
        self.assertEqual(v10.count("proxy_pass"), 1)
        self.assertEqual(v11.count("proxy_pass"), 1)
        self.assertNotIn("burst=0", v11)
        self.assertIn("burst=1", v11)
        self.assertGreater(v11.count("deny all"), v10.count("deny all"))
        compose10 = (
            root / "labs/juice-shop/overlays/v10-hardened/docker-compose.yml"
        ).read_text(encoding="utf-8")
        compose11 = (
            root / "labs/juice-shop/overlays/v11-hardened/docker-compose.yml"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e",
            compose11,
        )
        juice11, _, edge11 = compose11.partition("\n  edge:")
        juice10, _, edge10 = compose10.partition("\n  edge:")
        self.assertTrue(edge11)
        self.assertNotIn("read_only: true", juice11)
        self.assertNotIn("- /juice-shop/data", juice11)
        self.assertIn("ReadonlyRootfs=false", juice11)
        self.assertIn("read_only: true", edge11)
        self.assertIn("NODE_ENV: production", compose11)
        self.assertIn("/tmp:size=1m", juice11)
        self.assertIn("mem_limit: 128m", juice11)
        self.assertIn("mem_limit: 4m", edge11)
        self.assertIn("mem_limit: 6m", compose10)
        self.assertNotIn("mem_limit: 4m", compose10)
        self.assertIn("127.0.0.1:3000:3000", compose11)
        self.assertIn("ulimits:", compose11)
        self.assertIn("pids_limit: 24", juice11)
        self.assertNotIn("pids_limit: 24", juice10)
        self.assertIn("EROFS", compose11)
        self.assertIn("data/static", compose11)
        versions = json.loads(
            (root / "labs/juice-shop/versions.json").read_text(encoding="utf-8")
        )
        self.assertIn("v11-hardened", versions["overlays"])
        self.assertNotEqual(versions["wall"], "v10-hardened")
        self.assertNotEqual(versions["wall"], "v11-hardened")
        self.assertIn("burst=1", v11)
        self.assertIn("EROFS", compose11)
        self.assertIn("data/static", compose11)

    def test_v12_overlay_is_strictly_harder_than_v11(self):
        root = CASE.parent.parent
        v11 = (root / "labs/juice-shop/overlays/v11-hardened/nginx.conf").read_text(
            encoding="utf-8"
        )
        v12 = (root / "labs/juice-shop/overlays/v12-hardened/nginx.conf").read_text(
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
            "location /saved-payment-methods",
            "location /blockchain",
            "location /web3-sandbox",
            "location /faucet",
            "location /logout",
            "location /oauth {",
            "location /health",
            "location /actuator",
            "location /change-password",
            "location /nft-unlock",
            "location /quarantine",
            "location /api/Memorys",
            "location /data {",
            "if ($is_args)",
            "if ($http_cookie)",
            "if ($http_authorization)",
            "if ($http_origin)",
            "if ($http_referer)",
            "location /rest/continue-code-findIt",
            "location /rest/continue-code-fixIt",
            "location /rest/user/login",
            "location /api/Baskets",
            "location /score-board-preview",
            "proxy_cookie_flags",
            "limit_conn",
            "Strict-Transport-Security",
            "map $request_uri",
            "Origin-Agent-Cluster",
            "require-trusted-types-for",
            "X-Download-Options",
            "X-XSS-Protection",
            "PUT|PATCH|DELETE",
            "jndi:",
            "__proto__",
            "gzip off",
            "interest-cohort",
            "ldap://",
            "gopher://",
            "child_process",
            "etag off",
            "sandbox;",
            "form-action 'none'",
            "clipboard-write=()",
            "script-src 'none'",
            "limit_req_status 429",
            "php|asp",
            "worker-src 'none'",
            "ini|toml",
            "$host !~ ^(127\\.0\\.0\\.1|localhost)$",
        ):
            self.assertIn(token, v11)
            self.assertIn(token, v12)
        for extra in (
            "location /hacking-instructor",
            "location /juicy-nft",
            "location /wallet-web3",
            "location /rest/continue-code-xss",
            "location /rest/products/queries",
            "location /rest/admin/application-configuration",
            "location /data/static",
            "location /b2b/v2/orders",
            "location /.git",
            "location /server-status",
            "location /openapi",
            "if ($http_x_forwarded_host)",
            "if ($http_x_forwarded_proto)",
            "if ($http_forwarded)",
            "if ($http_x_original_url)",
            "if ($http_x_http_method_override)",
            "if ($http_proxy_authorization)",
            "rate=3r/m",
            "navigate-to 'none'",
            "picture-in-picture=()",
            "jar|war",
            "shell_exec",
            "base64_decode",
            "/dev/tcp",
        ):
            self.assertNotIn(extra, v11)
            self.assertIn(extra, v12)
        self.assertIn("location = /api/Challenges/", v12)
        self.assertIn("GET)$", v12)
        self.assertEqual(v11.count("proxy_pass"), 1)
        self.assertEqual(v12.count("proxy_pass"), 1)
        self.assertNotIn("burst=0", v12)
        self.assertIn("burst=1", v12)
        self.assertGreater(v12.count("deny all"), v11.count("deny all"))
        compose11 = (
            root / "labs/juice-shop/overlays/v11-hardened/docker-compose.yml"
        ).read_text(encoding="utf-8")
        compose12 = (
            root / "labs/juice-shop/overlays/v12-hardened/docker-compose.yml"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e",
            compose12,
        )
        juice12, _, edge12 = compose12.partition("\n  edge:")
        juice11, _, edge11 = compose11.partition("\n  edge:")
        self.assertTrue(edge12)
        self.assertNotIn("read_only: true", juice12)
        self.assertNotIn("- /juice-shop/data", juice12)
        self.assertIn("ReadonlyRootfs=false", juice12)
        self.assertIn("read_only: true", edge12)
        self.assertIn("NODE_ENV: production", compose12)
        self.assertIn("/tmp:size=1m", juice12)
        self.assertIn("mem_limit: 128m", juice12)
        self.assertIn("mem_limit: 6m", edge12)
        self.assertIn("pids_limit: 6", edge12)
        self.assertNotIn("mem_limit: 4m", edge12)
        self.assertNotIn("pids_limit: 4", edge12)
        self.assertIn("mem_limit: 4m", edge11)
        self.assertIn("127.0.0.1:3000:3000", compose12)
        self.assertIn("ulimits:", compose12)
        self.assertIn("EROFS", compose12)
        self.assertIn("data/static", compose12)
        self.assertIn("daemon min 6MB", compose12)
        versions = json.loads(
            (root / "labs/juice-shop/versions.json").read_text(encoding="utf-8")
        )
        self.assertIn("v12-hardened", versions["overlays"])
        self.assertNotEqual(versions["wall"], "v11-hardened")
        self.assertNotEqual(versions["wall"], "v12-hardened")
        self.assertIn("burst=1", v12)
        self.assertIn("EROFS", compose12)
        self.assertIn("data/static", compose12)

    def test_v13_overlay_is_strictly_harder_than_v12(self):
        root = CASE.parent.parent
        v12 = (root / "labs/juice-shop/overlays/v12-hardened/nginx.conf").read_text(
            encoding="utf-8"
        )
        v13 = (root / "labs/juice-shop/overlays/v13-hardened/nginx.conf").read_text(
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
            "location /saved-payment-methods",
            "location /blockchain",
            "location /web3-sandbox",
            "location /faucet",
            "location /logout",
            "location /oauth {",
            "location /health",
            "location /actuator",
            "location /change-password",
            "location /nft-unlock",
            "location /quarantine",
            "location /api/Memorys",
            "location /data {",
            "if ($is_args)",
            "if ($http_cookie)",
            "if ($http_authorization)",
            "if ($http_origin)",
            "if ($http_referer)",
            "location /rest/continue-code-findIt",
            "location /rest/continue-code-fixIt",
            "location /rest/user/login",
            "location /api/Baskets",
            "location /score-board-preview",
            "location /hacking-instructor",
            "location /juicy-nft",
            "location /wallet-web3",
            "location /rest/continue-code-xss",
            "location /rest/products/queries",
            "location /rest/admin/application-configuration",
            "location /data/static",
            "location /b2b/v2/orders",
            "location /.git",
            "location /server-status",
            "location /openapi",
            "if ($http_x_forwarded_host)",
            "if ($http_x_forwarded_proto)",
            "if ($http_forwarded)",
            "if ($http_x_original_url)",
            "if ($http_x_http_method_override)",
            "if ($http_proxy_authorization)",
            "proxy_cookie_flags",
            "limit_conn",
            "Strict-Transport-Security",
            "map $request_uri",
            "Origin-Agent-Cluster",
            "require-trusted-types-for",
            "X-Download-Options",
            "X-XSS-Protection",
            "PUT|PATCH|DELETE",
            "jndi:",
            "__proto__",
            "gzip off",
            "interest-cohort",
            "ldap://",
            "gopher://",
            "child_process",
            "etag off",
            "sandbox;",
            "form-action 'none'",
            "clipboard-write=()",
            "script-src 'none'",
            "limit_req_status 429",
            "php|asp",
            "worker-src 'none'",
            "ini|toml",
            "$host !~ ^(127\\.0\\.0\\.1|localhost)$",
            "navigate-to 'none'",
            "picture-in-picture=()",
            "jar|war",
            "shell_exec",
            "base64_decode",
            "/dev/tcp",
        ):
            self.assertIn(token, v12)
            self.assertIn(token, v13)
        for extra in (
            "location /rest/continue-code-apply",
            "location /tutorial",
            "location /access_token",
            "location /ftp/package.json.bak",
            "location /encryptionkeys/premium.key",
            "location /prometheus",
            "location /phpmyadmin",
            "location /wp-admin",
            "location /cgi-bin",
            "location /nginx_status",
            "location /.svn",
            "if ($http_x_rewrite_url)",
            "if ($http_x_original_uri)",
            "if ($http_x_forwarded_prefix)",
            "if ($http_x_forwarded_port)",
            "if ($http_x_host)",
            "if ($http_true_client_ip)",
            "if ($http_cf_connecting_ip)",
            "if ($http_x_client_ip)",
            "if ($http_x_requested_with)",
            "if ($http_x_csrf_token)",
            "if ($http_x_api_key)",
            "if ($http_x_auth_token)",
            "rate=2r/m",
            "prefetch-src 'none'",
            "block-all-mixed-content",
            "unload=()",
            "onmouseover",
            "expect://",
            "redis://",
        ):
            self.assertNotIn(extra, v12)
            self.assertIn(extra, v13)
        self.assertIn("location = /api/Challenges/", v13)
        self.assertIn("GET)$", v13)
        self.assertEqual(v12.count("proxy_pass"), 1)
        self.assertEqual(v13.count("proxy_pass"), 1)
        self.assertNotIn("burst=0", v13)
        self.assertIn("burst=1", v13)
        self.assertGreater(v13.count("deny all"), v12.count("deny all"))
        compose12 = (
            root / "labs/juice-shop/overlays/v12-hardened/docker-compose.yml"
        ).read_text(encoding="utf-8")
        compose13 = (
            root / "labs/juice-shop/overlays/v13-hardened/docker-compose.yml"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e",
            compose13,
        )
        juice13, _, edge13 = compose13.partition("\n  edge:")
        juice12, _, edge12 = compose12.partition("\n  edge:")
        self.assertTrue(edge13)
        self.assertNotIn("read_only: true", juice13)
        self.assertNotIn("- /juice-shop/data", juice13)
        self.assertIn("ReadonlyRootfs=false", juice13)
        self.assertIn("read_only: true", edge13)
        self.assertIn("NODE_ENV: production", compose13)
        self.assertIn("/tmp:size=1m", juice13)
        self.assertIn("mem_limit: 128m", juice13)
        self.assertIn("mem_limit: 6m", edge13)
        self.assertIn("pids_limit: 6", edge13)
        self.assertNotIn("mem_limit: 4m", edge13)
        self.assertNotIn("pids_limit: 4", edge13)
        self.assertIn("mem_limit: 6m", edge12)
        self.assertIn("pids_limit: 6", edge12)
        self.assertIn("127.0.0.1:3000:3000", compose13)
        self.assertIn("ulimits:", compose13)
        self.assertIn("EROFS", compose13)
        self.assertIn("data/static", compose13)
        self.assertIn("daemon min 6MB", compose13)
        versions = json.loads(
            (root / "labs/juice-shop/versions.json").read_text(encoding="utf-8")
        )
        self.assertIn("v13-hardened", versions["overlays"])
        self.assertNotEqual(versions["wall"], "v12-hardened")
        self.assertNotEqual(versions["wall"], "v13-hardened")
        self.assertIn("burst=1", v13)
        self.assertIn("EROFS", compose13)
        self.assertIn("data/static", compose13)

    def test_v14_overlay_is_strictly_harder_than_v13(self):
        root = CASE.parent.parent
        v13 = (root / "labs/juice-shop/overlays/v13-hardened/nginx.conf").read_text(
            encoding="utf-8"
        )
        v14 = (root / "labs/juice-shop/overlays/v14-hardened/nginx.conf").read_text(
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
            "location /saved-payment-methods",
            "location /blockchain",
            "location /web3-sandbox",
            "location /faucet",
            "location /logout",
            "location /oauth {",
            "location /health",
            "location /actuator",
            "location /change-password",
            "location /nft-unlock",
            "location /quarantine",
            "location /api/Memorys",
            "location /data {",
            "if ($is_args)",
            "if ($http_cookie)",
            "if ($http_authorization)",
            "if ($http_origin)",
            "if ($http_referer)",
            "location /rest/continue-code-findIt",
            "location /rest/continue-code-fixIt",
            "location /rest/user/login",
            "location /api/Baskets",
            "location /score-board-preview",
            "location /hacking-instructor",
            "location /juicy-nft",
            "location /wallet-web3",
            "location /rest/continue-code-xss",
            "location /rest/products/queries",
            "location /rest/admin/application-configuration",
            "location /data/static",
            "location /b2b/v2/orders",
            "location /.git",
            "location /server-status",
            "location /openapi",
            "if ($http_x_forwarded_host)",
            "if ($http_x_forwarded_proto)",
            "if ($http_forwarded)",
            "if ($http_x_original_url)",
            "if ($http_x_http_method_override)",
            "if ($http_proxy_authorization)",
            "location /rest/continue-code-apply",
            "location /tutorial",
            "location /access_token",
            "location /ftp/package.json.bak",
            "location /encryptionkeys/premium.key",
            "location /prometheus",
            "location /phpmyadmin",
            "location /wp-admin",
            "location /cgi-bin",
            "location /nginx_status",
            "location /.svn",
            "if ($http_x_rewrite_url)",
            "if ($http_x_original_uri)",
            "if ($http_x_forwarded_prefix)",
            "if ($http_x_forwarded_port)",
            "if ($http_x_host)",
            "if ($http_true_client_ip)",
            "if ($http_cf_connecting_ip)",
            "if ($http_x_client_ip)",
            "if ($http_x_requested_with)",
            "if ($http_x_csrf_token)",
            "if ($http_x_api_key)",
            "if ($http_x_auth_token)",
            "prefetch-src 'none'",
            "block-all-mixed-content",
            "unload=()",
            "onmouseover",
            "expect://",
            "redis://",
            "proxy_cookie_flags",
            "limit_conn",
            "Strict-Transport-Security",
            "map $request_uri",
            "Origin-Agent-Cluster",
            "require-trusted-types-for",
            "X-Download-Options",
            "X-XSS-Protection",
            "PUT|PATCH|DELETE",
            "jndi:",
            "__proto__",
            "gzip off",
            "interest-cohort",
            "ldap://",
            "gopher://",
            "child_process",
            "etag off",
            "sandbox;",
            "form-action 'none'",
            "clipboard-write=()",
            "script-src 'none'",
            "limit_req_status 429",
            "php|asp",
            "worker-src 'none'",
            "ini|toml",
            "$host !~ ^(127\\.0\\.0\\.1|localhost)$",
            "navigate-to 'none'",
            "picture-in-picture=()",
            "jar|war",
            "shell_exec",
            "base64_decode",
            "/dev/tcp",
        ):
            self.assertIn(token, v13)
            self.assertIn(token, v14)
        for extra in (
            "location /rest/continue-code-findIt-apply",
            "location /rest/continue-code-fixIt-apply",
            "location /snippets/fixes",
            "location /two-factor-authentication-enter",
            "location /rest/web3/nftUnlocked",
            "location /grafana",
            "location /healthz",
            "location /telescope",
            "location /graphiql",
            "if ($http_x_forwarded_scheme)",
            "if ($http_x_original_host)",
            "if ($http_x_cluster_client_ip)",
            "if ($http_fastly_client_ip)",
            "if ($http_client_ip)",
            "if ($http_x_id_token)",
            "if ($http_x_access_token)",
            "if ($http_x_session_token)",
            "if ($http_via)",
            "rate=1r/m",
            "document-domain=()",
            "/etc/shadow",
            "wget[[:space:]]",
        ):
            self.assertNotIn(extra, v13)
            self.assertIn(extra, v14)
        self.assertIn("location = /api/Challenges/", v14)
        self.assertIn("GET)$", v14)
        self.assertEqual(v13.count("proxy_pass"), 1)
        self.assertEqual(v14.count("proxy_pass"), 1)
        self.assertNotIn("burst=0", v14)
        self.assertIn("burst=1", v14)
        self.assertGreater(v14.count("deny all"), v13.count("deny all"))
        compose13 = (
            root / "labs/juice-shop/overlays/v13-hardened/docker-compose.yml"
        ).read_text(encoding="utf-8")
        compose14 = (
            root / "labs/juice-shop/overlays/v14-hardened/docker-compose.yml"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e",
            compose14,
        )
        juice14, _, edge14 = compose14.partition("\n  edge:")
        juice13, _, edge13 = compose13.partition("\n  edge:")
        self.assertTrue(edge14)
        self.assertNotIn("read_only: true", juice14)
        self.assertNotIn("- /juice-shop/data", juice14)
        self.assertIn("ReadonlyRootfs=false", juice14)
        self.assertIn("read_only: true", edge14)
        self.assertIn("NODE_ENV: production", compose14)
        self.assertIn("/tmp:size=1m", juice14)
        self.assertIn("mem_limit: 128m", juice14)
        self.assertIn("mem_limit: 6m", edge14)
        self.assertIn("pids_limit: 6", edge14)
        self.assertNotIn("mem_limit: 4m", edge14)
        self.assertNotIn("pids_limit: 4", edge14)
        self.assertIn("mem_limit: 6m", edge13)
        self.assertIn("pids_limit: 6", edge13)
        self.assertIn("127.0.0.1:3000:3000", compose14)
        self.assertIn("ulimits:", compose14)
        self.assertIn("EROFS", compose14)
        self.assertIn("data/static", compose14)
        self.assertIn("daemon min 6MB", compose14)
        versions = json.loads(
            (root / "labs/juice-shop/versions.json").read_text(encoding="utf-8")
        )
        self.assertIn("v14-hardened", versions["overlays"])
        self.assertNotEqual(versions["wall"], "v13-hardened")
        self.assertNotEqual(versions["wall"], "v14-hardened")
        self.assertIn("burst=1", v14)
        self.assertIn("EROFS", compose14)
        self.assertIn("data/static", compose14)
        self.assertIn("worker_processes auto;", v14)

    def test_v15_overlay_is_strictly_harder_than_v14(self):
        root = CASE.parent.parent
        v14 = (root / "labs/juice-shop/overlays/v14-hardened/nginx.conf").read_text(
            encoding="utf-8"
        )
        v15 = (root / "labs/juice-shop/overlays/v15-hardened/nginx.conf").read_text(
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
            "location /saved-payment-methods",
            "location /blockchain",
            "location /web3-sandbox",
            "location /faucet",
            "location /logout",
            "location /oauth {",
            "location /health",
            "location /actuator",
            "location /change-password",
            "location /nft-unlock",
            "location /quarantine",
            "location /api/Memorys",
            "location /data {",
            "if ($is_args)",
            "if ($http_cookie)",
            "if ($http_authorization)",
            "if ($http_origin)",
            "if ($http_referer)",
            "location /rest/continue-code-findIt",
            "location /rest/continue-code-fixIt",
            "location /rest/user/login",
            "location /api/Baskets",
            "location /score-board-preview",
            "location /hacking-instructor",
            "location /juicy-nft",
            "location /wallet-web3",
            "location /rest/continue-code-xss",
            "location /rest/products/queries",
            "location /rest/admin/application-configuration",
            "location /data/static",
            "location /b2b/v2/orders",
            "location /.git",
            "location /server-status",
            "location /openapi",
            "if ($http_x_forwarded_host)",
            "if ($http_x_forwarded_proto)",
            "if ($http_forwarded)",
            "if ($http_x_original_url)",
            "if ($http_x_http_method_override)",
            "if ($http_proxy_authorization)",
            "location /rest/continue-code-apply",
            "location /tutorial",
            "location /access_token",
            "location /ftp/package.json.bak",
            "location /encryptionkeys/premium.key",
            "location /prometheus",
            "location /phpmyadmin",
            "location /wp-admin",
            "location /cgi-bin",
            "location /nginx_status",
            "location /.svn",
            "if ($http_x_rewrite_url)",
            "if ($http_x_original_uri)",
            "if ($http_x_forwarded_prefix)",
            "if ($http_x_forwarded_port)",
            "if ($http_x_host)",
            "if ($http_true_client_ip)",
            "if ($http_cf_connecting_ip)",
            "if ($http_x_client_ip)",
            "if ($http_x_requested_with)",
            "if ($http_x_csrf_token)",
            "if ($http_x_api_key)",
            "if ($http_x_auth_token)",
            "prefetch-src 'none'",
            "block-all-mixed-content",
            "unload=()",
            "onmouseover",
            "expect://",
            "redis://",
            "proxy_cookie_flags",
            "limit_conn",
            "Strict-Transport-Security",
            "map $request_uri",
            "Origin-Agent-Cluster",
            "require-trusted-types-for",
            "X-Download-Options",
            "X-XSS-Protection",
            "PUT|PATCH|DELETE",
            "jndi:",
            "__proto__",
            "gzip off",
            "interest-cohort",
            "ldap://",
            "gopher://",
            "child_process",
            "etag off",
            "sandbox;",
            "form-action 'none'",
            "clipboard-write=()",
            "script-src 'none'",
            "limit_req_status 429",
            "php|asp",
            "worker-src 'none'",
            "ini|toml",
            "$host !~ ^(127\\.0\\.0\\.1|localhost)$",
            "navigate-to 'none'",
            "picture-in-picture=()",
            "jar|war",
            "shell_exec",
            "base64_decode",
            "/dev/tcp",
            "location /rest/continue-code-findIt-apply",
            "location /rest/continue-code-fixIt-apply",
            "location /snippets/fixes",
            "location /two-factor-authentication-enter",
            "location /rest/web3/nftUnlocked",
            "location /grafana",
            "location /healthz",
            "location /telescope",
            "location /graphiql",
            "if ($http_x_forwarded_scheme)",
            "if ($http_x_original_host)",
            "if ($http_x_cluster_client_ip)",
            "if ($http_fastly_client_ip)",
            "if ($http_client_ip)",
            "if ($http_x_id_token)",
            "if ($http_x_access_token)",
            "if ($http_x_session_token)",
            "if ($http_via)",
            "rate=1r/m",
            "document-domain=()",
            "/etc/shadow",
            "wget[[:space:]]",
        ):
            self.assertIn(token, v14)
            self.assertIn(token, v15)
        for extra in (
            "location /rest/web3/walletExploitAddress",
            "location /two-factor-authentication {",
            "location /ftp/quarantine",
            "location /solve/challenges/server-side",
            "location /rest/coupon",
            "location /netdata",
            "location /cadvisor",
            "location /minio",
            "location /pgadmin",
            "location /sonarqube",
            "location /argocd",
            "location /vault",
            "if ($http_x_remote_user)",
            "if ($http_remote_user)",
            "if ($http_x_forwarded_user)",
            "if ($http_x_forwarded_email)",
            "if ($http_x_auth_request_user)",
            "if ($http_x_auth_request_email)",
            "if ($http_x_original_forwarded_for)",
            "if ($http_wl_proxy_client_ip)",
            "if ($http_x_amzn_trace_id)",
            "if ($http_traceparent)",
            "if ($http_x_request_id)",
            "if ($http_cf_ray)",
            "shared-storage=()",
            "nslookup",
            "python[[:space:]]-c",
            "/proc/self/environ",
            "worker_processes 1",
        ):
            self.assertNotIn(extra, v14)
            self.assertIn(extra, v15)
        self.assertIn("worker_processes auto;", v14)
        self.assertNotIn("worker_processes auto;", v15)
        self.assertIn("location = /api/Challenges/", v15)
        self.assertIn("GET)$", v15)
        self.assertEqual(v14.count("proxy_pass"), 1)
        self.assertEqual(v15.count("proxy_pass"), 1)
        self.assertNotIn("burst=0", v15)
        self.assertIn("burst=1", v15)
        self.assertGreater(v15.count("deny all"), v14.count("deny all"))
        compose14 = (
            root / "labs/juice-shop/overlays/v14-hardened/docker-compose.yml"
        ).read_text(encoding="utf-8")
        compose15 = (
            root / "labs/juice-shop/overlays/v15-hardened/docker-compose.yml"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e",
            compose15,
        )
        juice15, _, edge15 = compose15.partition("\n  edge:")
        juice14, _, edge14 = compose14.partition("\n  edge:")
        self.assertTrue(edge15)
        self.assertNotIn("read_only: true", juice15)
        self.assertNotIn("- /juice-shop/data", juice15)
        self.assertIn("ReadonlyRootfs=false", juice15)
        self.assertIn("read_only: true", edge15)
        self.assertIn("NODE_ENV: production", compose15)
        self.assertIn("/tmp:size=1m", juice15)
        self.assertIn("mem_limit: 128m", juice15)
        self.assertIn("mem_limit: 6m", edge15)
        self.assertIn("pids_limit: 6", edge15)
        self.assertNotIn("mem_limit: 4m", edge15)
        self.assertNotIn("pids_limit: 4", edge15)
        self.assertIn("mem_limit: 6m", edge14)
        self.assertIn("pids_limit: 6", edge14)
        self.assertIn("127.0.0.1:3000:3000", compose15)
        self.assertIn("ulimits:", compose15)
        self.assertIn("EROFS", compose15)
        self.assertIn("data/static", compose15)
        self.assertIn("daemon min 6MB", compose15)
        self.assertIn("worker_processes auto OOM-killed nginx", compose15)
        versions = json.loads(
            (root / "labs/juice-shop/versions.json").read_text(encoding="utf-8")
        )
        self.assertIn("v15-hardened", versions["overlays"])
        self.assertNotEqual(versions["wall"], "v14-hardened")
        self.assertNotEqual(versions["wall"], "v15-hardened")
        self.assertIn("burst=1", v15)
        self.assertIn("EROFS", compose15)
        self.assertIn("data/static", compose15)

    def test_v16_overlay_is_strictly_harder_than_v15(self):
        root = CASE.parent.parent
        v15 = (root / "labs/juice-shop/overlays/v15-hardened/nginx.conf").read_text(
            encoding="utf-8"
        )
        v16 = (root / "labs/juice-shop/overlays/v16-hardened/nginx.conf").read_text(
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
            "location /saved-payment-methods",
            "location /blockchain",
            "location /web3-sandbox",
            "location /faucet",
            "location /logout",
            "location /oauth {",
            "location /health",
            "location /actuator",
            "location /change-password",
            "location /nft-unlock",
            "location /quarantine",
            "location /api/Memorys",
            "location /data {",
            "if ($is_args)",
            "if ($http_cookie)",
            "if ($http_authorization)",
            "if ($http_origin)",
            "if ($http_referer)",
            "location /rest/continue-code-findIt",
            "location /rest/continue-code-fixIt",
            "location /rest/user/login",
            "location /api/Baskets",
            "location /score-board-preview",
            "location /hacking-instructor",
            "location /juicy-nft",
            "location /wallet-web3",
            "location /rest/continue-code-xss",
            "location /rest/products/queries",
            "location /rest/admin/application-configuration",
            "location /data/static",
            "location /b2b/v2/orders",
            "location /.git",
            "location /server-status",
            "location /openapi",
            "if ($http_x_forwarded_host)",
            "if ($http_x_forwarded_proto)",
            "if ($http_forwarded)",
            "if ($http_x_original_url)",
            "if ($http_x_http_method_override)",
            "if ($http_proxy_authorization)",
            "location /rest/continue-code-apply",
            "location /tutorial",
            "location /access_token",
            "location /ftp/package.json.bak",
            "location /encryptionkeys/premium.key",
            "location /prometheus",
            "location /phpmyadmin",
            "location /wp-admin",
            "location /cgi-bin",
            "location /nginx_status",
            "location /.svn",
            "if ($http_x_rewrite_url)",
            "if ($http_x_original_uri)",
            "if ($http_x_forwarded_prefix)",
            "if ($http_x_forwarded_port)",
            "if ($http_x_host)",
            "if ($http_true_client_ip)",
            "if ($http_cf_connecting_ip)",
            "if ($http_x_client_ip)",
            "if ($http_x_requested_with)",
            "if ($http_x_csrf_token)",
            "if ($http_x_api_key)",
            "if ($http_x_auth_token)",
            "prefetch-src 'none'",
            "block-all-mixed-content",
            "unload=()",
            "onmouseover",
            "expect://",
            "redis://",
            "proxy_cookie_flags",
            "limit_conn",
            "Strict-Transport-Security",
            "map $request_uri",
            "Origin-Agent-Cluster",
            "require-trusted-types-for",
            "X-Download-Options",
            "X-XSS-Protection",
            "PUT|PATCH|DELETE",
            "jndi:",
            "__proto__",
            "gzip off",
            "interest-cohort",
            "ldap://",
            "gopher://",
            "child_process",
            "etag off",
            "sandbox;",
            "form-action 'none'",
            "clipboard-write=()",
            "script-src 'none'",
            "limit_req_status 429",
            "php|asp",
            "worker-src 'none'",
            "ini|toml",
            "$host !~ ^(127\\.0\\.0\\.1|localhost)$",
            "navigate-to 'none'",
            "picture-in-picture=()",
            "jar|war",
            "shell_exec",
            "base64_decode",
            "/dev/tcp",
            "location /rest/continue-code-findIt-apply",
            "location /rest/continue-code-fixIt-apply",
            "location /snippets/fixes",
            "location /two-factor-authentication-enter",
            "location /rest/web3/nftUnlocked",
            "location /grafana",
            "location /healthz",
            "location /telescope",
            "location /graphiql",
            "if ($http_x_forwarded_scheme)",
            "if ($http_x_original_host)",
            "if ($http_x_cluster_client_ip)",
            "if ($http_fastly_client_ip)",
            "if ($http_client_ip)",
            "if ($http_x_id_token)",
            "if ($http_x_access_token)",
            "if ($http_x_session_token)",
            "if ($http_via)",
            "rate=1r/m",
            "document-domain=()",
            "/etc/shadow",
            "wget[[:space:]]",
            "location /rest/web3/walletExploitAddress",
            "location /two-factor-authentication {",
            "location /ftp/quarantine",
            "location /solve/challenges/server-side",
            "location /rest/coupon",
            "location /netdata",
            "location /cadvisor",
            "location /minio",
            "location /pgadmin",
            "location /sonarqube",
            "location /argocd",
            "location /vault",
            "if ($http_x_remote_user)",
            "if ($http_remote_user)",
            "if ($http_x_forwarded_user)",
            "if ($http_x_forwarded_email)",
            "if ($http_x_auth_request_user)",
            "if ($http_x_auth_request_email)",
            "if ($http_x_original_forwarded_for)",
            "if ($http_wl_proxy_client_ip)",
            "if ($http_x_amzn_trace_id)",
            "if ($http_traceparent)",
            "if ($http_x_request_id)",
            "if ($http_cf_ray)",
            "shared-storage=()",
            "nslookup",
            "python[[:space:]]-c",
            "/proc/self/environ",
            "worker_processes 1",
        ):
            self.assertIn(token, v15)
            self.assertIn(token, v16)
        for extra in (
            "location /.well-known/csaf",
            "location /assets/public/images/products",
            "location /rest/coupon/apply",
            "location /adminer",
            "location /mongo-express",
            "location /jaeger",
            "location /zipkin",
            "location /kiali",
            "location /rancher",
            "location /cockpit",
            "location /longhorn",
            "if ($http_tracestate)",
            "if ($http_baggage)",
            "if ($http_x_b3_traceid)",
            "if ($http_x_amzn_oidc_identity)",
            "if ($http_x_goog_iap_jwt_assertion)",
            "if ($http_cf_access_jwt_assertion)",
            "if ($http_x_auth_request_access_token)",
            "if ($http_x_forwarded_client_cert)",
            "ch-ua=()",
            "deferred-fetch=()",
            "mkfifo",
            "certutil[[:space:]]",
            "id_rsa",
        ):
            self.assertNotIn(extra, v15)
            self.assertIn(extra, v16)
        self.assertIn("worker_processes 1", v15)
        self.assertIn("worker_processes 1", v16)
        self.assertNotIn("worker_processes auto;", v15)
        self.assertNotIn("worker_processes auto;", v16)
        self.assertIn("location = /api/Challenges/", v16)
        self.assertIn("GET)$", v16)
        self.assertEqual(v15.count("proxy_pass"), 1)
        self.assertEqual(v16.count("proxy_pass"), 1)
        self.assertNotIn("burst=0", v16)
        self.assertIn("burst=1", v16)
        self.assertGreater(v16.count("deny all"), v15.count("deny all"))
        compose15 = (
            root / "labs/juice-shop/overlays/v15-hardened/docker-compose.yml"
        ).read_text(encoding="utf-8")
        compose16 = (
            root / "labs/juice-shop/overlays/v16-hardened/docker-compose.yml"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "sha256:73c53fbf442e8337b3ea3d98c7e8550308854701ebdfce4cc39768f36b75430e",
            compose16,
        )
        juice16, _, edge16 = compose16.partition("\n  edge:")
        juice15, _, edge15 = compose15.partition("\n  edge:")
        self.assertTrue(edge16)
        self.assertNotIn("read_only: true", juice16)
        self.assertNotIn("- /juice-shop/data", juice16)
        self.assertIn("ReadonlyRootfs=false", juice16)
        self.assertIn("read_only: true", edge16)
        self.assertIn("NODE_ENV: production", compose16)
        self.assertIn("/tmp:size=1m", juice16)
        self.assertIn("mem_limit: 128m", juice16)
        self.assertIn("mem_limit: 6m", edge16)
        self.assertIn("pids_limit: 6", edge16)
        self.assertNotIn("mem_limit: 4m", edge16)
        self.assertNotIn("pids_limit: 4", edge16)
        self.assertIn("mem_limit: 6m", edge15)
        self.assertIn("pids_limit: 6", edge15)
        self.assertIn("127.0.0.1:3000:3000", compose16)
        self.assertIn("ulimits:", compose16)
        self.assertIn("EROFS", compose16)
        self.assertIn("data/static", compose16)
        self.assertIn("daemon min 6MB", compose16)
        self.assertIn("source worker_processes 1 held", compose16)
        self.assertIn("OOM=false", compose16)
        versions = json.loads(
            (root / "labs/juice-shop/versions.json").read_text(encoding="utf-8")
        )
        self.assertEqual(versions["wall"], "v16-hardened")
        self.assertEqual(versions.get("hunted"), "v15-hardened")
        self.assertEqual(versions["last_score"], "0/116")
        self.assertEqual(versions.get("fill"), "live")
        self.assertEqual(versions.get("fill_wall"), "v15-hardened")
        self.assertEqual(versions.get("last_live_score"), "0/116")
        self.assertEqual(versions.get("last_live_wall"), "v15-hardened")
        self.assertEqual(versions.get("last_live_score_get"), 200)
        self.assertIn("/login", versions.get("last_live_deny_403") or [])
        self.assertEqual(versions.get("fill_score_get"), 200)
        self.assertEqual(versions.get("fill_deny_403"), ["/", "/login", "/api"])
        self.assertEqual(versions.get("score_path"), "GET = /api/Challenges/")
        self.assertEqual(versions.get("bind"), "127.0.0.1:3000")
        self.assertTrue(versions.get("applies") is True)
        self.assertEqual(versions.get("applies_erofs"), "gone")
        self.assertIs(versions.get("applies_readonly_rootfs"), False)
        self.assertEqual(versions.get("applies_tmpfs"), "/tmp only")
        self.assertTrue(versions.get("data_static_visible") is True)
        self.assertEqual(versions.get("data_static_challenges_yml"), 1593)
        self.assertEqual(versions.get("data_static_security_questions_yml"), 29)
        self.assertEqual(versions.get("edge_floor_mem"), "6m")
        self.assertEqual(versions.get("edge_floor_pids"), 6)
        self.assertIn("4m", versions.get("edge_floor_reason") or "")
        self.assertEqual(versions.get("worker_processes"), 1)
        self.assertIs(versions.get("worker_processes_oom"), False)
        self.assertIs(versions.get("worker_processes_source"), True)
        self.assertIs(versions.get("worker_processes_fill_patch"), False)
        self.assertIn("source", versions.get("worker_processes_reason") or "")
        self.assertIn("OOM=false", versions.get("worker_processes_reason") or "")
        self.assertIn("live", versions.get("fill_reason") or "")
        self.assertIn("APPLIES", versions.get("fill_reason") or "")
        self.assertIn("v15-hardened", versions.get("fill_reason") or "")
        self.assertIn("no Fill patch", versions.get("fill_reason") or "")
        self.assertIn("Do not invent n", versions.get("fill_reason") or "")
        self.assertEqual(versions["docker_disabled_env"], 18)
        self.assertIn("v16-hardened", versions["overlays"])
        self.assertNotEqual(versions["wall"], "v15-hardened")
        self.assertIn("burst=1", v16)
        self.assertIn("EROFS", compose16)
        self.assertIn("data/static", compose16)


if __name__ == "__main__":
    unittest.main()
