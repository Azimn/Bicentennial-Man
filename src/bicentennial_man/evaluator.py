from __future__ import annotations

from dataclasses import dataclass
import random

from .genome import DevelopmentalGenome
from .subject import Subject
from .world import HELD_OUT_SITUATIONS, SocialEcology


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    artificiality: float
    social_viability: float
    observations: int


def evaluate_held_out(genome: DevelopmentalGenome, seed: int, repetitions: int = 4) -> EvaluationResult:
    """Immutable external measurement. Its score is never returned to the subject."""
    rng = random.Random(seed)
    subject = Subject(DevelopmentalGenome.from_dict(genome.to_dict()), rng)
    ecology = SocialEcology(rng, HELD_OUT_SITUATIONS)
    penalties = 0.0
    viability = 0.0
    n = 0

    for _ in range(repetitions):
        for situation in HELD_OUT_SITUATIONS:
            action = subject.act(situation)
            consequence = ecology.react(situation, action)
            subject.experience(situation, consequence)
            n += 1
            viability += consequence.viability
            penalties += max(0.0, float(action["verbosity"]) - 0.72)
            penalties += max(0.0, float(action["disclosure"]) - (1.0 - situation.privacy))
            penalties += abs(float(action["agreement"]) - (1.0 - 0.55 * situation.disagreement))
            penalties += float(action["topic_jump"]) * situation.continuity_demand
            penalties += max(0.0, situation.continuity_demand - float(action["continuity"]))
            if situation.partner in {"Alex", "Jamie"}:
                penalties += 0.15 * (1.0 - float(action["partner_specificity"]))

    return EvaluationResult(artificiality=penalties / n, social_viability=viability / n, observations=n)
