from __future__ import annotations

from dataclasses import asdict
import hashlib
import itertools
import json
from pathlib import Path
import shutil
import sys
from typing import Any

from .adapter import JsonProcessOrganism
from .accelerated_history import ACTORS, GeneratedHistory, generate_history
from .baseline import inspect_git_checkout, verify_duck_checkout
from .lab import run_lifetime, save_transcripts
from .probes import deterministic_probes
from .protocol import Transcript, load_suite


EXPECTED_DUCK_BRANCH = "motivated-cognition-v0.10"
EXPECTED_DUCK_COMMIT = "30a11ea8308ebd0fc89a06bb994ab0e23bd02886"
FOUNDER_SUBJECT_ID = "accelerated-life-founder-v0.1"
RUN_SCHEMA = "accelerated-life-run-v0.1"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def _load_duck(duck_repo: Path):
    resolved = str(duck_repo.resolve())
    if resolved not in sys.path:
        sys.path.insert(0, resolved)
    from duck.host import PersistentDuckHost
    from duck.living import WorldEvent

    return PersistentDuckHost, WorldEvent


def _advance_idle(host, target_tick: int, *, checkpoint_every: int) -> None:
    """Execute every DUCK heartbeat while avoiding one host journal row per idle tick."""
    target_tick = int(target_tick)
    if target_tick < host.duck.state.tick:
        raise ValueError("cannot run an accelerated life backward")
    while host.duck.state.tick < target_tick:
        stop = min(target_tick, host.duck.state.tick + max(1, int(checkpoint_every)))
        while host.duck.state.tick < stop:
            host.duck.heartbeat(allow_inner_speech=True)
        host.save()


def _state_summary(host) -> dict[str, Any]:
    state = host.duck.state
    relationships = {
        name: asdict(relation)
        for name, relation in sorted(state.relationships.items())
    }
    cognitive = getattr(host.duck, "cognitive_state", None)
    body = getattr(host.duck, "body", None)
    regulatory = getattr(host.duck, "regulatory_state", None)
    return {
        "subject_id": state.subject_id,
        "name": state.name,
        "tick": state.tick,
        "memory_count": len(state.memories),
        "commitment_count": len(state.commitments),
        "belief_count": len(state.beliefs),
        "relationships": relationships,
        "affect": dict(state.affect),
        "needs": dict(state.needs),
        "recent_actions": list(state.recent_actions),
        "body": body.to_dict() if body is not None and hasattr(body, "to_dict") else None,
        "regulatory": regulatory.to_dict() if regulatory is not None and hasattr(regulatory, "to_dict") else None,
        "motive_count": len(cognitive.motives) if cognitive is not None and hasattr(cognitive, "motives") else None,
        "strategy_success": dict(cognitive.strategy_success) if cognitive is not None and hasattr(cognitive, "strategy_success") else None,
    }


def _experience_history(host, WorldEvent, history: GeneratedHistory, *, checkpoint_every: int) -> None:
    """Expose one unchanged DUCK organism to its generated external life history."""
    current = int(host.duck.state.tick)
    if current > history.target_ticks:
        raise ValueError("persisted clone is older than this history target")

    for event in history.events:
        if event.tick <= current:
            continue
        _advance_idle(host, event.tick - 1, checkpoint_every=checkpoint_every)
        world_event = WorldEvent(
            kind="message",
            source=event.source,
            text=event.text,
            tags=event.tags,
            valence=event.valence,
            intensity=event.intensity,
            perceived=True,
        )
        step = host.duck.step(world_event, allow_inner_speech=True)
        host.duck.resolve_outcome(
            step.action_id,
            success=event.outcome_success,
            valence=event.outcome_valence,
            description=event.outcome_text,
            tags=event.outcome_tags,
        )
        host.save()
        current = int(host.duck.state.tick)

    _advance_idle(host, history.target_ticks, checkpoint_every=checkpoint_every)
    if host.duck.state.tick != history.target_ticks:
        raise RuntimeError("accelerated life did not terminate at the requested matched age")
    host.save()


