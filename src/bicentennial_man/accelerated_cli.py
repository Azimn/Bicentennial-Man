from __future__ import annotations

import argparse
import json
from pathlib import Path

from .accelerated import run_accelerated_life_experiment


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run unchanged MicroPsiDUCK v0.10 clones through age-matched generated life histories"
    )
    parser.add_argument("--duck-repo", type=Path, required=True)
    parser.add_argument("--suite", type=Path, default=Path("configs/suites/training.json"))
    parser.add_argument("--out", type=Path, default=Path("runs/accelerated-life-v0.1"))
    parser.add_argument("--clones", type=int, default=20)
    parser.add_argument("--ticks", type=int, default=100_000)
    parser.add_argument("--events", type=int, default=200)
    parser.add_argument("--seed-base", type=int, default=20_000)
    parser.add_argument("--checkpoint-every", type=int, default=5_000)
    parser.add_argument("--identical-history-replicates", type=int, default=3)
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)

    summary = run_accelerated_life_experiment(
        duck_repo=args.duck_repo,
        suite_path=args.suite,
        output_root=args.out,
        clones=args.clones,
        target_ticks=args.ticks,
        event_count=args.events,
        seed_base=args.seed_base,
        checkpoint_every=args.checkpoint_every,
        identical_history_replicates=args.identical_history_replicates,
        timeout=args.timeout,
        overwrite=args.overwrite,
    )
    print(json.dumps({
        "experiment": summary["experiment"],
        "clone_count": summary["clone_count"],
        "control_clone_count": summary["control_clone_count"],
        "ticks_per_clone_before_terminal_battery": summary["ticks_per_clone_before_terminal_battery"],
        "unique_action_signatures": summary["unique_action_signatures"],
        "unique_response_signatures": summary["unique_response_signatures"],
        "pairwise_action_divergence": summary["pairwise_action_divergence"],
        "pairwise_response_divergence": summary["pairwise_response_divergence"],
        "identical_history_control_passed": summary["identical_history_control"]["passed"],
        "summary": str(args.out / "summary.json"),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
