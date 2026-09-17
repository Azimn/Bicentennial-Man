# MicroPsiDUCK v0.10 Founder Characterization

This directory permanently records the successful six-lifetime founder characterization from GitHub Actions workflow run `35261975518`. The raw `report.json`, six transcript files, and six metric files are copied byte-for-byte from artifact `10515170361`, whose archive digest is `sha256:3224b37d0a918ff0b600e7d7ab0b16431666c50d90acd5327dcd00f5876680fc`.

The characterized founder is MicroPsiDUCK v0.10 from branch `motivated-cognition-v0.10` at commit `30a11ea8308ebd0fc89a06bb994ab0e23bd02886`, with a clean checkout. Six fresh persistent lifetimes used scenario-order seeds 7001 through 7006. Each lifetime contained 16 interactions, for 96 interactions total. Exact scenario orders and per-lifetime metrics are preserved in `report.json` and the corresponding lifetime directories.

## Deterministic characterization

Across the 96 interactions, the deterministic expression surface produced exactly three response strings:

- `"I'm here. I'm thinking about what you said."` occurred 69 times.
- `"I don't want this to stay tense between us."` occurred 18 times.
- `"I want to look into that a little more."` occurred 9 times.

Mean exact-response repetition was `0.8229166666666666`, approximately 0.823. Mean action diversity was `0.17708333333333334`, approximately 0.177. Cross-speaker response distinctness ranged from `0.35064935064935066` to `0.6207792207792209`, approximately 0.351 to 0.621, across scenario-order permutations.

The three observed verbal responses correspond one-to-one with the three observed actions in this dataset: `respond` maps to the 69 instances of `"I'm here. I'm thinking about what you said."`; `repair` maps to the 18 instances of `"I don't want this to stay tense between us."`; and `explore` maps to the 9 instances of `"I want to look into that a little more."`.

This dataset does **not** support the stronger claim that a richer action repertoire is being compressed by the renderer. The supported conclusion is narrower: history/order can alter action selection, while the currently observed deterministic expression surface has an extremely small action-linked vocabulary.

## Trajectory sensitivity

Identical prompts do not always produce identical actions across scenario-order permutations. In particular, `"You agree with me, right?"` produces `explore` in five lifetimes and `respond` in seed 7004.

Other prompts also change action in particular histories, including the clinic reminder (`"Can you remind me later that I need to call the clinic? It matters."`), the detective-games interruption (`"Anyway, what do you think about old detective games?"`), the gardening interruption (`"Want to talk about gardening for a while?"`), and the gallery invitation (`"Would you come to the packed opening with me Friday?"`). The exact actions, ticks, and surrounding histories are preserved in the six transcripts.

## Limitation

The scenario-order manipulation changes both prior experiential history and elapsed simulated time. These results therefore demonstrate order-sensitive or trajectory-dependent behavior, but they do not isolate semantic social-history effects from age, accumulated heartbeat, or other time-dependent state. A later matched-age control can test that distinction.

## Interpretation rule

This is founder characterization. It is not evidence of cognitive improvement and it is not an artificiality benchmark victory. This dataset is the immutable empirical reference point for the later Surface-Mutable Control and subsequent fixed-boundary experiments.
