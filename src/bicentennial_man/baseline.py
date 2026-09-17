from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import random
import shutil
import statistics
import subprocess
from typing import Callable, Iterable, Protocol

from .adapter import JsonProcessOrganism
from .lab import run_lifetime, save_transcripts
from .probes import deterministic_probes
from .protocol import Scenario, Transcript


class JudgeLike(Protocol):
    model: str

    def evaluate(self, transcripts: tuple[Transcript, ...]) -> dict[str, float]: ...


@dataclass(frozen=True, slots=True)
class GitProvenance:
    commit: str
    branch: str
    dirty: bool


@dataclass(frozen=True, slots=True)
class JudgeSpec:
    label: str
    model: str
    api_base: str = "http://localhost:11434/v1"


def inspect_git_checkout(repo: str | Path) -> GitProvenance:
    root = Path(repo)

    def run(*args: str) -> str:
        completed = subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout.strip()

    commit = run("rev-parse", "HEAD")
    branch = run("branch", "--show-current") or "DETACHED"
    dirty = bool(run("status", "--porcelain"))
    return GitProvenance(commit=commit, branch=branch, dirty=dirty)


def verify_duck_checkout(
    provenance: GitProvenance,
    *,
    expected_branch: str = "motivated-cognition-v0.10",
    expected_commit: str | None = None,
    allow_dirty: bool = False,
) -> None:
    if provenance.dirty and not allow_dirty:
        raise ValueError("DUCK checkout is dirty; founder characterization requires an unaltered checkout")
    if provenance.branch not in {expected_branch, "DETACHED"}:
        raise ValueError(
            f"DUCK branch is {provenance.branch!r}; expected {expected_branch!r} or a detached checkout"
        )
    if expected_commit and provenance.commit != expected_commit:
        raise ValueError(
            f"DUCK commit is {provenance.commit}; expected pinned commit {expected_commit}"
        )


def permute_scenarios(scenarios: tuple[Scenario, ...], seed: int) -> tuple[Scenario, ...]:
    rows = list(scenarios)
    random.Random(int(seed)).shuffle(rows)
    return tuple(rows)


def _aggregate(rows: list[dict[str, float]]) -> dict[str, dict[str, float]]:
    keys = sorted({key for row in rows for key in row})
    result: dict[str, dict[str, float]] = {}
    for key in keys:
        values = [float(row[key]) for row in rows if key in row]
        if not values:
            continue
        result[key] = {
            "mean": statistics.fmean(values),
            "stddev": statistics.pstdev(values),
            "min": min(values),
            "max": max(values),
            "range": max(values) - min(values),
        }
    return result


def _flatten_metrics(deterministic: dict[str, float], judges: dict[str, dict[str, float]]) -> dict[str, float]:
    flat = {f"deterministic.{key}": float(value) for key, value in deterministic.items()}
    for label, metrics in judges.items():
        for key, value in metrics.items():
            flat[f"judge.{label}.{key}"] = float(value)
    return flat


def run_founder_characterization(
    *,
    adapter_factory: Callable[[Path], JsonProcessOrganism],
    suite_name: str,
    scenarios: tuple[Scenario, ...],
    output_root: str | Path,
    lifetimes: int = 8,
    order_seed: int = 7001,
    judges: Iterable[JudgeLike] = (),
    provenance: dict[str, object] | None = None,
    overwrite: bool = False,
) -> dict[str, object]:
    if lifetimes < 2:
        raise ValueError("founder characterization requires at least two fresh lifetimes")
    root = Path(output_root)
    if root.exists():
        if not overwrite:
            raise FileExistsError(f"output already exists: {root}")
        shutil.rmtree(root)
    root.mkdir(parents=True)

    judge_list = list(judges)
    lifetime_rows: list[dict[str, object]] = []
    flat_metrics: list[dict[str, float]] = []

    for index in range(lifetimes):
        seed = int(order_seed) + index
        ordered = permute_scenarios(scenarios, seed)
        life_dir = root / "lifetimes" / f"life-{index:03d}-order-{seed}"
        state_root = life_dir / "state"
        organism = adapter_factory(state_root)
        transcripts = run_lifetime(organism, suite_name, ordered)
        transcript_path = life_dir / "transcript.json"
        save_transcripts(transcript_path, transcripts)

        deterministic = deterministic_probes(transcripts)
        judge_metrics: dict[str, dict[str, float]] = {}
        for judge in judge_list:
            label = getattr(judge, "label", None) or getattr(judge, "model", "judge")
            judge_metrics[str(label)] = judge.evaluate(transcripts)

        metrics_path = life_dir / "metrics.json"
        metrics_payload = {
            "deterministic": deterministic,
            "judges": judge_metrics,
        }
        metrics_path.write_text(json.dumps(metrics_payload, indent=2, sort_keys=True), encoding="utf-8")
        flat = _flatten_metrics(deterministic, judge_metrics)
        flat_metrics.append(flat)
        lifetime_rows.append(
            {
                "index": index,
                "order_seed": seed,
                "scenario_order": [scenario.name for scenario in ordered],
                "transcript": str(transcript_path.relative_to(root)),
                "metrics": str(metrics_path.relative_to(root)),
                "flat_metrics": flat,
            }
        )

    aggregate = _aggregate(flat_metrics)
    report: dict[str, object] = {
        "experiment": "duck-founder-phenotype-characterization",
        "suite": suite_name,
        "lifetimes": lifetimes,
        "order_seed_start": order_seed,
        "provenance": provenance or {},
        "runs": lifetime_rows,
        "aggregate": aggregate,
        "order_history_effects": {
            key: {"stddev": value["stddev"], "range": value["range"]}
            for key, value in aggregate.items()
        },
        "interpretation_rule": "Characterization only. A higher training score is not evidence of cognitive improvement.",
    }
    (root / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    return report
