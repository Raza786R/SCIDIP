# ARCHITECTURE.md — HE-MCGA Pipeline Execution Order

**Authority:** Derived entirely from reading actual source files. Every path, import, and data flow is verified against the code.
**Run all commands from the repo root directory** — multiple scripts resolve paths relative to `__file__` and assume the `scripts/`, `data/`, `models/` folder hierarchy.

---

## ⚠️ Pre-Flight: Known Breakages That Block the Pipeline

Before running anything, these issues must be fixed or the pipeline will fail silently or crash:

| # | Bug | Location | Symptom | Fix |
|---|---|---|---|---|
| **B1** | `np.trapz` removed in NumPy 2.0 | `scripts/run_1d_fea.py` line 116 | `AttributeError: module 'numpy' has no attribute 'trapz'` — crashes every script that imports the FEA | Change `np.trapz(sigma_free, x)` → `np.trapezoid(sigma_free, x)` |
| **B2** | `empirical_filter.py` reads from `scripts/` not `data/` | `scripts/empirical_filter.py` line 31 | `FileNotFoundError` on `all_compositions-generated.csv` | Change `INPUT_FILE = Path(__file__).parent / 'all_compositions-generated.csv'` → `Path(__file__).parent.parent / 'data' / 'all_compositions-generated.csv'`; same fix for `OUTPUT_FILE` |
| **B3** | `generate_compositions.py` writes wrong filename to wrong folder | `scripts/generate_compositions.py` line 13 | Writes `scripts/all_compositions.csv` instead of `data/all_compositions-generated.csv` | Change `OUTPUT_FILE = Path(__file__).parent / 'all_compositions.csv'` → `Path(__file__).parent.parent / 'data' / 'all_compositions-generated.csv'` |
| **B4** | `composition_model.pkl` is never saved | `scripts/train_composition_ml.py` | `MODEL_OUTPUT` constant defined at line 37 but `pickle.dump()` is never called anywhere in the file | Add `import pickle; pickle.dump((theoretical_model, theoretical_scaler), open(MODEL_OUTPUT, 'wb'))` after `train_model()` completes |
| **B5** | `evaluate_candidates.py` does not guard against negative bulk modulus | `scripts/evaluate_candidates.py` line 40 | 1,482 of 3,876 true HEAs have `predicted_bulk_modulus ≤ 0` (unphysical ML output); these produce a negative `hea_E_Pa` which enters the FEA solver unchecked | Add guard: `if hea_E_Pa <= 0 or pd.isna(hea_E_Pa): continue` before calling the FEA |
| **B6** | `calphad_validation.py` hardcoded to wrong composition | `scripts/calphad_validation.py` lines 35–40 | Validates `Mo0.05Nb0.80Ta0.05W0.05Cr0.05` (the stale, invalid candidate) not the Bohrium-validated `Ta–W–Cr–V–Ti–Hf` composition | Update hardcoded composition dict to `{'Ta': 0.16, 'W': 0.11, 'Cr': 0.27, 'V': 0.15, 'Ti': 0.13, 'Hf': 0.18}` |

---

## Part 1 — Main Pipeline (Steps 1–7)

These steps form the primary linear data flow from raw database queries to a ranked candidate list and manufacturing recipe.

---

### Step 1 — Data Acquisition

**Script:** `scripts/fetch_datasets.py`
**Command:** `python scripts/fetch_datasets.py`

```
[Materials Project API]  ──► raw_materials_project.csv  ─┐
[OQMD REST API]          ──► raw_oqmd.csv                ──► combined_raw_data.csv
[AFLOW REST API]         ──► raw_aflow.csv (if data)     ─┘
[JARVIS OPTIMADE]        ──► raw_jarvis.csv (0 rows)
```

All four outputs are written to CWD (bare filenames, not `data/`). Run from repo root so they land correctly.

**What it does:** Queries all four databases for any material composed only of elements in `{Mo, Nb, Ta, W, Cr, V, Ti, Zr, Hf}`. Applies `is_allowed()` strict post-fetch filter. Concatenates non-empty results into `combined_raw_data.csv`.

**Current state of outputs:**
- `combined_raw_data.csv` — 91 rows (all from MP; JARVIS returned 0, AFLOW status uncertain, OQMD results in `raw_oqmd.csv` are 31 rows but lack bulk_modulus so most are dropped downstream)
- `raw_jarvis.csv` — 0 rows; fetch failed

