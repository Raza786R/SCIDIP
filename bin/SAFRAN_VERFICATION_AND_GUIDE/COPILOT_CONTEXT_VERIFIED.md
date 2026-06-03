# COPILOT_CONTEXT.md — HE-MCGA Project Context for AI Coding Agent
**Read this before every session. Do not modify this file.**

---

## What This Project Does
Inverse design of a Refractory High-Entropy Alloy (RHEA) for aerospace turbine blade
coatings. The alloy must survive 10,000 thermal cycles between 300K and 1400K bonded to
a Lanthanum Zirconate (LZO) ceramic, with a Safety Factor >= 1.50 under combined loading.
This is a submission to the Safran Explore Smart Materials Challenge 2026 (Challenge 2).

## Repo Layout (Root = repo root, run all commands from here)
```
scripts/        All pipeline and optimisation Python scripts
data/           Intermediate CSVs (compositions, filtered, processed)
models/         ML model artefacts and scored candidate CSVs
bin/            Raw fetch artefacts and utility scripts
phase_wise_analysis/  Validation scripts and Bohrium-phase outputs
docs/           Background docs only — NOT authoritative on code state
```

## The Current Best Candidate (Bohrium-Validated, External)
Composition: Ta0.16 W0.11 Cr0.27 V0.15 Ti0.13 Hf0.18 + 2.8% Al
Coating: LZO ceramic, FGM gradient exponent n=1.1, thickness 5mm
Safety Factor: 1.66 (after geometric fixes — root smoothing + film cooling)
Source: stage1_optimizer_with_constraints.py stdout + Bohrium cloud validation.
**This composition is NOT yet in any CSV file. It must be manually preserved.**

---

## The Single Source of Truth for Element Order
`ALL_ELEMENTS = ['Mo', 'Nb', 'Ta', 'W', 'Cr', 'V', 'Ti', 'Zr', 'Hf']`
Defined in: scripts/train_composition_ml.py
**Never reorder, rename, or add to this list without updating every script that uses it.**

## The Single Source of Truth for Physical Constants
`ELEMENT_DATA` dict in scripts/train_composition_ml.py contains:
- r (atomic radius Å), X (electronegativity), VEC, Tm (melting point K), mass (g/mol), K (bulk modulus GPa)
**Never change these values. They are literature constants.**

## Key Engineering Variables
- delta: atomic size mismatch %. Must be < 6.6% for BCC solid solution.
- Hmix: mixing enthalpy kJ/mol. Must be in [-15, +5] for phase stability.
- VEC: valence electron concentration. Must be < 6.8 for BCC, avoid [6.8, 8.2] sigma phase range.
- CTE: coefficient of thermal expansion µm/m/K. Must be close to LZO (9.1 µm/m/K) at interface.
- SF: Safety Factor = YS_hot / interface_stress_MPa. Must be >= 1.50 (Safran requirement).
- density: g/cm³. Must be < 11.0 for aerospace weight budget.

## What Copilot Must NEVER Change
- The `ALL_ELEMENTS` list order in any script
- The `ELEMENT_DATA` dict values
- The `solve_1d_thermoelastic_surrogate()` function signature in run_1d_fea.py
- Any CSV column names (downstream scripts depend on exact column strings)
- The ML model interfaces (train_model, load_experimental_data return signatures)
- Any existing logging / print statements
- The CERAMIC_MATERIALS dict in run_1d_fea.py

## What Copilot Must ALWAYS Do
- Check for NaN and non-positive values before division or passing to FEA
- Use `row.get(f'{el}_frac', 0.0)` pattern (not `row[f'{el}_frac']`) for 9-element lookups
- Use `Path(__file__).parent.parent / 'data'` for data/ paths when script is in scripts/
- Use `Path(__file__).parent.parent / 'models'` for models/ paths when script is in scripts/
- Keep all changes surgical — edit only the exact lines specified in the task
- Show a diff before applying any change

## Critical Known State of Key Files
- scripts/run_1d_fea.py line 116: uses np.trapz (REMOVED in NumPy 2.0) — crashes on import
- models/top_50_candidates.csv: EMPTY — pipeline has not produced valid output yet
- models/top1_manufacturing_recipe.csv: INVALID — shows Nb=80% (not a true HEA)
- scripts/empirical_filter.py: reads from wrong path (scripts/ instead of data/)
- scripts/generate_compositions.py: writes to wrong path and filename
- scripts/train_composition_ml.py: never calls pickle.dump — model not saved
- evaluate_candidates.py SF threshold: 1.45 in code, must be 1.50 (Safran requirement)
- evaluate_candidates.py HEA filter: requires Mo/Nb/Ta/W/Cr all > 0 — misses Ta-W-Cr-V-Ti-Hf

## Dependency Chain (Fix in This Order)
FIX-1 (np.trapz) → unblocks FEA → unblocks Steps 6, 8, 9, 10
FIX-2,3 (paths) → unblocks Steps 3, 4
FIX-4,5 (HEA filter + neg E guard) → makes evaluate_candidates.py produce real output
FIX-6,7 (thermal physics) → makes CTE/conductivity correct for 9-element compositions
FIX-8 (pickle.dump) → model persistence works
FIX-9 (CALPHAD composition) → CALPHAD validates correct alloy when TDB available
FIX-10 to FIX-14 → safety and correctness improvements

## SF Threshold: Always 1.50, Not 1.45
The Safran requirement is SF >= 1.50. The code currently uses 1.45 in evaluate_candidates.py.
This is a submission risk. SF_MIN must be corrected to 1.50 as part of the fix sequence.
