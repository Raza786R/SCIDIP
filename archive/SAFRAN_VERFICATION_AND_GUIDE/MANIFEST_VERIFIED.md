# MANIFEST.md — HE-MCGA Authoritative File Register

**Scope:** Every script in `scripts/` and `phase_wise_analysis/`, every CSV in `data/` and `models/`, and all utility files in `bin/`.
**Authority:** Derived entirely from reading the actual source files. Supersedes all prior documentation in `docs/`.
**Last generated:** May 2026

---

## 1. scripts/ — Pipeline and Optimisation Scripts

---

### `scripts/fetch_datasets.py`

**Purpose:** Queries four public materials databases (Materials Project, OQMD, AFLOW, JARVIS-DFT) and writes merged raw CSV data for the Mo–Nb–Ta–W–Cr–V–Ti–Zr–Hf element set.

**Inputs:** None at runtime. Uses hardcoded MP API key `REVOKED_KEY_REMOVED_USE_MP_API_KEY` via `get_mp_key()`. Requires `mp-api`, `requests`, `urllib3` packages.

**Outputs (all written to the current working directory — must be run from repo root):**
- `raw_materials_project.csv` — MP entries after strict element filter
- `raw_oqmd.csv` — OQMD entries
- `raw_aflow.csv` — AFLOW entries (only written if AFLOW returns data)
- `raw_jarvis.csv` — JARVIS entries (currently 0 rows — JARVIS fetch failed)
- `combined_raw_data.csv` — union of all non-empty results

**Key functions:**
- `get_mp_key()` — returns hardcoded MP API key string
- `fetch_materials_project()` — queries MP via `MPRester`; requests `formula_pretty`, `formation_energy_per_atom`, `energy_above_hull`, `bulk_modulus` (VRH), `shear_modulus` (VRH), `density`; applies `is_allowed()` filter; writes `raw_materials_project.csv`
- `fetch_oqmd()` — paginates `http://oqmd.org/oqmdapi/formationenergy` with `element_set=(Mo-Nb-Ta-W-Cr)`; renames `name→formula`, `delta_e→formation_energy`, `stability→energy_hull`; writes `raw_oqmd.csv`
- `fetch_aflow()` — queries AFLOW REST API; writes `raw_aflow.csv` only if response is non-empty
- `fetch_jarvis()` — queries JARVIS OPTIMADE endpoint; currently returns 0 rows due to fetch failure; writes `raw_jarvis.csv`
- `is_allowed(formula)` — regex check that all elements in a formula string are within `{Mo, Nb, Ta, W, Cr, V, Ti, Zr, Hf}`; used by all four fetch functions as a strict post-fetch filter
- `main()` — calls all four fetchers, concatenates non-empty results, writes `combined_raw_data.csv`

**Known issues:**
- All output CSVs are written to the current working directory via bare filename (e.g., `'raw_materials_project.csv'`), not to `data/`. Run from repo root or the files will land in the wrong place.
- JARVIS fetch always returns 0 rows in current state.
- AFLOW fetch may silently fail; `raw_aflow.csv` may not be written.

---

### `scripts/calculate_properties.py`

**Purpose:** Reads the combined raw DFT data, computes intermediate thermodynamic descriptors (Category E), estimates thermal conductivity via the Slack model and CTE via Rule of Mixtures (Category C), then drops the intermediates, producing a cleaned dataset with final properties only.

**Inputs:**
- `combined_raw_data.csv` (read via bare path — must be in CWD, i.e., repo root)

**Outputs:**
- `processed_candidate_properties.csv` (written to CWD)

**Key functions:**
- `parse_formula(formula)` — regex parser that extracts element fractions from strings like `"Mo0.20Nb0.20Ta0.20W0.20Cr0.20"`; normalises to sum=1
- `calc_elastic_modulus(K, G)` — Voigt–Reuss–Hill formula: `E = 9KG / (3K+G)`
- `calc_poissons_ratio(K, G)` — `ν = (3K-2G) / (2(3K+G))`
- `calc_debye_temperature(E, rho, V, n)` — standard phonon Debye model with unit conversions (GPa→Pa, g/cm³→kg/m³, Å³→m³)
- `calc_gruneisen(nu)` — `γ = 3(1+ν) / (2(2-3ν))`
- `slack_thermal_conductivity(M_avg, theta_D, V_atom, gamma, n, T=1000)` — Slack lattice thermal conductivity; outputs W/mK
- `rule_of_mixtures_CTE(composition_fractions)` — linear weighted average of elemental CTE values from `ELEMENT_CTE` dict (Mo:4.8, Nb:7.3, Ta:6.3, W:4.5, Cr:4.9, Zr:5.7, Hf:5.9 µm/mK)
- `main()` — orchestrates the full pipeline: load → parse formulas → fill missing columns with placeholders → compute E/intermediates → Slack model → Rule of Mixtures → drop Category E columns → write output

