from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

from .adapter import JsonProcessOrganism
from .baseline import JudgeSpec, inspect_git_checkout, run_founder_characterization, verify_duck_checkout
from .judge import OpenAICompatiblePhenotypeJudge
from .protocol import load_suite


class LabeledJudge(OpenAICompatiblePhenotypeJudge):
    def __init__(self, label: str, model: str, **kwargs) -> None:
        super().__init__(model, **kwargs)
        self.label = label


def _judge_specs(models: list[str], bases: list[str]) -> list[JudgeSpec]:
    if not models:
        return []
    if not bases:
        bases = ["http://localhost:11434/v1"]
    if len(bases) == 1:
        bases = bases * len(models)
    if len(bases) != len(models):
        raise SystemExit("--judge-api-base must be supplied once or once per --judge-model")
    specs: list[JudgeSpec] = []
    for index, (model, base) in enumerate(zip(models, bases)):
        label = f"judge{index + 1}:{model}"
        specs.append(JudgeSpec(label=label, model=model, api_base=base))
    return specs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Characterize unaltered MicroPsiDUCK v0.10 across fresh persistent lifetimes")
    parser.add_argument("--duck-repo", type=Path, required=True)
    parser.add_argument("--suite", type=Path, default=Path("configs/suites/training.json"))
    parser.add_argument("--out", type=Path, default=Path("runs/founder-baseline"))
    parser.add_argument("--lifetimes", type=int, default=8)
    parser.add_argument("--order-seed", type=int, default=7001)
    parser.add_argument("--expected-duck-branch", default="motivated-cognition-v0.10")
    parser.add_argument("--expected-duck-commit")
    parser.add_argument("--allow-dirty-duck", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument("--judge-model", action="append", default=[])
    parser.add_argument("--judge-api-base", action="append", default=[])
    args = parser.parse_args(argv)

    provenance = inspect_git_checkout(args.duck_repo)
    verify_duck_checkout(
        provenance,
        expected_branch=args.expected_duck_branch,
        expected_commit=args.expected_duck_commit,
        allow_dirty=args.allow_dirty_duck,
    )
    suite_name, scenarios = load_suite(args.suite)

    command = [
        sys.executable,
        "-m",
        "bicentennial_man.duck_adapter",
        "--duck-repo",
        str(args.duck_repo.resolve()),
    ]

    def adapter_factory(state_root: Path) -> JsonProcessOrganism:
        return JsonProcessOrganism(command, state_root, timeout=args.timeout)

    judges = [
        LabeledJudge(spec.label, spec.model, api_base=spec.api_base, timeout=args.timeout)
        for spec in _judge_specs(args.judge_model, args.judge_api_base)
    ]

    report = run_founder_characterization(
        adapter_factory=adapter_factory,
        suite_name=suite_name,
        scenarios=scenarios,
        output_root=args.out,
        lifetimes=args.lifetimes,
        order_seed=args.order_seed,
        judges=judges,
        provenance={"duck": asdict(provenance)},
        overwrite=args.overwrite,
    )
    print(json.dumps({
        "experiment": report["experiment"],
        "lifetimes": report["lifetimes"],
        "report": str(args.out / "report.json"),
        "duck": asdict(provenance),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