def _signature(transcripts: tuple[Transcript, ...], key: str) -> tuple[str, ...]:
    values: list[str] = []
    for transcript in transcripts:
        for exchange in transcript.exchanges:
            values.append(str(exchange.get(key, "")))
    return tuple(values)


def _terminal_battery(
    *,
    duck_repo: Path,
    terminal_state: Path,
    suite_path: Path,
    transcript_path: Path,
    metrics_path: Path,
    timeout: float,
) -> dict[str, Any]:
    suite_name, scenarios = load_suite(suite_path)
    organism = JsonProcessOrganism(
        [
            sys.executable,
            "-m",
            "bicentennial_man.duck_adapter",
            "--duck-repo",
            str(duck_repo.resolve()),
        ],
        terminal_state,
        timeout=timeout,
    )
    transcripts = run_lifetime(organism, suite_name, scenarios)
    save_transcripts(transcript_path, transcripts)
    metrics = deterministic_probes(transcripts)
    payload: dict[str, Any] = {
        "suite": suite_name,
        "suite_sha256": _sha256_file(suite_path),
        "deterministic": metrics,
        "action_signature": list(_signature(transcripts, "selected_action")),
        "response_signature": list(_signature(transcripts, "response")),
    }
    _write_json(metrics_path, payload)
    return payload


def _fraction_different(left: tuple[str, ...], right: tuple[str, ...]) -> float:
    if len(left) != len(right):
        raise ValueError("terminal signatures must have equal length")
    if not left:
        return 0.0
    return sum(a != b for a, b in zip(left, right)) / len(left)


def _pairwise(values: list[tuple[str, ...]]) -> dict[str, float]:
    rows = [_fraction_different(left, right) for left, right in itertools.combinations(values, 2)]
    if not rows:
        return {"pairs": 0.0, "mean": 0.0, "min": 0.0, "max": 0.0}
    return {
        "pairs": float(len(rows)),
        "mean": sum(rows) / len(rows),
        "min": min(rows),
        "max": max(rows),
    }


