# Bicentennial Man project instructions

Bicentennial Man is a phenotype-first research laboratory for persistent artificial organisms. Do not add another character architecture.

The original v0.1 genome-search implementation is preserved on `original-approach`. MicroPsiDUCK v0.10 is the current founder.

Current sequence:

`DUCK founder characterization -> Surface-Mutable Control -> exploit analysis -> fixed-boundary Mechanism-Mutable DUCK -> held-out transfer -> ablation`

Critical boundaries:

1. Founder characterization is a distribution across multiple fresh persistent lifetimes, not one score. Record complete transcripts, metrics, scenario order, order seed, and exact DUCK Git provenance.
2. Reproducible scenario-order permutations are required so order and history effects remain visible.
3. The existing OpenEvolve wrapper is the Surface-Mutable Control. DUCK is not mutable in this condition.
4. Input rewriting, output rewriting, prompt recognition, wrapper-owned relationship state, timing manipulation, or other external compensation are benchmark exploitation, not organism improvement. Instrument and preserve them.
5. Naturalness is diagnostic only during early evolution. The optimization score excludes it.
6. A language model judge is never sole milestone evidence. Preserve deterministic probes and use at least one additional model family when practical.
7. Generated candidate code must be isolated before execution. It may not read laboratory source, evaluators, sealed suites, unrelated repository files, DUCK source in the Surface-Mutable Control, or another candidate's state.
8. The Mechanism-Mutable condition remains disabled until Surface-Mutable exploit analysis is complete. Do not populate its mutable path list yet.
9. When Mechanism-Mutable is activated, subject input and final external output pass through fixed laboratory-controlled boundaries. The renderer is fixed and outside the mutable set.
10. Held-out transfer is measurement only and must not feed back into the search it evaluates.
11. Do not greatly expand the fixed scenario count. After the first two phases work, parameterize the behavioral requirements into scenario families.
12. Do not infer mechanism from a score. Require fixed-boundary transfer and ablation before making causal claims.
13. Keep negative results, regressions, candidate lineage, model identity, settings, seeds, transcripts, and resource usage when available.

Verification:

`python -m unittest discover -s tests -v`

Founder characterization:

`bicentennial-baseline --duck-repo ../DUCK --lifetimes 8 --order-seed 7001 --out runs/founder-baseline`

Use the hostile reviewer whenever apparent progress occurs. Search specifically for surface compensation, judge bias, script recognition, order effects, state leakage, renderer substitution, evaluator access, and lack of held-out transfer.
