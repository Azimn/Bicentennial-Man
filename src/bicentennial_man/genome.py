from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import random
from typing import Any


@dataclass(slots=True)
class DevelopmentalGenome:
    """Small, inspectable search space for developmental organization.

    Loci are intentionally substrate-neutral. They specify capacities and dynamics,
    not named human faculties such as "emotion" or "theory of mind".
    """

    trace_capacity: int = 2
    actor_partitioning: float = 0.0
    carryover: float = 0.05
    thread_persistence: float = 0.05
    transition_inertia: float = 0.05
    action_reuse_bias: float = 0.0
    disclosure_threshold: float = 0.0
    routing_sparsity: float = 0.0
    agreement_bias: float = 0.9
    verbosity_bias: float = 0.9
    plasticity: float = 0.05
    exploration: float = 0.15

    def clamp(self) -> "DevelopmentalGenome":
        self.trace_capacity = max(0, min(64, int(self.trace_capacity)))
        for f in fields(self):
            if f.name == "trace_capacity":
                continue
            setattr(self, f.name, max(0.0, min(1.0, float(getattr(self, f.name)))))
        return self

    def mutate(self, rng: random.Random, rate: float = 0.25, scale: float = 0.12) -> "DevelopmentalGenome":
        data = asdict(self)
        if rng.random() < rate:
            data["trace_capacity"] += rng.choice([-2, -1, 1, 2])
        for key, value in list(data.items()):
            if key == "trace_capacity":
                continue
            if rng.random() < rate:
                data[key] = float(value) + rng.gauss(0.0, scale)
        return DevelopmentalGenome(**data).clamp()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DevelopmentalGenome":
        allowed = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in allowed}).clamp()
