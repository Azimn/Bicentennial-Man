# Bicentennial Man project instructions

This repository is a research experiment, not a product demo. Preserve causal interpretability and experimental provenance over feature count.

The central question is whether an artificial social subject can discover mechanisms that reduce detectable artificiality through developmental interaction and social consequences.

Critical invariants:

1. The subject must never receive the held-out artificiality score, evaluator rubric, evaluator explanation, or architectural diagnosis.
2. Selection in v0.1 uses only consequences available inside the developmental ecology. Held-out evaluation is measurement only.
3. Do not add a mechanism merely because it sounds human-like. Prefer substrate-neutral capacities and dynamics, then test their causal role.
4. Every mutation must be reconstructable from seed, parent identity, genome, and code version.
5. New mechanisms require controls, held-out transfer, and ablation before claims are strengthened.
6. Do not silently introduce an LLM into fitness, mutation, or hidden evaluation. LLM use must be explicitly logged by role and model.
7. Keep raw experiment mechanics deterministic under a fixed seed.
8. Never replace a failed experiment with post hoc storytelling. Preserve negative results.

Verification before committing code:

`python -m unittest discover -s tests -v`

For a smoke run:

`bicentennial --generations 5 --population 12 --episodes 100 --output runs/smoke.jsonl`

When reviewing apparent progress, use the `hostile-reviewer` subagent and ask it to search for evaluator leakage, Goodharting, overfitting, untracked architectural hand-design, seed sensitivity, and lack of transfer.
