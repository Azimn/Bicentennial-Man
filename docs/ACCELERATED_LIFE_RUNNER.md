# Accelerated Life Runner v0.1

## Research question

Can accumulated experience alone create persistent behavioral individuality in unchanged MicroPsiDUCK v0.10?

The first target is deliberately narrow:

```text
20 identical founder clones
20 reproducibly generated histories
100,000 organism ticks per primary clone
3 identical-history replicate controls
no evolution
no Surface-Mutable wrapper
no DUCK code changes
one identical terminal phenotype battery
```

MicroPsiDUCK is pinned to commit `30a11ea8308ebd0fc89a06bb994ab0e23bd02886`.

## Controlled variables

Every primary clone starts with the same subject id, `accelerated-life-founder-v0.1`, and the same clean DUCK code. Every clone reaches exactly the same pre-battery age. Every clone receives the same number of generated social events at the same absolute event ticks. The recurring actor set is the same, and actor exposure is balanced. Every clone receives the same terminal battery in the same order.

The planned between-primary-clone manipulation is generated experiential history. Each seed changes actor dispositions, experienced event sequence, topics, valence, intensity, and consequences.

This design controls the age confound identified in the six-lifetime founder characterization. A clone is not older merely because its history happened in a different order.

## Identical-history reproducibility control

Three additional control clones replicate the first three primary histories by default. Each replicate receives a `history.json` copied byte-for-byte from its paired primary clone.

For every pair, the runner requires all of the following to match:

* the history file bytes and SHA-256;
* the mature endpoint summary at the end of the life history;
* the 16-action terminal signature;
* the terminal response signature.

If any matched-history pair diverges, the experiment writes the control failure into `summary.json` and exits with an error. Primary-clone divergence must not be attributed to experience alone unless this control passes.

The 20 primary clones remain the population used for unique-signature counts and pairwise divergence statistics. Replicate controls are reported separately and do not inflate the primary sample.

## Generated histories

The default life contains 200 generated social events spread across 100,000 ticks. Morgan, Sarah, Alex, and Jamie each appear 50 times. The generator creates reproducible actor profiles and selects among supportive, conflict, repair, challenge, discovery, and ordinary experiences. Each event has an explicit external consequence that is delivered through DUCK's existing outcome-learning interface.

The generator is laboratory code. It does not change the organism and it does not own character state.

Each `history.json` is written before the life is completed and has a stable SHA-256 fingerprint.

## Exogenous outcome limitation

Accelerated Life v0.1 uses exogenous outcomes. Event success, valence, and outcome text are generated from the actor profile and event category before DUCK chooses its action. DUCK experiences those consequences and can learn from them, but its selected action does not determine the world's next consequence.

Therefore v0.1 tests:

> Can different experienced histories produce persistent divergence in an unchanged organism?

It does not yet test:

> Can different choices create different lives through reciprocal interaction?

A later Accelerated Life v0.2 can add reciprocal social consequences without changing the interpretation of this v0.1 result.

## Acceleration

The runner still executes every DUCK heartbeat. It does not numerically skip organism time. To make 100,000-tick runs practical, idle heartbeats call the unchanged DUCK organism directly rather than writing one host journal row for every tick. The complete DUCK persistent state is checkpointed periodically and after every generated life event.

Inner cognition remains enabled, matching normal non-LLM DUCK execution. No LLM is used in the life generator or the organism.

## Terminal battery

At tick 100,000 the runner saves the mature state. It then copies that state and runs the existing `configs/suites/training.json` battery against the copy. The mature endpoint remains unchanged by measurement.

The terminal report preserves the full transcript, deterministic phenotype probes, exact action signature, and exact response signature for every clone.

Across the 20 primary clones the summary reports the number of unique terminal action and response signatures and pairwise positional divergence across the common battery.

## Interpretation

Terminal divergence under matched code, initial identity, age, interaction density, actor set, and battery is evidence of experience-conditioned phenotypic divergence only if the identical-history reproducibility control passes.

It is not by itself evidence of human-like individuality, cognitive improvement, consciousness, or an artificiality benchmark victory. A null result is also informative: it would show that these histories and this duration are insufficient to produce behaviorally persistent differentiation in the current architecture.

Three outcomes are especially informative. Near-identical terminal behavior suggests the current system is strongly attractor-dominated or forgetful. Internal endpoint divergence with terminal behavioral convergence suggests differentiated internal trajectories that the present action-selection or expression surface does not expose. Persistent terminal action divergence with passing identical-history controls is evidence that developmental history alone differentiated initially identical artificial subjects under this protocol.

## Local run

From the Bicentennial Man repository with DUCK checked out beside it:

```powershell
bicentennial-life `
  --duck-repo ..\DUCK `
  --suite configs\suites\training.json `
  --clones 20 `
  --ticks 100000 `
  --events 200 `
  --seed-base 20000 `
  --checkpoint-every 5000 `
  --out runs\accelerated-life-v0.1
```

The identical-history control defaults to three replicate pairs, so the merged command above does not need another option.

The run is restartable. Reissuing the same command without `--overwrite` reopens each persisted clone and verifies that the run manifest and generated histories match before continuing.

## Output layout

```text
runs/accelerated-life-v0.1/
  run_manifest.json
  summary.json
  clones/
    clone-000/
      history.json
      matured-state/
      endpoint.json
      terminal-state/
      terminal-transcript.json
      terminal-metrics.json
    ...
  controls/
    identical-history/
      pair-000/
        replicate/
          history.json
          matured-state/
          endpoint.json
          terminal-state/
          terminal-transcript.json
          terminal-metrics.json
      ...
```

Do not commit the large working state directories automatically. After the full experiment succeeds, preserve the compact manifests, histories, terminal transcripts, metrics, endpoint summaries, identical-history control records, and a characterization summary under a versioned `results/` path, following the founder-baseline preservation pattern.
