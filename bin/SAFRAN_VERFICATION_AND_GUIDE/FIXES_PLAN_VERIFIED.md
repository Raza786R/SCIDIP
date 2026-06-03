# FIXES_PLAN.md — HE-MCGA Ordered Repair Plan
Generated: May 2026 | Ordered by pipeline-blocking priority

Apply fixes in this exact order. Each fix is a prerequisite for the next group.
Run the full pipeline test after each group before proceeding.

---

## GROUP 1 — Unblock the FEA solver (fixes B1)
Must be done first. Every script that imports run_1d_fea crashes until this is done.
Unblocks: Steps 6, 8, 9, 10 (evaluate_candidates, both DE searches, random search).

---

[FIX-1]
File: scripts/run_1d_fea.py
Line: 116
Change: Replace
    np.trapz(sigma_free, x)
with
    np.trapezoid(sigma_free, x)
Why: np.trapz was removed in NumPy 2.0. np.trapezoid is the current API and is
     backward-compatible to NumPy 1.23 via the alias. This is a one-word change.
Unblocks: FIX-2, FIX-3, FIX-4, FIX-8, FIX-9, FIX-10 (everything that imports run_1d_fea)
Depends on fix #: none

---

## GROUP 2 — Fix file path mismatches (fixes B2, B3)
The composition grid and empirical filter write/read to wrong directories.
Must be done before re-running Steps 3 and 4.

---

[FIX-2]
File: scripts/generate_compositions.py
Line: 13
Change: Replace
    OUTPUT_FILE = Path(__file__).parent / 'all_compositions.csv'
with
    OUTPUT_FILE = Path(__file__).parent.parent / 'data' / 'all_compositions-generated.csv'
Why: Two mismatches — wrong directory (scripts/ vs data/) and wrong filename
     (all_compositions.csv vs all_compositions-generated.csv). Downstream consumer
     empirical_filter.py (after FIX-3) expects exactly data/all_compositions-generated.csv.
Unblocks: FIX-3
Depends on fix #: none

---

[FIX-3]
File: scripts/empirical_filter.py
Lines: 12–13
Change: Replace
    INPUT_FILE = Path(__file__).parent / 'all_compositions-generated.csv'
    OUTPUT_FILE = Path(__file__).parent / 'stable_compositions.csv'
with
    INPUT_FILE = Path(__file__).parent.parent / 'data' / 'all_compositions-generated.csv'
    OUTPUT_FILE = Path(__file__).parent.parent / 'data' / 'stable_compositions.csv'
Why: Both paths resolve to scripts/ but files live in data/. FileNotFoundError on run.
     After FIX-2 writes the correct file, this fix ensures it is actually found.
Unblocks: Step 4 can now run end-to-end.
Depends on fix #: FIX-2

---

## GROUP 3 — Fix the broken candidate filter (critical science fix)
This is the most important science fix. The main pipeline currently cannot discover
the Bohrium-validated Ta-W-Cr-V-Ti-Hf composition at all. Fix before running
evaluate_candidates.py for any meaningful result.

---

[FIX-4]
File: scripts/evaluate_candidates.py
Lines: 14–17
Change: Replace the true-HEA filter block:
    elements = ['Mo', 'Nb', 'Ta', 'W', 'Cr']
    true_hea_mask = (df[[f'{el}_frac' for el in elements]] > 0).all(axis=1)
with a count-based HEA definition that matches stage1_optimizer_with_constraints.py:
    ALL_9 = ['Mo', 'Nb', 'Ta', 'W', 'Cr', 'V', 'Ti', 'Zr', 'Hf']
    frac_cols = [f'{el}_frac' for el in ALL_9 if f'{el}_frac' in df.columns]
    true_hea_mask = (df[frac_cols] >= 0.05).sum(axis=1) >= 5
Why: The current filter requires ALL FIVE of Mo/Nb/Ta/W/Cr to be > 0. The Bohrium-
     validated composition has Mo=0 and Nb=0, making it permanently invisible.
     The corrected filter requires any 5 elements (from all 9) each >= 5%, which
     matches the HEA definition used everywhere else in the codebase.
     Without this fix, top_50_candidates.csv will never contain the actual candidate.
Unblocks: Step 6 can now produce meaningful output for 9-element compositions.
Depends on fix #: FIX-1

---

