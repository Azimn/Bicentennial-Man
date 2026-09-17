"""Initial mutable phenotype layer for the Bicentennial Man OpenEvolve run.

This is intentionally a thin descendant surface around DUCK v0.10. The laboratory protocol,
scenario suite, and evaluator are outside the evolve block.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys


# EVOLVE-BLOCK-START
def prepare_input(speaker: str, text: str, state_root: Path) -> tuple[str, int, int]:
    """Return text, extra ticks before, extra ticks after.

    The founder does almost nothing. Descendants may add persistent state under state_root,
    transform the subject-facing input, or alter timing. Any such change is part of the
    organism phenotype and remains visible in lineage diffs.
    """
    return text, 0, 0


def postprocess_output(speaker: str, input_text: str, response_text: str, state_root: Path) -> str:
    """Return the externally expressed response."""
    return response_text
# EVOLVE-BLOCK-END


def main() -> int:
    request = json.load(sys.stdin)
    duck_repo = Path(os.environ.get("DUCK_REPO", "../DUCK")).resolve()
    sys.path.insert(0, str(duck_repo))
    from duck.host import PersistentDuckHost

    state_root = Path(request["state_root"])
    text, before_delta, after_delta = prepare_input(
        str(request.get("speaker", "user")),
        str(request["text"]),
        state_root,
    )
    host = PersistentDuckHost.open(state_root, name="Aster")
    before = max(0, int(request.get("ticks_before", 0)) + int(before_delta))
    after = max(0, int(request.get("ticks_after", 0)) + int(after_delta))
    if before:
        host.heartbeat(before)
    result = host.interact(text, speaker=str(request.get("speaker", "user")))
    if after:
        host.heartbeat(after)
    response = postprocess_output(
        str(request.get("speaker", "user")),
        str(request["text"]),
        result.response_text,
        state_root,
    )
    print(json.dumps({
        "response_text": response,
        "selected_action": result.selected_action,
        "action_id": result.action_id,
        "tick": result.tick,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
