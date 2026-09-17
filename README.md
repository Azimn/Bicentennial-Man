# Bicentennial Man

**A phenotype-first laboratory for evolving more lifelike persistent artificial characters.**

The original developmental-genome experiment is preserved on `original-approach`. The active project treats Bicentennial Man as the laboratory and existing persistent organisms as experimental subjects.

MicroPsiDUCK v0.10 is the first founder organism. The current question is:

> Given a persistent artificial organism, controlled social lifetimes, phenotype evaluation, and carefully bounded modification, what changes produce behavior that remains less detectably artificial across histories and unfamiliar situations?

## Current empirical sequence

```text
DUCK founder phenotype characterization
            |
            v
Accelerated Life Runner
experience-only divergence test
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
ablation
```

Do not interpret a higher training score as cognitive improvement until the change survives fixed-boundary evaluation and held-out transfer.

## 1. Founder characterization

The exact successful six-lifetime founder characterization is permanently preserved under `results/micropsiduck-v0.10/30a11ea8308ebd0fc89a06bb994ab0e23bd02886/`.

Founder characterization uses multiple fresh persistent lifetimes rather than one benchmark run. Every lifetime gets a new DUCK state root and a reproducible scenario-order permutation. The lab preserves complete transcripts, deterministic probes, optional judge metrics, exact scenario order, and exact DUCK Git provenance.

## 2. Accelerated Life Runner

The next experiment asks whether accumulated experience alone creates persistent behavioral individuality in unchanged DUCK.

The first target is 20 identical founder clones, 20 reproducibly generated histories, 100,000 organism ticks per clone, no evolution, and one identical terminal phenotype battery.

All clones use MicroPsiDUCK v0.10 commit `30a11ea8308ebd0fc89a06bb994ab0e23bd02886`. They begin from the same founder identity, receive the same number of social events at the same absolute ages with balanced exposure to Morgan, Sarah, Alex, and Jamie, and end life history at exactly tick 100,000. Only generated experiential history is intended to differ.

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

The runner preserves each generated history, mature endpoint state, endpoint summary, terminal-state copy, terminal transcript, and terminal metrics. It reports unique terminal action and response signatures plus pairwise divergence across clones.

See `docs/ACCELERATED_LIFE_RUNNER.md`.

## 3. Surface-Mutable Control

The existing OpenEvolve wrapper experiment is formally the **Surface-Mutable Control**. DUCK stays unchanged. Candidate code may rewrite input, rewrite output, manipulate timing, or maintain wrapper-owned state. These channels are instrumented and any gains primarily caused by them are benchmark exploitation, not organism improvement.

Generated Surface-Mutable candidates are isolated in Docker. They receive only their candidate program, their assigned surface-state directory, and explicit prepare/postprocess payloads. They do not mount DUCK, Bicentennial Man, evaluators, scenario files, sealed suites, or other candidate state.

See `docs/SURFACE_MUTABLE_CONTROL.md` and `docs/OPENEvolve.md`.

## 4. Mechanism-Mutable DUCK

The Mechanism-Mutable condition is specified but disabled. Its mutable path list is intentionally empty until the Surface-Mutable Control has been characterized and exploit analysis is complete. When activated, the lab owns the input boundary, fixed renderer, final response boundary, scenarios, evaluators, and sealed transfer suite.

See `docs/MECHANISM_MUTABLE.md`.

## Local setup

```powershell
git clone https://github.com/Azimn/Bicentennial-Man.git
git clone --branch motivated-cognition-v0.10 https://github.com/Azimn/DUCK.git
cd Bicentennial-Man
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m unittest discover -s tests -v
```

The current six scenarios remain deliberately small. Do not grow them into a larger fixed script benchmark. After the early control phases work, the next scenario work is parameterization into behavioral families.