**Known issues:**
- Rows missing `bulk_modulus` are silently dropped (`df.dropna(subset=['bulk_modulus'])`). Only 54 of 91+ raw entries survive, as OQMD does not supply bulk modulus.
- Missing `shear_modulus` is filled with a placeholder 80.0 GPa; `density` with 9.0 g/cm³; `volume` with 15.0 Å³/atom. These are rough defaults, not real data.
- Output path is bare `'processed_candidate_properties.csv'` — writes to CWD.

---

### `scripts/generate_compositions.py`

**Purpose:** Enumerates all possible fractional compositions of the 5-element Mo–Nb–Ta–W–Cr system at 5% increments where fractions sum to exactly 1.0. Produces the full combinatorial grid including unary, binary, ternary, quaternary, and quinary compositions.

**Inputs:** None.

**Outputs:**
- `all_compositions.csv` — written to `Path(__file__).parent / 'all_compositions.csv'`, i.e., `scripts/all_compositions.csv`. **Note:** the file on disk is named `all_compositions-generated.csv` and lives in `data/` — this output path does not match the actual file location. The CSV in `data/` was produced by a previous run or manually moved.

**Key functions:**
- `generate_compositions(step, min_frac, require_all_elements)` — itertools product over 5 fraction dimensions; filters to `sum==1.0`; optionally enforces minimum fraction per element for true-HEA constraint
- `create_formula(fracs)` — builds human-readable formula string, e.g., `"Mo0.20Nb0.20Ta0.20W0.20Cr0.20"`
- `main()` — generates both full grid (10,626 rows including all sub-systems) and true-HEA-only subset; saves the full grid; prints summary statistics

**Key constants:**
- `ELEMENTS = ['Mo', 'Nb', 'Ta', 'W', 'Cr']` — 5-element target system only
- `STEP = 0.05` (5% increments)
- `MIN_FRAC = 0.05` (minimum per element for true HEA flag)

---

### `scripts/empirical_filter.py`

**Purpose:** Applies Miedema-derived thermodynamic stability criteria to every composition in the grid, computing δ (atomic size mismatch), ΔHmix (mixing enthalpy), ΔSmix (mixing entropy), VEC (valence electron concentration), Tm_avg (average melting point), and Ω (entropy-to-enthalpy ratio), then filters to compositions meeting all thresholds.

**Inputs:**
- `data/all_compositions-generated.csv` — resolved as `Path(__file__).parent / 'all_compositions-generated.csv'`; i.e., `scripts/all_compositions-generated.csv`. **Path mismatch:** the actual file lives in `data/`. This script will fail unless the file is present at `scripts/all_compositions-generated.csv` or the path constant is corrected.

**Outputs:**
- `data/stable_compositions.csv` — resolved as `Path(__file__).parent / 'stable_compositions.csv'`; same mismatch as above; will write to `scripts/stable_compositions.csv`.

**Key constants (thresholds):**
- `DELTA_MAX = 6.6` % — atomic size mismatch
- `HMIX_MIN = -15`, `HMIX_MAX = 5` kJ/mol — mixing enthalpy window
- `VEC_MIN = 4.0`, `VEC_MAX = 6.8` — BCC-favoring VEC range
- `OMEGA_MIN = 1.1` — minimum entropy/enthalpy ratio

**Key functions:**
- `get_binary_enthalpy(el1, el2)` — symmetric lookup in `BINARY_ENTHALPY` dict (10 Mo/Nb/Ta/W/Cr pairs)
- `calculate_delta(fracs)` — weighted RMS of (1 - r_i / r_avg)²
- `calculate_hmix(fracs)` — Σ 4·H_ij·c_i·c_j over all i<j pairs
- `calculate_smix(fracs)` — -R·Σ c_i·ln(c_i)
- `calculate_vec(fracs)` — linear weighted average of elemental VECs
- `calculate_tm_avg(fracs)` — linear weighted average of elemental melting points
- `calculate_omega(fracs)` — ΔSmix·Tm / |ΔHmix|; returns 999 when |ΔHmix| < 0.01 to avoid div-by-zero
- `apply_filters(df)` — computes all six parameters, applies four masks, reports pass/fail counts, returns filtered DataFrame
- `main()` — loads input, calls `apply_filters()`, saves output, prints top-10 by Ω

**Critical known issue:** All 10,626 input compositions pass all four filters simultaneously. The Mo–Nb–Ta–W–Cr system elements are chemically too similar (atomic radii within 0.18 Å, all negative or near-zero mixing enthalpies, VEC 5–6) for these thresholds to reject anything. The filter provides zero pre-screening.

