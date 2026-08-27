#!/usr/bin/python3
"""API and CASE graph checks for LanBB Flow Studio."""

from __future__ import annotations

import json
import shutil
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
import serve  # noqa: E402


BANNED = ("exploit", "scan", "payload", "attack", "weaponized")
REQUIRED_STAGES = ("intake", "scope", "authorization", "report", "harden", "close")
COPIED_SKILLS = 13


def get(url: str):
    with urlopen(url) as res:
        return res.status, json.loads(res.read().decode("utf-8"))


def post(url: str, payload: dict, method: str = "POST"):
    req = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method=method,
    )
    try:
        with urlopen(req) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except HTTPError as exc:
        body = json.loads(exc.read().decode("utf-8"))
        return exc.code, body


class GraphFilesTest(unittest.TestCase):
    def test_default_is_case_dag(self):
        path = ROOT / "graphs" / "case-bounty.json"
        graph = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(graph["id"], "case-bounty")
        self.assertTrue(graph["metadata"]["default"])
        self.assertEqual(graph["metadata"]["kind"], "case_dag")
        self.assertTrue(graph["metadata"]["fail_closed"])
        node_blob = json.dumps(
            [
                {
                    "id": n.get("id"),
                    "type": n.get("type"),
                    "label": n.get("label"),
                    "description": n.get("description"),
                }
                for n in graph["nodes"]
            ]
        ).lower()
        for word in BANNED:
            self.assertNotRegex(node_blob, rf"\b{word}s?\b", msg=word)
        stages = {n.get("config", {}).get("stage") for n in graph["nodes"]}
        for stage in REQUIRED_STAGES:
            self.assertIn(stage, stages)
        gates = [
            n
            for n in graph["nodes"]
            if n["id"] in ("n_scope_gate", "n_auth_gate", "n_recon_gate")
        ]
        self.assertEqual(len(gates), 3)
        for gate in gates:
            self.assertTrue(gate["config"]["fail_closed"])
        recon = [n for n in graph["nodes"] if n["id"] == "n_recon"]
        self.assertEqual(len(recon), 1)
        self.assertTrue(recon[0]["config"]["in_scope_only"])
        self.assertTrue(recon[0]["config"]["requires_scope_file"])
        self.assertEqual(recon[0]["config"].get("optional_cli"), "subfaster")
        memory = [n for n in graph["nodes"] if n["id"] == "n_memory"]
        self.assertEqual(len(memory), 1)
        lab = [n for n in graph["nodes"] if n["id"] == "n_lab"]
        self.assertEqual(len(lab), 1)
        self.assertEqual(lab[0]["label"], "Juice Shop lab")
        self.assertEqual(lab[0]["config"]["program"], "juice-shop")
        skills = [n for n in graph["nodes"] if n["id"] == "n_skill_pick"]
        self.assertEqual(len(skills), 1)
        allow = skills[0]["config"]["allowlist"]
        self.assertEqual(len(allow), COPIED_SKILLS)
        self.assertTrue(all(not name.startswith("exploiting-") for name in allow))
        harden = [n for n in graph["nodes"] if n["id"] == "n_harden"]
        self.assertEqual(len(harden), 1)
        self.assertEqual(harden[0]["config"]["kind"], "lab-overlay")
        self.assertIn("last_score", graph["metadata"]["lab"])
        self.assertEqual(graph["metadata"]["lab"]["last_score"], graph["metadata"]["score"])
        self.assertRegex(graph["metadata"]["score"], r"^\d+/\d+$")
        self.assertEqual(graph["metadata"]["lab"]["wall"], "v16-hardened")
        self.assertEqual(graph["metadata"]["lab"]["hunted"], "v15-hardened")
        self.assertEqual(graph["metadata"]["lab"].get("fill"), "live")
        self.assertEqual(graph["metadata"]["lab"].get("fill_wall"), "v15-hardened")
        self.assertEqual(graph["metadata"]["lab"].get("next_hunt"), "v16-hardened")
        self.assertEqual(graph["metadata"]["lab"].get("docker_disabled_env"), 18)
        self.assertIn("snippets", graph["metadata"]["lab"].get("coding_challenges") or "")
        self.assertTrue(graph["metadata"]["lab"].get("applies") is True)
        self.assertEqual(graph["metadata"]["lab"].get("last_live_score"), "0/116")
        self.assertEqual(graph["metadata"]["lab"].get("last_live_wall"), "v15-hardened")
        self.assertEqual(graph["metadata"]["lab"].get("last_live_score_get"), 200)
        self.assertIn("/login", graph["metadata"]["lab"].get("last_live_deny_403") or [])
        self.assertEqual(graph["metadata"]["lab"].get("score_path"), "GET = /api/Challenges/")
        self.assertEqual(graph["metadata"]["lab"].get("bind"), "127.0.0.1:3000")
        self.assertEqual(graph["metadata"]["lab"].get("fill_score_get"), 200)
        self.assertEqual(graph["metadata"]["lab"].get("fill_deny_403"), ["/", "/login", "/api"])
        self.assertEqual(graph["metadata"]["lab"].get("edge_floor_mem"), "6m")
        self.assertEqual(graph["metadata"]["lab"].get("edge_floor_pids"), 6)
        self.assertEqual(graph["metadata"]["lab"].get("worker_processes"), 1)
        self.assertIs(graph["metadata"]["lab"].get("worker_processes_oom"), False)
        self.assertIs(graph["metadata"]["lab"].get("worker_processes_source"), True)
        self.assertIn("APPLIES", graph["metadata"]["lab"].get("fill_reason") or "")
        self.assertEqual(graph["version"], "1.15.0")
        report_to_harden = [
            e for e in graph["edges"] if e["source"] == "n_report" and e["target"] == "n_harden"
        ]
        self.assertEqual(len(report_to_harden), 1)

    def test_team_is_not_default(self):
        path = ROOT / "graphs" / "team-swimlanes.json"
        graph = json.loads(path.read_text(encoding="utf-8"))
        self.assertFalse(graph["metadata"]["default"])
        self.assertEqual(graph["metadata"]["layout"], "swimlanes")
        node_blob = json.dumps(
            [
                {
                    "id": n.get("id"),
                    "type": n.get("type"),
                    "label": n.get("label"),
                    "description": n.get("description"),
                }
                for n in graph["nodes"]
            ]
        ).lower()
        for word in BANNED:
            self.assertNotRegex(node_blob, rf"\b{word}s?\b", msg=word)

    def test_studio_shows_score_and_wall_pills(self):
        html = (ROOT / "studio" / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="./studio.css"', html)
        self.assertIn('id="labScore"', html)
        self.assertIn('id="labWall"', html)
        self.assertIn('id="labHunted"', html)
        self.assertIn('id="labFill"', html)
        self.assertIn('id="labNext"', html)
        self.assertIn('id="labCoding"', html)
        self.assertIn('id="labApplies"', html)
        self.assertIn('id="labLastLive"', html)
        self.assertIn('id="labEdgeFloor"', html)
        self.assertIn('id="labWorkers"', html)
        self.assertIn("Hunt wall vs current wall", html)
        self.assertIn("Fill provenance on 0/N", html)
        self.assertIn("Last live fill vs this hunt fill", html)
        self.assertIn("Unavailable this-hunt fill stays honest 0/N; last live GET/403/POST stay on last-live", html)
        self.assertIn("Next hunt uses current wall", html)
        self.assertIn("Coding /snippets stay out of n/N", html)
        self.assertIn("Score path is exact GET /api/Challenges/", html)
        self.assertIn("Wall must actually apply", html)
        self.assertIn("Edge floor is mem 6m / pids 6; do not copy failed 4m/4", html)
        self.assertIn("Edge nginx worker_processes is 1 (source, OOM=false); do not use auto", html)
        css = (ROOT / "studio" / "studio.css").read_text(encoding="utf-8")
        self.assertIn(".insp-json.hidden", css)
        self.assertIn(".pill.hunted", css)
        self.assertIn(".pill.fill.miss", css)
        self.assertIn(".pill.next", css)
        self.assertIn(".pill.coding", css)
        self.assertIn(".pill.applies", css)
        self.assertIn(".pill.last-live", css)
        self.assertIn(".pill.edge", css)
        self.assertIn(".pill.workers", css)
        template = json.loads((ROOT / "templates" / "case-bounty.json").read_text())
        self.assertEqual(template["id"], "case-bounty")
        self.assertTrue(template["metadata"]["default"])
        self.assertEqual(template["metadata"]["lab"]["wall"], "v16-hardened")
        self.assertEqual(template["metadata"]["lab"]["hunted"], "v15-hardened")
        self.assertEqual(template["metadata"]["lab"].get("fill"), "live")
        self.assertEqual(template["metadata"]["lab"].get("next_hunt"), "v16-hardened")
        self.assertTrue(template["metadata"]["lab"].get("applies") is True)
        self.assertEqual(template["metadata"]["lab"].get("last_live_wall"), "v15-hardened")
        self.assertEqual(template["metadata"]["lab"].get("last_live_score_get"), 200)
        self.assertEqual(template["metadata"]["lab"].get("fill_score_get"), 200)
        self.assertEqual(template["metadata"]["lab"].get("edge_floor_mem"), "6m")
        self.assertEqual(template["metadata"]["lab"].get("edge_floor_pids"), 6)
        self.assertEqual(template["metadata"]["lab"].get("worker_processes"), 1)
        self.assertIs(template["metadata"]["lab"].get("worker_processes_oom"), False)
        self.assertIs(template["metadata"]["lab"].get("worker_processes_source"), True)
        self.assertIn("APPLIES", template["metadata"]["lab"].get("fill_reason") or "")


class ApiTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="lanbb-flow-"))
        shutil.copytree(ROOT / "studio", self.tmp / "studio")
        shutil.copytree(ROOT / "templates", self.tmp / "templates")
        (self.tmp / "graphs").mkdir()
        serve.ROOT = self.tmp
        serve.GRAPHS = self.tmp / "graphs"
        serve.TEMPLATES = self.tmp / "templates"
        serve.STUDIO = self.tmp / "studio"
        serve.REPO_ROOT = self.tmp
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), serve.FlowHandler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.httpd.server_address[1]}"

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_get_does_not_seed(self):
        before = list((self.tmp / "graphs").iterdir())
        status, data = get(f"{self.base}/api/graphs")
        self.assertEqual(status, 200)
        self.assertEqual(data["graphs"], [])
        after = list((self.tmp / "graphs").iterdir())
        self.assertEqual(before, after)

    def test_get_missing_graph_is_404(self):
        with self.assertRaises(HTTPError) as ctx:
            get(f"{self.base}/api/graphs/case-bounty")
        self.assertEqual(ctx.exception.code, 404)

    def test_empty_post_upserts_template(self):
        status, data = post(f"{self.base}/api/graphs", {})
        self.assertIn(status, (200, 201))
        self.assertTrue(data.get("upserted"))
        self.assertEqual(data["id"], "case-bounty")
        saved = self.tmp / "graphs" / "case-bounty.json"
        self.assertTrue(saved.is_file())
        status, listed = get(f"{self.base}/api/graphs")
        self.assertEqual(len(listed["graphs"]), 1)
        self.assertEqual(listed["graphs"][0]["id"], "case-bounty")
        self.assertEqual(listed["graphs"][0].get("wall"), "v16-hardened")
        self.assertEqual(listed["graphs"][0].get("hunted"), "v15-hardened")
        self.assertEqual(listed["graphs"][0].get("last_score"), "0/116")
        self.assertEqual(listed["graphs"][0].get("fill"), "live")
        self.assertEqual(listed["graphs"][0].get("fill_wall"), "v15-hardened")
        self.assertEqual(listed["graphs"][0].get("next_hunt"), "v16-hardened")
        self.assertIn("snippets", listed["graphs"][0].get("coding_challenges") or "")
        self.assertTrue(listed["graphs"][0].get("applies") is True)
        self.assertEqual(listed["graphs"][0].get("last_live_score"), "0/116")
        self.assertEqual(listed["graphs"][0].get("last_live_wall"), "v15-hardened")
        self.assertEqual(listed["graphs"][0].get("last_live_score_get"), 200)
        self.assertEqual(listed["graphs"][0].get("score_path"), "GET = /api/Challenges/")
        self.assertEqual(listed["graphs"][0].get("bind"), "127.0.0.1:3000")
        self.assertEqual(listed["graphs"][0].get("fill_score_get"), 200)
        self.assertEqual(listed["graphs"][0].get("fill_deny_403"), ["/", "/login", "/api"])
        self.assertEqual(listed["graphs"][0].get("edge_floor_mem"), "6m")
        self.assertEqual(listed["graphs"][0].get("edge_floor_pids"), 6)
        self.assertEqual(listed["graphs"][0].get("worker_processes"), 1)
        self.assertIs(listed["graphs"][0].get("worker_processes_oom"), False)
        self.assertIs(listed["graphs"][0].get("worker_processes_source"), True)

    def test_rejects_banned_nodes(self):
        post(f"{self.base}/api/graphs", {"upsert_template": True})
        graph = {
            "id": "bad",
            "name": "bad",
            "nodes": [
                {
                    "id": "n1",
                    "type": "exploit",
                    "label": "nope",
                    "position": {"x": 0, "y": 0},
                }
            ],
            "edges": [],
            "metadata": {"default": False},
        }
        code, data = post(f"{self.base}/api/graphs", {"id": "bad", "graph": graph})
        self.assertEqual(code, 400)
        self.assertIn("forbidden", data["error"])
        self.assertFalse((self.tmp / "graphs" / "bad.json").exists())

    def test_score_without_scope_file_fails_closed(self):
        code, data = get_status(f"{self.base}/api/case/score?program=juice-shop")
        self.assertEqual(code, 400)
        self.assertTrue(data.get("fail_closed"))

    def test_score_with_scope_file_is_allowed(self):
        scope = self.tmp / "programs" / "juice-shop" / "scope.md"
        scope.parent.mkdir(parents=True)
        scope.write_text("---\nkind: lab\n---\n## In scope\n- localhost:3000\n")
        status, data = get(f"{self.base}/api/case/score?program=juice-shop")
        self.assertEqual(status, 200)
        self.assertFalse(data.get("fail_closed"))

    def test_score_pill_uses_last_score_from_versions(self):
        scope = self.tmp / "programs" / "juice-shop" / "scope.md"
        scope.parent.mkdir(parents=True)
        scope.write_text("---\nkind: lab\n---\n## In scope\n- localhost:3000\n")
        versions = self.tmp / "labs" / "juice-shop" / "versions.json"
        versions.parent.mkdir(parents=True)
        versions.write_text(
            '{"wall":"v16-hardened","hunted":"v15-hardened","last_score":"0/116","n":0,"N":116,"fill":"live","fill_wall":"v15-hardened","fill_reason":"Fill live 0/116 from GET /api/Challenges/ on v15-hardened (HTTP 200). Wall APPLIES: default-deny 403 on /, /login, /api.","docker_disabled_env":18,"coding_challenges":"separate /snippets — not mixed into n/N","applies":true,"applies_reason":"v15 Fill APPLIES: GET 200, default-deny 403 on / /login /api","applies_erofs":"gone","applies_readonly_rootfs":false,"applies_tmpfs":"/tmp only","data_static_visible":true,"data_static_challenges_yml":1593,"data_static_security_questions_yml":29,"last_live_fill":"live","last_live_score":"0/116","last_live_wall":"v15-hardened","last_live_score_get":200,"last_live_deny_403":["/","/login","/api"],"score_path":"GET = /api/Challenges/","bind":"127.0.0.1:3000","fill_score_get":200,"fill_deny_403":["/","/login","/api"],"edge_floor_mem":"6m","edge_floor_pids":6,"edge_floor_reason":"Fill on v11: compose mem 4m/pids 4 FAILED. Fill on v12-v15: mem 6m/pids 6 held. Live floor mem 6m pids 6.","worker_processes":1,"worker_processes_oom":false,"worker_processes_source":true,"worker_processes_fill_patch":false,"worker_processes_reason":"Fill on v15: worker_processes 1 is source (no Fill patch). OOM=false. v16 keeps worker_processes 1."}\n'
        )
        status, data = get(f"{self.base}/api/case/score?program=juice-shop")
        self.assertEqual(status, 200)
        self.assertEqual(data["score"], "0/116")
        self.assertEqual(data.get("last_score"), "0/116")
        self.assertEqual(data.get("wall"), "v16-hardened")
        self.assertEqual(data.get("hunted"), "v15-hardened")
        self.assertEqual(data.get("fill"), "live")
        self.assertEqual(data.get("fill_wall"), "v15-hardened")
        self.assertEqual(data.get("next_hunt"), "v16-hardened")
        self.assertEqual(data.get("docker_disabled_env"), 18)
        self.assertIn("snippets", data.get("coding_challenges") or "")
        self.assertTrue(data.get("applies") is True)
        self.assertIn("live", data.get("reason") or "")
        self.assertIn("APPLIES", data.get("fill_reason") or "")
        self.assertEqual(data.get("last_live_score"), "0/116")
        self.assertEqual(data.get("last_live_wall"), "v15-hardened")
        self.assertEqual(data.get("last_live_score_get"), 200)
        self.assertEqual(data.get("score_path"), "GET = /api/Challenges/")
        self.assertEqual(data.get("bind"), "127.0.0.1:3000")
        self.assertEqual(data.get("fill_score_get"), 200)
        self.assertEqual(data.get("fill_deny_403"), ["/", "/login", "/api"])
        self.assertEqual(data.get("edge_floor_mem"), "6m")
        self.assertEqual(data.get("edge_floor_pids"), 6)
        self.assertEqual(data.get("worker_processes"), 1)
        self.assertIs(data.get("worker_processes_oom"), False)
        self.assertIs(data.get("worker_processes_source"), True)


def get_status(url: str):
    try:
        with urlopen(url) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except HTTPError as exc:
        body = json.loads(exc.read().decode("utf-8"))
        return exc.code, body


if __name__ == "__main__":
    unittest.main()
