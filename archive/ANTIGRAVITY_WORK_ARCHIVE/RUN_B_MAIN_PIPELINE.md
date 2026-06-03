# RUN B — Fixed Main Pipeline → Mo-Nb-Ta-W-Cr Family
## Architecture & Pipeline Document
**Status: REQUIRES Phase 1 (bug fixes) first, then execution**
**Search Space: Mo-Nb-Ta-W-Cr (5-element, 10,626 grid compositions)**
**Independence: 100% — Does NOT depend on Run A or Run C results**

---

## What This Run Is

RUN B runs the **standard screening pipeline** (`evaluate_candidates.py`) after all bugs are fixed.
It searches the **5-element Mo-Nb-Ta-W-Cr compositional grid** (10,626 compositions at 5% increments).

This will produce candidates from a **completely different compositional family** than the Bohrium candidate
(which has Mo=0, Nb=0 — entirely outside this grid).

**This is the first time this pipeline will ever produce valid output.**

---

## Search Space

```
Elements: Mo, Nb, Ta, W, Cr  (5 elements only)
Grid:     5% increments, all fractions summing to 1.0
Size:     10,626 compositions (unary through quinary)
Ceramics: ZrO2-HfO2, GZO, LZO, SrZrO3  (4 options)
Exponents: 0.5, 1.0, 2.0, 4.0  (4 gradient options)
FEA calls: up to 62,016 per full run
Output:   Top 50 candidates ranked by lowest interface stress, SF ≥ 1.50
```

---

## Why This is Different from Run C

| | Run B | Run C |
|--|-------|-------|
| Search method | Grid enumeration (all 10,626 in grid) | Differential Evolution (stochastic optimiser) |
| Search space | 5 elements: Mo-Nb-Ta-W-Cr | 9 elements: Mo-Nb-Ta-W-Cr-V-Ti-Zr-Hf |
| Can find Bohrium composition? | ❌ NO (Mo=0, Nb=0 not in grid) | ✅ YES (full 9-element space) |
| ML models | Trained from data files, predictions written to CSV | Trained in-memory on-the-fly |
| Output format | CSV files (top_50_candidates.csv) | stdout (must capture) |

---

## Phase 1 — Bug Fixes (SHARED with Run C — Done ONCE in scripts/)

**All fixes applied to `Saffron-Aero/scripts/`. This is the shared foundation.**
**Run B cannot start until ALL Phase 1 fixes marked [RUN B NEEDS] are done.**

### Critical fixes for Run B specifically:

| Task | File | Change | Run B Needs |
|------|------|--------|-------------|
| TASK-1 | `run_1d_fea.py:116` | `np.trapz` → `np.trapezoid` | ✅ CRITICAL |
| TASK-4 | `evaluate_candidates.py:14–17` | Replace 5-element AND filter with count-based 9-element filter | ✅ CRITICAL |
| TASK-5 | `evaluate_candidates.py:~42` | Add `if pd.isna(hea_E_Pa) or hea_E_Pa <= 0: continue` | ✅ CRITICAL |
| TASK-5B | `evaluate_candidates.py` | `SF_MIN = 1.45` → `SF_MIN = 1.50` | ✅ CRITICAL |
| TASK-6 | `train_composition_ml.py` | Add V(8.4), Ti(8.6), Zr(5.8), Hf(5.9) to `estimate_cte()` | ✅ IMPORTANT |
| TASK-7 | `train_composition_ml.py` | Add V(31), Ti(22), Zr(23), Hf(23) to `estimate_thermal_conductivity()` | ✅ IMPORTANT |
| TASK-8 | `train_composition_ml.py` | Fix MODEL_OUTPUT path; add `pickle.dump()` | ✅ IMPORTANT |
| TASK-2 | `generate_compositions.py:13` | Fix output path → `data/all_compositions-generated.csv` | ✅ NEEDED |
| TASK-3 | `empirical_filter.py:12–13` | Fix input/output paths to `data/` | ✅ NEEDED |
| TASK-14 | `generate_compositions.py` | Add 35% upper bound to `is_true_hea` flag | ✅ NEEDED |
| TASK-12 | `generate_manufacturing_recipe.py` | Add `if len(df) == 0:` guard | ✅ NEEDED |
| TASK-10 | `differential_evolution_search.py` | Add density + sigma-former constraints | ⬜ Optional |
| TASK-11 | `stage2_gradient_optimization.py` | Add `__main__` guard | ⬜ Optional |
| TASK-9 | `calphad_validation.py` | Fix composition dict (TCHEA4.TDB still needed) | ⬜ Optional |
| TASK-13 | `active_learning_bo.py` | Fix np.vstack + return type | ⬜ Optional |