---

### `scripts/train_composition_ml.py`

**Purpose:** Trains two ML surrogate models — a `RandomForestRegressor` for bulk modulus prediction and a `GradientBoostingRegressor` for yield strength — using composition-only elemental descriptor features. Predicts properties for all 10,626 stable compositions and writes the prediction CSV.

**Inputs:**
- `data/processed_candidate_properties.csv` — resolved as `Path(__file__).parent.parent / 'data' / 'processed_candidate_properties.csv'`; correct given script lives in `scripts/`
- `data/stable_compositions.csv` — resolved as `Path(__file__).parent.parent / 'data' / 'stable_compositions.csv'`; correct
- `data/EXP-MPEA_dataset.csv` — resolved as `Path(__file__).parent.parent / 'data' / 'EXP-MPEA_dataset.csv'`; correct

**Outputs:**
- `models/composition_model.pkl` — resolved as `Path(__file__).parent / 'composition_model.pkl'`; i.e., `scripts/composition_model.pkl`. **Path mismatch:** actual file on disk is in `models/`.
- `models/ml_predictions.csv` — resolved as `Path(__file__).parent.parent / 'models' / 'ml_predictions.csv'`; correct

**Key constants:**
- `TARGET_ELEMENTS = ['Mo', 'Nb', 'Ta', 'W', 'Cr']`
- `ALL_ELEMENTS = ['Mo', 'Nb', 'Ta', 'W', 'Cr', 'V', 'Ti', 'Zr', 'Hf']` — 9 elements used for feature vector to enable transfer learning
- 18 features per composition: `T_test`, 6 weighted-average elemental properties, 4 standard deviations, `n_elements`, 9 individual fractions

**Key functions:**
- `parse_formula_to_fractions(formula, allowed_elements)` — parses formula strings like `"Mo0.20Nb0.20..."` into fraction dicts; normalises if sum ≠ 1
- `calculate_features(fracs_dict, test_temp_c=25)` — builds the 18-feature vector: weighted averages of r, X, VEC, Tm, mass, K; standard deviations of r, X, VEC, Tm; n_elements; individual fractions for all 9 elements
- `load_and_prepare_base_data()` — loads `processed_candidate_properties.csv`; falls back to `create_synthetic_training_data()` if file missing or has <5 rows with bulk_modulus
- `create_synthetic_training_data()` — constructs ~75 training points from: 5 pure elements (textbook K values), 10 equimolar binaries (ROM×0.95), 20 non-equimolar binaries (ROM×0.96), 10 equimolar ternaries (ROM×0.93), 5 equimolar quaternaries (ROM×0.91), 1 equimolar quinary (literature 210 GPa), 4 additional HEA variants from Senkov et al.
- `train_model(df_train)` — fits `RandomForestRegressor(n_estimators=100, max_depth=10)` on features scaled by `StandardScaler`; evaluates on 20% holdout; returns `(model, scaler)`
- `predict_compositions(model, scaler, compositions_df, exp_model, exp_scaler)` — applies both models to all compositions; also calls `estimate_thermal_conductivity()` and `estimate_cte()`
- `estimate_thermal_conductivity(row, T=1400, layer_position=0.0)` — Rule-of-Mixtures phonon conductivity with 0.6× HEA scattering penalty for >2 elements; adds Rosseland radiative term for ceramic fraction (negligible at layer_position=0)
- `estimate_cte(row)` — Rule-of-Mixtures over TARGET_ELEMENTS only (not the 9-element set); values: Mo:4.8, Nb:7.3, Ta:6.3, W:4.5, Cr:4.9 µm/mK
- `load_experimental_data()` — reads `EXP-MPEA_dataset.csv`; filters rows to those composed only of `ALL_ELEMENTS`; assigns sample_weight=10 for TARGET_ELEMENTS-only rows and weight=1 for broader refractory alloys (transfer learning); trains `GradientBoostingRegressor(n_estimators=200, max_depth=6)` with sample weights; returns `(model, scaler)`

**Critical known issues:**
- `load_and_prepare_base_data()` uses real DFT data (54 rows from `processed_candidate_properties.csv`) if available, otherwise falls back to fully synthetic data. With only 54 real rows the model is anchored in real data but extrapolates heavily.
- The bulk modulus model is trained on data generated by the same Rule-of-Mixtures formulas used to build the features — creating circularity. R²=0.97 measures internal self-consistency, not real-world accuracy.
- `composition_model.pkl` is written to `scripts/` (same directory as the script), not `models/` where it lives on disk. The pkl in `models/` was produced by a prior run; the path will diverge if re-run.

