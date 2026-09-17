# DUCK v0.10 Integration

Bicentennial Man uses DUCK through its public persistent host instead of copying DUCK into this repository.

The adapter imports `PersistentDuckHost` from DUCK v0.10 and uses its public `interact()` and `heartbeat()` operations. DUCK therefore remains the continuing organism and retains its own persistent state.

## Local layout

A convenient Windows layout is:

```text
research/
  Bicentennial-Man/
  DUCK/
```

Check out DUCK's `motivated-cognition-v0.10` branch and install it in its own environment or leave the source checkout available to the adapter.

Run the phenotype lab from Bicentennial Man:

```powershell
bicentennial-lab --duck-repo ..\DUCK --suite configs\suites\training.json --state-root runs\duck-v010-state --transcript-out runs\duck-v010-transcript.json
```

To use DUCK's optional language model path, configure `DUCK_LLM_ENDPOINT`, `DUCK_LLM_MODEL`, and `DUCK_LLM_API_KEY`, then add `--duck-llm`.

To score the transcript with a local judge:

```powershell
bicentennial-lab --duck-repo ..\DUCK --suite configs\suites\training.json --state-root runs\duck-v010-state --transcript-out runs\duck-v010-transcript.json --judge-model qwen3:8b
```

The default judge endpoint is Ollama's OpenAI-compatible API at `http://localhost:11434/v1`.
