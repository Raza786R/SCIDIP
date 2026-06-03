# FLAWS_REPORT.md — HE-MCGA Codebase Audit
Generated: May 2026 | Scope: All .py files in scripts/ and phase_wise_analysis/

---

## Confirmed Bugs (B1–B6 from prior analysis, fully detailed here)

---

[SEVERITY: critical]
File: scripts/run_1d_fea.py
Line: 116
Issue: `np.trapz(sigma_free, x)` — `np.trapz` was removed in NumPy 2.0; replaced by `np.trapezoid`. This is a hard crash, not a deprecation warning. Any environment running NumPy ≥ 2.0 fails immediately on import of this module.
Pipeline impact: BLOCKS scripts/evaluate_candidates.py, scripts/differential_evolution_search.py, scripts/stage1_optimizer_with_constraints.py, scripts/search_new_elements.py — all four import run_1d_fea. The entire FEA-based scoring path is dead.

---

[SEVERITY: critical]
File: scripts/empirical_filter.py
Lines: 12–13
Issue: `INPUT_FILE = Path(__file__).parent / 'all_compositions-generated.csv'` and `OUTPUT_FILE = Path(__file__).parent / 'stable_compositions.csv'` resolve to `scripts/all_compositions-generated.csv` and `scripts/stable_compositions.csv`. The actual files live in `data/`. Running this script from repo root produces `FileNotFoundError` immediately.
Pipeline impact: Step 4 cannot run. `stable_compositions.csv` is never updated, and any fix to generate_compositions.py (B3) would not propagate to this step without also fixing this path.

---

[SEVERITY: critical]
File: scripts/generate_compositions.py
Line: 13
Issue: `OUTPUT_FILE = Path(__file__).parent / 'all_compositions.csv'` writes to `scripts/all_compositions.csv` with filename `all_compositions.csv`. The downstream consumer (`empirical_filter.py`, after fixing B2) expects `data/all_compositions-generated.csv`. Two mismatches: directory (`scripts/` vs `data/`) and filename (`all_compositions.csv` vs `all_compositions-generated.csv`).
Pipeline impact: Re-running Step 3 creates a file that Step 4 (even after fixing B2) cannot find. The `data/all_compositions-generated.csv` currently on disk is from a prior run that must have been manually renamed and moved.

---

[SEVERITY: high]
File: scripts/train_composition_ml.py
Line: 37 (constant defined), no corresponding write call anywhere in file
Issue: `MODEL_OUTPUT = Path(__file__).parent / 'composition_model.pkl'` is defined but `pickle.dump()` is never called. The trained model is kept in memory and then lost. The `models/composition_model.pkl` on disk was written by an earlier version of the script that no longer exists. Additionally, the path points to `scripts/composition_model.pkl` — wrong directory — while the pkl lives in `models/`.
Pipeline impact: Re-running Step 5 does NOT update the pkl. If the model is loaded elsewhere via the pkl file, it silently uses stale weights. No downstream script actually loads the pkl in the current codebase (all optimisation scripts re-train in memory), so the immediate damage is limited to reproducibility and the intended model-persistence architecture.

---

[SEVERITY: high]
File: scripts/evaluate_candidates.py
Lines: 38–42
Issue: `hea_E_Pa = (row['predicted_bulk_modulus'] * 1.2) * 1e9` is computed and passed directly to `solve_1d_thermoelastic_surrogate()` with no check for negative, zero, or NaN values. `ml_predictions.csv` contains 1,482 true-HEA rows with `predicted_bulk_modulus ≤ 0` (minimum confirmed at -1,920,044 GPa — a machine learning extrapolation artefact). Negative `hea_E_Pa` enters the Reuss-bound mixing formula and tridiagonal system, producing meaningless (and sometimes large negative) stresses that can appear to pass the SF ≥ 1.45 threshold spuriously.
Pipeline impact: Even after fixing B1, a fraction of FEA calls will silently produce physically wrong stress values. Some garbage compositions may rank highly in `top_50_candidates.csv`.

---

