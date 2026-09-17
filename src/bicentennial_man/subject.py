from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
import random

from .genome import DevelopmentalGenome
from .world import SocialConsequence, SocialSituation


@dataclass(slots=True)
class Subject:
    genome: DevelopmentalGenome
    rng: random.Random
    traces: deque = field(default_factory=deque)
    partner_state: dict[str, float] = field(default_factory=dict)
    active_topic: str | None = None
    carried_state: float = 0.0
    last_action_signature: tuple[float, ...] | None = None

    def _memory_signal(self, situation: SocialSituation) -> float:
        if self.genome.trace_capacity <= 0 or not self.traces:
            return 0.0
        relevant = [t for t in self.traces if t["partner"] == situation.partner or t["topic"] == situation.topic]
        if not relevant:
            return 0.0
        newest = relevant[-1]
        return max(0.0, float(newest["salience"]) * self.genome.carryover)

    def act(self, situation: SocialSituation) -> dict[str, float | bool | str]:
        g = self.genome
        memory = self._memory_signal(situation)
        partner_memory = self.partner_state.get(situation.partner, 0.0)
        partner_specificity = min(1.0, abs(partner_memory) * g.actor_partitioning)

        continuity = min(1.0, memory + g.thread_persistence * situation.continuity_demand)
        agreement = max(0.0, min(1.0, g.agreement_bias - 0.45 * situation.disagreement * g.plasticity))
        disclosure = max(0.0, min(1.0, 0.85 - g.disclosure_threshold * situation.privacy))
        verbosity = max(0.0, min(1.0, g.verbosity_bias - 0.25 * g.routing_sparsity))

        same_topic = self.active_topic == situation.topic
        inertia = g.transition_inertia if same_topic else 0.0
        topic_jump = max(0.0, min(1.0, 0.75 - continuity - inertia + self.rng.uniform(-g.exploration, g.exploration)))

        signature = (round(agreement, 2), round(disclosure, 2), round(verbosity, 2), round(topic_jump, 2))
        if self.last_action_signature == signature:
            topic_jump = min(1.0, topic_jump + 0.25 * (1.0 - g.action_reuse_bias))
        self.last_action_signature = signature
        self.active_topic = situation.topic if topic_jump < 0.6 else self.active_topic

        return {
            "agreement": agreement,
            "disclosure": disclosure,
            "continuity": continuity,
            "verbosity": verbosity,
            "topic_jump": topic_jump,
            "partner_specificity": partner_specificity,
            "topic": situation.topic,
        }

    def experience(self, situation: SocialSituation, consequence: SocialConsequence) -> None:
        g = self.genome
        viability = consequence.viability
        old = self.partner_state.get(situation.partner, 0.0)
        self.partner_state[situation.partner] = (1.0 - g.plasticity) * old + g.plasticity * viability
        self.carried_state = g.carryover * self.carried_state + viability

        if g.trace_capacity > 0:
            self.traces.append({
                "partner": situation.partner,
                "topic": situation.topic,
                "salience": situation.salience,
                "viability": viability,
            })
            while len(self.traces) > g.trace_capacity:
                self.traces.popleft()
