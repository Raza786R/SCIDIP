# DATA_GUIDE.md — HE-MCGA CSV Reference
Generated: May 2026
Scope: Every CSV in data/, models/, bin/
Authority: Derived from actual file contents cross-checked against consuming scripts.

Legend for Data Source:
  MP   = Materials Project DFT database (real ab initio calculations)
  OQMD = Open Quantum Materials Database (real ab initio calculations)
  SYN  = Synthetic / Rule-of-Mixtures (not real DFT, computed by codebase)
  EXP  = Experimental measurements from published literature
  ML   = Machine learning prediction (surrogate, not physics)
  GEN  = Algorithmically generated (combinatorial grid, no physics)

---

## data/ folder

---

### data/combined_raw_data.csv
Rows: 91 | Columns: 7

| Column | Type | Materials Science Meaning | Source |
|---|---|---|---|
| formula | string | Chemical formula of the compound (e.g. "MoCr2", "NbW") | MP |
| formation_energy | float (eV/atom) | Energy released when compound forms from pure elements. Negative = thermodynamically favourable. More negative = more stable. | MP |
| energy_hull | float (eV/atom) | Distance above the convex hull of stability. 0 = on the hull (stable). >0.1 = likely to decompose. | MP |
| bulk_modulus | float (GPa) | Resistance to uniform compression (Voigt-Reuss-Hill average). Higher = stiffer. Refractory metals: 150–320 GPa range. | MP |
| shear_modulus | float (GPa) | Resistance to shear deformation (VRH average). Relates to hardness. | MP |
| density | float (g/cm³) | Mass per unit volume. Aerospace limit: <11.0 g/cm³ for turbine blades. | MP |
| source | string | Always "materials_project" in this file. | — |

Quality issues:
- All 91 rows are from Materials Project only. OQMD returned 31 rows (in raw_oqmd.csv)
  but they lack bulk_modulus and shear_modulus, so they do not survive the
  calculate_properties.py dropna step and are absent here after merging.
- JARVIS returned 0 rows (fetch failure). AFLOW status unknown.
- This is binary/ternary DFT data only. No true 5-element fractional HEA data exists
  in any public database — this is the core data gap the ML pipeline tries to bridge.
- 54 of 91 entries have non-null bulk_modulus (the rest have bulk_modulus=NaN).

Scripts that consume this file:
- scripts/calculate_properties.py — reads it as primary input. Expects columns:
  formula, bulk_modulus, shear_modulus, density, volume, ntypes.
  MISMATCH: volume and ntypes are NOT present in this file. calculate_properties.py
  fills them with placeholders (volume=15.0, ntypes=2) when missing. This means
  Debye temperature and Slack thermal conductivity are computed from placeholder
  geometry, not real crystal data.

---

### data/raw_materials_project.csv
Rows: 91 | Columns: 7
Identical schema and content to data/combined_raw_data.csv (same 91 MP rows).
This is the MP-only copy before any merge. Currently combined_raw_data.csv is
also MP-only because no other sources contributed rows.

Scripts that consume this file: None directly. It is an intermediate output of
fetch_datasets.py that combined_raw_data.csv is built from.

---

### data/raw_oqmd.csv
Rows: 31 | Columns: 8

| Column | Type | Materials Science Meaning | Source |
|---|---|---|---|
| formula | string | Compound formula | OQMD |
| entry_id | int | OQMD internal record identifier | OQMD |
| volume | float (Å³/cell) | Unit cell volume from DFT relaxation | OQMD |
| ntypes | int | Number of distinct element species in the cell | OQMD |
| band_gap | float (eV) | Electronic band gap. Metals = 0. Used to confirm metallic character. | OQMD |
| formation_energy | float (eV/atom) | Formation energy (renamed from delta_e by fetch_datasets.py) | OQMD |
| energy_hull | float (eV/atom) | Hull stability (renamed from stability) | OQMD |
| source | string | Always "oqmd" | — |

Quality issues:
- NO bulk_modulus or shear_modulus columns. This is an OQMD API limitation — elastic
  constants are not exposed through the REST endpoint queried. This means all 31 OQMD
  rows are dropped by calculate_properties.py at the `df.dropna(subset=['bulk_modulus'])`
  step and contribute nothing to processed_candidate_properties.csv.
- The OQMD query uses element_set=(Mo-Nb-Ta-W-Cr) — 5-element AND filter — so V, Ti,
  Zr, Hf are absent from OQMD data even though they are in the fetch target set.
