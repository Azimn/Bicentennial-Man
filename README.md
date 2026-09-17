# Bicentennial Man

**Experimental evolution of lifelikeness in an artificial social organism.**

> Can an artificial character discover for itself the causal mechanisms required for lifelikeness by experiencing the social consequences of artificial behavior?

The subject begins deliberately primitive. It develops inside a simulated social ecology whose inhabitants react to behavior rather than expose architectural diagnoses. Adaptation occurs through a constrained, lineage-tracked developmental genome. A separate held-out evaluator measures transfer to unfamiliar situations.

The experiment is designed to distinguish social developmental adaptation from direct optimization against an artificiality test. The organism never sees the hidden artificiality score or evaluator rubric. In v0.1, selection uses only consequences available inside its developmental world: trust, comfort, engagement, and observable partner behavior.

## v0.1

The initial scaffold provides a deterministic Python simulation with no required dependencies, a deliberately weak founder, bounded genome mutation, lineage tracking, training and held-out social situations, an evaluator firewall, optional Ollama language rendering, OpenCode project instructions, an adversarial reviewer agent, tests, CI, and research protocol documentation.

The developmental genome uses substrate-neutral capacities and dynamics rather than named human faculties. It can vary trace capacity, person-specific partitioning, state carryover, unfinished-thread persistence, transition inertia, action reuse, disclosure threshold, routing sparsity, agreement, verbosity, plasticity, and exploration.

## Run locally

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m unittest discover -s tests -v
bicentennial --generations 25 --population 24 --episodes 200 --output runs\baseline-seed7.jsonl
```

See `docs/EXPERIMENT_PROTOCOL.md` before interpreting results. See `docs/LOCAL_RUN.md` for OpenCode and Ollama notes.

## Research discipline

A lower held-out artificiality score is evidence of behavioral transfer only. It is not evidence of consciousness, personhood, or human-equivalent cognition. Interesting adaptations should be replicated across seeds, reconstructed through lineage, tested in unfamiliar ecologies, ablated, and subjected to hostile review before being treated as architectural findings.
