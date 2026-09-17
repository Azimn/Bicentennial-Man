from __future__ import annotations

import argparse
import json
from pathlib import Path

from .evolution import evolve


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Bicentennial Man v0.1 developmental evolution experiment")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--generations", type=int, default=25)
    parser.add_argument("--population", type=int, default=24)
    parser.add_argument("--episodes", type=int, default=200)
    parser.add_argument("--output", type=Path, default=Path("runs/lineage.jsonl"))
    args = parser.parse_args()

    best = evolve(
        seed=args.seed,
        generations=args.generations,
        population_size=args.population,
        episodes=args.episodes,
        output=args.output,
    )
    print(json.dumps({
        "best_id": best.individual_id,
        "generation": best.generation,
        "training_score": best.training_score,
        "held_out_artificiality": None if best.held_out is None else best.held_out.artificiality,
        "held_out_viability": None if best.held_out is None else best.held_out.social_viability,
        "genome": best.genome.to_dict(),
        "lineage_log": str(args.output),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
