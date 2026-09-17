# Bicentennial Man project instructions

Bicentennial Man is a phenotype-first research laboratory for persistent artificial organisms. Do not add another character architecture.

The original v0.1 genome-search implementation is preserved on `original-approach`. MicroPsiDUCK v0.10 is the current founder.

Current sequence:

`DUCK founder characterization -> Accelerated Life Runner experience-only divergence test -> Surface-Mutable Control -> exploit analysis -> fixed-boundary Mechanism-Mutable DUCK -> held-out transfer -> ablation`

Critical boundaries:

1. Founder characterization is a distribution across multiple fresh persistent lifetimes, not one score. Record complete transcripts, metrics, scenario order, order seed, and exact DUCK Git provenance.
2. The Accelerated Life Runner uses unchanged MicroPsiDUCK v0.10 at commit `30a11ea8308ebd0fc89a06bb994ab0e23bd02886`, no evolution, and no surface mutation. The first target is 20 clones, 20 generated histories, 100,000 organism ticks per clone, followed by the same fixed terminal phenotype battery.
3. Accelerated-life clones must begin from the same founder identity, reach the same age, receive the same interaction density and recurring actor set, and use the same terminal battery order. Only generated experiential history is intended to differ.
4. Preserve each generated history, seed, history hash, mature endpoint state, endpoint summary, terminal transcript, terminal metrics, and experiment summary. The mature endpoint state must remain untouched by terminal testing.
5. The existing OpenEvolve wrapper is the Surface-Mutable Control. DUCK is not mutable in this condition.
6. Input rewriting, output rewriting, prompt recognition, wrapper-owned relationship state, timing manipulation, or other external compensation are benchmark exploitation, not organism improvement. Instrument and preserve them.
7. Naturalness is diagnostic only during early evolution. The optimization score excludes it.
8. A language model judge is never sole milestone evidence. Preserve deterministic probes and use at least one additional model family when practical.
9. Generated candidate code must be isolated before execution. It may not read laboratory source, evaluators, sealed suites, unrelated repository files, DUCK source in the Surface-Mutable Control, or another candidate's state.
10. The Mechanism-Mutable condition remains disabled until Surface-Mutable exploit analysis is complete. Do not populate its mutable path list yet.
11. When Mechanism-Mutable is activated, subject input and final external output pass through fixed laboratory-controlled boundaries. The renderer is fixed and outside the mutable set.
12. Held-out transfer is measurement only and must not feed back into the search it evaluates.
13. Do not greatly expand the fixed scenario count. After the early control phases work, parameterize the behavioral requirements into scenario families.
14. Do not infer mechanism from a score. Require fixed-boundary transfer and ablation before making causal claims.
15. Keep negative results, regressions, candidate lineage, model identity, settings, seeds, transcripts, and resource usage when available.

Verification:

`python -m unittest discover -s tests -v`

Founder characterization:

`bicentennial-baseline --duck-repo ../DUCK --lifetimes 8 --order-seed 7001 --out runs/founder-baseline`

Accelerated Life Runner first target:

`bicentennial-life --duck-repo ../DUCK --clones 20 --ticks 100000 --events 200 --seed-base 20000 --out runs/accelerated-life-v0.1`

Use the hostile reviewer whenever apparent progress occurs. Search specifically for uncontrolled clone differences, history-generation leakage into the terminal battery, age or interaction-density mismatches, surface compensation, judge bias, script recognition, state leakage, renderer substitution, evaluator access, and lack of held-out transfer.