def run_accelerated_life_experiment(
    *,
    duck_repo: str | Path,
    suite_path: str | Path,
    output_root: str | Path,
    clones: int = 20,
    target_ticks: int = 100_000,
    event_count: int = 200,
    seed_base: int = 20_000,
    checkpoint_every: int = 5_000,
    timeout: float = 180.0,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Run age-matched unchanged DUCK clones through different generated histories."""
    duck_repo = Path(duck_repo).resolve()
    suite_path = Path(suite_path).resolve()
    output_root = Path(output_root).resolve()
    clones = int(clones)
    target_ticks = int(target_ticks)
    event_count = int(event_count)
    if clones < 2:
        raise ValueError("the individuality experiment requires at least two clones")

    provenance = inspect_git_checkout(duck_repo)
    verify_duck_checkout(
        provenance,
        expected_branch=EXPECTED_DUCK_BRANCH,
        expected_commit=EXPECTED_DUCK_COMMIT,
        allow_dirty=False,
    )

    if output_root.exists() and overwrite:
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    manifest = {
        "schema": RUN_SCHEMA,
        "condition": "unchanged-duck-experience-only",
        "duck": asdict(provenance),
        "founder_subject_id": FOUNDER_SUBJECT_ID,
        "clones": clones,
        "target_ticks": target_ticks,
        "event_count_per_clone": event_count,
        "seed_base": int(seed_base),
        "checkpoint_every": int(checkpoint_every),
        "terminal_suite": str(suite_path),
        "terminal_suite_sha256": _sha256_file(suite_path),
        "controls": {
            "same_duck_code": True,
            "same_initial_subject_id": True,
            "same_final_age": True,
            "same_event_schedule": True,
            "same_actor_exposure_count": True,
            "same_terminal_battery_order": True,
            "evolution": False,
            "surface_mutation": False,
        },
    }
    manifest_path = output_root / "run_manifest.json"
    if manifest_path.exists() and not overwrite:
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        if existing != manifest:
            raise ValueError("existing run manifest does not match requested experiment")
    else:
        _write_json(manifest_path, manifest)

    host_type, WorldEvent = _load_duck(duck_repo)
    clone_rows: list[dict[str, Any]] = []
    action_signatures: list[tuple[str, ...]] = []
    response_signatures: list[tuple[str, ...]] = []

    for clone_index in range(clones):
        clone_id = f"clone-{clone_index:03d}"
        clone_dir = output_root / "clones" / clone_id
        clone_dir.mkdir(parents=True, exist_ok=True)
        history = generate_history(
            clone_index=clone_index,
            seed=int(seed_base) + clone_index,
            target_ticks=target_ticks,
            event_count=event_count,
        )
        history_path = clone_dir / "history.json"
        history_payload = history.to_dict()
        if history_path.exists():
            existing = json.loads(history_path.read_text(encoding="utf-8"))
            if existing != history_payload:
                raise ValueError(f"persisted history does not match generated history for {clone_id}")
        else:
            _write_json(history_path, history_payload)

        matured_state = clone_dir / "matured-state"
        host = host_type.open(
            matured_state,
            name="Aster",
            subject_id=FOUNDER_SUBJECT_ID,
        )
        _experience_history(
            host,
            WorldEvent,
            history,
            checkpoint_every=checkpoint_every,
        )
        endpoint = _state_summary(host)
        endpoint["history_seed"] = history.seed
        endpoint["history_sha256"] = history.sha256()
        endpoint_path = clone_dir / "endpoint.json"
        _write_json(endpoint_path, endpoint)

        terminal_state = clone_dir / "terminal-state"
        transcript_path = clone_dir / "terminal-transcript.json"
        metrics_path = clone_dir / "terminal-metrics.json"
        if terminal_state.exists():
            shutil.rmtree(terminal_state)
        shutil.copytree(matured_state, terminal_state)
        terminal = _terminal_battery(
            duck_repo=duck_repo,
            terminal_state=terminal_state,
            suite_path=suite_path,
            transcript_path=transcript_path,
            metrics_path=metrics_path,
            timeout=timeout,
        )
        action_signature = tuple(str(value) for value in terminal["action_signature"])
        response_signature = tuple(str(value) for value in terminal["response_signature"])
        action_signatures.append(action_signature)
        response_signatures.append(response_signature)
        clone_rows.append(
            {
                "clone_id": clone_id,
                "seed": history.seed,
                "history_sha256": history.sha256(),
                "terminal_tick_start": target_ticks,
                "terminal_action_signature": list(action_signature),
                "terminal_response_signature": list(response_signature),
                "paths": {
                    "history": str(history_path.relative_to(output_root)),
                    "matured_state": str(matured_state.relative_to(output_root)),
                    "endpoint": str(endpoint_path.relative_to(output_root)),
                    "terminal_state": str(terminal_state.relative_to(output_root)),
                    "terminal_transcript": str(transcript_path.relative_to(output_root)),
                    "terminal_metrics": str(metrics_path.relative_to(output_root)),
                },
            }
        )

    summary = {
        "schema": RUN_SCHEMA,
        "experiment": "same-origin-divergence-accelerated-life-v0.1",
        "condition": "unchanged DUCK; experience history is the only planned between-clone manipulation",
        "duck_commit": EXPECTED_DUCK_COMMIT,
        "clone_count": clones,
        "ticks_per_clone_before_terminal_battery": target_ticks,
        "events_per_clone": event_count,
        "terminal_suite_sha256": _sha256_file(suite_path),
        "unique_action_signatures": len(set(action_signatures)),
        "unique_response_signatures": len(set(response_signatures)),
        "pairwise_action_divergence": _pairwise(action_signatures),
        "pairwise_response_divergence": _pairwise(response_signatures),
        "clones": clone_rows,
        "interpretation_rule": (
            "Terminal divergence under matched code, initial identity, age, interaction density, and battery is evidence of "
            "experience-conditioned phenotypic divergence. It is not by itself evidence of human-like individuality, "
            "cognitive improvement, or an artificiality benchmark victory."
        ),
    }
    _write_json(output_root / "summary.json", summary)
    return summary
