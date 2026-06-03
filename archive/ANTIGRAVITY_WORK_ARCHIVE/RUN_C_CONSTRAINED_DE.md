# RUN C — Fixed Constrained DE → Ta-W-Cr-V-Ti-Hf Family
## Architecture & Pipeline Document
**Status: REQUIRES Phase 1 (bug fixes) first, then execution**
**Search Space: Full 9-element space (Mo, Nb, Ta, W, Cr, V, Ti, Zr, Hf)**
**Independence: 100% — Does NOT depend on Run A or Run B results**

---

## What This Run Is

RUN C re-runs `stage1_optimizer_with_constraints.py` with all bugs fixed.
This is the **same script that found the original Bohrium candidate**, but now:
1. The np.trapz crash is fixed (TASK-1) — so it can actually run
2. The ML models are trained with corrected CTE and k estimators
3. The physics in the FEA is more honest

**Expected outcome:** Similar Ta-W-Cr-V-Ti-Hf family BUT with:
- Slightly adjusted element fractions (corrected physics landscape)
- Slightly more accurate SF prediction (corrected thermal estimators)
- A corroborating or potentially improved result vs Run A

---

## Search Space

```
Elements:    Mo, Nb, Ta, W, Cr, V, Ti, Zr, Hf  (ALL 9 elements)
Method:      Differential Evolution (stochastic global optimiser)
Strategy:    'best1bin'
Iterations:  maxiter=200, popsize=20  (thorough — 4x more than unconstrained DE)
Objective:   Minimise -safety_factor subject to engineering constraints
Output:      stdout only (no CSV written — must capture)
```

### Engineering Constraints Built Into the Optimizer:
```
≥ 5 elements ≥ 5%:          penalty 1000.0 if violated  (HEA definition)
W + Cr + Mo sigma formers:  penalty +5.0 if > 50%       (sigma phase risk)
                            penalty +2.5 if > 40%
Vanadium (oxidation risk):  penalty +5.0 if V > 20%
                            penalty +2.0 if V > 15%
Chromium minimum:           penalty +5.0 if Cr < 15%    (oxidation protection)
Density:                    penalty +2.0 if > 11.0 g/cm³
```

---

## Why This is Different from Run B

| | Run B | Run C |
|--|-------|-------|
| Search method | Grid enumeration (deterministic, exhaustive in grid) | Differential Evolution (stochastic, adaptive) |
| Search space | 5-element Mo-Nb-Ta-W-Cr | 9-element full space |
| Can find Bohrium composition | ❌ NO | ✅ YES |
| Can find V, Ti, Zr, Hf compositions | ❌ NO | ✅ YES |
| Output | CSV files | stdout (must capture to file) |
| ML models | Written from data pipeline | Trained in-memory on-the-fly |
| Runs independently of main pipeline | NO (needs ml_predictions.csv) | ✅ YES (fully self-contained) |

---

## Phase 1 — Bug Fixes (SHARED with Run B — Done ONCE in scripts/)

**Important note about Run C specifically:**

`stage1_optimizer_with_constraints.py` has its OWN `_get_cte()` and `_get_k()` functions
that ALREADY use the correct 9-element dict. So TASK-6 and TASK-7 (which fix
`estimate_cte()` and `estimate_thermal_conductivity()` in `train_composition_ml.py`)
do NOT directly affect the CTE/k used inside Run C's objective function.

However, TASK-6 and TASK-7 affect the **ML training data quality** indirectly —
and since Run C trains its own ML models in-memory using the same `load_and_prepare_base_data()`
from `train_composition_ml.py`, the bulk modulus model benefits from consistent fixes.

### Fixes required for Run C:

| Task | File | Change | Run C Needs |
|------|------|--------|-------------|
| TASK-1 | `run_1d_fea.py:116` | `np.trapz` → `np.trapezoid` | ✅ CRITICAL — Run C crashes without this |
| TASK-6 | `train_composition_ml.py` | Fix `estimate_cte()` | ⬜ Indirect benefit (ML training consistency) |
| TASK-7 | `train_composition_ml.py` | Fix `estimate_thermal_cond()` | ⬜ Indirect benefit |
| TASK-8 | `train_composition_ml.py` | Fix pkl path + add pickle.dump | ⬜ No direct effect (trains in-memory) |
| TASK-10 | `differential_evolution_search.py` | Add density + sigma constraints | ⬜ Different script — doesn't affect Run C |
| All other tasks | Various | Various | ⬜ No direct effect on Run C |

**Minimum for Run C to work: TASK-1 only.**
**Recommended: All Phase 1 fixes (already done for Run B anyway — shared codebase).**

---

## Important: How Run C Trains Its ML Models

```
stage1_optimizer_with_constraints.py calls:
    ├── load_and_prepare_base_data()     from train_composition_ml.py
    │   └── reads: data/processed_candidate_properties.csv
    │   └── reads: data/EXP-MPEA_dataset.csv
    │   └── trains: RandomForestRegressor (bulk modulus) — in memory
    │
    └── load_experimental_data()         from train_composition_ml.py
        └── reads: data/EXP-MPEA_dataset.csv
        └── trains: GradientBoostingRegressor (yield strength) — in memory

CTE and k come from INTERNAL functions _get_cte() and _get_k()
(defined inside stage1_optimizer_with_constraints.py itself — already correct 9-element)

No ml_predictions.csv is read. No composition_model.pkl is used.
Run C is self-contained.
```

---

## Phase 2 — Run C Pipeline Execution

**Run from `Saffron-Aero/` as working directory.**
**Requires Phase 1 (TASK-1 minimum) to be complete.**

### Step C1 — Prepare Output Folder
```bash
mkdir -p runs\RUN_C_CONSTRAINED_DE
```

### Step C2 — Run Constrained DE Optimizer (Capture Full Output)
```bash
python scripts/stage1_optimizer_with_constraints.py > runs\RUN_C_CONSTRAINED_DE\stdout_capture.txt 2>&1
```

**What happens during this run:**
1. Loads training data from `data/processed_candidate_properties.csv`
2. Trains RF (bulk modulus) and GB (yield strength) models in-memory
3. Runs Differential Evolution over 9-element space with maxiter=200, popsize=20
4. Each iteration: softmax → fractions → constraint check → ML predict → FEA → SF
5. Converges to the composition that maximises SF under all constraints
6. Prints the winning composition to stdout

**Expected runtime:** 5–20 minutes (200 iterations × 20 population × 16 FEA calls each)

**Verify the run completed:**
```bash
# Check that the file was written and is non-empty
python -c "import os; size=os.path.getsize('runs/RUN_C_CONSTRAINED_DE/stdout_capture.txt'); print(f'Output file: {size} bytes')"

# Check the last few lines for the result
type runs\RUN_C_CONSTRAINED_DE\stdout_capture.txt
```

### Step C3 — Run Phase Validation on the Winner
Extract the winning composition from stdout, then run phase validation:

```bash
python phase_wise_analysis/phase1_calphad_phase_validation.py
copy phase_wise_analysis\day1_calphad_validation_curve.png runs\RUN_C_CONSTRAINED_DE\
```

**Note:** This script has the Bohrium composition hardcoded. If Run C finds a DIFFERENT
composition, you will need to manually update the composition dict in
`phase1_calphad_phase_validation.py` and re-run.

### Step C4 — Run Bohrium Reporter Scripts (For Comparison Context)
```bash
python phase_wise_analysis/execute_phases_2_to_5.py > runs\RUN_C_CONSTRAINED_DE\bohrium_context_phases_2_5.txt
python phase_wise_analysis/execute_phases_6_to_11.py > runs\RUN_C_CONSTRAINED_DE\bohrium_context_phases_6_11.txt
```

---

## Phase 3 — Extract and Document the Winner

From `stdout_capture.txt`, extract the best composition line. It will look like:
```
Best composition found: Ta=0.16, W=0.11, Cr=0.28, V=0.14, Ti=0.13, Hf=0.18
Predicted Safety Factor: X.XX
Interface Stress: XX.X MPa
Estimated Density: X.XX g/cm³
```