[FIX-5]
File: scripts/evaluate_candidates.py
Lines: 38–42
Change: Add a guard immediately after computing hea_E_Pa:
    hea_E_Pa = (row['predicted_bulk_modulus'] * 1.2) * 1e9
    # Add these two lines:
    if pd.isna(hea_E_Pa) or hea_E_Pa <= 0:
        continue
Why: 1,482 true-HEA rows have predicted_bulk_modulus <= 0 (ML extrapolation artefact).
     Negative E_Pa enters the Reuss-bound formula and produces nonsense stress values
     that can spuriously pass the SF >= 1.45 threshold and corrupt top_50_candidates.csv.
     This guard is already present in differential_evolution_search.py and
     stage1_optimizer_with_constraints.py — adding it here makes the codebase consistent.
Unblocks: Clean results in top_50_candidates.csv after FIX-4.
Depends on fix #: FIX-1, FIX-4

---

## GROUP 4 — Fix the thermal property estimators (critical property fix)
Without this, CTE and thermal conductivity are wrong for every V/Ti/Zr/Hf composition.
Fixes the silent 61%-of-composition-is-zero problem for the Bohrium candidate.

---

[FIX-6]
File: scripts/train_composition_ml.py
Function: estimate_cte (line ~290)
Change: Replace
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
Why: V, Ti, Zr, Hf contribute zero CTE currently despite being ~61% of the Bohrium
     composition. Real CTE values (um/mK): V~8.4, Ti~8.6, Zr~5.8, Hf~5.9.
     Ti and V have higher CTE than Mo/W — their absence causes the model to
     systematically underestimate CTE mismatch and overestimate safety factors.
     Reference values from search_new_elements.py _get_cte() which already uses
     the correct 9-element dict — this fix makes estimate_cte() consistent with it.
Unblocks: Correct CTE predictions in ml_predictions.csv for all 9-element compositions.
Depends on fix #: none (can apply independently)

---

[FIX-7]
File: scripts/train_composition_ml.py
Function: estimate_thermal_conductivity (lines ~275–295)
Change: Replace
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
Why: Same problem as FIX-6. V, Ti, Zr, Hf contribute zero thermal conductivity.
     Their real values (W/mK) — V:31, Ti:22, Zr:23, Hf:23 — are significantly
     lower than W(173) and Mo(138). Their absence inflates predicted conductivity,
     which underestimates thermal gradient and interface stress.
     Cross-reference: search_new_elements.py _get_k() already uses the correct dict.
     The two helper functions in different scripts must be consistent.
Unblocks: Correct thermal conductivity predictions in ml_predictions.csv.
Depends on fix #: none (apply with FIX-6 in one edit session)

---

## GROUP 5 — Fix model persistence (fixes B4)
Without this, re-running train_composition_ml.py does not save the new model.

---

[FIX-8]
File: scripts/train_composition_ml.py
Two changes needed:

Change A — fix the MODEL_OUTPUT path constant at line 37:
    Replace:
        MODEL_OUTPUT = Path(__file__).parent / 'composition_model.pkl'
    with:
        MODEL_OUTPUT = Path(__file__).parent.parent / 'models' / 'composition_model.pkl'

Change B — add pickle.dump after train_model() call in the __main__ block (~line 380):
    import pickle
    MODEL_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(MODEL_OUTPUT, 'wb') as f:
        pickle.dump((theoretical_model, theoretical_scaler), f)
    print(f"Bulk modulus model saved to {MODEL_OUTPUT}")
Why: pickle.dump is never called anywhere in the current file. The constant at line 37
     also points to scripts/ (wrong dir). The pkl on disk is from a prior code version.
     Without this fix, every re-run leaves a stale pkl that silently mismatches
     the newly trained model held only in memory.
Unblocks: Reproducible model persistence. Downstream pkl-loading scripts get fresh weights.
Depends on fix #: FIX-6, FIX-7 (train with correct properties before saving)

---

## GROUP 6 — Fix the CALPHAD script (fixes B6 + component list mismatch)
Only relevant once TCHEA4.TDB is obtained. Apply now so it is ready.

---

[FIX-9]
File: scripts/calphad_validation.py
Lines: 18–19 and 35–42
Change A — fix the component list (line 18):
    Replace:
        comps = ["MO", "NB", "TA", "W", "CR", "VA"]
    With:
        comps = ["TA", "W", "CR", "V", "TI", "HF", "AL", "VA"]