---

### `scripts/evaluate_candidates.py`

**Purpose:** Loads ML predictions for all compositions, runs each true HEA through the 1D thermoelastic FEA surrogate across 4 ceramic types and 4 gradient exponents, applies safety factor filtering (SF ≥ 1.45), and writes the top 50 candidates ranked by lowest interface stress.

**Inputs:**
- `models/ml_predictions.csv` — resolved as `Path(__file__).parent.parent / 'models' / 'ml_predictions.csv'`; correct given script is in `scripts/`

**Outputs:**
- `models/top_50_candidates.csv` — resolved as `Path(__file__).parent.parent / 'models' / 'top_50_candidates.csv'`; correct

**Key functions:**
- `temperature_corrected_ys(ys_rt, T=1400)` — scales room-temperature yield strength to high-temperature value using: `knockdown = max(0.3, 1.0 - 0.8 × T/3290)`; at T=1400K this gives knockdown ≈ 0.66, so YS_hot ≈ 0.66 × YS_RT
- `run_screening()` — main loop: filters for true HEAs (all 5 Mo/Nb/Ta/W/Cr fractions > 0); iterates over `ceramics = ['ZrO2-HfO2', 'GZO', 'LZO', 'SrZrO3']` and `exponents = [0.5, 1.0, 2.0, 4.0]`; calls `solve_1d_thermoelastic_surrogate()`; computes SF = YS_hot / stress; filters by SF ≥ 1.45; saves top 50 sorted by minimum stress

**Imported from other scripts:**
- `run_1d_fea.solve_1d_thermoelastic_surrogate` — the actual stress solver
- Note: uses `sys.path.append(os.path.dirname(os.path.abspath(__file__)))` to import from the same `scripts/` directory

**Critical known issues:**
- `top_50_candidates.csv` is currently empty — no candidate met the SF ≥ 1.45 threshold. Root cause: `predicted_yield_strength_MPa` values from the GB model are unreliable (over- or under-estimated due to synthetic/limited training data), producing SFs that fail the threshold.
- The true HEA filter requires ALL of `Mo_frac, Nb_frac, Ta_frac, W_frac, Cr_frac > 0` — but the stage1 optimizer found a Ta–W–Cr–V–Ti–Hf family that has Mo_frac=0, Nb_frac=0. Those compositions are invisible to this screening step entirely.

---

### `scripts/run_1d_fea.py`

**Purpose:** Implements the 1D reduced-order thermoelastic FEA surrogate that is the core physics engine for all candidate scoring scripts. Solves steady-state heat conduction and constrained thermoelastic stress across a 5mm gradient, applies a Coble creep relaxation approximation, and returns peak interface stress in MPa.

**Inputs:** Called as a module; no file I/O. Takes HEA properties and ceramic type as arguments.

**Outputs:** Returns a float (peak stress in MPa). No files written.

**Key constants:**
- `L_GRADIENT = 5e-3` m (5mm)
- `NODES = 51` (0.1mm spacing)
- `T_COLD = 300` K, `T_HOT = 1400` K
- `CERAMIC_MATERIALS` — dict with k (W/mK), alpha (CTE, /K), E (Pa) for: ZrO2-HfO2, GZO, LZO, SrZrO3

**Key functions:**
- `generate_gradient_mesh(n_nodes)` — returns `np.linspace(0, 5e-3, 51)`
- `get_component_fractions(x, exponent)` — power-law FGM: `ceramic_frac = (x/L)^n`; `hea_frac = 1 - ceramic_frac`
- `extract_coble_creep_stress(T, t, sigma, grain_size)` — placeholder; returns `sigma × 0.85` (hardcoded 15% relaxation; grain_size argument has no effect)
- `solve_1d_thermoelastic_surrogate(hea_E, hea_alpha, hea_k, ceramic_type, n_exponent, grain_size)` — full solver pipeline:
  1. Builds position-dependent E(x), α(x), k(x) arrays using Reuss bound mixing
  2. Solves steady-state heat conduction via tridiagonal matrix (T_HOT at x=0, T_COLD at x=L)
  3. Computes free thermal stress: `σ_free = -E(x) × α(x) × (T(x) - T_cold)`
  4. Enforces force equilibrium: `C = -∫σ_free dx / L`; `σ = σ_free + C`
  5. Applies Coble creep relaxation: nodes where T > 1200K get σ × 0.85
  6. Returns `max(|σ_relaxed|) / 1e6 × 1.3` (Pa→MPa, then ×1.3 edge stress concentration factor)