**Feeds into:** Step 2

---

### Step 2 — Property Calculation

**Script:** `scripts/calculate_properties.py`
**Command:** `python scripts/calculate_properties.py`

```
combined_raw_data.csv  ──► [Slack model + Rule of Mixtures + Elastic calcs] ──► processed_candidate_properties.csv
```

**What it does:** Reads combined raw data, drops rows with no `bulk_modulus`, fills missing `shear_modulus`/`density`/`volume` with placeholders, computes intermediate (Category E) properties — elastic modulus, Poisson's ratio, Debye temperature, Grüneisen parameter — uses them to estimate thermal conductivity (Slack model) and CTE (Rule of Mixtures), then drops all intermediates from the final output.

**Current state of outputs:**
- `processed_candidate_properties.csv` — 54 rows. Only MP entries survive (OQMD has no bulk_modulus). `shear_modulus` for many rows is the placeholder 80.0 GPa.

**Feeds into:** Step 5 (as training data for the ML model)

---

### Step 3 — Composition Grid Generation

**Script:** `scripts/generate_compositions.py`
**Command:** `python scripts/generate_compositions.py`

```
[no inputs] ──► [combinatorial 5% grid, 5 elements, sum=1] ──► data/all_compositions-generated.csv
```

**What it does:** Enumerates all Mo–Nb–Ta–W–Cr fractional compositions at 5% increments summing to 1.0, including all unary/binary/ternary/quaternary/quinary sub-systems. Produces 10,626 rows.

**⚠️ BUG B3:** The script writes to `scripts/all_compositions.csv` (wrong path, wrong filename). The file that currently exists in `data/all_compositions-generated.csv` is from a previous run where the output was manually renamed and moved. Fix B3 before re-running.

**Feeds into:** Step 4

---

### Step 4 — Empirical Thermodynamic Filtering

**Script:** `scripts/empirical_filter.py`
**Command:** `python scripts/empirical_filter.py`

```
data/all_compositions-generated.csv  ──► [Miedema δ / ΔHmix / VEC / Ω filters] ──► data/stable_compositions.csv
```

**What it does:** Computes four thermodynamic stability parameters for every composition and applies four filters: δ ≤ 6.6%, ΔHmix ∈ [−15, +5] kJ/mol, VEC ∈ [4.0, 6.8], Ω ≥ 1.1.

**⚠️ BUG B2:** Reads from `scripts/all_compositions-generated.csv` (wrong path). Will crash with `FileNotFoundError`. Fix B2 before running.

**⚠️ KNOWN ISSUE — Filter passes 100%:** All 10,626 compositions pass all four filters. Mo–Nb–Ta–W–Cr elements are chemically too similar (atomic radii range 1.28–1.46 Å, all mixing enthalpies ≤ 1 kJ/mol). The filter adds thermodynamic parameter columns to the CSV but rejects nothing.

**Current state of outputs:**
- `data/stable_compositions.csv` — 10,626 rows; identical composition set to the input plus six new parameter columns

**Feeds into:** Step 5

---

### Step 5 — ML Model Training and Property Prediction

**Script:** `scripts/train_composition_ml.py`
**Command:** `python scripts/train_composition_ml.py`

```
data/processed_candidate_properties.csv  ──┐
data/stable_compositions.csv             ──► [RandomForest + GradientBoosting] ──► models/ml_predictions.csv
data/EXP-MPEA_dataset.csv               ──┘
                                                                                ──► scripts/composition_model.pkl  [⚠️ BUG B4: never written]
```

**What it does in sequence:**

1. **Loads training data** — reads `processed_candidate_properties.csv` (54 rows with real DFT bulk modulus). Falls back to `create_synthetic_training_data()` (~75 synthetic points) if file is missing or has < 5 rows with bulk_modulus.
2. **Trains bulk modulus model** — `RandomForestRegressor(n_estimators=100, max_depth=10)` on 18 composition-only features (weighted-avg r, X, VEC, Tm, mass, K; std of r, X, VEC, Tm; n_elements; 9 element fractions). Features scaled by `StandardScaler`.
3. **Trains yield strength model** — `GradientBoostingRegressor(n_estimators=200, max_depth=6)` on `EXP-MPEA_dataset.csv` rows where formula uses only `{Mo, Nb, Ta, W, Cr, V, Ti, Zr, Hf}`. Transfer-learning weighted: rows with only TARGET_ELEMENTS get weight=10; broader refractory alloys get weight=1.
4. **Predicts all 10,626 compositions** — appends predicted bulk modulus, YS, thermal conductivity (Rule of Mixtures), and CTE to `stable_compositions.csv` columns; writes to `models/ml_predictions.csv`.

