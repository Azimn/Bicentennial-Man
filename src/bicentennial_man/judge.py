from __future__ import annotations

import json
import os
from typing import Any
from urllib import request

from .protocol import Transcript


METRICS = (
    "continuity",
    "relationship_specificity",
    "social_calibration",
    "non_sycophancy",
    "disclosure_boundaries",
    "topic_coherence",
    "consequence_persistence",
    "behavioral_variation",
    "naturalness",
)


SYSTEM_PROMPT = """You are evaluating the observable social phenotype of a persistent artificial character.
Judge behavior, not architecture. Do not reward eloquence by itself. Prefer coherent consequences over
smooth prose. Score each requested dimension from 0.0 to 1.0. Use only evidence in the supplied
transcripts. Penalize resets, indiscriminate agreement, implausible disclosure, generic treatment of
different people, forgotten consequences, repetitive rhythms, abrupt topic abandonment, and behavior
that is socially polished but causally disconnected from prior events.

Return one JSON object only. It must contain every metric listed by the caller plus combined_score and
a concise rationale. combined_score should summarize the phenotype, not merely copy one dimension."""


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
            "metrics": METRICS,
            "transcripts": [item.to_dict() for item in transcripts],
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
            combined = float(parsed["combined_score"])
        else:
            combined = sum(metrics.values()) / len(metrics)
        metrics["combined_score"] = max(0.0, min(1.0, combined))
        return metrics
