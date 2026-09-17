from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import random
from typing import Any, Iterable

from .evaluator import EvaluationResult, evaluate_held_out
from .genome import DevelopmentalGenome
from .subject import Subject
from .world import SocialEcology


CHECKPOINT_FORMAT_VERSION = 1


@dataclass(slots=True)
class Individual:
    individual_id: str
    generation: int
    parent_id: str | None
    genome: DevelopmentalGenome
    training_score: float = 0.0
    held_out: EvaluationResult | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "individual_id": self.individual_id,
            "generation": self.generation,
            "parent_id": self.parent_id,
            "genome": self.genome.to_dict(),
            "training_score": self.training_score,
            "held_out": None if self.held_out is None else {
                "artificiality": self.held_out.artificiality,
                "social_viability": self.held_out.social_viability,
                "observations": self.held_out.observations,
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Individual":
        held_out_data = data.get("held_out")
        held_out = None if held_out_data is None else EvaluationResult(**held_out_data)
        return cls(
            individual_id=str(data["individual_id"]),
            generation=int(data["generation"]),
            parent_id=data.get("parent_id"),
            genome=DevelopmentalGenome.from_dict(data["genome"]),
            training_score=float(data.get("training_score", 0.0)),
            held_out=held_out,
        )


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
            held_out = item.held_out
            f.write(json.dumps({
                "individual_id": item.individual_id,
                "generation": item.generation,
                "parent_id": item.parent_id,
                "genome": item.genome.to_dict(),
                "training_score": item.training_score,
                "held_out_artificiality": None if held_out is None else held_out.artificiality,
                "held_out_viability": None if held_out is None else held_out.social_viability,
            }, sort_keys=True) + "\n")


def _as_tuple(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(_as_tuple(v) for v in value)
    return value


def save_checkpoint(
    path: Path,
    *,
    seed: int,
    completed_generations: int,
    population: list[Individual],
    best: Individual | None,
    rng: random.Random,
    settings: dict[str, Any],
) -> None:
    """Atomically save enough state to resume the evolutionary search exactly."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "format_version": CHECKPOINT_FORMAT_VERSION,
        "seed": seed,
        "completed_generations": completed_generations,
        "population": [item.to_dict() for item in population],
        "best": None if best is None else best.to_dict(),
        "rng_state": rng.getstate(),
        "settings": settings,
    }
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    temp.replace(path)


def load_checkpoint(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if int(data.get("format_version", -1)) != CHECKPOINT_FORMAT_VERSION:
        raise ValueError(f"Unsupported checkpoint format: {data.get('format_version')}")
    return data


def evolve(
    seed: int = 7,
    generations: int = 25,
    population_size: int = 24,
    episodes: int = 200,
    elite_fraction: float = 0.25,
    mutation_rate: float = 0.25,
    mutation_scale: float = 0.12,
    output: Path | None = None,
    checkpoint: Path | None = None,
    checkpoint_every: int = 1,
    resume: Path | None = None,
) -> Individual:
    if generations < 1:
        raise ValueError("generations must be at least 1")
    if population_size < 2:
        raise ValueError("population_size must be at least 2")
    if checkpoint_every < 1:
        raise ValueError("checkpoint_every must be at least 1")

    settings = {
        "population_size": population_size,
        "episodes": episodes,
        "elite_fraction": elite_fraction,
        "mutation_rate": mutation_rate,
        "mutation_scale": mutation_scale,
    }

    if resume is not None:
        saved = load_checkpoint(resume)
        if int(saved["seed"]) != seed:
            raise ValueError("Resume seed does not match checkpoint seed")
        saved_settings = saved.get("settings", {})
        if saved_settings != settings:
            raise ValueError("Resume settings do not match checkpoint settings")
        rng = random.Random()
        rng.setstate(_as_tuple(saved["rng_state"]))
        completed_generations = int(saved["completed_generations"])
        population = [Individual.from_dict(item) for item in saved["population"]]
        best = None if saved.get("best") is None else Individual.from_dict(saved["best"])
    else:
        rng = random.Random(seed)
        founder = DevelopmentalGenome()
        population = [
            Individual(f"g0000-i{i:04d}", 0, None, founder.mutate(rng, rate=0.75, scale=0.18))
            for i in range(population_size)
        ]
        population[0].genome = founder
        completed_generations = 0
        best: Individual | None = None

    if completed_generations >= generations:
        if best is None:
            raise ValueError("Checkpoint contains no evaluated individual")
        return best

    for generation in range(completed_generations, generations):
        for i, individual in enumerate(population):
            eval_seed = seed * 1_000_003 + generation * 10_007 + i
            individual.training_score = train_score(individual.genome, eval_seed, episodes)
            individual.held_out = evaluate_held_out(individual.genome, eval_seed + 91_991)

        population.sort(key=lambda x: x.training_score, reverse=True)
        if best is None or population[0].training_score > best.training_score:
            best = Individual.from_dict(population[0].to_dict())
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
        completed_generations = generation + 1

        if checkpoint and (completed_generations % checkpoint_every == 0 or completed_generations == generations):
            save_checkpoint(
                checkpoint,
                seed=seed,
                completed_generations=completed_generations,
                population=population,
                best=best,
                rng=rng,
                settings=settings,
            )

    assert best is not None
    return best