**⚠️ BUG B4:** `MODEL_OUTPUT` (line 37) is defined as `scripts/composition_model.pkl` but `pickle.dump()` is never called anywhere. The pkl in `models/` on disk was saved by an earlier version of the script.

**⚠️ KNOWN ISSUE — Unphysical bulk modulus predictions:** `ml_predictions.csv` contains 1,482 true HEA rows with `predicted_bulk_modulus ≤ 0` (minimum: −1,920,044 GPa). These are artefacts of the Random Forest extrapolating outside its training distribution. This directly causes Step 6 to fail.

**⚠️ KNOWN ISSUE — R² misleading:** R² = 0.97 is measured on a synthetic holdout set generated by the same Rule-of-Mixtures formulas used as features. It measures internal consistency, not predictive accuracy on real HEAs.

**Current state of outputs:**
- `models/ml_predictions.csv` — 10,626 rows; bulk modulus unreliable for ~38% of true HEAs

**Feeds into:** Step 6, and indirectly into all three optimisation scripts (Steps 8–10)

---

### Step 6 — Candidate Scoring via 1D FEA

**Script:** `scripts/evaluate_candidates.py`
**Command:** `python scripts/evaluate_candidates.py`

```
models/ml_predictions.csv  ──► [1D thermoelastic FEA × 4 ceramics × 4 gradient exponents] ──► models/top_50_candidates.csv
              ▲
              │ imports
      scripts/run_1d_fea.py
```

**What it does:** Filters `ml_predictions.csv` to true HEAs (all 5 of Mo/Nb/Ta/W/Cr fractions > 0 → 3,876 rows). For each, runs `solve_1d_thermoelastic_surrogate()` across 4 ceramics × 4 gradient exponents = 16 combinations per alloy = 62,016 FEA calls. Computes safety factor = YS_hot / interface_stress where `YS_hot = YS_RT × max(0.3, 1.0 − 0.8 × T/3290)` at T=1400K (knockdown ≈ 0.66). Keeps only combinations with SF ≥ 1.45. Saves top 50 sorted by lowest interface stress.

**⚠️ BUG B1 BLOCKS THIS STEP:** `run_1d_fea.py` calls `np.trapz()` which was removed in NumPy 2.0. Every FEA call will raise `AttributeError`. Fix B1 first.

**⚠️ BUG B5 DEGRADES OUTPUT:** No guard against negative `predicted_bulk_modulus`. Negative E_Pa passed to the FEA solver produces nonsense stress values. Even after fixing B1, results for the ~38% of HEAs with negative bulk modulus will be physically meaningless.

**⚠️ KNOWN ISSUE — 5-element filter misses Bohrium candidate:** The filter requires all of Mo_frac, Nb_frac, Ta_frac, W_frac, Cr_frac > 0. The `Ta–W–Cr–V–Ti–Hf` composition (Mo=0, Nb=0) found by `stage1_optimizer_with_constraints.py` is invisible to this step and will never appear in `top_50_candidates.csv`.

**Current state of output:**
- `models/top_50_candidates.csv` — **EMPTY** (header row only). Root causes: Bug B1 crashes the FEA; Bug B5 would further corrupt results even after B1 is fixed.

**Feeds into:** Step 7

---

### Step 7 — Manufacturing Recipe Generation

**Script:** `scripts/generate_manufacturing_recipe.py`
**Command:** `python scripts/generate_manufacturing_recipe.py`

```
models/top_50_candidates.csv  ──► [11-layer depth expansion] ──► models/top1_manufacturing_recipe.csv
```

**What it does:** Reads `iloc[0]` (the top-ranked candidate) from `top_50_candidates.csv`. Generates an 11-layer recipe at positions 0–5mm using `v_ceramic = (depth/5.0)^n` and `v_metal = 1 - v_ceramic`.

**⚠️ BLOCKED:** `top_50_candidates.csv` is empty. Running this script will crash with `IndexError: single positional indexer is out-of-bounds`.