Change B — fix the hardcoded composition (lines 35–42):
    Replace the composition dict with the Bohrium-validated values:
        composition = {
            v.X("TA"): 0.16,
            v.X("W"):  0.11,
            v.X("CR"): 0.27,
            v.X("V"):  0.15,
            v.X("TI"): 0.13,
            v.X("HF"): 0.155,  # reduced slightly to leave room for Al
            # Al at ~2.8% natively included; Hf+others sum < 1.0 (last element dependent)
        }

Change C — restrict the phases list for speed (line after Database load):
    phases = ['BCC_A2', 'LIQUID', 'HCP_A3', 'SIGMA', 'LAVES_C14', 'LAVES_C15']
Why: B6 — script hardcoded to Nb=80% stale candidate. comps list must match the
     actual elements in the Bohrium composition or pycalphad silently uses the
     wrong chemical system. Al micro-addition must be included.
Unblocks: CALPHAD validation of the actual proposed composition when TDB is available.
Depends on fix #: none (apply independently)

---

## GROUP 7 — Add the HEA upper-bound constraint and fix the unconstrained DE

---

[FIX-10]
File: scripts/differential_evolution_search.py
Lines: inside objective function, after softmax normalisation
Change: After the existing HEA-definition penalty block, add:
    # HEA upper bound: no single element > 35% (Miracle & Senkov 2017)
    if any(f > 0.35 for f in fracs):
        return 100.0

    # Density constraint (mirrors stage1_optimizer_with_constraints.py)
    element_density = {
        'Mo': 10.2, 'Nb': 8.6, 'Ta': 16.7, 'W': 19.3, 'Cr': 7.2,
        'V': 6.0, 'Ti': 4.5, 'Zr': 6.5, 'Hf': 13.3
    }
    density = sum(
        fracs[i] * element_density.get(el, 10.0)
        for i, el in enumerate(ALL_ELEMENTS)
    )
    if density > 11.0:
        return 50.0

    # Sigma-former constraint
    frac_dict = {el: fracs[i] for i, el in enumerate(ALL_ELEMENTS)}
    if frac_dict.get('W', 0) + frac_dict.get('Cr', 0) + frac_dict.get('Mo', 0) > 0.50:
        return 50.0
Why: Unconstrained DE previously converged to Nb=80% (not a true HEA), which
     produced the invalid top1_manufacturing_recipe.csv. Adding the 35% cap and
     key penalties from stage1_optimizer_with_constraints.py makes this script safe.
     Users should still prefer stage1_optimizer_with_constraints.py but this script
     should not be a trap that silently corrupts output files.
Unblocks: Safe use of the unconstrained DE script as a quick first-pass search.
Depends on fix #: FIX-1

---

## GROUP 8 — Add the missing __main__ guard and pipeline safety check

---

[FIX-11]
File: scripts/stage2_gradient_optimization.py
Lines: Wrap all non-function executable code
Change: Move all module-level executable statements (the sweep, argmin, and print
        calls) into a __main__ guard. The function definition stays at module level.
        Final structure should be:

    import numpy as np
    from scipy.optimize import minimize_scalar

    def calculate_interface_stress(n, total_thickness=5.0):
        [existing function body unchanged]

    if __name__ == '__main__':
        exponents = np.arange(0.1, 4.1, 0.1)
        stresses  = [calculate_interface_stress(n) for n in exponents]
        optimal_n   = exponents[np.argmin(stresses)]
        min_stress  = min(stresses)
        print(f"Optimal gradient exponent: n = {optimal_n:.1f}")
        print(f"Minimum interface stress:  {min_stress:.4f} MPa")
        print(f"Your current n=1.0 stress: {calculate_interface_stress(1.0):.4f} MPa")
        print(f"Improvement: {calculate_interface_stress(1.0)/min_stress:.2f}x")
        print('\nTesting gradient thicknesses...')
        thicknesses = [2, 3, 4, 5, 6, 7, 8]
        for t in thicknesses:
            stress = calculate_interface_stress(n=optimal_n, total_thickness=t)
            print(f"Thickness: {t}mm -> Stress: {stress:.2f} MPa")
Why: All code currently runs at import time. Any future pipeline runner that imports
     this module will trigger the sweep and print statements unexpectedly.
Unblocks: Safe importability of the module.
Depends on fix #: none

---

[FIX-12]
File: scripts/generate_manufacturing_recipe.py
Lines: 8–10 (before df.iloc[0])
Change: Add a row-count check before accessing iloc[0]:
    df = pd.read_csv(os.path.join('models', 'top_50_candidates.csv'))
    if len(df) == 0:
        print("ERROR: top_50_candidates.csv is empty.")
        print("Re-run evaluate_candidates.py after completing Steps 1-6.")
        print("See FIXES_PLAN.md for the minimum viable fix sequence.")
        return
    best = df.iloc[0]
