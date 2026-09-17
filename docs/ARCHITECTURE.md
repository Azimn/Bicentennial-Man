# Architecture

The v0.1 system has four deliberately separated layers.

The **subject** is the developing organism. It has only its genome, transient state, traces acquired through experience, and observable consequences. It has no evaluator access.

The **developmental ecology** generates social situations and converts observable actions into consequences. Partners do not say which mechanism is missing. Their behavior changes in response to interaction quality.

The **evolution loop** reproduces and mutates developmental genomes. Selection is based on ecology-visible social viability. Mutation is constrained and fully lineage-tracked.

The **held-out evaluator** measures artificiality in unfamiliar situations. It is not part of the subject's world and is not a reward channel.

## Developmental genome

The initial genome is intentionally substrate-neutral. Loci govern trace capacity, actor partitioning, carryover, thread persistence, transition inertia, action reuse, disclosure threshold, routing sparsity, agreement bias, verbosity, plasticity, and exploration.

These are not claims that such variables correspond one-to-one with human cognitive faculties. They define a tractable search space in which functionally useful organization can be discovered and later ablated.

## Staged self-modification

Stage 1, implemented here, changes bounded genome values only. Stage 2 should permit structural mutations over generic storage, routing, policy, and state slots. Stage 3 may allow constrained generated code inside a sandbox, but only after lineage reconstruction and causal attribution are strong enough to survive larger changes.

## LLM boundary

A local Ollama model may optionally render structured actions into natural language for qualitative social transcripts. In v0.1 it must not choose the structured action, calculate consequences, score fitness, mutate the genome, or see hidden evaluation. This keeps language quality from becoming the experiment itself.
