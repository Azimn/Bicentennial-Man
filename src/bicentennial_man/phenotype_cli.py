from __future__ import annotations

import argparse
import json
from pathlib import Path
import shlex
import sys

from .adapter import JsonProcessOrganism
from .judge import OpenAICompatiblePhenotypeJudge
from .lab import run_lifetime, save_transcripts
from .protocol import load_suite


def _command(args) -> list[str]:
    if args.duck_repo is not None:
        command = [
            sys.executable,
            "-m",
            "bicentennial_man.duck_adapter",
            "--duck-repo",
            str(args.duck_repo),
        ]
        if args.duck_llm:
            command.append("--llm")
        return command
    if not args.adapter_command:
        raise SystemExit("provide --duck-repo or --adapter-command")
    return shlex.split(args.adapter_command)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a persistent organism through the Bicentennial phenotype lab")
    parser.add_argument("--suite", type=Path, default=Path("configs/suites/training.json"))
    parser.add_argument("--state-root", type=Path, default=Path("runs/organism_state"))
    parser.add_argument("--transcript-out", type=Path, default=Path("runs/phenotype_transcript.json"))
    parser.add_argument("--duck-repo", type=Path)
    parser.add_argument("--duck-llm", action="store_true")
    parser.add_argument("--adapter-command")
    parser.add_argument("--judge-model")
    parser.add_argument("--judge-api-base", default="http://localhost:11434/v1")
    parser.add_argument("--timeout", type=float, default=180.0)
    args = parser.parse_args(argv)

    suite_name, scenarios = load_suite(args.suite)
    organism = JsonProcessOrganism(
        _command(args),
        args.state_root,
        timeout=args.timeout,
    )
    transcripts = run_lifetime(organism, suite_name, scenarios)
    save_transcripts(args.transcript_out, transcripts)

    report: dict[str, object] = {
        "suite": suite_name,
        "scenarios": len(transcripts),
        "transcript": str(args.transcript_out),
    }
    if args.judge_model:
        judge = OpenAICompatiblePhenotypeJudge(
            args.judge_model,
            api_base=args.judge_api_base,
            timeout=args.timeout,
        )
        report["metrics"] = judge.evaluate(transcripts)

    print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
