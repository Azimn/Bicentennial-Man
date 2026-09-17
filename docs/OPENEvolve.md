# OpenEvolve Integration

OpenEvolve is used as the first local code-evolution engine rather than rebuilding an archive, island model, diff mutation system, and checkpoint machinery inside Bicentennial Man.

The first target is deliberately small: `evolution/initial_program.py` is an organism-side layer around DUCK. OpenEvolve can mutate only the marked evolve block. This proves the phenotype optimization loop while leaving the lab fixed.

Install OpenEvolve separately:

```powershell
python -m pip install openevolve
$env:OPENAI_API_KEY="ollama"
$env:DUCK_REPO="..\DUCK"
$env:BICENTENNIAL_JUDGE_MODEL="qwen3:8b"
```

Then run:

```powershell
openevolve-run.py evolution\initial_program.py evolution\evaluator.py --config configs\openevolve_ollama.yaml --iterations 100 --output runs\openevolve
```

Both candidate generation and phenotype judging can use Ollama through its OpenAI-compatible endpoint. For stronger experiments, use different models for mutation and judging, or reserve an independent judge for transfer evaluation.

This first integration does not yet evolve arbitrary files inside DUCK. Multi-file organism evolution should be added only after the end-to-end loop is reproducible, because lineage, rollback, evaluator isolation, and candidate workspace boundaries must remain inspectable.
