# Bicentennial Man

**A phenotype-first laboratory for evolving more lifelike persistent artificial characters.**

The project has changed direction.

The original v0.1 experiment, in which a deliberately primitive subject evolved a bounded developmental genome from social consequences, is preserved on the `original-approach` branch.

`main` now treats Bicentennial Man as the laboratory rather than the organism.

The current question is:

> Given an existing persistent artificial organism, a social developmental world, phenotype evaluation, and the ability to modify organism-side code, what changes produce behavior that remains less detectably artificial across time and situations?

## Why the pivot

We already have persistent character architectures worth testing. Building another toy organism delays the experiment we actually care about.

The first ancestor is MicroPsiDUCK v0.10 from `Azimn/DUCK`, branch `motivated-cognition-v0.10`. Bicentennial Man supplies the social lifetime, transcript capture, phenotype evaluator, reproducibility rules, and evolution interface.

The default v0.2 condition focuses on end results. Training phenotype metrics are legitimate feedback to the code-evolution system. Separate held-out transfer evaluation remains protected so an improving score is not mistaken for general lifelikeness.

## Current stack

```text
social lifetime + situations
          |
          v
persistent organism
DUCK v0.10 first
          |
          v
observable transcript
          |
          v
phenotype evaluator
          |
          v
OpenEvolve + local Ollama
          |
          v
candidate organism-side change
          |
          +----> another persistent lifetime
```

The current OpenEvolve target is a thin mutable layer around DUCK. This gets the whole local loop running without pretending that a single-file wrapper is the final architecture. Multi-file organism evolution comes after the evaluator and transfer discipline are stable.

## Local setup

A convenient layout is:

```text
research/
  Bicentennial-Man/
  DUCK/
```

```powershell
git clone https://github.com/Azimn/Bicentennial-Man.git
git clone --branch motivated-cognition-v0.10 https://github.com/Azimn/DUCK.git

cd Bicentennial-Man
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m unittest discover -s tests -v
```

Run DUCK through the phenotype lab:

```powershell
bicentennial-lab --duck-repo ..\DUCK --suite configs\suites\training.json --state-root runs\duck-v010-state --transcript-out runs\duck-v010-transcript.json
```

Add local phenotype judging:

```powershell
bicentennial-lab --duck-repo ..\DUCK --suite configs\suites\training.json --state-root runs\duck-v010-state --transcript-out runs\duck-v010-transcript.json --judge-model qwen3:8b
```

OpenEvolve can use Ollama through `http://localhost:11434/v1`. See `docs/OPENEvolve.md`.

## What remains from v0.1

The evaluator firewall, reproducibility discipline, artificiality taxonomy, deterministic fixtures, checkpoint work, and hostile-reviewer mindset remain useful.

The old toy subject, bounded genome, and in-house evolutionary search are now legacy fixtures on `main` and the complete original approach is frozen on `original-approach`.

See `docs/PIVOT_v0.2.md` and `docs/DUCK_INTEGRATION.md`.