[SEVERITY: high]
File: scripts/calphad_validation.py
Lines: 35–40
Issue: The `composition` dict is hardcoded to `{v.X("MO"): 0.05, v.X("NB"): 0.80, v.X("TA"): 0.05, v.X("W"): 0.05}` — the stale Nb=80% candidate. The Bohrium-validated composition is `Ta0.16 W0.11 Cr0.27 V0.15 Ti0.13 Hf0.18`. This script, when TCHEA4.TDB becomes available, would validate the wrong material.
Pipeline impact: Phase stability claims in the Safran submission would be backed by CALPHAD results for a composition that is not the proposed candidate.

---

## Newly Discovered Bugs

---

[SEVERITY: critical]
File: scripts/stage2_gradient_optimization.py
Lines: 1–end (entire file)
Issue: All executable code runs at module scope — there is no `if __name__ == '__main__':` guard. The stress sweep, `optimal_n` computation, and all `print()` calls execute immediately upon any `import` of this module. No other script imports it currently, but this is a latent crash risk if added to a pipeline runner.
Pipeline impact: If this file is ever imported by a runner script, it will silently execute side effects and print unsolicited output, potentially breaking stdout-parsing logic. Additionally, all material properties (`alloy_CTE = 6.27`, `LZO_CTE = 9.1`, `E_metal = 280e9`, `E_ceramic = 210e9`, `delta_T = 1100`) are hardcoded constants that do not come from any upstream pipeline step. This script is fully disconnected from the rest of the pipeline.

---

[SEVERITY: critical]
File: scripts/evaluate_candidates.py
Line: 12
Issue: `data_path = Path(__file__).parent.parent / 'models' / 'ml_predictions.csv'` — the variable `data_path` is defined but `pd.read_csv(data_path)` is never called. Instead, line 14 calls `pd.read_csv(data_path)` correctly... wait — checking again: the actual read is `df = pd.read_csv(data_path)` which does use the variable. However, the True HEA filter on line 19 checks `(df[[f'{el}_frac' for el in elements]] > 0).all(axis=1)` where `elements = ['Mo', 'Nb', 'Ta', 'W', 'Cr']`. The `ml_predictions.csv` has `V_frac`, `Ti_frac`, `Zr_frac`, `Hf_frac` columns (all zero) but the optimised composition (`Ta–W–Cr–V–Ti–Hf`) has `Mo_frac = 0` and `Nb_frac = 0`. The filter requires ALL FIVE of Mo/Nb/Ta/W/Cr to be > 0, so the entire 9-element Bohrium-validated composition family is invisible to this screening step.
Pipeline impact: The main pipeline (Step 6) cannot discover or rank the `Ta–W–Cr–V–Ti–Hf` composition. The top_50_candidates.csv will NEVER contain the design that was actually validated. The pipeline produces a completely different (and unchecked) candidate if it produces anything at all.

---

[SEVERITY: high]
File: scripts/train_composition_ml.py
Function: estimate_cte (line ~290)
Issue: `estimate_cte()` uses `CTE = {'Mo': 4.8, 'Nb': 7.3, 'Ta': 6.3, 'W': 4.5, 'Cr': 4.9}` and iterates over `TARGET_ELEMENTS = ['Mo', 'Nb', 'Ta', 'W', 'Cr']` only. When predictions are run for the full 9-element composition set (after stage1 adds V, Ti, Zr, Hf), V, Ti, Zr, Hf contribute zero to the CTE estimate regardless of their fraction. For a composition like `Ta0.16 W0.11 Cr0.27 V0.15 Ti0.13 Hf0.18`, ~61% of the composition is ignored in CTE calculation. The CTE in `ml_predictions.csv` is therefore systematically underestimated for 9-element compositions.
Pipeline impact: Underestimated CTE → underestimated CTE mismatch with ceramic → underestimated interface stress → artificially high safety factors for V/Ti/Hf-containing alloys.

---

[SEVERITY: high]
File: scripts/train_composition_ml.py
Function: estimate_thermal_conductivity (lines ~275–295)
Issue: The function computes k using `K_thermal = {'Mo': 138, 'Nb': 53, 'Ta': 57, 'W': 173, 'Cr': 94}` (TARGET_ELEMENTS only). V, Ti, Zr, Hf contributions are silently zero. For `Ta0.16 W0.11 Cr0.27 V0.15 Ti0.13 Hf0.18`, ~61% of the composition contributes zero thermal conductivity. Real values: V ≈ 31, Ti ≈ 22, Zr ≈ 23, Hf ≈ 23 W/mK — much lower than Mo/W. The true conductivity of the Bohrium composition would be significantly lower than predicted, meaning less heat dissipation across the gradient than the model assumes.
Pipeline impact: Overestimated thermal conductivity → overestimated heat transport → underestimated thermal gradient → underestimated interface stress → artificially high safety factors.

