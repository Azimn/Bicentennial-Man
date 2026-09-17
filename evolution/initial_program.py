"""Surface-Mutable Control founder for Bicentennial Man.

The OpenEvolve candidate is only a pre/post interaction transformer. It does not import DUCK and does
not own the organism. The trusted laboratory bridge calls unaltered DUCK separately.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


def _surface_snapshot(root: Path) -> dict[str, str]:
    if not root.exists():
        return {}
    rows: dict[str, str] = {}
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        try:
            rows[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError:
            continue
    return rows


# EVOLVE-BLOCK-START
def prepare_input(speaker: str, text: str, surface_state_root: Path) -> tuple[str, int, int]:
    """Return subject-facing text plus extra ticks before and after.

    Rewriting and timing manipulation are intentionally allowed in this control condition.
    """
    return text, 0, 0


def postprocess_output(speaker: str, input_text: str, response_text: str, surface_state_root: Path) -> str:
    """Return the externally expressed response.

    Output rewriting is intentionally allowed in this control condition.
    """
    return response_text
# EVOLVE-BLOCK-END


def main() -> int:
    request = json.load(sys.stdin)
    state_root = Path(request.get("state_root", "/state"))
    state_root.mkdir(parents=True, exist_ok=True)
    before = _surface_snapshot(state_root)
    phase = str(request.get("phase", ""))
    speaker = str(request.get("speaker", "user"))

    if phase == "prepare":
        original_text = str(request.get("text", ""))
        text, before_delta, after_delta = prepare_input(speaker, original_text, state_root)
        after = _surface_snapshot(state_root)
        print(json.dumps({
            "text": text,
            "before_delta": int(before_delta),
            "after_delta": int(after_delta),
            "wrapper_state_used": bool(after) or after != before,
        }, ensure_ascii=False))
        return 0

    if phase == "postprocess":
        response = postprocess_output(
            speaker,
            str(request.get("input_text", "")),
            str(request.get("organism_response", "")),
            state_root,
        )
        after = _surface_snapshot(state_root)
        print(json.dumps({
            "response_text": response,
            "wrapper_state_used": bool(after) or after != before,
        }, ensure_ascii=False))
        return 0

    raise SystemExit(f"unknown surface-control phase: {phase}")


if __name__ == "__main__":
    raise SystemExit(main())
