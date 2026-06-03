# RUN C — Constrained DE Results
## Status: COMPLETE ✅

This folder contains the outputs of the fixed constrained Differential Evolution optimizer,
along with the generated FGM manufacturing recipe and projected phase analysis.

### What is here:
- `stdout_capture.txt`              — Full DE optimizer output (all iterations + winning composition)
- `top_candidate.md`                — Top composition extracted from stdout
- `calphad_validation_curve.png`    — Phase stability validation plot
- `bohrium_submission_input.md`     — What to feed Bohrium for Job 3
- `run_C_report.md`                 — Comparison to Run A (Bohrium original)

### Search space:
- Elements: Mo, Nb, Ta, W, Cr, V, Ti, Zr, Hf (ALL 9 elements)
- Method: Differential Evolution (maxiter=200, popsize=20)
- Engineering constraints: HEA def, sigma-former cap, V oxidation, Cr minimum, density
- SF threshold: maximize (take best result, typically > 1.50)

### Script that produces this output:
1. `python scripts/stage1_optimizer_with_constraints.py > runs\RUN_C_CONSTRAINED_DE\stdout_capture.txt 2>&1`

### Independence:
- Does NOT depend on Run A ✅
- Does NOT depend on Run B ✅
- Trains ML models in-memory (does not read ml_predictions.csv from Run B) ✅
- Shares fixed codebase with Run B (bug fixes already applied) ✅