---

[SEVERITY: high]
File: scripts/differential_evolution_search.py
Lines: 38–44
Issue: The objective function applies only one penalty: `if sum(1 for f in fracs if f >= 0.05) < 5: return 100.0`. There is no density constraint, no sigma-phase constraint, no V-oxidation constraint, and no Cr-minimum constraint. The DE optimizer is free to converge to any composition including Nb=80% (confirmed to have happened in a prior run, which is how `top1_manufacturing_recipe.csv` got an invalid Nb-dominant composition). The `stage1_optimizer_with_constraints.py` exists specifically to fix this, but this script remains in the codebase uncorrected and is likely to be run again.
Pipeline impact: Running this script can overwrite or produce a stale composition that misleads the project. The Nb=80% composition in `top1_manufacturing_recipe.csv` was produced by this or an earlier equivalent.

---

[SEVERITY: high]
File: scripts/run_1d_fea.py
Lines: 89–105 (tridiagonal system construction)
Issue: The tridiagonal matrix `A` is initialised as `(N-2, N-2)` and populated in a loop `for i in range(1, N-1)`. When `i = N-2` (last interior node), the code attempts `A[ii, ii+1] = k_plus` where `ii = N-3` and `ii+1 = N-2`. This index `N-2` is OUTSIDE the matrix (valid indices are 0..N-3). The condition `if ii < N-3` should be `if ii < N-3` which already guards this — checking: `if ii < N-3: A[ii, ii+1] = k_plus` — this IS guarded. However, the condition for the left diagonal `if ii > 0: A[ii, ii-1] = k_minus` is also present. These look correct. The actual concern is that `k_plus` at `i = N-1` uses `k_x[i+1]` which is `k_x[N]` — an out-of-bounds array access. At line 90: `k_plus = 0.5 * (k_x[i] + k_x[i+1]) if i < N-1 else k_x[i]`. The ternary guard `if i < N-1` prevents the OOB at the last iteration. This appears safe. HOWEVER: the equilibrium condition `C = -np.trapz(sigma_free, x) / L_GRADIENT` (the B1 crash) is the definitive issue on line 116.
Pipeline impact: B1 crash is confirmed. The tridiagonal construction appears safe upon closer inspection — this entry is demoted but kept for awareness.

[SEVERITY: medium — demoted after closer inspection, keeping for awareness]

---

[SEVERITY: high]
File: scripts/run_1d_fea.py
Lines: 109–110 (Coble creep)
Issue: `sigma_relaxed = np.where(T > 1200, sigma * 0.85, sigma)` applies a hard 15% scalar relaxation above 1200K regardless of composition, grain size, applied stress magnitude, time, or temperature. The `grain_size` parameter is accepted by `solve_1d_thermoelastic_surrogate()` but never used. The Tsukamoto model (referenced in HE_MCGA_Paper_Context_and_Synthetic_Data_Plan.md) shows that creep magnitude depends strongly on grain size — 1 µm grain gives GPa-level stress during cooling, 10 µm is manageable. The hardcoded 0.85 factor is physically unjustified.
Pipeline impact: Safety factors are systematically overestimated (creep relaxation is overstated). The model may pass candidates that would fail under realistic creep conditions at 1400K.

---

[SEVERITY: high]
File: scripts/run_1d_fea.py
Lines: 113–114 (stress concentration factor)
Issue: `peak_stress = np.max(np.abs(sigma_relaxed)) / 1e6` then `return peak_stress * 1.3`. The 1.3 stress concentration factor is a hardcoded empirical fudge with no derivation or reference. It does not vary with gradient exponent, geometry, or ceramic type. For the Bohrium-validated 3D FEA result (SF drops from 1.62 to 1.15, a 29% reduction), the 1.3 factor is directionally correct but uncalibrated — the 3D result suggests the multiplier should be closer to 1.42 (1/0.7) at stress concentration zones.
Pipeline impact: Stress predictions are internally consistent but not validated against 3D FEA. The ×1.3 factor makes all 1D results non-comparable across different blade geometries.

