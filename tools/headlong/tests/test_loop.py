#!/usr/bin/env python3
"""Tests for the offline Headlong / persistent RLM stub."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOOP = ROOT / "loop.py"


def run_loop(home: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(LOOP), "--home", str(home), *args],
        check=False,
        capture_output=True,
        text=True,
    )


class LoopStubTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.home = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_human_message_is_observation_not_new_session(self) -> None:
        first = run_loop(self.home, "observe", "hello from a human")
        self.assertEqual(first.returncode, 0, first.stderr)
        run_loop(self.home, "tick", "--ticks", "1")
        run_loop(self.home, "observe", "second ping")
        second_tick = run_loop(self.home, "tick", "--ticks", "1")
        self.assertEqual(second_tick.returncode, 0, second_tick.stderr)

        traj = (self.home / "trajectory.jsonl").read_text(encoding="utf-8").strip().splitlines()
        steps = [json.loads(line) for line in traj]
        types = [s["type"] for s in steps]
        self.assertEqual(types[0], "observation")
        self.assertEqual(steps[0]["source"], "human")
        self.assertIn("thought", types)
        self.assertEqual(len([s for s in steps if s["type"] == "observation"]), 2)

        st = json.loads(run_loop(self.home, "status").stdout)
        self.assertTrue(st["same_session"])
        self.assertFalse(st["agentsky"])
        self.assertFalse(st["llm"])
        self.assertEqual(st["steps"], len(steps))

    def test_nested_rlm_sub_tick_uses_isolated_context(self) -> None:
        run_loop(self.home, "observe", "sub: what is in CONTEXT")
        tick = run_loop(self.home, "tick")
        self.assertEqual(tick.returncode, 0, tick.stderr)
        steps = [
            json.loads(line)
            for line in (self.home / "trajectory.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        subs = [s for s in steps if s["type"] == "rlm_sub"]
        self.assertEqual(len(subs), 1)
        self.assertEqual(subs[0]["query"], "what is in CONTEXT")
        self.assertIn("FINAL=", subs[0]["content"])

    def test_refuses_secret_looking_text(self) -> None:
        bad = run_loop(self.home, "observe", "OPENAI_API_KEY=sk-ant-not-a-real-key")
        self.assertNotEqual(bad.returncode, 0)
        self.assertFalse((self.home / "trajectory.jsonl").exists())

    def test_idle_tick_without_observation(self) -> None:
        proc = run_loop(self.home, "tick")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rec = json.loads(proc.stdout)
        self.assertEqual(rec["type"], "thought")
        self.assertIn("idle", rec["content"])


if __name__ == "__main__":
    unittest.main()
