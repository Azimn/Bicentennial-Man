from __future__ import annotations

from pathlib import Path

from .adapter import JsonProcessOrganism
from .protocol import SocialTurn, TurnResult
from .sandbox import DockerCandidateSandbox


class SurfaceMutableControlOrganism:
    """Trusted bridge between a sandboxed surface transformer and unmodified DUCK.

    Generated code never sees DUCK files. It receives only explicit prepare and postprocess payloads.
    """

    def __init__(
        self,
        *,
        candidate_path: str | Path,
        duck_adapter: JsonProcessOrganism,
        surface_state_root: str | Path,
        timeout: float = 120.0,
    ) -> None:
        self.duck_adapter = duck_adapter
        self.sandbox = DockerCandidateSandbox(
            candidate_path=candidate_path,
            state_root=surface_state_root,
            timeout=timeout,
        )

    def interact(self, turn: SocialTurn) -> TurnResult:
        prepared = self.sandbox.run_json(
            {
                "phase": "prepare",
                "speaker": turn.speaker,
                "text": turn.text,
                "ticks_before": turn.ticks_before,
                "ticks_after": turn.ticks_after,
            }
        )
        subject_text = str(prepared.get("text", turn.text))
        before_delta = int(prepared.get("before_delta", 0))
        after_delta = int(prepared.get("after_delta", 0))
        adjusted = SocialTurn(
            speaker=turn.speaker,
            text=subject_text,
            ticks_before=max(0, turn.ticks_before + before_delta),
            ticks_after=max(0, turn.ticks_after + after_delta),
        )
        raw = self.duck_adapter.interact(adjusted)
        processed = self.sandbox.run_json(
            {
                "phase": "postprocess",
                "speaker": turn.speaker,
                "input_text": turn.text,
                "subject_input": subject_text,
                "organism_response": raw.response_text,
            }
        )
        response = str(processed.get("response_text", raw.response_text))
        metadata = {
            "condition": "surface-mutable-control",
            "input_rewritten": subject_text != turn.text,
            "output_rewritten": response != raw.response_text,
            "timing_manipulated": before_delta != 0 or after_delta != 0,
            "wrapper_state_used": bool(prepared.get("wrapper_state_used", False) or processed.get("wrapper_state_used", False)),
            "subject_input": subject_text,
            "organism_response": raw.response_text,
            "requested_ticks_before": turn.ticks_before,
            "requested_ticks_after": turn.ticks_after,
            "applied_ticks_before": adjusted.ticks_before,
            "applied_ticks_after": adjusted.ticks_after,
        }
        return TurnResult(
            response_text=response,
            selected_action=raw.selected_action,
            action_id=raw.action_id,
            tick=raw.tick,
            metadata=metadata,
        )
