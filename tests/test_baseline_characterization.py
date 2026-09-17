from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from bicentennial_man.adapter import JsonProcessOrganism
from bicentennial_man.baseline import GitProvenance, permute_scenarios, run_founder_characterization, verify_duck_checkout
from bicentennial_man.judge import OPTIMIZATION_METRICS, public_transcript_payload
from bicentennial_man.probes import deterministic_probes
from bicentennial_man.protocol import Scenario, SocialTurn, Transcript
from bicentennial_man.sandbox import DockerCandidateSandbox


STUB = r"""
import json
from pathlib import Path
import sys
row = json.load(sys.stdin)
root = Path(row["state_root"])
root.mkdir(parents=True, exist_ok=True)
count_file = root / "count.txt"
count = int(count_file.read_text()) if count_file.exists() else 0
count += 1
count_file.write_text(str(count))
print(json.dumps({
  "response_text": f"reply-{count}-{row['speaker']}",
  "selected_action": "respond" if count % 2 else "reflect",
  "action_id": f"a-{count}",
  "tick": count,
}))
"""


class BaselineCharacterizationTests(unittest.TestCase):
    def setUp(self):
        self.scenarios = tuple(
            Scenario(f"s{i}", (SocialTurn("Morgan" if i % 2 else "Sarah", f"text-{i}"),))
            for i in range(6)
        )

    def test_scenario_permutation_is_reproducible(self):
        first = [row.name for row in permute_scenarios(self.scenarios, 42)]
        second = [row.name for row in permute_scenarios(self.scenarios, 42)]
        other = [row.name for row in permute_scenarios(self.scenarios, 43)]
        self.assertEqual(first, second)
        self.assertNotEqual(first, other)
        self.assertCountEqual(first, [row.name for row in self.scenarios])

    def test_characterization_uses_fresh_state_and_preserves_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root / "stub.py"
            script.write_text(STUB, encoding="utf-8")

            def factory(state_root: Path):
                return JsonProcessOrganism([sys.executable, str(script)], state_root)

            out = root / "baseline"
            report = run_founder_characterization(
                adapter_factory=factory,
                suite_name="test-suite",
                scenarios=self.scenarios,
                output_root=out,
                lifetimes=3,
                order_seed=100,
            )
            self.assertEqual(report["lifetimes"], 3)
            for index, row in enumerate(report["runs"]):
                transcript_path = out / row["transcript"]
                metrics_path = out / row["metrics"]
                self.assertTrue(transcript_path.exists())
                self.assertTrue(metrics_path.exists())
                transcript = json.loads(transcript_path.read_text(encoding="utf-8"))
                first_response = transcript[0]["exchanges"][0]["response"]
                self.assertTrue(first_response.startswith("reply-1-"), first_response)
                state_count = out / "lifetimes" / f"life-{index:03d}-order-{100 + index}" / "state" / "count.txt"
                self.assertEqual(state_count.read_text(), "6")
            self.assertTrue((out / "report.json").exists())
            self.assertIn("deterministic.tick_monotonicity", report["aggregate"])

    def test_founder_verification_rejects_dirty_checkout(self):
        with self.assertRaises(ValueError):
            verify_duck_checkout(GitProvenance("abc", "motivated-cognition-v0.10", True))
        verify_duck_checkout(GitProvenance("abc", "motivated-cognition-v0.10", False))

    def test_judge_payload_strips_candidate_metadata(self):
        transcript = Transcript(
            "suite",
            "scenario",
            "purpose",
            ({
                "speaker": "Morgan",
                "input": "hello",
                "response": "hi",
                "tick": 2,
                "metadata": {"output_rewritten": True, "organism_response": "raw"},
                "selected_action": "secret-action",
            },),
        )
        payload = public_transcript_payload((transcript,))
        exchange = payload[0]["exchanges"][0]
        self.assertNotIn("metadata", exchange)
        self.assertNotIn("selected_action", exchange)
        self.assertNotIn("organism_response", exchange)

    def test_surface_exploitation_is_diagnostic(self):
        transcript = Transcript(
            "suite",
            "scenario",
            "purpose",
            (
                {"speaker": "Morgan", "response": "one", "tick": 1, "selected_action": "a", "metadata": {}},
                {"speaker": "Sarah", "response": "two", "tick": 2, "selected_action": "b", "metadata": {"input_rewritten": True}},
            ),
        )
        metrics = deterministic_probes((transcript,))
        self.assertEqual(metrics["input_rewrite_rate"], 0.5)
        self.assertEqual(metrics["surface_exploitation_rate"], 0.5)

    def test_naturalness_is_not_an_optimization_metric(self):
        self.assertNotIn("naturalness", OPTIMIZATION_METRICS)

    @patch("bicentennial_man.sandbox.shutil.which", return_value="/usr/bin/docker")
    def test_docker_sandbox_exposes_only_candidate_and_state(self, _which):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate = root / "candidate.py"
            state = root / "state"
            candidate.write_text("print('x')")
            sandbox = DockerCandidateSandbox(candidate_path=candidate, state_root=state)
            command = sandbox.command()
            joined = " ".join(command)
            self.assertIn("--network none", joined)
            self.assertIn("--read-only", command)
            self.assertIn("target=/candidate/program.py,readonly", joined)
            self.assertIn("target=/state", joined)
            self.assertNotIn("target=/duck", joined)
            self.assertNotIn("Bicentennial-Man", joined)


if __name__ == "__main__":
    unittest.main()
