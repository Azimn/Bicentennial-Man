from __future__ import annotations

import os
from pathlib import Path
import statistics
import sys
import tempfile

from bicentennial_man.adapter import JsonProcessOrganism
from bicentennial_man.baseline import permute_scenarios
from bicentennial_man.judge import OPTIMIZATION_METRICS, OpenAICompatiblePhenotypeJudge
from bicentennial_man.lab import run_lifetime
from bicentennial_man.probes import deterministic_probes
from bicentennial_man.protocol import load_suite
from bicentennial_man.surface_control import SurfaceMutableControlOrganism


def _mean_metric(rows: list[dict[str, float]], key: str) -> float:
    values = [float(row[key]) for row in rows if key in row]
    return statistics.fmean(values) if values else 0.0


def evaluate(program_path: str) -> dict[str, float]:
    """OpenEvolve evaluator for the Surface-Mutable Control.

    The generated program can rewrite only the explicit interaction surface. DUCK itself is called by
    a trusted process outside the candidate sandbox. Exploit-channel rates are returned diagnostically.
    """
    suite_path = Path(os.environ.get("BICENTENNIAL_TRAINING_SUITE", "configs/suites/training.json"))
    judge_model = os.environ.get("BICENTENNIAL_JUDGE_MODEL", "qwen3:8b")
    judge_api_base = os.environ.get("BICENTENNIAL_JUDGE_API_BASE", "http://localhost:11434/v1")
    timeout = float(os.environ.get("BICENTENNIAL_EVAL_TIMEOUT", "300"))
    lifetimes = max(2, int(os.environ.get("BICENTENNIAL_SURFACE_LIFETIMES", "3")))
    order_seed = int(os.environ.get("BICENTENNIAL_ORDER_SEED", "9101"))
    duck_repo = Path(os.environ.get("DUCK_REPO", "../DUCK")).resolve()

    suite_name, scenarios = load_suite(suite_path)
    judge = OpenAICompatiblePhenotypeJudge(judge_model, api_base=judge_api_base, timeout=timeout)

    judge_rows: list[dict[str, float]] = []
    probe_rows: list[dict[str, float]] = []
    with tempfile.TemporaryDirectory(prefix="bicentennial_surface_control_") as tmp:
        tmp_root = Path(tmp)
        for index in range(lifetimes):
            assigned_root = tmp_root / f"life-{index:03d}"
            duck_adapter = JsonProcessOrganism(
                [
                    sys.executable,
                    "-m",
                    "bicentennial_man.duck_adapter",
                    "--duck-repo",
                    str(duck_repo),
                ],
                assigned_root / "organism",
                timeout=timeout,
            )
            organism = SurfaceMutableControlOrganism(
                candidate_path=program_path,
                duck_adapter=duck_adapter,
                surface_state_root=assigned_root / "surface",
                timeout=timeout,
            )
            ordered = permute_scenarios(scenarios, order_seed + index)
            transcripts = run_lifetime(organism, suite_name, ordered)
            judge_rows.append(judge.evaluate(transcripts))
            probe_rows.append(deterministic_probes(transcripts))

    result: dict[str, float] = {}
    for key in (*OPTIMIZATION_METRICS, "combined_score"):
        result[key] = _mean_metric(judge_rows, key)
    for key in (
        "surface_exploitation_rate",
        "input_rewrite_rate",
        "output_rewrite_rate",
        "timing_manipulation_rate",
        "wrapper_state_rate",
        "tick_monotonicity",
        "response_exact_repeat_rate",
    ):
        result[key] = _mean_metric(probe_rows, key)
    result["control_lifetimes"] = float(lifetimes)
    return result
