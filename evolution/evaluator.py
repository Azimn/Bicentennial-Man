from __future__ import annotations

import os
from pathlib import Path
import sys
import tempfile

from bicentennial_man.adapter import JsonProcessOrganism
from bicentennial_man.judge import OpenAICompatiblePhenotypeJudge
from bicentennial_man.lab import run_lifetime
from bicentennial_man.protocol import load_suite


def evaluate(program_path: str) -> dict[str, float]:
    """OpenEvolve evaluator contract: candidate path in, phenotype metrics out."""
    suite_path = Path(os.environ.get("BICENTENNIAL_TRAINING_SUITE", "configs/suites/training.json"))
    judge_model = os.environ.get("BICENTENNIAL_JUDGE_MODEL", "qwen3:8b")
    judge_api_base = os.environ.get("BICENTENNIAL_JUDGE_API_BASE", "http://localhost:11434/v1")
    timeout = float(os.environ.get("BICENTENNIAL_EVAL_TIMEOUT", "300"))

    suite_name, scenarios = load_suite(suite_path)
    with tempfile.TemporaryDirectory(prefix="bicentennial_candidate_") as tmp:
        organism = JsonProcessOrganism(
            [sys.executable, str(Path(program_path).resolve())],
            Path(tmp) / "state",
            timeout=timeout,
            env=os.environ.copy(),
        )
        transcripts = run_lifetime(organism, suite_name, scenarios)
        judge = OpenAICompatiblePhenotypeJudge(
            judge_model,
            api_base=judge_api_base,
            timeout=timeout,
        )
        return judge.evaluate(transcripts)
