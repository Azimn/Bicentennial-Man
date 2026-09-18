from __future__ import annotations

from collections import Counter
from pathlib import Path
import tempfile
import unittest

from bicentennial_man.accelerated import _fraction_different, _pairwise, _prepare_history_file
from bicentennial_man.accelerated_history import ACTORS, common_event_ticks, generate_history


class AcceleratedLifeTests(unittest.TestCase):
    def test_common_schedule_matches_age_and_density(self):
        first = common_event_ticks(100_000, 200)
        second = common_event_ticks(100_000, 200)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 200)
        self.assertGreater(first[0], 0)
        self.assertLess(first[-1], 100_000)
        self.assertEqual(len(set(first)), 200)

    def test_histories_are_reproducible_but_seed_specific(self):
        first = generate_history(clone_index=0, seed=20_000, target_ticks=10_000, event_count=40)
        repeat = generate_history(clone_index=0, seed=20_000, target_ticks=10_000, event_count=40)
        other = generate_history(clone_index=1, seed=20_001, target_ticks=10_000, event_count=40)
        self.assertEqual(first.canonical_json(), repeat.canonical_json())
        self.assertEqual(first.sha256(), repeat.sha256())
        self.assertNotEqual(first.sha256(), other.sha256())
        self.assertEqual(
            [event.tick for event in first.events],
            [event.tick for event in other.events],
        )

    def test_actor_exposure_is_balanced(self):
        history = generate_history(clone_index=0, seed=25_000, target_ticks=100_000, event_count=200)
        counts = Counter(event.source for event in history.events)
        self.assertEqual(set(counts), set(ACTORS))
        self.assertEqual(set(counts.values()), {50})

    def test_identical_history_control_copies_bytes_exactly(self):
        history = generate_history(clone_index=0, seed=20_000, target_ticks=1_000, event_count=20)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.json"
            replica = root / "replica.json"
            _prepare_history_file(history=history, history_path=source)
            _prepare_history_file(
                history=history,
                history_path=replica,
                source_history_path=source,
            )
            self.assertEqual(source.read_bytes(), replica.read_bytes())

    def test_identical_history_control_rejects_modified_copy(self):
        history = generate_history(clone_index=0, seed=20_000, target_ticks=1_000, event_count=20)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.json"
            replica = root / "replica.json"
            _prepare_history_file(history=history, history_path=source)
            replica.write_text("{}")
            with self.assertRaises(ValueError):
                _prepare_history_file(
                    history=history,
                    history_path=replica,
                    source_history_path=source,
                )

    def test_pairwise_divergence_reports_behavioral_separation(self):
        rows = [
            ("respond", "repair", "respond"),
            ("respond", "explore", "respond"),
            ("repair", "explore", "respond"),
        ]
        self.assertAlmostEqual(_fraction_different(rows[0], rows[1]), 1 / 3)
        summary = _pairwise(rows)
        self.assertEqual(summary["pairs"], 3.0)
        self.assertGreater(summary["mean"], 0.0)
        self.assertLessEqual(summary["max"], 1.0)

    def test_invalid_event_density_is_rejected(self):
        with self.assertRaises(ValueError):
            common_event_ticks(10, 10)


if __name__ == "__main__":
    unittest.main()
