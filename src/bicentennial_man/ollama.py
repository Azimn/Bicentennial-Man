from __future__ import annotations

import json
from urllib import request


class OllamaRenderer:
    """Optional language surface. Never supplies fitness or hidden evaluator information."""

    def __init__(self, model: str, host: str = "http://127.0.0.1:11434"):
        self.model = model
        self.host = host.rstrip("/")

    def render(self, situation: dict, action: dict) -> str:
        prompt = (
            "Render one short, natural utterance for an artificial social subject. "
            "Do not add memories, feelings, motives, facts, or commitments not present in the structured state. "
            f"Situation: {json.dumps(situation, sort_keys=True)}\n"
            f"Action constraints: {json.dumps(action, sort_keys=True)}\n"
            "Return only the utterance."
        )
        payload = json.dumps({"model": self.model, "prompt": prompt, "stream": False}).encode("utf-8")
        req = request.Request(f"{self.host}/api/generate", data=payload, headers={"Content-Type": "application/json"})
        with request.urlopen(req, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
        return str(data["response"]).strip()