**Critical known issues:**
- Thermal-only stress model. Centrifugal load (15,000 RPM) and gas pressure (2.5 MPa) are entirely absent. The reported safety factors are therefore upper bounds — realistically 30–50% lower under combined loading.
- Coble creep is a fixed 15% scalar; grain size has no effect. This is a placeholder, not a real creep model.
- The ×1.3 edge stress concentration factor is an empirical fudge; it is not derived from geometry.
- `FENICS_AVAILABLE` flag is set but FEniCS is never actually used — the solver is pure numpy throughout.

---

### `scripts/generate_manufacturing_recipe.py`

**Purpose:** Reads the top candidate from `top_50_candidates.csv` and expands it into an 11-layer manufacturing recipe with volume fractions at each depth position, using the candidate's gradient exponent.

**Inputs:**
- `models/top_50_candidates.csv` — read via `os.path.join('models', 'top_50_candidates.csv')`; resolves relative to CWD, so must be run from repo root

**Outputs:**
- `models/top1_manufacturing_recipe.csv` — same relative path logic

**Key logic:**
- `generate_layer_recipe()` — reads best row (iloc[0]); creates 11 layers at `np.linspace(0, 5.0, 11)` mm; computes `v_ceramic = (depth/5.0)^n` and `v_metal = 1 - v_ceramic`; writes recipe DataFrame

**Current state:** The file on disk (`top1_manufacturing_recipe.csv`) was generated from a stale run where the top candidate was `Mo0.05Nb0.80Ta0.05W0.05Cr0.05` — 80% Nb, which is not a true HEA. This recipe is physically invalid.

---

### `scripts/differential_evolution_search.py`

**Purpose:** Unconstrained 9-element Differential Evolution search to maximize safety factor. Uses softmax parametrisation to ensure fractions sum to 1. Applies only a HEA definition penalty (requires ≥5 elements above 5%).

**Inputs:** No file inputs. Trains models on-the-fly by calling `load_and_prepare_base_data()` and `load_experimental_data()` from `train_composition_ml`.

**Outputs:** Results printed to stdout only. No CSV written.

**Key logic:**
- `objective(x)` — softmax transforms 9 unbounded values to fractions; penalises non-HEA compositions (returns 100.0); predicts bulk modulus and YS via trained models; computes 1D FEA stress; returns `-safety_factor`
- DE settings: `strategy='best1bin'`, `maxiter=50`, `popsize=15`
- `_get_k(row)` — Rule-of-Mixtures thermal conductivity with 0.6× multi-element penalty
- `_get_cte(row)` — Rule-of-Mixtures CTE for all 9 elements

**Note:** This is the unconstrained version. It can converge to compositions where one element dominates (as happened with Nb→80%). `stage1_optimizer_with_constraints.py` adds physics-motivated penalties to prevent this.

---

### `scripts/stage1_optimizer_with_constraints.py`

**Purpose:** Constrained 9-element Differential Evolution search. Adds explicit engineering penalties to the objective to steer the optimizer toward physically viable aerospace compositions.

**Inputs:** Same as `differential_evolution_search.py` — trains models on-the-fly.

**Outputs:** Results printed to stdout only. No CSV written.

**Constraints implemented in `objective(x)`:**
- HEA definition: ≥5 elements ≥5% (penalty 1000.0 if violated)
- Sigma phase formers (W+Cr+Mo): penalty +5.0 if >50%, +2.5 if >40%
- Vanadium (oxidation risk): penalty +5.0 if V>20%, +2.0 if V>15%
- Chromium minimum (oxidation protection): penalty +5.0 if Cr<15%
- Density: penalty +2.0 if estimated density >11.0 g/cm³

**DE settings:** `maxiter=200`, `popsize=20` — more thorough than unconstrained version.

**This script is the origin of the `Ta–W–Cr–V–Ti–Hf` composition family** reported in `docs/final_result.md` and validated by Bohrium. It does not write the result to disk — that composition must be manually recorded from stdout.

---

### `scripts/search_new_elements.py`

**Purpose:** Monte Carlo random search over 9 elements using Dirichlet-sampled compositions. Generates 10,000 random HEA compositions, evaluates each through the ML + 1D FEA pipeline, and reports any that exceed SF ≥ 1.5.

**Inputs:** Trains models on-the-fly (same as DE scripts).

**Outputs:**
- `models/expanded_winners.csv` — written only if any composition achieves SF ≥ 1.5; resolved as `Path(__file__).parent.parent / 'models' / 'expanded_winners.csv'`; correct path given script is in `scripts/`
- Results also printed to stdout

**Key functions:**
- `generate_random_compositions(num_samples=10000)` — samples from `np.random.dirichlet(np.ones(9), 10000)`; flags true HEAs (≥5 elements above 5%); returns DataFrame
- `optimize_search()` — filters to true HEAs; downsamples to max 2000; batch-predicts properties; runs 1D FEA for LZO at n=[1.0, 2.0]; reports max SF found; saves winners if any