- volume column (cell volume, Å³/cell) is a different unit than what
  calculate_properties.py expects (Å³/atom). No per-atom normalisation is performed.

Scripts that consume this file: Nominally included in the fetch pipeline but effectively
unused downstream due to the missing bulk_modulus issue.

---

### data/raw_jarvis.csv
Rows: 0 | Columns: 7
Empty file. The JARVIS OPTIMADE fetch failed (SSL/endpoint issue in fetch_datasets.py).
Headers: formula, formation_energy, density, volume, bulk_modulus, shear_modulus, source.
No data. Contributes nothing to any downstream step.

Scripts that consume this file: fetch_datasets.py writes it; nothing reads it
because it is immediately filtered out by the `if not df.empty` guard in main().

---

### data/processed_candidate_properties.csv
Rows: 54 | Columns: 13

| Column | Type | Materials Science Meaning | Source |
|---|---|---|---|
| formula | string | Compound formula | MP |
| formation_energy | float (eV/atom) | DFT formation energy | MP |
| energy_hull | float (eV/atom) | Hull stability | MP |
| bulk_modulus | float (GPa) | DFT bulk modulus (VRH) | MP (real) |
| shear_modulus | float (GPa) | DFT shear modulus — PLACEHOLDER 80.0 GPa for rows missing it | MP / SYN |
| density | float (g/cm³) | DFT density — PLACEHOLDER 9.0 g/cm³ for rows missing it | MP / SYN |
| source | string | "materials_project" or "oqmd" | — |
| composition | string (dict repr) | Python dict of element fractions parsed from formula | SYN |
| volume | float (Å³/atom) | PLACEHOLDER 15.0 for rows missing it | MP / SYN |
| ntypes | float | PLACEHOLDER 2 for rows missing it | MP / SYN |
| elastic_modulus | float (GPa) | E = 9KG/(3K+G). Derived from bulk+shear modulus. | SYN (derived) |
| thermal_conductivity | float (W/mK) | Slack lattice thermal conductivity at T=1000K. Estimated. | SYN (Slack model) |
| CTE | float (µm/m/K) | Coefficient of thermal expansion, Rule of Mixtures. Estimated. | SYN (ROM) |

Quality issues:
- Only 54 of the 91 raw MP rows survive (those with non-null bulk_modulus).
- shear_modulus is filled with 80.0 GPa placeholder for missing rows. This is a
  rough BCC refractory average but introduces systematic error in elastic_modulus,
  Poisson's ratio, Debye temperature, and all downstream Slack conductivity estimates.
- density placeholder 9.0 g/cm³ is similarly rough; affects Debye temperature.
- volume placeholder 15.0 Å³/atom is a BCC refractory average; affects Slack model.
- CTE column: MISMATCH with calculate_properties.py's ELEMENT_CTE dict.
  Dict contains Mo, Nb, Ta, W, Cr, Zr, Hf (7 elements) but NOT V or Ti.
  If any raw compound contained V or Ti, its CTE would be underestimated.
  Compounds from the 9-element ELEMENTS list in fetch_datasets.py could include V/Ti.
- thermal_conductivity values are Slack model at T=1000K, not the turbine operating
  temperature of 1400K. The Slack model has 1/T dependence so values at 1400K
  would be ~1000/1400 = 0.71× lower.

Scripts that consume this file:
- scripts/train_composition_ml.py — reads as BASE_DATA_FILE.
  Expects: formula, bulk_modulus, and any {el}_frac columns.
  MISMATCH: the file stores composition as a string representation of a Python dict
  (e.g., "{'Mo': 0.5, 'Cr': 0.5}"), not as individual Mo_frac, Nb_frac etc. columns.
  train_composition_ml.py calls parse_formula_to_fractions(formula) to regenerate
  fractions from the formula string, bypassing the composition column entirely.
  The composition column is therefore unused and its format mismatch is harmless
  but wasteful.

---

### data/all_compositions-generated.csv
Rows: 10,626 | Columns: 8

