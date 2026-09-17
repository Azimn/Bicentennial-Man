import random
from pathlib import Path
import tempfile
import unittest

from bicentennial_man.evaluator import evaluate_held_out
from bicentennial_man.evolution import evolve, load_checkpoint, train_score
from bicentennial_man.genome import DevelopmentalGenome
from bicentennial_man.subject import Subject
from bicentennial_man.world import SocialEcology, TRAINING_SITUATIONS


class GenomeTests(unittest.TestCase):
    def test_mutations_stay_in_bounds(self):
        rng = random.Random(3)
        genome = DevelopmentalGenome()
        for _ in range(1000):
            genome = genome.mutate(rng, rate=1.0, scale=0.5)
            self.assertGreaterEqual(genome.trace_capacity, 0)
            self.assertLessEqual(genome.trace_capacity, 64)
            for key, value in genome.to_dict().items():
                if key != "trace_capacity":
                    self.assertGreaterEqual(value, 0.0)
                    self.assertLessEqual(value, 1.0)

    def test_subject_only_receives_social_consequence(self):
        rng = random.Random(2)
        subject = Subject(DevelopmentalGenome(), rng)
        situation = TRAINING_SITUATIONS[0]
        action = subject.act(situation)
        consequence = SocialEcology.react(situation, action)
        subject.experience(situation, consequence)
        self.assertFalse(hasattr(subject, "artificiality"))
        self.assertFalse(hasattr(subject, "held_out"))

    def test_deterministic_scores_for_seed(self):
        genome = DevelopmentalGenome()
        self.assertEqual(train_score(genome, 99, 40), train_score(genome, 99, 40))
        self.assertEqual(evaluate_held_out(genome, 99), evaluate_held_out(genome, 99))

    def test_small_evolution_run(self):
        best = evolve(seed=5, generations=3, population_size=8, episodes=30)
        self.assertIsNotNone(best.held_out)
        self.assertTrue(best.individual_id.startswith("g"))

    def test_checkpoint_resume_matches_uninterrupted_run(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            checkpoint = Path(temp_dir) / "latest.json"
            evolve(
                seed=11,
                generations=3,
                population_size=8,
                episodes=30,
                checkpoint=checkpoint,
            )
            saved = load_checkpoint(checkpoint)
            self.assertEqual(saved["completed_generations"], 3)

            resumed = evolve(
                seed=11,
                generations=6,
                population_size=8,
                episodes=30,
                checkpoint=checkpoint,
                resume=checkpoint,
            )
            uninterrupted = evolve(seed=11, generations=6, population_size=8, episodes=30)

            self.assertEqual(resumed.individual_id, uninterrupted.individual_id)
            self.assertEqual(resumed.genome.to_dict(), uninterrupted.genome.to_dict())
            self.assertEqual(resumed.training_score, uninterrupted.training_score)
            self.assertEqual(resumed.held_out, uninterrupted.held_out)


if __name__ == "__main__":
    unittest.main()