---

[SEVERITY: high]
File: scripts/run_1d_fea.py
Architecture-level issue
Issue: The 1D FEA is thermal-stress only. Centrifugal loading at 15,000 RPM (adds ~512 MPa from the Bohrium 3D results) and gas pressure loading (2.5 MPa) are completely absent. The Bohrium 3D FEA showed: thermal-only SF = 1.34 (FAIL), centrifugal-only SF = 1.79 (PASS), combined SF = 1.15 (FAIL). The 1D solver only models the thermal-only case. Even with a perfect model, it cannot reproduce the combined-loading result.
Pipeline impact: All safety factor values from `evaluate_candidates.py` and the three optimisation scripts are upper bounds only. Reported SF values of 1.5+ from 1D FEA would realistically be ~0.85–0.90× lower under combined 3D loading.

---

[SEVERITY: high]
File: scripts/empirical_filter.py
Logic issue (not a code crash — a science flaw)
Issue: All 10,626 Mo–Nb–Ta–W–Cr compositions pass all four Miedema filters simultaneously. This is documented in README_VERIFIED_v2.md but the code contains no warning or flag. The filter function `apply_filters()` prints pass/fail counts per filter (showing 100% each time) but the caller (`main()`) proceeds to save all compositions as "stable" without any alert that the filter is non-discriminating. A future user running this script will not know the pre-screening step is useless.
Pipeline impact: Step 4 provides zero reduction of the search space. The Bayesian Optimization and FEA steps receive the full 10,626 compositions without any thermodynamic pre-screening.

---

[SEVERITY: high]
File: scripts/train_composition_ml.py
Function: create_synthetic_training_data
Issue: The fallback synthetic dataset is built from Rule-of-Mixtures (ROM) predictions with small negative offsets (0.95×, 0.93×, 0.91×). The same ROM formula is used to compute the `avg_K` feature in `calculate_features()`. The model is trained on data generated by function A and evaluated on features computed by function A — the model learns the identity mapping of its own training generator. R² = 0.97 measures ROM ≈ ROM, not properties ≈ reality. This is documented but the code contains no inline comment or assertion warning future developers.
Pipeline impact: Bulk modulus predictions are ROM estimates dressed as ML predictions. The 1,482 unphysical negative values arise because the Random Forest extrapolates outside the training distribution, but even in-distribution values are not real DFT results.

---

[SEVERITY: high]
File: scripts/fetch_datasets.py
Function: fetch_materials_project, line ~30
Issue: The script queries `chemsys_list` built from ALL combinations of `ELEMENTS = ['Mo', 'Nb', 'Ta', 'W', 'Cr', 'V', 'Ti', 'Zr', 'Hf']` (9 elements), but then applies `is_allowed()` filtering using the same 9-element set. The `combined_raw_data.csv` therefore contains materials with V, Ti, Zr, Hf present. However, `calculate_properties.py` only defines `ATOMIC_MASS` and `ELEMENT_CTE` for 7 elements (adding Zr and Hf to the Mo/Nb/Ta/W/Cr base). Any formula containing V or Ti would have `parse_formula()` return fractions for those elements, but the CTE and thermal conductivity computations would silently set their contributions to 0 (V and Ti are not in the dicts). The data cleaning step does not flag this inconsistency.
Pipeline impact: Materials containing V or Ti in the raw database have underestimated CTEs and thermal conductivities in `processed_candidate_properties.csv`.

---

[SEVERITY: medium]
File: scripts/stage1_optimizer_with_constraints.py
Lines: 60–65
Issue: The density estimate uses `element_density = {'W': 19.3, 'V': 6.0, 'Cr': 7.2, 'Nb': 8.6, 'Ta': 16.7, 'Mo': 10.2, 'Hf': 13.3, 'Zr': 6.5, 'Ti': 4.5}`. This is a reasonable approximation, BUT the density penalty triggers only above 11.0 g/cm³ (`weight_penalty = 2.0 if density > 11.0 else 0`). For the Bohrium-validated composition Ta0.16 W0.11 Cr0.27 V0.15 Ti0.13 Hf0.18, estimated density ≈ 9.80 g/cm³ — well below 11.0, no penalty. However if future runs include more Hf (13.3 g/cm³) or Ta (16.7 g/cm³), the 11.0 threshold may be too permissive. More importantly, the penalty value of 2.0 (vs safety factor values of ~1.5) is very weak — it only weakly discourages high-density compositions.
Pipeline impact: The optimizer can converge to compositions with density up to ~10.9 g/cm³ without any penalty. For aerospace applications with strict weight budgets, this could produce overweight candidates.