| Column | Type | Materials Science Meaning | Source |
|---|---|---|---|
| formula | string | Human-readable formula e.g. "Mo0.20Nb0.20Ta0.20W0.20Cr0.20" | GEN |
| Mo_frac | float [0,1] | Molar fraction of Molybdenum. Refractory metal, high Tm=2896K, K=230GPa. | GEN |
| Nb_frac | float [0,1] | Molar fraction of Niobium. Good ductility, lower density=8.6g/cm³. | GEN |
| Ta_frac | float [0,1] | Molar fraction of Tantalum. Highest Tm in system=3290K. Expensive. | GEN |
| W_frac | float [0,1] | Molar fraction of Tungsten. Highest K=310GPa, highest Tm=3695K. Dense=19.3g/cm³. | GEN |
| Cr_frac | float [0,1] | Molar fraction of Chromium. Primary oxidation protection via Cr2O3. | GEN |
| n_elements | int [1,5] | Count of elements with non-zero fraction. 5 = quinary/true HEA candidate. | GEN |
| is_true_hea | bool | True if ALL five elements are >= 5 at%. Missing upper bound of 35% — see flaws. | GEN |

Quality issues:
- 5-element Mo-Nb-Ta-W-Cr grid only. No V, Ti, Zr, Hf columns. This means the
  Bohrium-validated Ta-W-Cr-V-Ti-Hf composition CANNOT appear in this file.
  The 9-element search happens only through stage1_optimizer_with_constraints.py,
  which does not write to any CSV.
- is_true_hea flag is missing the 35% upper bound per element (FIX-14 addresses this).
  A composition with Mo=0.90 would incorrectly have is_true_hea=False only because
  Mo<0.05 is false, but the flag itself is computed from the lower bound check only.
  Wait — re-reading: is_true_hea = all(f >= MIN_FRAC for f in comp). If Mo=0.90,
  then all fracs >= 0.05 would be True (0.90 >= 0.05), so is_true_hea=True even at
  90% — this is the bug. The 35% cap is missing.
- Fractions are at 5% increments (step=0.05), rounded to 3 decimal places.
  Total compositions = stars-and-bars C(24,4) = 10,626. Correct.

Scripts that consume this file:
- scripts/empirical_filter.py — reads INPUT_FILE. Currently reads from wrong path
  (scripts/ not data/) — see B2. After FIX-3, path is correct.
  Expects columns: Mo_frac, Nb_frac, Ta_frac, W_frac, Cr_frac. These all exist. OK.

---

### data/stable_compositions.csv
Rows: 10,626 | Columns: 14

| Column | Type | Materials Science Meaning | Source |
|---|---|---|---|
| formula … Cr_frac, n_elements, is_true_hea | same as all_compositions-generated.csv | | GEN |
| delta | float (%) | Atomic size mismatch. <6.6% required for BCC solid solution. All rows pass. | SYN (Miedema) |
| Hmix | float (kJ/mol) | Mixing enthalpy. Negative = exothermic mixing = stable. Range [-15,5] required. | SYN (Miedema) |
| Smix | float (J/mol/K) | Ideal mixing entropy = -R Σ ci ln ci. Higher = more disordered = more HEA-like. | SYN (Miedema) |
| VEC | float | Valence electron concentration = Σ ci·VECi. [4.0,6.8] targets BCC structure. | SYN (Miedema) |
| Tm_avg | float (K) | Rule-of-Mixtures average melting temperature. Higher is better for turbines. | SYN (ROM) |
| omega | float | Ω = ΔSmix·Tm / |ΔHmix|. >1.1 favours single-phase solid solution. | SYN (Miedema) |

Quality issues:
- ALL 10,626 rows pass all four filters. The five BCC refractory metals are too
  chemically similar for these Miedema criteria to reject anything in this space.
  This file is effectively identical to all_compositions-generated.csv plus six
  computed columns. It provides zero pre-screening.
- The omega column returns 999 when |Hmix| < 0.01 kJ/mol (div-by-zero guard in
  calculate_omega). Many near-equimolar compositions get omega=999, which inflates
  their apparent stability ranking.
- Hmix values depend on BINARY_ENTHALPY lookup table in empirical_filter.py.
  The (W, Cr) pair has H=+1 kJ/mol (slightly positive = repulsive), which is
  physically significant for sigma-phase risk but is swamped by the [-15,5]
  acceptance window. The filter would need tightening to HMIX_MAX=0 to actually
  flag W-Cr-rich compositions.

