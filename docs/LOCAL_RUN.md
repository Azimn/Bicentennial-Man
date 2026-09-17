# Local Run Guide

Python 3.11 or newer is sufficient for the mechanics-only baseline. The core experiment has no third-party runtime dependencies.

Create a virtual environment, activate it, install the repository in editable mode, and run the tests:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m unittest discover -s tests -v
```

Run a small experiment:

```powershell
bicentennial --generations 25 --population 24 --episodes 200 --output runs\baseline-seed7.jsonl --checkpoint checkpoints\latest.json
```

For a longer local run, first benchmark a smaller run and then raise generations, population, and episodes. Raw JSONL run outputs are gitignored by default because large trace files should not bloat the repository. Commit compact summaries, configs, code version, seeds, and selected checkpoints needed to reconstruct a result.

## Ollama

Ollama is optional. `OllamaRenderer` talks to the local default server at `http://127.0.0.1:11434`. Its role is limited to rendering a structured action as an utterance. Do not route hidden evaluator data into its prompt.

## OpenCode

Current OpenCode V2 recognizes the committed root `AGENTS.md` as project instructions. Start OpenCode from the repository root. The project also includes a read-only-style `hostile-reviewer` subagent under `.opencode/agents/` for adversarial experiment review. Model/provider selection is deliberately left in your local OpenCode configuration so the repository does not assume a paid provider or overwrite your Ollama setup.

## Recovery

Runs checkpoint atomically and can be resumed exactly. See `docs/RECOVERY.md`. Compact checkpoint JSON is intended for periodic Git backup; raw lineage logs remain ignored to avoid repository bloat.
