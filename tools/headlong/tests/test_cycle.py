#!/usr/bin/env python3
"""Tests for the think-run-FINAL cycle."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOOP = ROOT / "loop.py"
TOY_TASK = "Print 6 times 7 as a single integer."


def run_loop(home: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(LOOP), "--home", str(home), *args],
        check=False,
        capture_output=True,
        text=True,
    )


class CycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.home = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_toy_cycle_sets_final_42(self) -> None:
        proof = self.home / "proof.md"
        proc = run_loop(
            self.home,
            "cycle",
            "--task",
            TOY_TASK,
            "--proof",
            str(proof),
        )
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        out = json.loads(proc.stdout)
        self.assertTrue(out["ok"])
        self.assertEqual(out["final"], "42")
        self.assertEqual(out["reason"], "final")
        self.assertEqual(out["rounds"], 1)

        steps = [
            json.loads(line)
            for line in (self.home / "trajectory.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        types = [s["type"] for s in steps]
        self.assertEqual(types[:4], ["observation", "think", "run", "final"])
        self.assertIn("print(6 * 7)", steps[1]["content"])
        self.assertEqual(steps[2]["exit"], 0)
        self.assertEqual(steps[3]["content"], "42")
        self.assertTrue(proof.exists())
        body = proof.read_text(encoding="utf-8")
        self.assertIn("## Invoke", body)
        self.assertIn("## Trajectory snippet (think + run)", body)
        self.assertIn("## FINAL", body)
        self.assertIn("42", body)

    def test_same_fingerprint_twice_stops(self) -> None:
        think = self.home / "noop.sh"
        think.write_text('echo "no final this round"\n', encoding="utf-8")
        proc = run_loop(
            self.home,
            "cycle",
            "--task",
            "echo only",
            "--think-file",
            str(think),
        )
        self.assertEqual(proc.returncode, 1, proc.stderr + proc.stdout)
        out = json.loads(proc.stdout)
        self.assertFalse(out["ok"])
        self.assertEqual(out["reason"], "same_fingerprint")
        self.assertEqual(out["rounds"], 2)

        steps = [
            json.loads(line)
            for line in (self.home / "trajectory.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        types = [s["type"] for s in steps]
        self.assertIn("stop", types)
        stop = next(s for s in steps if s["type"] == "stop")
        self.assertEqual(stop["reason"], "same_fingerprint")
        thinks = [s for s in steps if s["type"] == "think"]
        self.assertEqual(thinks[0]["fingerprint"], thinks[1]["fingerprint"])

    def test_cycle_refuses_secrets(self) -> None:
        proc = run_loop(
            self.home,
            "cycle",
            "--task",
            "OPENAI_API_KEY=sk-ant-not-a-real-key",
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertFalse((self.home / "trajectory.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