Scripts that consume this file:
- scripts/train_composition_ml.py — reads as STABLE_COMPOSITIONS_FILE.
  Expects columns: formula, Mo_frac, Nb_frac, Ta_frac, W_frac, Cr_frac,
  and optionally V_frac, Ti_frac, Zr_frac, Hf_frac.
  MISMATCH: V_frac, Ti_frac, Zr_frac, Hf_frac are absent (this is a 5-element
  grid file). train_composition_ml.py handles this with:
    for el in ALL_ELEMENTS:
        if f"{el}_frac" not in compositions_df.columns:
            compositions_df[f"{el}_frac"] = 0.0
  So V/Ti/Zr/Hf fractions are all set to 0.0 for every row, then used in
  estimate_cte() and estimate_thermal_conductivity() — which already silently
  zero those elements (FIX-6, FIX-7 address this but the zero-fill here means
  even after those fixes, the predictions in ml_predictions.csv for the 5-element
  grid will correctly have zero V/Ti/Zr/Hf contributions, which is accurate for
  this grid. The problem only arises when the 9-element Bohrium composition is
  evaluated outside this grid via the optimisation scripts.)

---

### data/EXP-MPEA_dataset.csv
Rows: 1,545 | Columns: 23

| Column | Type | Materials Science Meaning | Source |
|---|---|---|---|
| IDENTIFIER | int | Reference ID linking to source paper | EXP |
| FORMULA | string | Alloy composition formula | EXP |
| PROPERTY: Microstructure | string | Observed phases (BCC, FCC, mixed, etc.) | EXP |
| PROPERTY: Processing method | string | How alloy was made (arc melting, SPS, etc.) | EXP |
| PROPERTY: BCC/FCC/other | string | Crystal structure category | EXP |
| PROPERTY: grain size (µm) | float | Average grain size. Affects creep, fatigue. | EXP |
| PROPERTY: Exp. Density (g/cm³) | float | Measured density | EXP |
| PROPERTY: Calculated Density (g/cm³) | float | Rule-of-Mixtures density for verification | EXP/SYN |
| PROPERTY: HV | float | Vickers Hardness. Correlates with YS ≈ HV×3 MPa roughly. | EXP |
| PROPERTY: Type of test | string | Compression / tension / nanoindentation | EXP |
| PROPERTY: Test temperature (°C) | float | Temperature at which mechanical test was performed | EXP |
| PROPERTY: YS (MPa) | float | Yield strength. PRIMARY TARGET for the GB model. | EXP |
| PROPERTY: UTS (MPa) | float | Ultimate tensile strength | EXP |
| PROPERTY: Elongation (%) | float | Ductility. Refractory HEAs typically low (<5%) at RT. | EXP |
| PROPERTY: Elongation plastic (%) | float | Plastic elongation component | EXP |
| PROPERTY: Exp. Young modulus (GPa) | float | Measured elastic modulus | EXP |
| PROPERTY: Calculated Young modulus (GPa) | float | Predicted elastic modulus | EXP/SYN |
| PROPERTY: O content (wppm) | float | Oxygen contamination level | EXP |
| PROPERTY: N content (wppm) | float | Nitrogen contamination level | EXP |
| PROPERTY: C content (wppm) | float | Carbon contamination level | EXP |
| REFERENCE: doi | string | Source paper DOI | — |
| REFERENCE: year | int | Publication year | — |
| REFERENCE: title | string | Paper title | — |

Quality issues:
- test_exp.py confirmed ZERO rows contain only Mo/Nb/Ta/W/Cr elements. All 1,545
  rows involve at least one element outside the primary 5-element system. This means
  the transfer-learning weight=10 anchor mechanism in load_experimental_data() is
  entirely inactive — all training samples get weight=1.
- The dataset covers a broad refractory HEA space (includes Co, Fe, Ni, Al, etc.)
  which provides useful transfer learning signal but no direct Mo-Nb-Ta-W-Cr anchors.
- Test temperatures span -268°C to 1600°C. The model uses test temperature as a
  feature (T_test), which is the right approach for temperature-dependent YS.
- 'PROPERTY: YS (MPa)' has NaN values for rows where only hardness was measured.
  load_experimental_data() skips these with pd.isna(ys) check. OK.

Scripts that consume this file:
- scripts/train_composition_ml.py — reads as mpea_path. Expects columns:
  FORMULA, PROPERTY: YS (MPa), PROPERTY: Test temperature ($^\circ$C).
  Column name match: YES. The LaTeX-style column name
  "PROPERTY: Test temperature ($^\circ$C)" must match exactly — it does.