**Note:** Only tests LZO ceramic at two gradient exponents (1.0 and 2.0). Less thorough than `evaluate_candidates.py` but covers 9-element space.

---

### `scripts/active_learning_bo.py`

**Purpose:** Scaffold for a cost-aware Multi-Fidelity Bayesian Optimisation (MFBO) surrogate using a Gaussian Process with Matérn kernel. Not connected to the main pipeline — exists as a callable class for future integration.

**Inputs:** Takes a CSV `data_path` at instantiation; reads it into a DataFrame (unused in current implementation).

**Outputs:** None. No files written.

**Key class: `CostAwareMFBOSurrogate`**
- `__init__(data_path)` — initialises GP with `ConstantKernel × Matérn(ν=2.5) + WhiteKernel`; initialises empty training lists
- `update_model(X_new, y_new)` — appends new observation, tracks `y_best`, re-fits GP
- `expected_improvement(X_candidate, xi=0.01)` — standard EI for minimisation: `EI = Δ·Φ(Z) + σ·φ(Z)` where `Δ = y_best - μ - xi`
- `expected_improvement_per_cost(X_candidate, fea_cost=1.0)` — cost-aware EI: `EI / fea_cost`
- `suggest_next(X_candidates, fea_cost)` — scans array of candidates, returns the one with highest EI/cost

**Status: Scaffold only.** No script in the pipeline calls this class. It is not integrated with the FEA solver or any data source. Would require a complete integration wrapper to be functional.

---

### `scripts/stage2_gradient_optimization.py`

**Purpose:** Standalone script that sweeps gradient exponent n from 0.1 to 4.0 and FGM thickness from 2–8mm to find the combination minimising inter-layer interface stress. Uses hardcoded alloy and LZO properties — not connected to the ML pipeline.

**Inputs:** None. All material properties are hardcoded:
- `alloy_CTE = 6.27` µm/mK
- `LZO_CTE = 9.1` µm/mK
- `E_metal = 280 GPa`, `E_ceramic = 210 GPa`
- `delta_T = 1100` K

**Outputs:** Prints results to stdout. No files written.

**Key function:**
- `calculate_interface_stress(n, total_thickness=5.0)` — computes stress at each 0.1mm position from CTE mismatch across adjacent layers: `σ = E1 × |ΔCTE| × ΔT × 1e-6`; returns maximum across all positions

**Note:** This script runs at import time — the sweep and print statements execute at module level, not inside a `main()` guard. Importing this module will immediately run and print output.

---

### `scripts/calphad_validation.py`

**Purpose:** Full CALPHAD equilibrium phase calculation using pycalphad and the TCHEA4 thermodynamic database. Checks phase stability at 1400K for the near-equimolar `Mo0.05Nb0.80Ta0.05W0.05Cr0.05` composition (the current — flawed — top candidate).

**Inputs:**
- `TCHEA4.TDB` — proprietary thermodynamic database; not in repo; must be obtained separately

**Outputs:** Prints equilibrium phase fractions at 1400K to stdout. No files written.

**Key function:**
- `run_calphad_simulation(tdb_path)` — checks for TDB file existence; gracefully warns and returns if missing; otherwise loads database via `pycalphad.Database`, runs `equilibrium()` at T=1400K, P=101325 Pa for the hardcoded composition; prints phase names and fractions

**Critical issues:**
- `TCHEA4.TDB` is not present in the repo. The script will always print a warning and exit.
- The hardcoded composition still reflects the old Nb-dominant candidate, not the Bohrium-validated `Ta–W–Cr–V–Ti–Hf` composition.

---

### `scripts/stage5_sustainability.py`

**Purpose:** Runs the Gorsse 2025 AlloySustainability framework on the Bohrium-validated composition to compute embodied energy, supply risk, and other sustainability indicators.

**Inputs:** None at runtime. Composition is hardcoded as a mass-fraction vector.

**Outputs:** Prints sustainability impact results to stdout. No files written.

**Hardcoded composition (mass fractions, 18-element order):**
- Cr: 0.27, Hf: 0.18, Ta: 0.16, Ti: 0.13, V: 0.15, W: 0.11 (all others 0.0)

**Critical issue:** Requires `from AlloySustainability.computations import ...` which is not a standard pip package. Will crash with `ModuleNotFoundError` unless manually installed.

---

## 2. phase_wise_analysis/ — Validation and Phase-Gate Scripts

---

### `phase_wise_analysis/phase1_calphad_phase_validation.py`

