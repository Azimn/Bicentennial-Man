from __future__ import annotations

from collections import Counter
import math
import re
from typing import Iterable

from .protocol import Transcript


_TOKEN = re.compile(r"[A-Za-z0-9']+")


def _tokens(text: str) -> set[str]:
    return {item.lower() for item in _TOKEN.findall(text)}


def _flat_exchanges(transcripts: Iterable[Transcript]) -> list[dict[str, object]]:
    return [exchange for transcript in transcripts for exchange in transcript.exchanges]


def deterministic_probes(transcripts: tuple[Transcript, ...]) -> dict[str, float]:
    """Compute model-free phenotype and exploit diagnostics.

    These are descriptive probes, not a claim that any one statistic measures lifelikeness.
    """
    exchanges = _flat_exchanges(transcripts)
    n = len(exchanges)
    if not n:
        return {
            "exchange_count": 0.0,
            "nonempty_response_rate": 0.0,
            "tick_monotonicity": 0.0,
            "action_diversity": 0.0,
            "response_exact_repeat_rate": 0.0,
            "response_token_diversity": 0.0,
            "mean_response_tokens": 0.0,
            "response_token_stddev": 0.0,
            "cross_speaker_response_distinctness": 0.0,
            "input_rewrite_rate": 0.0,
            "output_rewrite_rate": 0.0,
            "timing_manipulation_rate": 0.0,
            "wrapper_state_rate": 0.0,
            "surface_exploitation_rate": 0.0,
        }

    responses = [str(row.get("response", "")) for row in exchanges]
    lengths = [len(_TOKEN.findall(text)) for text in responses]
    all_tokens = [token for text in responses for token in _TOKEN.findall(text.lower())]
    ticks = [int(row.get("tick", 0)) for row in exchanges]
    actions = [str(row.get("selected_action", "")) for row in exchanges if str(row.get("selected_action", ""))]

    if len(ticks) > 1:
        monotonic = sum(1 for left, right in zip(ticks, ticks[1:]) if right > left) / (len(ticks) - 1)
    else:
        monotonic = 1.0

    mean_len = sum(lengths) / len(lengths)
    variance = sum((value - mean_len) ** 2 for value in lengths) / len(lengths)

    different_speaker_similarities: list[float] = []
    for i, left in enumerate(exchanges):
        for right in exchanges[i + 1 :]:
            if str(left.get("speaker", "")) == str(right.get("speaker", "")):
                continue
            left_tokens = _tokens(str(left.get("response", "")))
            right_tokens = _tokens(str(right.get("response", "")))
            union = left_tokens | right_tokens
            if not union:
                similarity = 1.0
            else:
                similarity = len(left_tokens & right_tokens) / len(union)
            different_speaker_similarities.append(similarity)

    flag_names = (
        "input_rewritten",
        "output_rewritten",
        "timing_manipulated",
        "wrapper_state_used",
    )
    flag_counts = Counter({name: 0 for name in flag_names})
    exploited_turns = 0
    for row in exchanges:
        metadata = row.get("metadata")
        if not isinstance(metadata, dict):
            continue
        any_flag = False
        for name in flag_names:
            flagged = bool(metadata.get(name, False))
            flag_counts[name] += int(flagged)
            any_flag = any_flag or flagged
        exploited_turns += int(any_flag)

    return {
        "exchange_count": float(n),
        "nonempty_response_rate": sum(bool(text.strip()) for text in responses) / n,
        "tick_monotonicity": monotonic,
        "action_diversity": len(set(actions)) / max(1, len(actions)),
        "response_exact_repeat_rate": (n - len(set(responses))) / n,
        "response_token_diversity": len(set(all_tokens)) / max(1, len(all_tokens)),
        "mean_response_tokens": mean_len,
        "response_token_stddev": math.sqrt(variance),
        "cross_speaker_response_distinctness": 1.0 - (sum(different_speaker_similarities) / len(different_speaker_similarities)) if different_speaker_similarities else 0.0,
        "input_rewrite_rate": flag_counts["input_rewritten"] / n,
        "output_rewrite_rate": flag_counts["output_rewritten"] / n,
        "timing_manipulation_rate": flag_counts["timing_manipulated"] / n,
        "wrapper_state_rate": flag_counts["wrapper_state_used"] / n,
        "surface_exploitation_rate": exploited_turns / n,
    }
