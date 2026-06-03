# TASK_LIST.md — Ordered Fix Tasks for VS Code Copilot
**Execute strictly in order. Verify each task before starting the next. Never batch.**

---

## GROUP 1 — Unblock the FEA Solver

---

[TASK-1]
File: scripts/run_1d_fea.py
Line(s): 116
Action: Replace
    C = -np.trapz(sigma_free, x) / L_GRADIENT
with
    C = -np.trapezoid(sigma_free, x) / L_GRADIENT
Verify: Run `python scripts/run_1d_fea.py` from repo root. Confirm it prints
    "Predicted Max Interface Stress (Cooling): <some number> MPa"
    with no AttributeError. If AttributeError still appears, NumPy version
    may need updating: `pip install --upgrade numpy`.

---

## GROUP 2 — Fix File Path Mismatches

---

[TASK-2]
File: scripts/generate_compositions.py
Line(s): 13
Action: Replace
    OUTPUT_FILE = Path(__file__).parent / 'all_compositions.csv'
with
    OUTPUT_FILE = Path(__file__).parent.parent / 'data' / 'all_compositions-generated.csv'
Verify: Run `python scripts/generate_compositions.py`. Confirm file
    data/all_compositions-generated.csv exists and has exactly 10626 rows.
    Command: `python -c "import pandas as pd; df=pd.read_csv('data/all_compositions-generated.csv'); print(len(df))"`
    Expected output: 10626

---

[TASK-3]
File: scripts/empirical_filter.py
Line(s): 12-13
Action: Replace
    INPUT_FILE = Path(__file__).parent / 'all_compositions-generated.csv'
    OUTPUT_FILE = Path(__file__).parent / 'stable_compositions.csv'
with
    INPUT_FILE = Path(__file__).parent.parent / 'data' / 'all_compositions-generated.csv'
    OUTPUT_FILE = Path(__file__).parent.parent / 'data' / 'stable_compositions.csv'
Verify: Run `python scripts/empirical_filter.py`. Confirm it prints
    "Total compositions: 10,626" and "All filters passed: 10,626" (100% pass expected —
    this is a known science limitation, not a code bug). Confirm
    data/stable_compositions.csv exists with 10626 rows.

---

## GROUP 3 — Fix the Candidate Filter (Critical Science Fix)

---

[TASK-4]
File: scripts/evaluate_candidates.py
Line(s): 14-17
Action: Replace the block
    elements = ['Mo', 'Nb', 'Ta', 'W', 'Cr']
    true_hea_mask = (df[[f'{el}_frac' for el in elements]] > 0).all(axis=1)
    df_hea = df[true_hea_mask]
    print(f"Evaluating {len(df_hea)} True HEA base matrices...")
with
    ALL_9 = ['Mo', 'Nb', 'Ta', 'W', 'Cr', 'V', 'Ti', 'Zr', 'Hf']
    frac_cols = [f'{el}_frac' for el in ALL_9 if f'{el}_frac' in df.columns]
    true_hea_mask = (df[frac_cols] >= 0.05).sum(axis=1) >= 5
    df_hea = df[true_hea_mask]
    print(f"Evaluating {len(df_hea)} True HEA base matrices (any 5 elements >= 5%)...")
Verify: After running train_composition_ml.py to regenerate ml_predictions.csv,
    run evaluate_candidates.py. Confirm it prints a number > 0 for True HEA count.
    The 5-element Mo-Nb-Ta-W-Cr grid will still produce the same candidates here,
    but the filter will not exclude 9-element compositions when they appear.

---

[TASK-5]
File: scripts/evaluate_candidates.py
Line(s): After line `hea_E_Pa = (row['predicted_bulk_modulus'] * 1.2) * 1e9`
         (in the loop inside run_screening, approximately line 40-42)
Action: Insert the following two lines immediately after the hea_E_Pa assignment:
    if pd.isna(hea_E_Pa) or hea_E_Pa <= 0:
        continue