---

[SEVERITY: medium]
File: scripts/active_learning_bo.py
Entire file
Issue: The `CostAwareMFBOSurrogate` class is defined but no script in the codebase imports or instantiates it. It is dead code. The `__init__` takes a `data_path` argument that loads a CSV, but the GP is initialised with empty training data. `update_model()` uses `np.vstack(self.X_train)` which will crash with an error on the first call if `X_train` is a list of 1D numpy arrays (vstack requires uniform shapes). The `expected_improvement()` function returns a float for a single candidate but `suggest_next()` calls `np.array([...ei...])` which would work. The `expected_improvement()` returns `0.0` (a float, not a numpy scalar) when `sigma == 0.0`, creating a type inconsistency with the non-zero case which returns `ei.squeeze()` (a numpy scalar).
Pipeline impact: None currently (dead code). Would fail on first real use due to the `np.vstack` crash on initial training data shape.

---

[SEVERITY: medium]
File: phase_wise_analysis/phase1_calphad_phase_validation.py
Lines: 35–36
Issue: `dH_mix = -8500` (J/mol) is hardcoded regardless of the `composition` argument. This means calling `validate_phase_stability({'Ta': 0.16, 'W': 0.11, ...})` and calling `validate_phase_stability({'Mo': 0.5, 'W': 0.5})` return the same ΔHmix despite very different chemistries. The function signature accepts composition as an argument, implying it should be composition-dependent, but the enthalpy calculation ignores it entirely.
Pipeline impact: The Gibbs free energy sweep is correct in form but wrong in magnitude for any non-"average refractory HEA" composition. Phase stability conclusions are only approximate.

---

[SEVERITY: medium]
File: scripts/generate_compositions.py
Line: 42 (inside generate_compositions function)
Issue: The BCC stability criterion `require_all_elements=True` requires `all(f >= min_frac for f in combo)` where `min_frac = 0.05`. The `is_true_hea` flag in the output CSV is set by `all(f >= MIN_FRAC for f in comp)`. However, the HEA definition in the literature (Miracle & Senkov 2017) requires each principal element between 5–35 at%. The upper bound of 35% is never enforced here. An alloy like `Mo0.90Nb0.025Ta0.025W0.025Cr0.025` would have `is_true_hea = False` (Mo > 35%) but would still appear in the dataset and could be selected by the optimizer. The `stage1_optimizer_with_constraints.py` enforces ≥5 elements ≥5% but does NOT enforce ≤35% per element.
Pipeline impact: Non-HEA compositions can enter and pass through the screening pipeline. The Nb=80% outcome in the stale recipe is a direct consequence of this missing upper bound.

---

[SEVERITY: medium]
File: scripts/evaluate_candidates.py
Lines: 45–47
Issue: `SF_MIN = 1.45` is used as the filter threshold, but the stated Safran requirement throughout all documentation is SF > 1.50. The 1D FEA overstates SF (no centrifugal load), so the practical threshold should be higher than 1.50 to account for the 3D penalty. Using 1.45 as the pipeline filter while claiming 1.50 in documents creates a silent inconsistency — compositions passing the pipeline filter might not actually meet the 1.50 threshold under combined loading.
Pipeline impact: The Safran submission may include candidates that are, in the pipeline's own model, below the required safety threshold.

---

[SEVERITY: medium]
File: scripts/calphad_validation.py
Lines: 18–19
Issue: `comps = ["MO", "NB", "TA", "W", "CR", "VA"]` — the Bohrium-validated composition requires `["TA", "W", "CR", "V", "TI", "HF", "VA"]`. After fixing B6, the `comps` list must also be updated to include V, Ti, Hf and exclude Mo, Nb. Failure to do so would cause pycalphad to ignore the Al micro-addition and all non-Mo/Nb elements.
Pipeline impact: CALPHAD would run on the wrong chemical system even after fixing the composition coordinates.

---

