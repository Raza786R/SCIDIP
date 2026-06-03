# RUN B — Main Pipeline Results
## Status: AWAITING EXECUTION

This folder will contain the outputs of the fixed main screening pipeline.
**Do NOT add files here manually.** They will be copied here after the pipeline run completes.

### What will be here after Run B executes:
- `top_50_candidates.csv`      — All qualifying candidates (SF ≥ 1.50)
- `top1_manufacturing_recipe.csv` — 11-layer recipe for #1 candidate
- `ml_predictions.csv`         — All 10,626 compositions with predicted properties
- `composition_model.pkl`      — Trained bulk modulus model snapshot
- `run_B_report.md`            — Top candidate summary + comparison to Run A

### Search space:
- Elements: Mo, Nb, Ta, W, Cr (5-element grid)
- Compositions: 10,626 at 5% increments
- Ceramics tested: ZrO2-HfO2, GZO, LZO, SrZrO3
- Gradient exponents: 0.5, 1.0, 2.0, 4.0
- SF threshold: ≥ 1.50

### Scripts that produce this output (run in order):
1. `python scripts/train_composition_ml.py`
2. `python scripts/evaluate_candidates.py`
3. `python scripts/generate_manufacturing_recipe.py`

### Independence:
- Does NOT depend on Run A ✅
- Does NOT depend on Run C ✅
- Shares fixed codebase with Run C (bug fixes already applied) ✅