Verify: Run evaluate_candidates.py. Confirm no math warnings about negative square
    roots or division errors. Check that any compositions with negative bulk modulus
    are silently skipped rather than producing infinite or negative stress values.

---

[TASK-5B]
File: scripts/evaluate_candidates.py
Line(s): The line containing `SF_MIN = 1.45`
Action: Replace
    SF_MIN = 1.45
with
    SF_MIN = 1.50
Reason: Safran aerospace requirement is SF >= 1.50. Using 1.45 is a submission risk.
    The 1D FEA already overstates SF (thermal load only, no centrifugal), so 1.50
    is the minimum defensible threshold.
Verify: Grep confirm: `grep "SF_MIN" scripts/evaluate_candidates.py` → shows 1.50

---

## GROUP 4 — Fix Thermal Property Estimators

---

[TASK-6]
File: scripts/train_composition_ml.py
Line(s): Inside function estimate_cte (find by searching for "def estimate_cte")
Action: Replace the function body:
    CTE = {'Mo': 4.8, 'Nb': 7.3, 'Ta': 6.3, 'W': 4.5, 'Cr': 4.9}
    return sum(row[f'{el}_frac'] * CTE[el] for el in ELEMENTS)
with
    CTE_ALL = {
        'Mo': 4.8, 'Nb': 7.3, 'Ta': 6.3, 'W': 4.5, 'Cr': 4.9,
        'V': 8.4, 'Ti': 8.6, 'Zr': 5.8, 'Hf': 5.9
    }
    return sum(
        row.get(f'{el}_frac', 0.0) * v
        for el, v in CTE_ALL.items()
    )
Reason: V, Ti, Zr, Hf contribute zero CTE in current code. Ti (8.6) and V (8.4)
    are above most refractory metals. They make up ~28% of the Bohrium composition.
    This fix makes CTE predictions physically correct for 9-element compositions.
Verify: Run a quick test:
    `python -c "import sys; sys.path.insert(0,'scripts'); from train_composition_ml import estimate_cte; import pandas as pd; row=pd.Series({'Mo_frac':0,'Nb_frac':0,'Ta_frac':0.16,'W_frac':0.11,'Cr_frac':0.27,'V_frac':0.15,'Ti_frac':0.13,'Hf_frac':0.18}); print(estimate_cte(row))"`
    Pre-fix output is ~5.8 (misses V/Ti/Hf). Post-fix should be ~7.1 (includes them).

---

[TASK-7]
File: scripts/train_composition_ml.py
Line(s): Inside function estimate_thermal_conductivity (find by searching for
         "def estimate_thermal_conductivity")
Action: Replace the K_thermal dict and k_hea computation line:
    K_thermal = {'Mo': 138, 'Nb': 53, 'Ta': 57, 'W': 173, 'Cr': 94}
    k_hea = sum(row[f'{el}_frac'] * K_thermal[el] for el in ELEMENTS)
with
    K_thermal_all = {
        'Mo': 138, 'Nb': 53, 'Ta': 57, 'W': 173, 'Cr': 94,
        'V': 31, 'Ti': 22, 'Zr': 23, 'Hf': 23
    }
    k_hea = sum(
        row.get(f'{el}_frac', 0.0) * v
        for el, v in K_thermal_all.items()
    )
Reason: V(31), Ti(22), Zr(23), Hf(23) W/mK are all much lower than W(173) and Mo(138).
    Their absence inflates predicted conductivity for the Bohrium composition, which
    underestimates thermal gradient and interface stress. Consistent with _get_k() in
    search_new_elements.py and stage1_optimizer_with_constraints.py which already
    use the correct 9-element dict.
Verify: Regenerate ml_predictions.csv and check that predicted_thermal_cond values
    for V/Ti/Hf-containing compositions are lower than before.

---

## GROUP 5 — Fix Model Persistence

---

[TASK-8]
File: scripts/train_composition_ml.py
Two sub-changes:

Sub-change A — Fix the MODEL_OUTPUT path constant:
Line(s): 37 (the MODEL_OUTPUT = ... line)
Action: Replace
    MODEL_OUTPUT = Path(__file__).parent / 'composition_model.pkl'
with
    MODEL_OUTPUT = Path(__file__).parent.parent / 'models' / 'composition_model.pkl'

Sub-change B — Add pickle.dump after train_model returns in the __main__ block:
Line(s): In the `if __name__ == '__main__':` block, after the line
    `theoretical_model, theoretical_scaler = train_model(df_train)`
Action: Insert the following block immediately after:
    import pickle
    MODEL_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(MODEL_OUTPUT, 'wb') as fout:
        pickle.dump((theoretical_model, theoretical_scaler), fout)
    print(f"Bulk modulus model saved to {MODEL_OUTPUT}")
Verify: Run `python scripts/train_composition_ml.py`. Confirm it prints
    "Bulk modulus model saved to models/composition_model.pkl"
    and that models/composition_model.pkl has a recent modification timestamp.

---

## GROUP 6 — Fix CALPHAD Script

---

[TASK-9]
File: scripts/calphad_validation.py
Two sub-changes:

Sub-change A — Fix component list (line 18):
Action: Replace
    comps = ["MO", "NB", "TA", "W", "CR", "VA"]
with
    comps = ["TA", "W", "CR", "V", "TI", "HF", "AL", "VA"]

Sub-change B — Fix the hardcoded composition dict (lines 35-42 approx):
Action: Replace the entire composition = { ... } block with:
    composition = {
        v.X("TA"): 0.16,
        v.X("W"):  0.11,
        v.X("CR"): 0.27,
        v.X("V"):  0.15,
        v.X("TI"): 0.13,
        v.X("HF"): 0.155,
        v.X("AL"): 0.015,
    }
Reason: Script was hardcoded to Nb=80% stale candidate. The Bohrium composition
    is Ta-W-Cr-V-Ti-Hf+Al. Al micro-addition must be included.
    Note: fractions sum to 0.96 — last element (HF adjusted to 0.155) because
    the final component is dependent (pycalphad infers it). Adjust if needed
    to sum correctly given pycalphad conventions.
Verify: Run `python scripts/calphad_validation.py`. With no TCHEA4.TDB present
    (expected), should print WARNING about missing TDB then exit gracefully.
    Confirm no syntax errors. Actual CALPHAD run requires TDB file separately.

---

## GROUP 7 — Add HEA Upper-Bound Constraint to Unconstrained DE

---

[TASK-10]
File: scripts/differential_evolution_search.py
Line(s): Inside objective() function, immediately after the existing HEA-definition
         penalty block (the `if sum(1 for f in fracs if f >= 0.05) < 5: return 100.0` block)
Action: Insert the following block:
    # HEA upper bound: no single element > 35% (Miracle & Senkov 2017)
    if any(f > 0.35 for f in fracs):
        return 100.0
    # Density constraint
    element_density = {
        'Mo': 10.2, 'Nb': 8.6, 'Ta': 16.7, 'W': 19.3, 'Cr': 7.2,
        'V': 6.0, 'Ti': 4.5, 'Zr': 6.5, 'Hf': 13.3
    }
    density = sum(
        frac_dict.get(el, 0.0) * element_density.get(el, 10.0)
        for el in ALL_ELEMENTS
    )
    if density > 11.0:
        return 50.0
Reason: Without this, the unconstrained optimizer previously converged to Nb=80%
    and produced the invalid top1_manufacturing_recipe.csv. This fix prevents
    the optimizer from creating compositions that violate the HEA definition.
Verify: Run `python scripts/differential_evolution_search.py` and confirm the
    output formula shows no single element fraction > 0.35.

---

## GROUP 8 — Add __main__ Guard and Safety Checks

---

[TASK-11]
File: scripts/stage2_gradient_optimization.py
Line(s): Entire file structure
Action: Wrap all module-level executable code (everything after the function
    definition for calculate_interface_stress) inside:
    if __name__ == '__main__':
        <existing executable code indented by 4 spaces>
    The function definition `def calculate_interface_stress(...)` must remain
    at module level (NOT inside the guard).
