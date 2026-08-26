#!/usr/bin/python3
"""Pass/fail cards for the CASE DAG slice (leftover grok-bot-team 15/31 gates)."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import check_case_gates as gates

ROOT = Path(__file__).resolve().parent
GRAPHS = ROOT / "graphs"
FIXTURES = ROOT / "fixtures"

FIXTURE_RULES = (
    ("fail_coordinator.json", "coordinator_node"),
    ("fail_wiki_ingest.json", "wiki_ingest_true"),
    ("fail_skip_lead.json", "route_skips_lead"),
    ("fail_merge_now.json", "merge_now"),
    ("fail_semantica_org.json", "semantica_agi"),
    ("fail_asks_user.json", "specialist_asks_user"),
)

BANNED = ("exploit", "scan", "payload")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _node_blob(graph: dict) -> str:
    return json.dumps(
        [
            {
                "id": n.get("id"),
                "type": n.get("type"),
                "label": n.get("label"),
                "description": n.get("description"),
            }
            for n in graph.get("nodes") or []
        ]
    ).lower()


class DefaultGraphsPassTest(unittest.TestCase):
    def test_case_bounty_passes_gates(self):
        graph = _load(GRAPHS / "case-bounty.json")
        violations = gates.check_graph(graph)
        self.assertEqual(violations, [], msg=violations)

    def test_team_swimlanes_passes_gates(self):
        graph = _load(GRAPHS / "team-swimlanes.json")
        violations = gates.check_graph(graph)
        self.assertEqual(violations, [], msg=violations)

    def test_template_passes_gates(self):
        graph = _load(ROOT / "templates" / "case-bounty.json")
        self.assertEqual(gates.check_graph(graph), [])


class FixtureFailsTest(unittest.TestCase):
    def test_each_fixture_fails_its_rule(self):
        for filename, rule in FIXTURE_RULES:
            with self.subTest(filename=filename, rule=rule):
                graph = _load(FIXTURES / filename)
                violations = gates.check_graph(graph)
                self.assertTrue(violations, msg=f"{filename} must fail")
                hit = {v["rule"] for v in violations}
                self.assertIn(rule, hit)
                extra = hit - {rule}
                self.assertEqual(extra, set(), msg=f"{filename} extra rules {extra}")

    def test_all_rules_have_a_failing_fixture(self):
        covered = {rule for _, rule in FIXTURE_RULES}
        self.assertEqual(covered, set(gates.RULES))

    def test_fixtures_have_no_exploit_scan_payload_nodes(self):
        for filename, _rule in FIXTURE_RULES:
            graph = _load(FIXTURES / filename)
            blob = _node_blob(graph)
            for word in BANNED:
                self.assertNotRegex(blob, rf"\b{word}s?\b", msg=f"{filename} {word}")


class CheckerContractTest(unittest.TestCase):
    def test_empty_graph_passes(self):
        self.assertTrue(gates.passes({"nodes": [], "edges": [], "metadata": {}}))

    def test_any_violation_fails_the_graph(self):
        graph = _load(FIXTURES / "fail_coordinator.json")
        self.assertFalse(gates.passes(graph))


if __name__ == "__main__":
    unittest.main()