Write this to `run_C_report.md`:
```markdown
# Run C Report — Constrained DE Results

## Top Candidate
Formula: TaX.XX WX.XX CrX.XX VX.XX TiX.XX HfX.XX [AlX.XX if present]
Predicted Safety Factor (local 1D FEA): X.XX
Interface Stress: XX.X MPa
Estimated Density: X.XX g/cm³
VEC: X.X
ΔHmix: −X.X kJ/mol

## How This Compares to Run A (Bohrium Original)
[Are the fractions similar? Is the SF higher or lower?]
[Is it still in the Ta-W-Cr-V-Ti-Hf family?]

## Changed vs Original Run
[What fractions shifted and why — corrected CTE/k physics]
```

---

## Output Folder Structure

```
Saffron-Aero/
└── runs/
    └── RUN_C_CONSTRAINED_DE/
        ├── stdout_capture.txt              ← Full optimizer output (all iterations)
        ├── run_C_report.md                 ← Top candidate extracted + comparison to Run A
        ├── calphad_validation_curve.png    ← Phase validation plot for winner
        ├── bohrium_context_phases_2_5.txt  ← Prior Bohrium context (for comparison)
        └── bohrium_context_phases_6_11.txt ← Prior Bohrium context (SF=1.66 benchmark)
```

---

## Bohrium Submission Input (Job 3)

Extract from stdout_capture.txt, write to `bohrium_submission_input.md`:
```
Alloy:    [best composition found by DE, with fractions]
Ceramic:  LZO (expected — constrained optimizer prefers LZO due to CTE match)
Gradient: Power-law n=[from stdout], thickness=5.0mm
Test:     10,000 thermal cycles 300K–1400K, 15,000 RPM, 2.5 MPa
Target:   SF ≥ 1.50
Source:   Fixed constrained DE (Run C) — 9-element Ta-W-Cr-V-Ti-Hf family
Compare:  Run A prior result had SF=1.66 (Bohrium validated May 2026)
```

---

## What To Expect From Run C

### Scenario 1 — Most Likely (~70% probability)
DE converges to a **similar but not identical** Ta-W-Cr-V-Ti-Hf composition.
Fractions shift slightly (±3-5% per element). Predicted SF changes by ±0.05–0.10.
This CORROBORATES Run A and gives Safran confidence the result is robust.

### Scenario 2 — Possible (~20% probability)
DE converges to a **different sub-family** (e.g., Ta-Cr-V-Ti-Hf with no W, or
includes some Nb). This would be a genuinely new candidate to validate on Bohrium.

### Scenario 3 — Unlikely (~10% probability)
DE converges to a composition with **higher predicted SF** than Run A (>1.66 local prediction).
This would be the most interesting result — a potentially better candidate than the
current validated one. Send to Bohrium immediately.

---

## Dependencies

- **Depends on Phase 1 (bug fixes):** ✅ YES — TASK-1 minimum (strongly recommend all)
- **Depends on Run A:** ❌ NO
- **Depends on Run B:** ❌ NO (trains ML models in-memory, does NOT read ml_predictions.csv)
- **Shares codebase with Run B:** ✅ YES (same fixed scripts)
- **Output folder is isolated:** ✅ YES (`runs/RUN_C_CONSTRAINED_DE/`)
- **Results do NOT overwrite Run B:** ✅ YES — different search algorithm, different output format

---

## Timing Recommendation

Run C after Run B because:
1. Run B already trains and writes ML models — Run C trains its own in-memory anyway, but
   the data files (processed_candidate_properties.csv, EXP-MPEA_dataset.csv) must exist
2. Phase 1 bug fixes cover both Run B and Run C — do them once before either run

**Suggested execution order:**
```
Phase 1 (fixes) → Run B (pipeline) → Copy B outputs → Run C (DE) → Copy C outputs
```

This takes ~3–4 hours total after all fixes are in place.