### Order to apply fixes (dependency-ordered):
```
TASK-1 first (unblocks FEA → unblocks everything that calls run_1d_fea)
TASK-6, TASK-7 together (both in train_composition_ml.py, thermal property estimators)
TASK-8 (also in train_composition_ml.py — do in same session as TASK-6/7)
TASK-4, TASK-5, TASK-5B together (all in evaluate_candidates.py)
TASK-2 (generate_compositions.py)
TASK-14 (also in generate_compositions.py — do in same session as TASK-2)
TASK-3 (empirical_filter.py)
TASK-12 (generate_manufacturing_recipe.py)
```

---

## Phase 2 — Run B Pipeline Execution

**Run all commands from `Saffron-Aero/` as working directory.**
**Do NOT run until ALL Phase 1 fixes are complete and verified.**

### Step B1 — Data Fetch
```bash
python scripts/fetch_datasets.py
```
**Reads:** Materials Project API, OQMD, JARVIS (will return 0 rows), AFLOW
**Writes:** `raw_materials_project.csv`, `raw_oqmd.csv`, `raw_jarvis.csv`, `combined_raw_data.csv`
**Expected:** ~91 MP rows, 0 JARVIS rows
**Verify:** `python -c "import pandas as pd; print(len(pd.read_csv('combined_raw_data.csv')), 'rows')"`

### Step B2 — Property Calculation
```bash
python scripts/calculate_properties.py
```
**Reads:** `combined_raw_data.csv`
**Writes:** `processed_candidate_properties.csv`
**Expected:** 54 rows (only rows with bulk_modulus survive)
**Verify:** `python -c "import pandas as pd; print(len(pd.read_csv('processed_candidate_properties.csv')), 'rows')"`

### Step B3 — Composition Grid Generation
```bash
python scripts/generate_compositions.py
```
**Reads:** Nothing (generates from scratch)
**Writes:** `data/all_compositions-generated.csv` (AFTER TASK-2 fix)
**Expected:** 10,626 rows, Mo-Nb-Ta-W-Cr at 5% increments
**Verify:** `python -c "import pandas as pd; df=pd.read_csv('data/all_compositions-generated.csv'); print(len(df), 'rows')"`
**Expected output:** `10626 rows`

### Step B4 — Empirical Filter
```bash
python scripts/empirical_filter.py
```
**Reads:** `data/all_compositions-generated.csv`
**Writes:** `data/stable_compositions.csv`
**Expected:** 10,626 rows (all pass — known science limitation, filter is non-discriminating)
**Verify:** `python -c "import pandas as pd; df=pd.read_csv('data/stable_compositions.csv'); print(len(df), 'rows — all filters passed')"`

### Step B5 — ML Training & Property Prediction
```bash
python scripts/train_composition_ml.py
```
**Reads:** `data/processed_candidate_properties.csv`, `data/stable_compositions.csv`, `data/EXP-MPEA_dataset.csv`
**Writes:** `models/ml_predictions.csv`, `models/composition_model.pkl`
**Expected:** 10,626 rows in predictions; pkl file saved (after TASK-8 fix)
**Verify:**
```bash
python -c "import pandas as pd; df=pd.read_csv('models/ml_predictions.csv'); print(len(df), 'predictions,', (df['predicted_bulk_modulus']>0).sum(), 'with positive bulk modulus')"
python -c "import os; print('pkl exists:', os.path.exists('models/composition_model.pkl'))"
```

### Step B6 — FEA Scoring (THE KEY STEP)
```bash
python scripts/evaluate_candidates.py
```
**Reads:** `models/ml_predictions.csv`
**Writes:** `models/top_50_candidates.csv`
**Expected:** >0 rows with SF ≥ 1.50 (first time this has ever worked!)
**Verify:**
```bash
python -c "import pandas as pd; df=pd.read_csv('models/top_50_candidates.csv'); print(len(df), 'candidates found'); print(df[['formula','ceramic_type','safety_factor']].head(5))"
```

