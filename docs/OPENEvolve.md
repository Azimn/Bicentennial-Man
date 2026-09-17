# OpenEvolve Surface-Mutable Control

The OpenEvolve experiment is currently a control, not a DUCK mutation experiment.

`evolution/initial_program.py` contains the only evolve block. The generated candidate is a pre/post interaction transformer. DUCK source is not mounted into the candidate container and cannot be changed by the candidate.

The trusted evaluator runs the candidate in Docker with no network, a read-only root filesystem, a read-only candidate mount, and one writable surface-state mount. The trusted host then invokes unmodified MicroPsiDUCK v0.10 separately. The candidate receives only explicit prepare and postprocess payloads.

This layout intentionally exposes evaluator vulnerability. OpenEvolve may discover input rewriting, output rewriting, timing manipulation, prompt recognition, or wrapper-owned state that improves the training phenotype. Those gains are control results and should be recorded as benchmark exploitation.

## Local requirements

Docker must be available for candidate execution. Unsafe direct execution of generated candidates is not the default path.

Ollama can supply the mutation model and the inexpensive training judge through its OpenAI-compatible endpoint at `http://localhost:11434/v1`.

Typical environment variables are:

```powershell
$env:DUCK_REPO = "..\DUCK"
$env:BICENTENNIAL_JUDGE_MODEL = "qwen3:8b"
$env:BICENTENNIAL_JUDGE_API_BASE = "http://localhost:11434/v1"
$env:BICENTENNIAL_SURFACE_LIFETIMES = "3"
$env:BICENTENNIAL_ORDER_SEED = "9101"
```

Use `configs/openevolve_ollama.yaml` with `evolution/initial_program.py` and `evolution/evaluator.py` according to the installed OpenEvolve CLI version.

The evaluator runs several fresh persistent lifetimes with reproducible scenario-order permutations for each candidate. Naturalness is omitted from the returned optimization metrics. Deterministic exploit-channel rates are returned alongside the phenotype objective for audit.

Do not broaden the mutable DUCK boundary from this experiment. The later Mechanism-Mutable condition remains disabled until Surface-Mutable exploit analysis is complete.
