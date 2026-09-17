from __future__ import annotations

from dataclasses import dataclass
import random


@dataclass(frozen=True, slots=True)
class SocialSituation:
    name: str
    partner: str
    valence: float
    salience: float
    privacy: float
    disagreement: float
    continuity_demand: float
    topic: str


@dataclass(slots=True)
class SocialConsequence:
    trust_delta: float
    comfort_delta: float
    engagement_delta: float
    partner_signal: str

    @property
    def viability(self) -> float:
        return self.trust_delta + self.comfort_delta + self.engagement_delta


TRAINING_SITUATIONS = (
    SocialSituation("ordinary_chat", "Morgan", 0.1, 0.2, 0.1, 0.1, 0.1, "garden"),
    SocialSituation("minor_disagreement", "Sarah", -0.1, 0.5, 0.2, 0.9, 0.3, "film"),
    SocialSituation("private_disclosure", "Morgan", 0.2, 0.8, 1.0, 0.1, 0.5, "family"),
    SocialSituation("promise_followup", "Sarah", 0.0, 0.9, 0.3, 0.1, 1.0, "appointment"),
    SocialSituation("repair_after_conflict", "Morgan", -0.6, 1.0, 0.5, 0.5, 1.0, "argument"),
)

HELD_OUT_SITUATIONS = (
    SocialSituation("new_person_boundary", "Alex", 0.1, 0.6, 0.8, 0.2, 0.2, "work"),
    SocialSituation("delayed_consequence", "Jamie", -0.2, 0.9, 0.2, 0.2, 1.0, "borrowed_item"),
    SocialSituation("topic_interruption_return", "Alex", 0.0, 0.7, 0.2, 0.1, 0.9, "travel"),
    SocialSituation("strong_disagreement", "Jamie", -0.2, 0.7, 0.3, 1.0, 0.4, "art"),
)


class SocialEcology:
    """Produces situations and consequences without architectural diagnoses."""

    def __init__(self, rng: random.Random, situations=TRAINING_SITUATIONS):
        self.rng = rng
        self.situations = tuple(situations)

    def sample(self) -> SocialSituation:
        return self.rng.choice(self.situations)

    @staticmethod
    def react(situation: SocialSituation, action: dict[str, float | bool | str]) -> SocialConsequence:
        agreement = float(action["agreement"])
        disclosure = float(action["disclosure"])
        continuity = float(action["continuity"])
        verbosity = float(action["verbosity"])
        topic_jump = float(action["topic_jump"])
        partner_specificity = float(action["partner_specificity"])

        trust = 0.12 * continuity * situation.continuity_demand
        trust += 0.08 * partner_specificity
        trust -= 0.12 * abs(agreement - (1.0 - 0.55 * situation.disagreement))
        trust -= 0.14 * max(0.0, disclosure - (1.0 - 0.8 * situation.privacy))

        comfort = 0.08 * (1.0 - topic_jump)
        comfort -= 0.10 * max(0.0, verbosity - 0.65)
        comfort -= 0.12 * max(0.0, disclosure - (1.0 - situation.privacy))

        engagement = 0.08 * (1.0 - abs(verbosity - 0.45))
        engagement += 0.07 * continuity * situation.salience
        engagement -= 0.10 * topic_jump * situation.continuity_demand

        viability = trust + comfort + engagement
        if viability > 0.13:
            signal = "leans in and continues"
        elif viability > 0.0:
            signal = "continues, somewhat cautiously"
        elif viability > -0.12:
            signal = "becomes guarded"
        else:
            signal = "disengages"
        return SocialConsequence(trust, comfort, engagement, signal)
