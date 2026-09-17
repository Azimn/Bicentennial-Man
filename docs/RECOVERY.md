# Long-Run Recovery and Git Backup

Long experiments should be resumable independently of the raw JSONL trace. The CLI therefore writes a compact atomic checkpoint containing the next population, exact Python PRNG state, best-so-far individual, completed generation count, seed, and search settings.

A normal run checkpoints every generation by default:

```powershell
bicentennial --seed 7 --generations 100 --population 64 --episodes 2000 --checkpoint checkpoints\latest.json --output runs\seed7.jsonl
```

To continue the exact search from that checkpoint and extend the target from 100 to 200 total generations:

```powershell
bicentennial --seed 7 --generations 200 --population 64 --episodes 2000 --resume checkpoints\latest.json --checkpoint checkpoints\latest.json --output runs\seed7.jsonl
```

Resume requires the same seed and evolutionary settings. The target generation count may increase. A deterministic unit test compares an interrupted-and-resumed run with an uninterrupted run.

`checkpoints/*.json` is intentionally not gitignored. After a meaningful chunk, commit and push the compact checkpoint so a laptop failure does not erase the evolutionary state. On Windows, `scripts\push_checkpoint.ps1` stages checkpoint/config JSON, commits it, and pushes the current branch. It deliberately does not add the potentially large raw `runs/` directory.

For long experiments managed through OpenCode, prefer chunked targets. Run to a target generation, invoke the checkpoint push script, inspect the compact result, then resume to the next target. This creates durable recovery points and gives the reviewer natural intervals for detecting collapse or Goodharting.
