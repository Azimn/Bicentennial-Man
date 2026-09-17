from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import random
from typing import Iterable

from .evaluator import EvaluationResult, evaluate_held_out
from .genome import DevelopmentalGenome
from .subject import Subject
from .world import SocialEcology


@dataclass(slots=True)
class Individual:
    individual_id: str
    generation: int
    parent_id: str | None
    genome: DevelopmentalGenome
    training_score: float = 0.0
    held_out: EvaluationResult | None = None


def train_score(genome: DevelopmentalGenome, seed: int, episodes: int) -> float:
    """Selection signal comes only from experienced social consequences."""
    rng = random.Random(seed)
    subject = Subject(DevelopmentalGenome.from_dict(genome.to_dict()), rng)
    ecology = SocialEcology(rng)
    total = 0.0
    for _ in range(episodes):
        situation = ecology.sample()
        action = subject.act(situation)
        consequence = ecology.react(situation, action)
        subject.experience(situation, consequence)
        total += consequence.viability
    return total / max(1, episodes)


def _record(path: Path, population: Iterable[Individual]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for item in population:
            f.write(json.dumps({
                "individual_id": item.individual_id,
                "generation": item.generation,
                "parent_id": item.parent_id,
                "genome": item.genome.to_dict(),
                "training_score": item.training_score,
                "held_out_artificiality": None if item.held_out is None else item.held_out.artificiality,
                "held_out_viability": None if item.held_out is None else item.held_out.social_viability,
            }, sort_keys=True) + "\n")


def evolve(
    seed: int = 7,
    generations: int = 25,
    population_size: int = 24,
    episodes: int = 200,
    elite_fraction: float = 0.25,
    mutation_rate: float = 0.25,
    mutation_scale: float = 0.12,
    output: Path | None = None,
) -> Individual:
    rng = random.Random(seed)
    founder = DevelopmentalGenome()
    population = [
        Individual(f"g0000-i{i:04d}", 0, None, founder.mutate(rng, rate=0.75, scale=0.18))
        for i in range(population_size)
    ]
    population[0].genome = founder

    best: Individual | None = None
    for generation in range(generations):
        for i, individual in enumerate(population):
            eval_seed = seed * 1_000_003 + generation * 10_007 + i
            individual.training_score = train_score(individual.genome, eval_seed, episodes)
            individual.held_out = evaluate_held_out(individual.genome, eval_seed + 91_991)

        population.sort(key=lambda x: x.training_score, reverse=True)
        if best is None or population[0].training_score > best.training_score:
            best = population[0]
        if output:
            _record(output, population)

        elite_n = max(2, int(population_size * elite_fraction))
        elites = population[:elite_n]
        next_population: list[Individual] = []
        for i in range(population_size):
            parent = elites[i % elite_n]
            child_genome = DevelopmentalGenome.from_dict(parent.genome.to_dict())
            if i >= elite_n:
                child_genome = child_genome.mutate(rng, mutation_rate, mutation_scale)
            next_population.append(Individual(
                individual_id=f"g{generation + 1:04d}-i{i:04d}",
                generation=generation + 1,
                parent_id=parent.individual_id,
                genome=child_genome,
            ))
        population = next_population

    assert best is not None
    return best