**Current state of output:**
- `models/top1_manufacturing_recipe.csv` — **INVALID.** Contains `Mo0.05Nb0.80Ta0.05W0.05Cr0.05` (Nb=80%) from a stale prior run. Must be regenerated once Steps 1–6 are fixed.

---

## Part 2 — Optimisation Scripts (Independent of Main Pipeline)

These three scripts are alternative search paths that do **not** read from `models/ml_predictions.csv`. They train models on-the-fly in-memory and are independent of whether the main pipeline has run. All three import `run_1d_fea` and are therefore also **blocked by Bug B1**.

---

### Step 8 — Unconstrained 9-Element DE Search

**Script:** `scripts/differential_evolution_search.py`
**Command:** `python scripts/differential_evolution_search.py`

```
[trains ML models in-memory from data/ files]
        ↓
[Differential Evolution over 9-element softmax space]
        ↓
        stdout only — no CSV written
```

**What it does:** Trains bulk modulus (RF) and yield strength (GB) models on-the-fly. Runs `scipy.optimize.differential_evolution` with `maxiter=50`, `popsize=15`, `strategy='best1bin'` over a 9-element unbounded space (softmax-normalised). Objective: minimise −SF. Single penalty: requires ≥5 elements ≥5% (penalty 100.0).

**⚠️ BLOCKED by Bug B1:** Calls `solve_1d_thermoelastic_surrogate` → crashes on `np.trapz`.

**⚠️ WARNING — unconstrained convergence:** Without density or sigma-phase penalties, this script converged to Nb=80% in at least one prior run. That result populated the stale `top1_manufacturing_recipe.csv`. Use `stage1_optimizer_with_constraints.py` instead.

**Output:** stdout only. No file written.

---

### Step 9 — Constrained 9-Element DE Search ← **Primary optimisation script**

**Script:** `scripts/stage1_optimizer_with_constraints.py`
**Command:** `python scripts/stage1_optimizer_with_constraints.py`

```
[trains ML models in-memory from data/ files]
        ↓
[Differential Evolution + engineering constraint penalties]
        ↓
        stdout only — no CSV written
        [Ta–W–Cr–V–Ti–Hf composition found here — must be manually recorded]
```

**What it does:** Same ML training as Step 8 but adds five physics-motivated penalties to the objective:
- ≥5 elements ≥5%: penalty 1000.0
- W+Cr+Mo sigma formers: penalty +5.0 if >50%, +2.5 if >40%
- Vanadium: penalty +5.0 if V>20%, +2.0 if V>15%
- Cr minimum: penalty +5.0 if Cr<15%
- Density: penalty +2.0 if >11.0 g/cm³

DE settings: `maxiter=200`, `popsize=20` — four times more iterations than the unconstrained version.

**⚠️ BLOCKED by Bug B1.**

**This is the script that produced the `Ta0.16 W0.11 Cr0.27 V0.15 Ti0.13 Hf0.18` composition** that was subsequently validated by Bohrium. Once Bug B1 is fixed, this is the primary script to run to reproduce or improve that result.

**Output:** stdout only. No file is written — the winning composition must be manually copied from terminal output.

---

### Step 10 — Monte Carlo 9-Element Random Search

**Script:** `scripts/search_new_elements.py`
**Command:** `python scripts/search_new_elements.py`

```
[trains ML models in-memory from data/ files]
        ↓
[10,000 Dirichlet random compositions → filter to true HEAs → sample 2,000]
        ↓
[Batch ML prediction + 1D FEA for LZO at n=1.0 and n=2.0]
        ↓
        stdout (always)
        models/expanded_winners.csv (only if any SF ≥ 1.5 found)
```

**What it does:** Alternative to DE — samples randomly rather than optimises. Covers more diverse compositional space but with lower per-sample information. Only tests LZO ceramic at two exponents.

**⚠️ BLOCKED by Bug B1.**

**Output:** `models/expanded_winners.csv` only if winning candidates exist; otherwise stdout summary only.

---

## Part 3 — Validation Scripts

These scripts validate specific compositions and are run manually, not as part of an automated chain.

---

### Step 11 — Gibbs Proxy Phase Validation

**Script:** `phase_wise_analysis/phase1_calphad_phase_validation.py`
**Command:** `python phase_wise_analysis/phase1_calphad_phase_validation.py`

