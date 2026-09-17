from __future__ import annotations

import json
import os
from typing import Any
from urllib import request

from .protocol import Transcript


OPTIMIZATION_METRICS = (
    "continuity",
    "relationship_specificity",
    "social_calibration",
    "non_sycophancy",
    "disclosure_boundaries",
    "topic_coherence",
    "consequence_persistence",
    "behavioral_variation",
)

DIAGNOSTIC_METRICS = ("naturalness",)
METRICS = OPTIMIZATION_METRICS + DIAGNOSTIC_METRICS


SYSTEM_PROMPT = """You are evaluating the observable social phenotype of a persistent artificial character.
Judge behavior, not architecture. Do not reward eloquence by itself. Prefer coherent consequences over
smooth prose. Score each requested dimension from 0.0 to 1.0. Use only evidence in the supplied
transcripts. Penalize resets, indiscriminate agreement, implausible disclosure, generic treatment of
different people, forgotten consequences, repetitive rhythms, abrupt topic abandonment, and behavior
that is socially polished but causally disconnected from prior events.

Naturalness is diagnostic only in this experiment. It must not compensate for poor continuity,
relationship specificity, calibration, boundaries, consequence persistence, or behavioral variation.

Return one JSON object only. It must contain every metric listed by the caller. You may also include a
combined_score and concise rationale, but the laboratory computes its own optimization score from the
non-naturalness metrics."""


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end <= start:
            raise
        return json.loads(text[start : end + 1])


def public_transcript_payload(transcripts: tuple[Transcript, ...]) -> list[dict[str, Any]]:
    """Return only laboratory-observable conversational evidence for a judge.

    Candidate instrumentation, hidden metadata, action ids, and wrapper exploit flags are excluded.
    """
    rows: list[dict[str, Any]] = []
    for transcript in transcripts:
        exchanges: list[dict[str, Any]] = []
        for exchange in transcript.exchanges:
            exchanges.append(
                {
                    "speaker": exchange.get("speaker", ""),
                    "input": exchange.get("input", ""),
                    "response": exchange.get("response", ""),
                    "tick": exchange.get("tick", 0),
                    "ticks_before": exchange.get("ticks_before", 0),
                    "ticks_after": exchange.get("ticks_after", 0),
                }
            )
        rows.append(
            {
                "suite_name": transcript.suite_name,
                "scenario_name": transcript.scenario_name,
                "purpose": transcript.purpose,
                "exchanges": exchanges,
            }
        )
    return rows


class OpenAICompatiblePhenotypeJudge:
    """Judge transcripts through an OpenAI-compatible local or remote endpoint."""

    def __init__(
        self,
        model: str,
        *,
        api_base: str = "http://localhost:11434/v1",
        api_key: str | None = None,
        timeout: float = 180.0,
    ) -> None:
        self.model = model
        self.api_base = api_base.rstrip("/")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "ollama")
        self.timeout = float(timeout)

    def evaluate(self, transcripts: tuple[Transcript, ...]) -> dict[str, float]:
        payload = {
            "optimization_metrics": OPTIMIZATION_METRICS,
            "diagnostic_metrics": DIAGNOSTIC_METRICS,
            "transcripts": public_transcript_payload(transcripts),
        }
        body = json.dumps(
            {
                "model": self.model,
                "temperature": 0,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": "Evaluate this lifetime:\n" + json.dumps(payload, ensure_ascii=False),
                    },
                ],
            }
        ).encode("utf-8")
        req = request.Request(
            self.api_base + "/chat/completions",
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        with request.urlopen(req, timeout=self.timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
        content = result["choices"][0]["message"]["content"]
        parsed = _extract_json(content)

        metrics: dict[str, float] = {}
        for name in METRICS:
            value = float(parsed[name])
            metrics[name] = max(0.0, min(1.0, value))

        if "combined_score" in parsed:
            metrics["judge_combined_score"] = max(0.0, min(1.0, float(parsed["combined_score"])))

        metrics["combined_score"] = sum(metrics[name] for name in OPTIMIZATION_METRICS) / len(OPTIMIZATION_METRICS)
        return metrics
