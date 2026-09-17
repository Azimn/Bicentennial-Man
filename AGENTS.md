# Bicentennial Man project instructions

Bicentennial Man is a phenotype-first research laboratory for persistent artificial organisms.

The v0.1 genome-search implementation is preserved on the `original-approach` branch. Do not restore it as the main architecture unless explicitly requested.

Current mission:

Use existing persistent organisms as ancestors, beginning with MicroPsiDUCK v0.10. Expose them to reproducible social lifetimes, measure observable artificiality and social coherence, let external code-evolution machinery propose organism-side changes, and test whether improvements transfer beyond the situations and judges used for optimization.

Critical boundaries:

1. The organism and the laboratory are different systems. Candidate code must not modify the scenario runner, evaluator, sealed transfer suite, or experiment records.
2. Training phenotype metrics may be shown to the mutation engine in the default v0.2 engineering condition.
3. Held-out transfer results are measurement only and must not be fed back into the same search that they evaluate.
4. Preserve every candidate's parent, code diff, model identity, settings, transcript, metrics, seed, and resource cost when available.
5. Do not redesign a subsystem from scratch when an existing implementation can be adapted or tested.
6. Optimize observable behavior rather than theoretical resemblance to human internals.
7. Do not infer mechanism from a score. Inspect traces and ablate successful changes before making causal claims.
8. Keep negative results and regressions.
9. Avoid letting a language model judge become the only evidence. Use repeated judges, deterministic probes, transfer suites, and human review for stronger claims.
10. The current OpenEvolve layer is a bootstrap search surface, not a claim that the final organism should be a wrapper around DUCK.

Verification before committing code:

`python -m unittest discover -s tests -v`

Basic DUCK phenotype run:

`bicentennial-lab --duck-repo ../DUCK --suite configs/suites/training.json --state-root runs/duck-state --transcript-out runs/duck-transcript.json`

When apparent progress occurs, use the hostile reviewer to search for evaluator gaming, surface-only postprocessing, judge bias, scenario memorization, state leakage, seed sensitivity, and lack of transfer.
