from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

from bicentennial_man.adapter import JsonProcessOrganism
from bicentennial_man.lab import run_lifetime
from bicentennial_man.protocol import Scenario, SocialTurn


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
    "response_text": f"turn-{count}:{row['speaker']}:{row['text']}",
    "selected_action": "respond",
    "action_id": f"a-{count}",
    "tick": count,
}))
"""


class PhenotypeLabTests(unittest.TestCase):
    def test_process_adapter_preserves_state_across_scenarios(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root / "stub.py"
            script.write_text(STUB, encoding="utf-8")
            organism = JsonProcessOrganism([sys.executable, str(script)], root / "state")
            scenarios = (
                Scenario("one", (SocialTurn("Morgan", "hello"),)),
                Scenario("two", (SocialTurn("Sarah", "again"),)),
            )
            transcripts = run_lifetime(organism, "test", scenarios)
            self.assertEqual(transcripts[0].exchanges[0]["response"], "turn-1:Morgan:hello")
            self.assertEqual(transcripts[1].exchanges[0]["response"], "turn-2:Sarah:again")

    def test_bad_json_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root / "bad.py"
            script.write_text("print('not-json')", encoding="utf-8")
            organism = JsonProcessOrganism([sys.executable, str(script)], root / "state")
            with self.assertRaises(RuntimeError):
                organism.interact(SocialTurn("Morgan", "hello"))


if __name__ == "__main__":
    unittest.main()
