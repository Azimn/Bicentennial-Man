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

## 1. Characterize unaltered DUCK first

Founder characterization uses multiple fresh persistent lifetimes rather than one benchmark run. Every lifetime gets a new DUCK state root and a reproducible scenario-order permutation. The lab preserves complete transcripts, deterministic probes, optional judge metrics, exact scenario order, and the exact DUCK Git provenance.

A dirty DUCK checkout is rejected by default.

```powershell
bicentennial-baseline `
  --duck-repo ..\DUCK `
  --suite configs\suites\training.json `
  --lifetimes 8 `
  --order-seed 7001 `
  --out runs\founder-baseline
```

For milestone characterization, more than one judge can be recorded. On a local Ollama endpoint, for example:

```powershell
bicentennial-baseline `
  --duck-repo ..\DUCK `
  --lifetimes 8 `
  --judge-model qwen3:8b `
  --judge-model gemma3:12b `
  --out runs\founder-baseline-with-judges
```

Naturalness is diagnostic only. The laboratory recomputes the combined phenotype objective from the other dimensions.

## 2. Surface-Mutable Control

The existing OpenEvolve wrapper experiment is formally the **Surface-Mutable Control**. DUCK stays unchanged. Candidate code may rewrite input, rewrite output, manipulate timing, or maintain wrapper-owned state. These channels are instrumented and any gains primarily caused by them are benchmark exploitation, not organism improvement.

Generated Surface-Mutable candidates are isolated in Docker. They receive only their candidate program, their assigned surface-state directory, and explicit prepare/postprocess payloads. They do not mount DUCK, Bicentennial Man, evaluators, scenario files, sealed suites, or other candidate state.

See `docs/SURFACE_MUTABLE_CONTROL.md` and `docs/OPENEvolve.md`.

## 3. Mechanism-Mutable DUCK

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

The current six scenarios remain deliberately small. Do not grow them into a larger fixed script benchmark. After founder characterization and the Surface-Mutable Control are working, the next scenario work is parameterization into behavioral families.

See `docs/EXPERIMENT_SEQUENCE_v0.3.md` for the governing sequence.