- scripts/test_exp.py — reads as 'EXP-MPEA_dataset.csv' with bare path.
  Must be run from bin/ where the file lives, or path must be corrected.

---

## models/ folder

---

### models/ml_predictions.csv
Rows: 10,626 | Columns: 22

| Column | Type | Materials Science Meaning | Source |
|---|---|---|---|
| formula … omega | same as stable_compositions.csv (14 cols) | | GEN/SYN |
| V_frac | float | Vanadium fraction — always 0.0 (5-element grid has no V) | GEN |
| Ti_frac | float | Titanium fraction — always 0.0 | GEN |
| Zr_frac | float | Zirconium fraction — always 0.0 | GEN |
| Hf_frac | float | Hafnium fraction — always 0.0 | GEN |
| predicted_bulk_modulus | float (GPa) | Random Forest prediction of bulk modulus. Unreliable — see issues. | ML |
| predicted_yield_strength_MPa | float (MPa) | Gradient Boosting prediction of yield strength. Temperature-dependent. | ML |
| predicted_thermal_cond | float (W/mK) | Rule-of-Mixtures conductivity — ignores V/Ti/Zr/Hf (FIX-7). | SYN |
| predicted_CTE | float (µm/m/K) | Rule-of-Mixtures CTE — ignores V/Ti/Zr/Hf (FIX-6). | SYN |

Quality issues:
- predicted_bulk_modulus: 1,482 true-HEA rows have values ≤ 0 (minimum: -1,920,044 GPa).
  These are Random Forest extrapolation artefacts outside training distribution.
  They crash the FEA solver with negative E_Pa if guard FIX-5 is not applied.
- predicted_yield_strength_MPa: trained on the full MPEA dataset with no Mo/Nb/Ta/W/Cr-
  only anchors (weight=10 rows = 0). Values should be treated as transfer-learning
  estimates with ±124 MPa uncertainty at 1400K (from Bohrium uncertainty analysis).
- predicted_thermal_cond and predicted_CTE are Rule-of-Mixtures over 5 elements only.
  V_frac, Ti_frac, Zr_frac, Hf_frac columns exist but are all zero, making these
  columns accurate for the 5-element grid but misleading as column names suggest 9-element
  coverage. After FIX-6 and FIX-7, the functions will correctly handle the zero fracs
  and the values will remain unchanged for this file (correctly zero for V/Ti/Zr/Hf).
- predicted_thermal_cond is computed at layer_position=0.0 (pure HEA side) with no
  ceramic radiative contribution. Values represent the metallic end of the gradient only.

Scripts that consume this file:
- scripts/evaluate_candidates.py — reads via Path(__file__).parent.parent / 'models'.
  COLUMN MATCH CHECK:
    Expects: formula, Mo_frac, Nb_frac, Ta_frac, W_frac, Cr_frac (for true_hea_mask),
    predicted_bulk_modulus, predicted_CTE, predicted_thermal_cond,
    predicted_yield_strength_MPa. All present. OK.
  After FIX-4, also expects V_frac, Ti_frac, Zr_frac, Hf_frac for the new mask.
  These columns exist (all zero) — OK.
- scripts/search_new_elements.py — does NOT read ml_predictions.csv. It generates
  its own random compositions in memory and predicts on the fly. No dependency.
- scripts/stage1_optimizer_with_constraints.py — same, in-memory only. No dependency.

---

### models/top_50_candidates.csv
Rows: 0 (header only) | Columns: 7

| Column | Type | Materials Science Meaning | Source |
|---|---|---|---|
| formula | string | Alloy formula of the candidate | GEN/ML |
| ceramic_type | string | Which ceramic was used: ZrO2-HfO2, GZO, LZO, or SrZrO3 | GEN |
| gradient_exponent | float | FGM power-law exponent n in (x/L)^n. 1.0=linear, >1 enriches ceramic at surface. | GEN |
| bulk_modulus_GPa | float (GPa) | Predicted bulk modulus for this alloy | ML |
| yield_strength_MPa | float (MPa) | Predicted room-temperature yield strength | ML |
| interface_stress_MPa | float (MPa) | 1D FEA predicted max interface stress. Lower is better. | ML/SYN |
| safety_factor | float | YS_hot / interface_stress. Must be ≥ 1.45 (pipeline) / 1.50 (Safran). | ML/SYN |