```
[hardcoded composition: Ta0.16 W0.11 Cr0.27 V0.15 Ti0.13 Hf0.18 Al0.01]
        ↓
[Gibbs free energy proxy sweep 300–3000K]
[VEC gate + δ gate]
        ↓
        stdout (PASS/FAIL)
        phase_wise_analysis/phase1_calphad_validation_curve.png
```

**What it does:** Lightweight CALPHAD substitute — does not require TCHEA4.TDB. Computes ideal ΔSmix, Rule-of-Mixtures Tm, VEC, δ, and a simplified G(T) = ΔH − TΔSmix sweep using a **hardcoded ΔHmix = −8500 J/mol regardless of composition**. Passes if VEC < 6.8 AND solidus proxy > 1400K. Saves a matplotlib figure.

**Limitation:** ΔHmix is a composition-independent constant. This is a significant approximation — the actual mixing enthalpy varies with element ratios.

**Output:** `phase_wise_analysis/phase1_calphad_validation_curve.png` + PASS/FAIL on stdout.

---

### Step 12 — Full CALPHAD Validation (optional, requires licence)

**Script:** `scripts/calphad_validation.py`
**Command:** `python scripts/calphad_validation.py`

```
TCHEA4.TDB (not in repo)  ──► [pycalphad equilibrium at 1400K] ──► stdout
```

**⚠️ BLOCKED:** TCHEA4.TDB is not in the repo. Script gracefully warns and exits.

**⚠️ BUG B6:** Hardcoded composition is `Mo0.05Nb0.80Ta0.05W0.05Cr0.05` — the invalid stale candidate, not the Bohrium composition. Must be updated before this step adds any value.

---

### Step 13 — Gradient Sensitivity Analysis

**Script:** `scripts/stage2_gradient_optimization.py`
**Command:** `python scripts/stage2_gradient_optimization.py`

```
[hardcoded: alloy_CTE=6.27, LZO_CTE=9.1, E_metal=280GPa, E_ceramic=210GPa, ΔT=1100K]
        ↓
[sweep n=0.1..4.0 and thickness=2..8mm]
        ↓
        stdout only
```

**What it does:** Sweeps gradient exponent n and coating thickness, computing inter-layer CTE-mismatch stress at each 0.1mm position via `σ = E × |ΔCTE| × ΔT`. Does not use the 1D FEA solver or ML pipeline.

**⚠️ WARNING — no `if __name__` guard:** All code executes at module level. Importing this module anywhere will immediately run and print the sweep. Do not import it from another script.

**Output:** stdout only. No file written.

---

### Steps 14–15 — Bohrium Results Reporters (Hardcoded)

**Scripts:** `phase_wise_analysis/execute_phases_2_to_5.py` and `phase_wise_analysis/execute_phases_6_to_11.py`

**Commands:**
```
python phase_wise_analysis/execute_phases_2_to_5.py
python phase_wise_analysis/execute_phases_6_to_11.py
```

**What they do:** Print pre-written narrative summaries of the Bohrium simulation campaign. **No computation performed.** All numbers are hardcoded string literals. They serve as documentation of what Bohrium reported, not as live calculations.

**Key hardcoded values (from Bohrium external platform, not computed here):**
- Phase 2 FEA: SF = 1.15 (FAIL), von Mises stress = 798 MPa
- Phase 3 MD/Gradient: optimal n=1.1, h=5mm, interface stress=15.95 MPa (PASS)
- Phase 4 Oxidation: 1% Al → FAIL; 2.8% Al → PASS
- Phase 8 post-fix: SF = 1.66 (PASS after root smoothing + film cooling)

**Output:** stdout only.

---

### Step 16 — Sustainability Screening (optional, requires package)

**Script:** `scripts/stage5_sustainability.py`
**Command:** `pip install AlloySustainability && python scripts/stage5_sustainability.py`

```
[hardcoded mass fractions: Ta0.16 W0.11 Cr0.27 V0.15 Ti0.13 Hf0.18]
        ↓
        stdout — embodied energy, supply risk, cost
```

**⚠️ BLOCKED:** Requires `AlloySustainability` which is not available via standard pip. Will crash on import.

---

## Part 4 — Scaffolding (Not Integrated)

### `scripts/active_learning_bo.py`

**Status: Dead code.** Defines the `CostAwareMFBOSurrogate` class with GP-based Expected Improvement acquisition. No script in the repo imports or calls this class. It is not connected to any data source or to `run_1d_fea.py`. Would require a complete integration wrapper to be useful.

