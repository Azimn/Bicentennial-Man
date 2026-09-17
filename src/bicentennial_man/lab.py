from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .adapter import JsonProcessOrganism
from .protocol import Scenario, Transcript


def run_lifetime(
    adapter: JsonProcessOrganism,
    suite_name: str,
    scenarios: Iterable[Scenario],
) -> tuple[Transcript, ...]:
    """Run scenarios against one persistent organism state.

    Scenarios do not reset the organism. This is intentional because the primary
    phenotype includes carryover, relationship change, unresolved concerns, and
    consequences that survive beyond a single dialogue turn.
    """
    transcripts: list[Transcript] = []
    for scenario in scenarios:
        exchanges: list[dict[str, object]] = []
        for turn in scenario.turns:
            result = adapter.interact(turn)
            exchanges.append(
                {
                    "speaker": turn.speaker,
                    "input": turn.text,
                    "ticks_before": turn.ticks_before,
                    "ticks_after": turn.ticks_after,
                    "response": result.response_text,
                    "selected_action": result.selected_action,
                    "action_id": result.action_id,
                    "tick": result.tick,
                    "metadata": result.metadata or {},
                }
            )
        transcripts.append(
            Transcript(
                suite_name=suite_name,
                scenario_name=scenario.name,
                purpose=scenario.purpose,
                exchanges=tuple(exchanges),
            )
        )
    return tuple(transcripts)


def save_transcripts(path: str | Path, transcripts: Iterable[Transcript]) -> None:
    import json

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps([item.to_dict() for item in transcripts], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