### Step B7 — Manufacturing Recipe
```bash
python scripts/generate_manufacturing_recipe.py
```
**Reads:** `models/top_50_candidates.csv`
**Writes:** `models/top1_manufacturing_recipe.csv`
**Expected:** 11-layer recipe for the #1 ranked candidate (no element > 35%)
**Verify:** `python -c "import pandas as pd; print(pd.read_csv('models/top1_manufacturing_recipe.csv'))"`

---

## Phase 3 — Isolate Run B Outputs

After pipeline completes, copy all outputs to the isolated Run B folder:

```bash
# Create Run B output folder
mkdir -p runs\RUN_B_MAIN_PIPELINE

# Copy all outputs
copy models\top_50_candidates.csv runs\RUN_B_MAIN_PIPELINE\
copy models\top1_manufacturing_recipe.csv runs\RUN_B_MAIN_PIPELINE\
copy models\ml_predictions.csv runs\RUN_B_MAIN_PIPELINE\
copy models\composition_model.pkl runs\RUN_B_MAIN_PIPELINE\

# Take a snapshot of data files used
copy data\all_compositions-generated.csv runs\RUN_B_MAIN_PIPELINE\
copy data\stable_compositions.csv runs\RUN_B_MAIN_PIPELINE\
copy data\processed_candidate_properties.csv runs\RUN_B_MAIN_PIPELINE\
```

---

## Output Folder Structure

```
Saffron-Aero/
└── runs/
    └── RUN_B_MAIN_PIPELINE/
        ├── top_50_candidates.csv        ← ALL qualifying candidates (SF ≥ 1.50)
        ├── top1_manufacturing_recipe.csv ← 11-layer recipe for #1 candidate
        ├── ml_predictions.csv           ← All 10,626 compositions with predicted properties
        ├── composition_model.pkl        ← The trained bulk modulus model
        ├── all_compositions-generated.csv (snapshot)
        ├── stable_compositions.csv     (snapshot)
        ├── processed_candidate_properties.csv (snapshot)
        └── run_B_report.md             ← Write after run: top candidate, SF, properties
```

---

## What run_B_report.md Should Contain

After the run completes, extract and document:
```markdown
# Run B Report — Main Pipeline Results

## Top Candidate
Formula: [from top_50_candidates.csv row 1]
Ceramic: [ceramic_type]
Gradient exponent: [gradient_exponent]
Safety Factor: [safety_factor]
Interface Stress: [interface_stress_MPa] MPa
Bulk Modulus: [bulk_modulus_GPa] GPa
Yield Strength: [yield_strength_MPa] MPa

## How Many Candidates Passed SF ≥ 1.50?
[count from top_50_candidates.csv]

## Comparison to Run A (Bohrium Original)
[Compare SF, composition family, ceramic type]
```

---

## Bohrium Submission Input (Job 2)

Extract from `top_50_candidates.csv` row 1:
```
Alloy:    [formula from top of CSV]
Ceramic:  [ceramic_type]
Gradient: Power-law n=[gradient_exponent], thickness=5.0mm
Test:     10,000 thermal cycles 300K–1400K, 15,000 RPM, 2.5 MPa
Target:   SF ≥ 1.50
Source:   Fixed main pipeline (Run B) — Mo-Nb-Ta-W-Cr family
```

---

## Dependencies

- **Depends on Phase 1 (bug fixes):** ✅ YES — all 10 critical/important tasks must be done first
- **Depends on Run A:** ❌ NO
- **Depends on Run C:** ❌ NO
- **Shares codebase with Run C:** ✅ YES (same fixed scripts — fixes done once)
- **Output folder is isolated:** ✅ YES (`runs/RUN_B_MAIN_PIPELINE/`)
- **Results do NOT overwrite Run C:** ✅ YES — different search algorithm, different output

---

## Key Expectation: What Will Run B Find?

Run B will find Mo-Nb-Ta-W-Cr compositions. The best candidates will likely be:
- **Ternary or quaternary** compositions (not equimolar 5-element) — the optimizer will naturally
  favour compositions where thermally lighter elements (lower CTE, better mismatch) dominate
- **LZO ceramic** most likely — it has the closest CTE (9.1 µm/mK) to typical RHEA CTEs
- **Gradient exponent n=1.0 or n=2.0** — empirically optimal for most systems

**These will be completely new candidates never before validated.**