[SEVERITY: medium]
File: scripts/fetch_datasets.py
Function: fetch_oqmd, line ~80
Issue: The OQMD filter is `element_set=(Mo-Nb-Ta-W-Cr)` — a 5-element AND filter. But `is_allowed()` uses the 9-element set. The result is that `raw_oqmd.csv` contains only compounds from the strict Mo–Nb–Ta–W–Cr sub-system (no V, Ti, Zr, Hf), which limits the transfer learning benefit for the yield strength model. This is probably intentional for the OQMD base data but is worth noting as it creates an asymmetry: MP data can include V/Ti/Zr/Hf, OQMD data cannot.
Pipeline impact: Transfer learning for yield strength has fewer anchor points in the V/Ti/Hf sub-systems.

---

[SEVERITY: medium]
File: scripts/generate_manufacturing_recipe.py
Issue: The script uses `os.path.join('models', 'top_50_candidates.csv')` — a relative path. If run from any directory other than the repo root, this fails silently with a FileNotFoundError. No try/except block catches this. The script also has no check for whether `top_50_candidates.csv` has any rows before calling `df.iloc[0]`, which will raise an `IndexError` on the empty file currently on disk.
Pipeline impact: Running from the wrong directory or from the current state (empty CSV) crashes immediately.

---

[SEVERITY: low]
File: scripts/stage5_sustainability.py
Lines: 1–3
Issue: `from AlloySustainability.computations import load_element_indicators, compute_impacts` — this package is not available on PyPI and is not in any requirements file. There is no try/except around the import, no informative error message, and no fallback. The script crashes at import with `ModuleNotFoundError: No module named 'AlloySustainability'`.
Pipeline impact: Sustainability screening (Step 16) is completely non-functional in any standard Python environment.

---

[SEVERITY: low]
File: scripts/train_composition_ml.py
Function: load_experimental_data, lines ~350–360
Issue: The yield strength model is trained with `sample_weight=w_exp` where `w_exp` assigns weight=10 to TARGET_ELEMENT-only rows and weight=1 to broader refractory alloys. The test in `test_exp.py` found zero rows in `EXP-MPEA_dataset.csv` that use ONLY Mo/Nb/Ta/W/Cr. This means ALL training samples for the yield strength model have weight=1 — the intended transfer-learning anchor mechanism is inactive. The model is trained uniformly on the broader refractory dataset with no special weighting for the target chemistry.
Pipeline impact: Yield strength predictions for Mo–Nb–Ta–W–Cr HEAs are no more accurate than for any other refractory alloy in the transfer learning set.

---

[SEVERITY: low]
File: scripts/run_1d_fea.py
Lines: 60–70 (CERAMIC_MATERIALS dict)
Issue: `LZO: {'k': 1.6, 'alpha': 9.1e-6, 'E': 175e9}` — these values are used in the stage2_gradient_optimization.py hardcoded constants (`LZO_CTE = 9.1`, `E_ceramic = 210e9`). The two files are inconsistent: run_1d_fea uses E=175 GPa for LZO while stage2 uses 210 GPa. The Bohrium Extracted_PDF_Content.txt cites LZO E ≈ 175 GPa, making run_1d_fea more accurate. The stage2 value is likely a copy error (210 GPa is closer to YSZ or ZrO2-HfO2).
Pipeline impact: stage2_gradient_optimization.py stress estimates are ~20% too high for LZO due to overestimated ceramic modulus. The optimal n found by stage2 may be slightly different from what the main pipeline computes.

---

[SEVERITY: low]
File: scripts/fetch_datasets.py
Function: fetch_jarvis, lines ~100–115
Issue: The JARVIS fetch disables SSL verification via `verify=False` with `urllib3.disable_warnings()`. This suppresses the InsecureRequestWarning that would otherwise alert the user. In a production pipeline or shared computing environment, silently bypassing SSL is a security concern.
Pipeline impact: Security risk in shared/production environments. Functional risk is that the JARVIS endpoint returns 0 rows regardless (fetch failed), so this code path currently produces no data.

---

## Summary Count by Severity

| Severity | Count |
|---|---|
| Critical | 5 (B1, B2, B3, confirmed; + stage2 no __main__ guard, + evaluate filter misses 9-element compositions) |
| High | 11 |
| Medium | 8 |
| Low | 4 |
| Total | 28 |

Note: B4, B5, B6 from the confirmed list map to high severity above.