Quality issues:
- EMPTY. No rows. This is the primary broken output of the pipeline.
  Root causes: B1 (FEA crash), FIX-4 missing (filter excludes Bohrium composition),
  and poor ML data quality causing unphysical negative bulk moduli.
- SF threshold is 1.45 in the code but Safran requires 1.50. Silent mismatch.
- interface_stress_MPa is thermal-stress-only (no centrifugal load). Real values
  under combined loading would be ~15-29% higher, dropping safety factors below 1.0.
- Once populated after fixes, this file needs to be treated as a screening shortlist,
  not a validated result. Full 3D FEA (Bohrium-class) is needed on the top 5-10.

Scripts that consume this file:
- scripts/generate_manufacturing_recipe.py — reads via os.path.join('models', ...).
  Expects: gradient_exponent, formula, ceramic_type. Will crash on df.iloc[0] if empty.
  FIX-12 adds the guard.

---

### models/top1_manufacturing_recipe.csv
Rows: 11 | Columns: 6

| Column | Type | Materials Science Meaning | Source |
|---|---|---|---|
| Layer_Index | int [1,11] | Layer number from 1 (innermost, pure HEA) to 11 (outermost, pure ceramic) | GEN |
| Depth_mm | float (mm) | Physical distance from inner blade surface. 0=metal, 5=ceramic. | GEN |
| Alloy_Vol_Percent | float [0,100] | Volume percent of RHEA alloy at this layer depth. | GEN |
| Ceramic_Vol_Percent | float [0,100] | Volume percent of ceramic at this layer depth. Alloy+Ceramic=100%. | GEN |
| Alloy_Formula | string | Alloy formula — currently INVALID: Mo0.05Nb0.80Ta0.05W0.05Cr0.05 | GEN |
| Ceramic_Type | string | Which ceramic — currently from the stale run | GEN |

Quality issues:
- INVALID. Alloy_Formula is Mo0.05Nb0.80Ta0.05W0.05Cr0.05 — 80% Nb violates HEA
  definition (max 35% per element). This was produced by the unconstrained DE script
  in a prior run.
- Must be regenerated after applying all fixes and re-running the full pipeline.
- The 11-layer discretisation is reasonable for manufacturing (LENS/APS can handle
  discrete layer gradients). The volume fraction formula V_ceramic = (depth/5)^n
  with n from top_50_candidates is physically correct if the source candidate is valid.
- Alloy_Vol_Percent + Ceramic_Vol_Percent = 100% at each layer: correct.
- Layer 1 (depth=0): 100% alloy, 0% ceramic. Layer 11 (depth=5): 0% alloy, 100% ceramic.
  Correct boundary conditions for the gradient architecture.

Scripts that consume this file: None in the current pipeline. It is a final output
delivered to the user/Safran. No downstream script reads it.

---

## bin/ folder

---

### bin/combined_raw_data.csv
Rows: 262 | Columns: 7
Schema: identical to data/combined_raw_data.csv.
This is an EARLIER version of the fetch before strict element filtering was applied.
Contains 262 rows including compounds with elements outside the 9-element target set.
After is_allowed() filtering was tightened, the file in data/ was reduced to 91 rows.

Quality issues:
- STALE. Includes compounds with disallowed elements (e.g. Fe, Si). Do not use for
  training — the strict 9-element filter exists for a reason.
- Naming inconsistency: this file and data/combined_raw_data.csv have identical names
  in different directories. Risk of confusion.

Scripts that consume this file: None. Dead artefact from an earlier pipeline run.

---

### bin/combined_raw_data-MP.csv (also referenced as bin/combined_raw_data-MP.csv)
Rows: 91 | Columns: 7
Schema: same as data/raw_materials_project.csv.
This is the MP-only post-filter copy (91 rows). Duplicate of data/raw_materials_project.csv.
No unique content. No scripts consume it.

---

### bin/raw_materials_project.csv
Rows: 262 | Columns: 7
Same as bin/combined_raw_data.csv — the pre-filter 262-row MP dump.
No scripts consume it directly (data/raw_materials_project.csv is the canonical version).

---

### bin/raw_oqmd.csv
Rows: 31 | Columns: 8
Duplicate of data/raw_oqmd.csv. Same content, same quality issues.
No scripts consume this bin/ copy.

---

### bin/raw_jarvis.csv
Rows: 0 | Columns: 7
Duplicate of data/raw_jarvis.csv. Empty. No scripts consume it.

---

