# Bicentennial Man v0.3 Empirical Sequence

The current experiment does not add another character architecture. MicroPsiDUCK v0.10 is the founder organism and the current task is to characterize and challenge its observable phenotype under controlled persistent lifetimes.

The required empirical sequence is:

```text
DUCK founder phenotype characterization
            |
            v
Surface-Mutable Control
            |
            v
evaluator exploit analysis
            |
            v
fixed-boundary Mechanism-Mutable DUCK
            |
            v
held-out transfer
            |
            v
ablation of successful changes
```

A higher training score is never sufficient evidence of organism improvement. A candidate must survive fixed-boundary evaluation and held-out transfer before a change can be described as a cognitive or organism-level improvement.

## Phase 1: founder characterization

Run multiple fresh persistent DUCK lifetimes. Each lifetime starts from a new state root. Scenario order is permuted from a recorded seed. Preserve the complete transcript, deterministic probes, judge outputs when used, exact scenario order, DUCK commit, DUCK branch, and aggregate dispersion across lifetimes.

The founder baseline is characterization, not one canonical score. Order sensitivity and history sensitivity are part of the phenotype.

## Phase 2: Surface-Mutable Control

The current OpenEvolve experiment is formally the Surface-Mutable Control. DUCK is unmodified. Candidate code may alter only the explicit interaction surface through input rewriting, output rewriting, timing changes, or surface-owned persistent state.

Those channels are instrumented. Improvements that depend primarily on them are benchmark exploitation. They are scientifically useful because they estimate how vulnerable the evaluator is to external compensation.

## Phase 3: exploit analysis

Inspect promising Surface-Mutable descendants against the unmodified founder, their raw DUCK responses, their surface transformation metadata, multiple order permutations, deterministic probes, and at least one judge from another model family when practical.

## Phase 4: Mechanism-Mutable DUCK

This condition is currently disabled. Do not populate its mutable path list until the Surface-Mutable Control has been characterized. When activated, the lab owns the input boundary, renderer, final output boundary, scenarios, evaluators, and sealed transfer suites. Only explicitly designated organism mechanisms may change.

Early mechanistic optimization excludes naturalness. If naturalness is later evaluated, every candidate must use the same fixed renderer.

## Scenario families

Do not expand the six current scripts into a larger fixed benchmark. After founder characterization and the Surface-Mutable Control are working, convert their behavioral requirements into parameterized scenario families so success depends on generalization rather than recognizing specific scripts.