**Purpose:** Implements a Gibbs free energy proxy CALPHAD validation — a lightweight substitute for real pycalphad. Computes dS_mix, a hardcoded dH_mix, VEC, atomic size mismatch δ, and a Gibbs sweep from 300K to 3000K. Produces a validation plot. Acts as a phase-gate: returns True/False.

**Inputs:** None at runtime. Default composition is hardcoded: `{'Ta':0.16, 'W':0.11, 'Cr':0.27, 'V':0.15, 'Ti':0.13, 'Hf':0.18, 'Al':0.01}`.

**Outputs:**
- `phase_wise_analysis/phase1_calphad_validation_curve.png` — Gibbs free energy vs temperature plot with 1400K and solidus markers; written via relative path, so must be run from repo root

**Key function:**
- `validate_phase_stability(composition)` — computes: ideal ΔSmix (−R Σ c·ln(c)); Tm_mix by Rule of Mixtures; VEC; atomic size mismatch δ; hardcoded ΔHmix = −8500 J/mol; G(T) = ΔH − T·ΔSmix sweep; solidus proxy = Tm_mix × 1.05; passes if VEC < 6.8 AND solidus > 1400K

**Critical limitation:** ΔHmix is hardcoded at −8500 J/mol for all compositions — it does not depend on the actual composition input. This is a significant approximation; the real enthalpy should be composition-dependent via binary interaction parameters.

---

### `phase_wise_analysis/execute_phases_2_to_5.py`

**Purpose:** Reporter script that prints pre-written phase results (2–5) from the Bohrium validation campaign. **Not a live simulation** — all numbers are hardcoded constants.

**Inputs:** None.

**Outputs:** Prints to stdout only. No files written.

**Hardcoded values:**
- Phase 2 FEA: von Mises stress = 798.0 MPa, YS = 917.7 MPa, SF = 1.15 → FAIL
- Phase 3 MD/Gradient: optimal n=1.10, h=5.00mm, interface stress=15.95 MPa → PASS
- Phase 4 Oxidation: 1% Al → FAIL; 2.8% Al → PASS
- Phase 5: Failure mode table and TRL-4 transition narrative

**Status: Illustrative output only.** The safety factor of 1.15 and stress of 798 MPa are results from an external Bohrium simulation, not computed by this codebase.

---

### `phase_wise_analysis/execute_phases_6_to_11.py`

**Purpose:** Reporter script that prints pre-written phase results (6–11). **Not a live simulation** — all numbers are hardcoded constants from the post-Bohrium analysis.

**Inputs:** None.

**Outputs:** Prints to stdout only. No files written.

**Hardcoded content:**
- Phase 6: Al fix (1% → 2.8%) and geometry fix (root smoothing r=3.5mm, film cooling)
- Phase 7: Cost estimate $201/kg, budget ₹20,00,000
- Phase 8: Interface stress 15.95 MPa, safety factor 1.66 (post-geometric-fix)
- Phase 9: Monte Carlo tolerance results (±0.1 exponent → ±1.2 MPa)
- Phase 10 & 11: Final composition and submission status

**Status: Illustrative output only.**

---

## 3. data/ — Intermediate and Processed Data CSVs

| File | Rows | Columns | Description |
|---|---|---|---|
| `combined_raw_data.csv` | 91 | 7 | MP + OQMD entries after strict element filter: formula, formation_energy, energy_hull, bulk_modulus, shear_modulus, density, source |
| `raw_materials_project.csv` | 91 | 7 | MP-only entries (same schema as above) |
| `raw_oqmd.csv` | 31 | 8 | OQMD entries; includes volume, ntypes, band_gap; **no bulk_modulus column** |
| `raw_jarvis.csv` | 0 | 7 | Empty — JARVIS fetch failed |
| `processed_candidate_properties.csv` | 54 | 13 | After `calculate_properties.py`: formula, formation_energy, energy_hull, bulk_modulus, shear_modulus, density, source, composition (dict), volume, ntypes, elastic_modulus, thermal_conductivity, CTE |
| `all_compositions-generated.csv` | 10,626 | 8 | Full Mo–Nb–Ta–W–Cr fractional grid: formula, Mo_frac, Nb_frac, Ta_frac, W_frac, Cr_frac, n_elements, is_true_hea |
| `stable_compositions.csv` | 10,626 | 14 | Same as above + Miedema parameters: delta, Hmix, Smix, VEC, Tm_avg, omega. All 10,626 rows pass all filters. |
| `EXP-MPEA_dataset.csv` | 1,545 | 23 | Experimental MPEA dataset: FORMULA, YS (MPa), test temperature, UTS, elongation, density, Young's modulus, processing method, grain size, etc. |

---

## 4. models/ — ML Model Artefacts and Final Scored Outputs

