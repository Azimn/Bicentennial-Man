# Accelerated Life Runner v0.1

## Research question

Can accumulated experience alone create persistent behavioral individuality in unchanged MicroPsiDUCK v0.10?

The first target is deliberately narrow:

```text
20 identical founder clones
20 reproducibly generated histories
100,000 organism ticks per clone
no evolution
no Surface-Mutable wrapper
no DUCK code changes
one identical terminal phenotype battery
```

MicroPsiDUCK is pinned to commit `30a11ea8308ebd0fc89a06bb994ab0e23bd02886`.

## Controlled variables

Every clone starts with the same subject id, `accelerated-life-founder-v0.1`, and the same clean DUCK code. Every clone reaches exactly the same pre-battery age. Every clone receives the same number of generated social events at the same absolute event ticks. The recurring actor set is the same, and actor exposure is balanced. Every clone receives the same terminal battery in the same order.

The planned between-clone manipulation is generated experiential history. Each seed changes actor dispositions, experienced event sequence, topics, valence, intensity, and consequences.

This design controls the age confound identified in the six-lifetime founder characterization. A clone is not older merely because its history happened in a different order.

## Generated histories

The default life contains 200 generated social events spread across 100,000 ticks. Morgan, Sarah, Alex, and Jamie each appear 50 times. The generator creates reproducible actor profiles and selects among supportive, conflict, repair, challenge, discovery, and ordinary experiences. Each event has an explicit external consequence that is delivered through DUCK's existing outcome-learning interface.

The generator is laboratory code. It does not change the organism and it does not own character state.

Each `history.json` is written before the life is completed and has a stable SHA-256 fingerprint.

## Acceleration

The runner still executes every DUCK heartbeat. It does not numerically skip organism time. To make 100,000-tick runs practical, idle heartbeats call the unchanged DUCK organism directly rather than writing one host journal row for every tick. The complete DUCK persistent state is checkpointed periodically and after every generated life event.

Inner cognition remains enabled, matching normal non-LLM DUCK execution. No LLM is used in the life generator or the organism.

## Terminal battery

At tick 100,000 the runner saves the mature state. It then copies that state and runs the existing `configs/suites/training.json` battery against the copy. The mature endpoint remains unchanged by measurement.

The terminal report preserves the full transcript, deterministic phenotype probes, exact action signature, and exact response signature for every clone.

Across all 20 clones the summary reports the number of unique terminal action and response signatures and pairwise positional divergence across the common battery.

## Interpretation

Terminal divergence under matched code, initial identity, age, interaction density, actor set, and battery is evidence of experience-conditioned phenotypic divergence.

It is not by itself evidence of human-like individuality, cognitive improvement, consciousness, or an artificiality benchmark victory. A null result is also informative: it would show that these histories and this duration are insufficient to produce behaviorally persistent differentiation in the current architecture.

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
```

Do not commit the large working state directories automatically. After the full experiment succeeds, preserve the compact manifests, histories, terminal transcripts, metrics, endpoint summaries, and a characterization summary under a versioned `results/` path, following the founder-baseline preservation pattern.