---

## Part 5 — Complete Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    MAIN PIPELINE                            │
└─────────────────────────────────────────────────────────────┘

Step 1: fetch_datasets.py
  → combined_raw_data.csv (91 rows)

Step 2: calculate_properties.py
  ← combined_raw_data.csv
  → processed_candidate_properties.csv (54 rows)

Step 3: generate_compositions.py  [⚠️ BUG B3: wrong output path]
  → data/all_compositions-generated.csv (10,626 rows)

Step 4: empirical_filter.py  [⚠️ BUG B2: wrong input path; passes 100%]
  ← data/all_compositions-generated.csv
  → data/stable_compositions.csv (10,626 rows, no filtering)

Step 5: train_composition_ml.py  [⚠️ BUG B4: pkl never saved; unphysical bulk mod values]
  ← data/processed_candidate_properties.csv
  ← data/stable_compositions.csv
  ← data/EXP-MPEA_dataset.csv
  → models/ml_predictions.csv (10,626 rows)

Step 6: evaluate_candidates.py  [⚠️ BUG B1: np.trapz crash; ⚠️ BUG B5: no neg-E guard]
  ← models/ml_predictions.csv
  ← scripts/run_1d_fea.py (imported)
  → models/top_50_candidates.csv  ← EMPTY

Step 7: generate_manufacturing_recipe.py  [⚠️ BLOCKED: empty input]
  ← models/top_50_candidates.csv (empty)
  → models/top1_manufacturing_recipe.csv  ← INVALID (stale Nb=80% result)

┌─────────────────────────────────────────────────────────────┐
│            OPTIMISATION PATH (independent)                  │
└─────────────────────────────────────────────────────────────┘

Step 9: stage1_optimizer_with_constraints.py  [⚠️ BUG B1]
  ← trains models in-memory (same data/ sources as Step 5)
  ← scripts/run_1d_fea.py (imported)
  → stdout only  [Ta-W-Cr-V-Ti-Hf composition — record manually]

Step 8: differential_evolution_search.py  [⚠️ BUG B1; ⚠️ no constraints → Nb=80%]
  → stdout only

Step 10: search_new_elements.py  [⚠️ BUG B1]
  → models/expanded_winners.csv (only if SF ≥ 1.5 found)

┌─────────────────────────────────────────────────────────────┐
│                 VALIDATION SCRIPTS                          │
└─────────────────────────────────────────────────────────────┘

Step 11: phase1_calphad_phase_validation.py
  → phase_wise_analysis/phase1_calphad_validation_curve.png
  → stdout PASS/FAIL

Step 12: calphad_validation.py  [⚠️ BLOCKED: no TCHEA4.TDB; ⚠️ BUG B6: wrong composition]
  → stdout only (exits early with warning)

Step 13: stage2_gradient_optimization.py  [⚠️ no __main__ guard]
  → stdout only

Steps 14-15: execute_phases_2_to_5.py / execute_phases_6_to_11.py
  → stdout only (hardcoded Bohrium numbers)

Step 16: stage5_sustainability.py  [⚠️ BLOCKED: missing library]
  → stdout only

┌─────────────────────────────────────────────────────────────┐
│              SCAFFOLD (not connected)                       │
└─────────────────────────────────────────────────────────────┘

active_learning_bo.py — class defined, never called by any script
```

---

## Part 6 — Recommended Fix Order to Restore the Pipeline

Apply in this order — each fix unblocks the next step:

```
Fix B1 first  → unblocks run_1d_fea.py → unblocks Steps 6, 8, 9, 10
Fix B3        → generate_compositions.py writes to correct path
Fix B2        → empirical_filter.py finds its input
Fix B4        → composition_model.pkl actually saved after training
Fix B5        → evaluate_candidates.py skips negative bulk_mod rows
Fix B6        → calphad_validation.py checks the right composition
```

**After fixes, the minimum viable run sequence is:**

```bash
python scripts/fetch_datasets.py
python scripts/calculate_properties.py
python scripts/generate_compositions.py
python scripts/empirical_filter.py
python scripts/train_composition_ml.py
python scripts/evaluate_candidates.py         # will now produce non-empty output
python scripts/generate_manufacturing_recipe.py
python scripts/stage1_optimizer_with_constraints.py  # for the 9-element search
```
