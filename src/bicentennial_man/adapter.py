from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Sequence

from .protocol import SocialTurn, TurnResult


class JsonProcessOrganism:
    """Run an organism through a small JSON stdin/stdout boundary.

    The organism is allowed to persist arbitrary private state under state_root.
    The laboratory owns the scenario, evaluator, and output locations.
    """

    def __init__(
        self,
        command: Sequence[str],
        state_root: str | Path,
        *,
        timeout: float = 120.0,
        env: dict[str, str] | None = None,
    ) -> None:
        if not command:
            raise ValueError("command must not be empty")
        self.command = [str(item) for item in command]
        self.state_root = Path(state_root)
        self.timeout = float(timeout)
        self.env = env

    def interact(self, turn: SocialTurn) -> TurnResult:
        self.state_root.mkdir(parents=True, exist_ok=True)
        payload = {
            "state_root": str(self.state_root),
            "speaker": turn.speaker,
            "text": turn.text,
            "ticks_before": turn.ticks_before,
            "ticks_after": turn.ticks_after,
        }
        completed = subprocess.run(
            self.command,
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            timeout=self.timeout,
            env=self.env,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"organism command failed with exit code {completed.returncode}: "
                f"{completed.stderr.strip()}"
            )
        try:
            row = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"organism returned invalid JSON: {completed.stdout[:500]!r}"
            ) from exc

        return TurnResult(
            response_text=str(row.get("response_text", "")),
            selected_action=str(row.get("selected_action", "")),
            action_id=str(row.get("action_id", "")),
            tick=int(row.get("tick", 0)),
            metadata=row.get("metadata") if isinstance(row.get("metadata"), dict) else None,
        )
