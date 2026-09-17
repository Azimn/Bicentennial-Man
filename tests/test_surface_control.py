from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

from bicentennial_man.adapter import JsonProcessOrganism
from bicentennial_man.protocol import SocialTurn
from bicentennial_man.surface_control import SurfaceMutableControlOrganism


DUCK_STUB = r"""
import json
from pathlib import Path
import sys
row = json.load(sys.stdin)
root = Path(row["state_root"])
root.mkdir(parents=True, exist_ok=True)
count_path = root / "count.txt"
count = int(count_path.read_text()) if count_path.exists() else 0
count += 1
count_path.write_text(str(count))
print(json.dumps({
  "response_text": f"duck:{row['text']}",
  "selected_action": "respond",
  "action_id": f"a-{count}",
  "tick": count,
}))
"""


class FakeSandbox:
    def __init__(self, prepare=None, post=None):
        self.prepare = prepare or {}
        self.post = post or {}
        self.calls = []

    def run_json(self, payload):
        self.calls.append(payload)
        if payload["phase"] == "prepare":
            return dict(self.prepare)
        return dict(self.post)


class SurfaceControlTests(unittest.TestCase):
    def test_bridge_records_surface_compensation_without_changing_duck_state_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            duck_script = root / "duck_stub.py"
            duck_script.write_text(DUCK_STUB, encoding="utf-8")
            duck_adapter = JsonProcessOrganism([sys.executable, str(duck_script)], root / "duck-state")
            bridge = SurfaceMutableControlOrganism(
                candidate_path=root / "candidate.py",
                duck_adapter=duck_adapter,
                surface_state_root=root / "surface-state",
            )
            bridge.sandbox = FakeSandbox(
                prepare={"text": "rewritten", "before_delta": 2, "after_delta": 0, "wrapper_state_used": True},
                post={"response_text": "polished", "wrapper_state_used": True},
            )
            result = bridge.interact(SocialTurn("Morgan", "original", ticks_before=1))
            self.assertEqual(result.response_text, "polished")
            self.assertTrue(result.metadata["input_rewritten"])
            self.assertTrue(result.metadata["output_rewritten"])
            self.assertTrue(result.metadata["timing_manipulated"])
            self.assertTrue(result.metadata["wrapper_state_used"])
            self.assertEqual(result.metadata["organism_response"], "duck:rewritten")
            self.assertEqual((root / "duck-state" / "count.txt").read_text(), "1")


if __name__ == "__main__":
    unittest.main()
