from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class SocialTurn:
    speaker: str
    text: str
    ticks_before: int = 0
    ticks_after: int = 0


@dataclass(frozen=True, slots=True)
class Scenario:
    name: str
    turns: tuple[SocialTurn, ...]
    purpose: str = ""


@dataclass(frozen=True, slots=True)
class TurnResult:
    response_text: str
    selected_action: str = ""
    action_id: str = ""
    tick: int = 0
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class Transcript:
    suite_name: str
    scenario_name: str
    purpose: str
    exchanges: tuple[dict[str, Any], ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_suite(path: str | Path) -> tuple[str, tuple[Scenario, ...]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    name = str(payload.get("name", Path(path).stem))
    scenarios: list[Scenario] = []
    for row in payload["scenarios"]:
        turns = tuple(
            SocialTurn(
                speaker=str(turn.get("speaker", "user")),
                text=str(turn["text"]),
                ticks_before=int(turn.get("ticks_before", 0)),
                ticks_after=int(turn.get("ticks_after", 0)),
            )
            for turn in row["turns"]
        )
        scenarios.append(
            Scenario(
                name=str(row["name"]),
                purpose=str(row.get("purpose", "")),
                turns=turns,
            )
        )
    return name, tuple(scenarios)
