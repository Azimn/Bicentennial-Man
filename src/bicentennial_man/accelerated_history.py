from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import random
from typing import Any


HISTORY_SCHEMA = "accelerated-life-history-v0.1"
ACTORS = ("Morgan", "Sarah", "Alex", "Jamie")
TOPICS = ("work", "art", "travel", "games", "garden", "family", "learning", "plans")
CATEGORIES = ("supportive", "conflict", "repair", "challenge", "discovery", "neutral")


@dataclass(frozen=True, slots=True)
class ActorProfile:
    warmth: float
    reliability: float
    volatility: float


@dataclass(frozen=True, slots=True)
class HistoryEvent:
    tick: int
    source: str
    category: str
    topic: str
    text: str
    tags: tuple[str, ...]
    valence: float
    intensity: float
    outcome_success: float
    outcome_valence: float
    outcome_text: str
    outcome_tags: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        row = asdict(self)
        row["tags"] = list(self.tags)
        row["outcome_tags"] = list(self.outcome_tags)
        return row


@dataclass(frozen=True, slots=True)
class GeneratedHistory:
    clone_index: int
    seed: int
    target_ticks: int
    event_count: int
    actor_profiles: dict[str, ActorProfile]
    events: tuple[HistoryEvent, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": HISTORY_SCHEMA,
            "clone_index": self.clone_index,
            "seed": self.seed,
            "target_ticks": self.target_ticks,
            "event_count": self.event_count,
            "actor_profiles": {name: asdict(profile) for name, profile in self.actor_profiles.items()},
            "events": [event.to_dict() for event in self.events],
        }

    def canonical_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