| File | Description |
|---|---|
| `composition_model.pkl` | Trained `RandomForestRegressor` + `StandardScaler` for bulk modulus prediction. Produced by `train_composition_ml.py`. May have been trained on synthetic data. |
| `ml_predictions.csv` | 10,626 rows. Columns: all columns from `stable_compositions.csv` plus V_frac, Ti_frac, Zr_frac, Hf_frac (all zero — these elements not in the 5-element grid), predicted_bulk_modulus, predicted_yield_strength_MPa, predicted_thermal_cond, predicted_CTE |
| `top_50_candidates.csv` | **EMPTY** — header row only. `evaluate_candidates.py` ran but no composition achieved SF ≥ 1.45. |
| `top1_manufacturing_recipe.csv` | 11 layers. Formula column shows `Mo0.05Nb0.80Ta0.05W0.05Cr0.05` — **invalid composition** (Nb=80% violates HEA definition). Must be regenerated after fixing ML data quality and re-running the pipeline. |

---

## 5. bin/ — Raw Fetch Artefacts and Utility Scripts

| File | Description |
|---|---|
| `api.txt` | OQMD API documentation + JARVIS database index + MP API key (`REVOKED_KEY_REMOVED_USE_MP_API_KEY`) |
| `combined_raw_data.csv` | Earlier MP-only combined fetch — 262 rows before strict element filtering |
| `combined_raw_data-MP.csv` | MP-only 91-row copy (post-filter) |
| `raw_materials_project.csv` | MP raw 262-row version (pre-strict-filter) |
| `raw_oqmd.csv` | 31 OQMD rows (copy of `data/raw_oqmd.csv`) |
| `raw_jarvis.csv` | 0 rows (copy of `data/raw_jarvis.csv`) |
| `processed_candidate_properties-MP.csv` | 91-row processed MP copy (all with real bulk modulus from MP) |
| `EXP-GE_RefractoryAlloyScreeningDataset_FINAL.csv` | 86 GE refractory alloy records: Hf/Mo/Nb/Re/Ru/Ta/Ti/W/Zr at%, plus ductility ranking (0-5), predicted solidus (°C), hardness (GPa) |
| `test_exp.py` | One-off probe script: filters `EXP-MPEA_dataset.csv` to Mo/Nb/Ta/W/Cr-only rows; filters GE dataset to target-element-only rows; prints results. Uses bare CSV paths — must be run from `bin/`. |
| `update_ml.py` | One-time patch script: appends the `load_experimental_data()` function text to `train_composition_ml.py`. Was run once; the function is already in the current `train_composition_ml.py`. Running again would duplicate the function. |
| `train_composition_ml.bak` | Backup of `train_composition_ml.py` taken before `update_ml.py` ran. |
| `EXP-HEA_database/HEA_database/database_of_HEAs.csv` | 12,427 literature HEA phase records: alloy, number of phases, phase type (BCC/FCC/etc.), experimental or theoretical, processing details |
| `EXP-HEA_database/HEA_database/database_of_raw_responses.csv` | 58 MB raw scraped data — excluded from KB per `NOTE.txt`; not processed by any script |

---

## 6. Cross-Script Dependencies Map

```
fetch_datasets.py
    └─► combined_raw_data.csv (data/)
            └─► calculate_properties.py
                    └─► processed_candidate_properties.csv (data/)
                            └─► train_composition_ml.py ◄── EXP-MPEA_dataset.csv (data/)
                                    │                   ◄── stable_compositions.csv (data/)
                                    └─► ml_predictions.csv (models/)
                                                └─► evaluate_candidates.py ◄── run_1d_fea.py
                                                        └─► top_50_candidates.csv (models/) [EMPTY]
                                                                └─► generate_manufacturing_recipe.py
                                                                        └─► top1_manufacturing_recipe.csv (models/) [INVALID]

generate_compositions.py
    └─► all_compositions-generated.csv (data/)
            └─► empirical_filter.py
                    └─► stable_compositions.csv (data/)

── OPTIMISATION PATH (independent of main pipeline) ──
stage1_optimizer_with_constraints.py
    ├─► imports train_composition_ml (trains models on-the-fly)
    ├─► imports run_1d_fea
    └─► stdout only (no CSV written)
        └─► [Ta-W-Cr-V-Ti-Hf composition identified — must be recorded manually]
                └─► phase1_calphad_phase_validation.py (manual input)
                └─► execute_phases_2_to_5.py (hardcoded Bohrium results)
                └─► execute_phases_6_to_11.py (hardcoded Bohrium results)

── SCAFFOLD (not connected) ──
active_learning_bo.py  [class defined; never called by any script]
```