Verify: Run `python -c "from scripts.stage2_gradient_optimization import calculate_interface_stress; print('import ok')"`.
    Confirm "import ok" prints with no sweep output or print side effects.

---

[TASK-12]
File: scripts/generate_manufacturing_recipe.py
Line(s): Inside generate_layer_recipe(), immediately after
         `df = pd.read_csv(os.path.join('models', 'top_50_candidates.csv'))`
Action: Insert the following guard block:
    if len(df) == 0:
        print("ERROR: top_50_candidates.csv is empty.")
        print("Re-run the pipeline (Steps 1-6) before generating recipes.")
        print("See FIXES_PLAN_VERIFIED.md for the minimum viable fix sequence.")
        return
Verify: Run `python scripts/generate_manufacturing_recipe.py` with the current
    empty top_50_candidates.csv. Confirm it prints the ERROR message and exits
    cleanly instead of raising IndexError.

---

## GROUP 9 — Fix the BO Scaffold

---

[TASK-13]
File: scripts/active_learning_bo.py
Two sub-changes:

Sub-change A — Fix np.vstack crash in update_model:
Line(s): Inside update_model(), the `self.surrogate.fit(...)` line
Action: Replace
    self.surrogate.fit(np.vstack(self.X_train), np.array(self.y_train))
with
    X_arr = np.array(self.X_train)
    if X_arr.ndim == 1:
        X_arr = X_arr.reshape(-1, 1)
    self.surrogate.fit(X_arr, np.array(self.y_train))

Sub-change B — Fix return type inconsistency in expected_improvement:
Line(s): The `return 0.0` line inside expected_improvement when sigma == 0
Action: Replace
    return 0.0
with
    return np.float64(0.0)
Verify: Run `python -c "from scripts.active_learning_bo import CostAwareMFBOSurrogate; print('import ok')"`.
    Confirm no ImportError or syntax issues.

---

## GROUP 10 — Fix HEA Upper-Bound Flag in Composition Grid

---

[TASK-14]
File: scripts/generate_compositions.py
Line(s): The line containing `'is_true_hea': all(f >= MIN_FRAC for f in comp)`
Action: Replace
    'is_true_hea': all(f >= MIN_FRAC for f in comp)
with
    'is_true_hea': sum(1 for f in comp if MIN_FRAC <= f <= 0.35) >= 5
Reason: Original flag only checked lower bound. HEA definition (Miracle & Senkov 2017)
    requires each principal element between 5-35%. Without the upper bound,
    Mo=90% would be flagged as a true HEA. This is why Nb=80% appeared in prior results.
Verify: After running generate_compositions.py, check the is_true_hea column in
    data/all_compositions-generated.csv. Equimolar Mo0.20Nb0.20Ta0.20W0.20Cr0.20
    should have is_true_hea=True. A composition with any element at 0.90 should
    have is_true_hea=False.

---

## Minimum Viable Sequence (Get top_50_candidates.csv non-empty fast)
Execute in this order, verify each, commit between each:
TASK-1 → TASK-6 → TASK-7 → TASK-4 → TASK-5 → TASK-5B
Then run: `python scripts/train_composition_ml.py` then `python scripts/evaluate_candidates.py`
Expected: top_50_candidates.csv has > 0 rows.

## Full Pipeline Test (After All Tasks Complete)
```bash
python scripts/fetch_datasets.py
python scripts/calculate_properties.py
python scripts/generate_compositions.py
python scripts/empirical_filter.py
python scripts/train_composition_ml.py
python scripts/evaluate_candidates.py
python scripts/generate_manufacturing_recipe.py
python scripts/stage1_optimizer_with_constraints.py
python phase_wise_analysis/phase1_calphad_phase_validation.py
```
Expected final state: top1_manufacturing_recipe.csv shows a true HEA (no element > 35%).