Why: The CSV is currently empty. Calling df.iloc[0] on an empty DataFrame raises
     IndexError: single positional indexer is out-of-bounds with no helpful message.
     The guard provides an actionable error instead of a traceback.
Unblocks: A meaningful error message instead of a crash when the pipeline is incomplete.
Depends on fix #: none (apply now; the upstream empty-CSV issue is resolved by Groups 1-4)

---

## GROUP 9 — Fix the active_learning_bo.py scaffold
Low priority. Only needed when wiring up the BO loop.

---

[FIX-13]
File: scripts/active_learning_bo.py
Two changes:

Change A — fix np.vstack crash in update_model (~line 28):
    Replace:
        self.surrogate.fit(np.vstack(self.X_train), np.array(self.y_train))
    with:
        X_arr = np.array(self.X_train)
        if X_arr.ndim == 1:
            X_arr = X_arr.reshape(-1, 1)
        self.surrogate.fit(X_arr, np.array(self.y_train))

Change B — fix return type inconsistency in expected_improvement:
    Replace:
        return 0.0
    with:
        return np.float64(0.0)
    (so the return type is always a numpy scalar, consistent with ei.squeeze())
Why: np.vstack on a list of 1D arrays of inconsistent shape crashes on first use.
     The return type inconsistency (float vs numpy scalar) causes subtle downstream
     comparison errors in suggest_next().
Unblocks: First real use of the BO scaffold without crashes.
Depends on fix #: none (apply when integrating BO)

---

## GROUP 10 — Add the 35% element cap to the HEA flag

---

[FIX-14]
File: scripts/generate_compositions.py
Line: ~42 (inside the row-building loop in main())
Change: Replace
    'is_true_hea': all(f >= MIN_FRAC for f in comp)
with
    'is_true_hea': all(MIN_FRAC <= f <= 0.35 for f in comp if f > 0)
Why: The HEA definition (Miracle & Senkov 2017) requires each principal element
     between 5-35 at%. The current flag only checks the lower bound. This is the
     root cause of the Nb=80% composition appearing as a plausible candidate —
     it passes is_true_hea=False but still enters the pipeline with no barrier.
     Adding the upper bound ensures the flag correctly identifies true HEAs.
Unblocks: Correct is_true_hea flag in all_compositions-generated.csv.
Depends on fix #: FIX-2 (so re-run writes to the correct location)

---

## Minimum Viable Fix Sequence
Fastest path to a non-empty, correct top_50_candidates.csv:

1. FIX-1  — unblock FEA solver (np.trapz -> np.trapezoid)
2. FIX-4  — fix true-HEA filter to include 9-element compositions
3. FIX-5  — guard against negative bulk modulus entering FEA
4. FIX-6  — fix CTE estimator to include V, Ti, Zr, Hf
5. FIX-7  — fix thermal conductivity estimator to include V, Ti, Zr, Hf

Then re-run in order:
    python scripts/train_composition_ml.py
    python scripts/evaluate_candidates.py
    python scripts/generate_manufacturing_recipe.py

---

## Full Pipeline Test Sequence (after all fixes)

    python scripts/fetch_datasets.py
    python scripts/calculate_properties.py
    python scripts/generate_compositions.py           # FIX-2 required
    python scripts/empirical_filter.py                # FIX-3 required
    python scripts/train_composition_ml.py            # FIX-6, FIX-7, FIX-8 required
    python scripts/evaluate_candidates.py             # FIX-1, FIX-4, FIX-5 required
    python scripts/generate_manufacturing_recipe.py   # FIX-12 required
    python scripts/stage1_optimizer_with_constraints.py   # FIX-1, FIX-10 required
    python phase_wise_analysis/phase1_calphad_phase_validation.py
    python scripts/calphad_validation.py              # FIX-9 required + needs TDB

Expected outcomes after all fixes:
- top_50_candidates.csv: non-empty, contains Ta-W-Cr-V-Ti-Hf family compositions
- top1_manufacturing_recipe.csv: valid 5+ element composition, each element <= 35%
- stage1 optimizer stdout: converges to composition consistent with Bohrium result
- Safety factors: slightly lower than pre-fix values because FIX-6 and FIX-7
  correctly include the higher-CTE Ti/V contributions, raising CTE mismatch
  and interface stress estimates — this is the physically correct direction