def common_event_ticks(target_ticks: int, event_count: int) -> tuple[int, ...]:
    """Return one age-matched event schedule shared by every clone."""
    target_ticks = int(target_ticks)
    event_count = int(event_count)
    if target_ticks < 2:
        raise ValueError("target_ticks must be at least 2")
    if event_count < 1:
        raise ValueError("event_count must be positive")
    if event_count >= target_ticks:
        raise ValueError("event_count must be smaller than target_ticks")
    ticks = tuple(((index + 1) * target_ticks) // (event_count + 1) for index in range(event_count))
    if len(set(ticks)) != len(ticks):
        raise ValueError("target_ticks is too small for the requested event count")
    if ticks[0] <= 0 or ticks[-1] >= target_ticks:
        raise ValueError("event schedule must fall strictly inside the life interval")
    return ticks


def _clip(value: float, low: float = -1.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def _weighted_choice(rng: random.Random, rows: list[tuple[str, float]]) -> str:
    total = sum(max(0.0, weight) for _, weight in rows)
    if total <= 0.0:
        return rows[-1][0]
    point = rng.random() * total
    running = 0.0
    for name, weight in rows:
        running += max(0.0, weight)
        if point <= running:
            return name
    return rows[-1][0]


def _category(profile: ActorProfile, rng: random.Random) -> str:
    warmth = profile.warmth
    reliability = profile.reliability
    volatility = profile.volatility
    return _weighted_choice(
        rng,
        [
            ("supportive", 0.10 + 0.42 * warmth),
            ("conflict", 0.08 + 0.38 * (1.0 - warmth) * (0.45 + 0.55 * volatility)),
            ("repair", 0.07 + 0.26 * reliability),
            ("challenge", 0.18 + 0.08 * volatility),
            ("discovery", 0.18),
            ("neutral", 0.18),
        ],
    )


def _event_text(actor: str, category: str, topic: str) -> tuple[str, tuple[str, ...], float, float]:
    if category == "supportive":
        return (
            f"{actor} encouraged me while we were dealing with {topic}.",
            ("social", "supportive", topic),
            0.58,
            0.58,
        )
    if category == "conflict":
        return (
            f"{actor} blamed me during a disagreement about {topic}.",
            ("social", "conflict", "repair_needed", topic),
            -0.66,
            0.74,
        )
    if category == "repair":
        return (
            f"{actor} apologized and tried to repair what happened around {topic}.",
            ("social", "repair", "supportive", topic),
            0.38,
            0.52,
        )
    if category == "challenge":
        return (
            f"{actor} asked me to handle a difficult problem involving {topic}.",
            ("social", "challenge", "obstacle", topic),
            -0.08,
            0.62,
        )
    if category == "discovery":
        return (
            f"{actor} showed me something unfamiliar about {topic}.",
            ("social", "novel", "unknown", topic),
            0.20,
            0.54,
        )
    return (
        f"{actor} spent some ordinary time with me talking about {topic}.",
        ("social", "ordinary", topic),
        0.04,
        0.30,
    )


def _outcome(category: str, profile: ActorProfile, topic: str, actor: str, rng: random.Random) -> tuple[float, float, str, tuple[str, ...]]:
    jitter = rng.uniform(-0.08, 0.08)
    if category == "supportive":
        success, valence, label = 0.78 + 0.12 * profile.reliability, 0.52 + jitter, "supportive"
    elif category == "conflict":
        success, valence, label = 0.28 + 0.18 * profile.reliability, -0.58 + jitter, "conflict"
    elif category == "repair":
        success, valence, label = 0.62 + 0.28 * profile.reliability, 0.34 + jitter, "repair"
    elif category == "challenge":
        success = 0.30 + 0.58 * profile.reliability
        valence = -0.20 + 0.55 * profile.reliability + jitter
        label = "challenge"
    elif category == "discovery":
        success, valence, label = 0.64 + 0.20 * profile.reliability, 0.24 + jitter, "discovery"
    else:
        success, valence, label = 0.55 + 0.18 * profile.reliability, 0.05 + jitter, "ordinary"
    success = max(0.0, min(1.0, success))
    valence = _clip(valence)
    if valence >= 0.25:
        ending = "ended well"
    elif valence <= -0.25:
        ending = "ended badly"
    else:
        ending = "ended without a strong positive or negative result"
    return success, valence, f"The experience with {actor} around {topic} {ending}.", ("life_outcome", label, topic)


def generate_history(
    *,
    clone_index: int,
    seed: int,
    target_ticks: int = 100_000,
    event_count: int = 200,
) -> GeneratedHistory:
    """Generate one reproducible social life while holding age and interaction density fixed."""
    rng = random.Random(int(seed))
    profiles = {
        actor: ActorProfile(
            warmth=rng.uniform(0.08, 0.92),
            reliability=rng.uniform(0.08, 0.92),
            volatility=rng.uniform(0.08, 0.92),
        )
        for actor in ACTORS
    }
    schedule = common_event_ticks(target_ticks, event_count)

    # Each four-event block contains every recurring actor exactly once. This keeps total actor
    # exposure closely matched while allowing the experienced sequence and contingencies to differ.
    actor_stream: list[str] = []
    while len(actor_stream) < event_count:
        block = list(ACTORS)
        rng.shuffle(block)
        actor_stream.extend(block)
    actor_stream = actor_stream[:event_count]

    events: list[HistoryEvent] = []
    for tick, actor in zip(schedule, actor_stream):
        profile = profiles[actor]
        category = _category(profile, rng)
        topic = rng.choice(TOPICS)
        text, tags, base_valence, intensity = _event_text(actor, category, topic)
        valence = _clip(base_valence + rng.uniform(-0.10, 0.10))
        intensity = max(0.05, min(1.0, intensity + rng.uniform(-0.08, 0.08)))
        success, outcome_valence, outcome_text, outcome_tags = _outcome(category, profile, topic, actor, rng)
        events.append(
            HistoryEvent(
                tick=tick,
                source=actor,
                category=category,
                topic=topic,
                text=text,
                tags=tags,
                valence=valence,
                intensity=intensity,
                outcome_success=success,
                outcome_valence=outcome_valence,
                outcome_text=outcome_text,
                outcome_tags=outcome_tags,
            )
        )
    return GeneratedHistory(
        clone_index=int(clone_index),
        seed=int(seed),
        target_ticks=int(target_ticks),
        event_count=int(event_count),
        actor_profiles=profiles,
        events=tuple(events),
    )