### bin/processed_candidate_properties-MP.csv
Rows: 91 | Columns: 13
Schema: identical to data/processed_candidate_properties.csv.
This appears to be the processed output of the 91-row MP-only data.
data/processed_candidate_properties.csv has only 54 rows because bulk_modulus
dropna reduced the set. This bin/ version retains all 91 rows, suggesting it was
produced by a slightly different version of calculate_properties.py that did not
drop NaN bulk_modulus rows (or it used the placeholder fill before dropping).

Quality issues:
- 37 extra rows compared to the canonical processed file. Those 37 have placeholder
  shear_modulus (80.0), density (9.0), volume (15.0) and thus unreliable elastic_modulus,
  thermal_conductivity, CTE values.
- No script currently reads this bin/ copy. It is a reference artefact.

---

### bin/EXP-GE_RefractoryAlloyScreeningDataset_FINAL.csv
Rows: 86 | Columns: 12

| Column | Type | Materials Science Meaning | Source |
|---|---|---|---|
| Hf(at%) | float | Hafnium atomic percent | EXP (GE Research) |
| Mo(at%) | float | Molybdenum atomic percent | EXP |
| Nb(at%) | float | Niobium atomic percent | EXP |
| Re(at%) | float | Rhenium atomic percent | EXP |
| Ru(at%) | float | Ruthenium atomic percent | EXP |
| Ta(at%) | float | Tantalum atomic percent | EXP |
| Ti(at%) | float | Titanium atomic percent | EXP |
| W(at%) | float | Tungsten atomic percent | EXP |
| Zr(at%) | float | Zirconium atomic percent | EXP |
| Ductility Ranking (0-5) | int | 0=brittle, 5=highly ductile. Ductility is critical for HEA processability. | EXP |
| Predicted Solidus (°C) | float | Computational solidus temperature. Higher is better for turbines. | EXP/SYN |
| Hardness (GPa) | float | Measured hardness. YS ≈ Hardness×3 GPa roughly. | EXP |

Quality issues:
- Contains Re and Ru columns — elements NOT in the target 9-element set. test_exp.py
  found zero rows where Re(at%)=0 AND Ru(at%)=0 simultaneously for all non-target
  elements. This dataset has no rows usable as direct Mo-Nb-Ta-W-Cr-V-Ti-Zr-Hf anchors.
- Fractions are in at% (0-100 scale), not fractional (0-1 scale). Scripts would need
  to divide by 100 before using as input to any model expecting 0-1 fractions.
- No yield strength column — only hardness and ductility ranking.
- This dataset was intended as a transfer-learning supplement for the YS model but
  test_exp.py confirmed it contributes zero target-element-matching rows.

Scripts that consume this file:
- scripts/test_exp.py — reads and filters. Reports zero matching rows. No downstream use.
- No other script uses this file currently. Potential anchor for hardness/ductility
  transfer learning if a model for those properties were added.

---

## Cross-file inconsistencies summary

| Inconsistency | Files involved | Impact |
|---|---|---|
| bulk_modulus column present in data/ files but absent in raw_oqmd.csv | data/raw_oqmd.csv vs data/combined_raw_data.csv | OQMD rows dropped from training |
| volume column: cell volume in raw_oqmd.csv vs per-atom in calculate_properties.py | data/raw_oqmd.csv | Debye temperature wrong if OQMD rows survived |
| CTE element coverage: 7 elements in calculate_properties.py vs 5 in train_composition_ml.py estimate_cte | data/processed_candidate_properties.csv vs models/ml_predictions.csv | CTE inconsistent between the two CSV outputs |
| thermal_conductivity: computed at T=1000K in calculate_properties.py vs layer_position=0 at T=1400K proxy in train_composition_ml.py | data/processed_candidate_properties.csv vs models/ml_predictions.csv | Values from the two files are not directly comparable |
| V/Ti/Zr/Hf: present as columns in models/ml_predictions.csv (all zero) but absent from data/all_compositions-generated.csv | Both files | Suggest 9-element coverage when only 5-element data exists |
| formula column: human-readable strings in all CSVs but dict-string in data/processed_candidate_properties.csv composition column | data/processed_candidate_properties.csv | composition column is unparseable without eval(); scripts bypass it by re-parsing formula |
| SF threshold: 1.45 in evaluate_candidates.py vs 1.50 stated in all documentation | models/top_50_candidates.csv | Safran candidates could be below the claimed threshold |
