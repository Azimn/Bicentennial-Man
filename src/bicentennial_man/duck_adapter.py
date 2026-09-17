from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys


def _load_duck(repo: Path):
    sys.path.insert(0, str(repo.resolve()))
    from duck.host import PersistentDuckHost

    return PersistentDuckHost


def _llm_components():
    from duck.language import ModelExpression, ModelInnerVoice, OpenAICompatiblePort
    from duck.semantics import ModelEventInterpreter

    port = OpenAICompatiblePort.from_env()
    return ModelInnerVoice(port), ModelExpression(port), ModelEventInterpreter(port)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Bicentennial Man adapter for MicroPsiDUCK v0.10")
    parser.add_argument(
        "--duck-repo",
        type=Path,
        default=Path(os.getenv("DUCK_REPO", "../DUCK")),
    )
    parser.add_argument("--name", default="Aster")
    parser.add_argument("--llm", action="store_true")
    args = parser.parse_args(argv)

    payload = json.load(sys.stdin)
    host_type = _load_duck(args.duck_repo)

    cognition = expression = interpreter = None
    if args.llm:
        cognition, expression, interpreter = _llm_components()

    host = host_type.open(
        Path(payload["state_root"]),
        name=args.name,
        cognition=cognition,
        expression=expression,
        interpreter=interpreter,
    )

    ticks_before = max(0, int(payload.get("ticks_before", 0)))
    ticks_after = max(0, int(payload.get("ticks_after", 0)))
    if ticks_before:
        host.heartbeat(ticks_before)

    result = host.interact(
        str(payload["text"]),
        speaker=str(payload.get("speaker", "user")),
    )

    if ticks_after:
        host.heartbeat(ticks_after)

    print(
        json.dumps(
            {
                "response_text": result.response_text,
                "selected_action": result.selected_action,
                "action_id": result.action_id,
                "tick": result.tick,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
